"""
ID: X-OP-01
Title: LLM adapter with mock and OpenAI-compatible providers
Stage: OP
Purpose: Give every script one function, complete(prompt), that returns text
    from a language model. The default mock provider is deterministic and
    offline, so tests and dry runs need no network and no key.
Usage: python3 scripts/common/llm_adapter.py --prompt TEXT [--provider NAME]
    In Python, call complete(prompt) and use the returned text.
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: The prompt, plus the environment variables LLM_PROVIDER,
    LLM_BASE_URL, LLM_MODEL and LLM_API_KEY.
Outputs: The completion text, printed to standard output by the command line.

The provider is the provider argument if given, else the LLM_PROVIDER
environment variable, else mock.

- mock returns `MOCK:` followed by the first 12 hex characters of the SHA-256
  of the prompt. It is deterministic and never touches the network.
- openai_compatible sends one HTTP POST to LLM_BASE_URL plus
  /chat/completions, using only urllib from the standard library. It reads
  LLM_BASE_URL and LLM_MODEL, and LLM_API_KEY when the server needs a key. The
  Authorization header is omitted when the key is empty, because local servers
  often need none. The request timeout defaults to 60 seconds.

Request and response shapes follow the widely implemented chat-completions
convention; verify against your provider's current documentation.

Settings and keys come only from environment variables. A key is never
printed, logged, put in an error message, or written to a file. Any problem
raises LLMError with a message that says what to fix. This module writes no
files.

Options accepted by complete() are temperature and max_tokens, which are sent
to the openai_compatible provider only when given, and timeout in seconds.
Every provider accepts and checks the same options, so switching providers
never needs a code change.
"""

import argparse
import hashlib
import http.client
import json
import math
import os
import sys
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlsplit

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "llm_adapter: this module needs Python 3.10 or newer, but this is "
        f"{sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

PROVIDER_ENV = "LLM_PROVIDER"
DEFAULT_PROVIDER = "mock"
PROVIDERS = ("mock", "openai_compatible")
DEFAULT_TIMEOUT = 60.0
SUPPORTED_OPTS = ("temperature", "max_tokens", "timeout")
ERROR_BODY_CHARS = 200
_BODY_READ_LIMIT = 1024


class LLMError(Exception):
    """Raised for any configuration, network, HTTP, or response problem."""


def _utf8(prompt: str) -> bytes:
    """Return the prompt as UTF-8 bytes, or raise LLMError."""
    try:
        return prompt.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise LLMError("the prompt is not valid Unicode text") from exc


def _validate_opts(opts: dict[str, Any]) -> None:
    """Reject unknown or badly typed options so typos are never ignored."""
    unknown = sorted(set(opts) - set(SUPPORTED_OPTS))
    if unknown:
        raise LLMError(
            f"unknown option(s) {', '.join(unknown)}; "
            f"supported options are {', '.join(SUPPORTED_OPTS)}"
        )
    for name in ("temperature", "timeout"):
        value = opts.get(name)
        if value is None:
            continue
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise LLMError(f"option {name} must be a finite number")
    timeout = opts.get("timeout")
    if timeout is not None and timeout <= 0:
        raise LLMError("option timeout must be greater than 0 seconds")
    max_tokens = opts.get("max_tokens")
    if max_tokens is not None and (
        isinstance(max_tokens, bool)
        or not isinstance(max_tokens, int)
        or max_tokens < 1
    ):
        raise LLMError("option max_tokens must be a positive integer")


def _snippet(raw: bytes, secret: str) -> str:
    """Return the first characters of a response body with the key hidden."""
    text = raw[:_BODY_READ_LIMIT].decode("utf-8", errors="replace")
    if secret:
        text = text.replace(secret, "[key hidden]")
    return text[:ERROR_BODY_CHARS]


def _mock(prompt: str) -> str:
    """Deterministic offline provider: MOCK: plus 12 hex of the SHA-256."""
    return "MOCK:" + hashlib.sha256(_utf8(prompt)).hexdigest()[:12]


def _endpoint(base_url: str) -> tuple[str, str]:
    """Validate LLM_BASE_URL; return (chat-completions URL, host label)."""
    try:
        parts = urlsplit(base_url)
        port = parts.port
    except ValueError as exc:
        raise LLMError("LLM_BASE_URL is not a valid URL") from exc
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise LLMError(
            "LLM_BASE_URL must start with http:// or https:// and include a host"
        )
    if parts.username or parts.password:
        raise LLMError(
            "LLM_BASE_URL must not contain a user name or password; "
            "put the key in LLM_API_KEY instead"
        )
    if parts.query or parts.fragment:
        raise LLMError("LLM_BASE_URL must not contain a query or fragment")
    host = parts.hostname + (f":{port}" if port else "")
    return base_url.rstrip("/") + "/chat/completions", host


def _settings() -> tuple[str, str, str]:
    """Read (LLM_BASE_URL, LLM_MODEL, LLM_API_KEY) from the environment."""
    base_url = os.environ.get("LLM_BASE_URL", "").strip()
    model = os.environ.get("LLM_MODEL", "").strip()
    api_key = os.environ.get("LLM_API_KEY", "").strip()
    missing = [
        name
        for name, value in (("LLM_BASE_URL", base_url), ("LLM_MODEL", model))
        if not value
    ]
    if missing:
        raise LLMError(
            "provider openai_compatible needs the environment variable(s) "
            + " and ".join(missing)
            + ". Set LLM_BASE_URL to the server address (for example "
            "http://localhost:8000/v1) and LLM_MODEL to a model name. "
            "LLM_API_KEY is optional for servers that need no key."
        )
    if api_key and not (api_key.isascii() and api_key.isprintable()):
        raise LLMError(
            "LLM_API_KEY contains control or non-ASCII characters, such as a "
            "stray newline, that cannot be sent in an HTTP header; "
            "its value is not shown"
        )
    return base_url, model, api_key


def _build_request(
    url: str, model: str, api_key: str, prompt: str, opts: dict[str, Any]
) -> urllib.request.Request:
    """Build the chat-completions POST; the key goes only in a header."""
    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }
    for name in ("temperature", "max_tokens"):
        if opts.get(name) is not None:
            payload[name] = opts[name]
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    if api_key:
        # Unredirected: urllib must not forward the key if the server redirects.
        request.add_unredirected_header("Authorization", "Bearer " + api_key)
    return request


def _send(
    request: urllib.request.Request, host: str, timeout: float, api_key: str
) -> bytes:
    """Send the request and return the raw body, or raise LLMError."""
    try:
        # The scheme was checked in _endpoint, so only http and https open.
        with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310
            body: bytes = response.read()
            return body
    except urllib.error.HTTPError as exc:
        try:
            error_body = exc.read(_BODY_READ_LIMIT)
        except (OSError, http.client.HTTPException):
            error_body = b""
        finally:
            exc.close()
        shown = _snippet(error_body, api_key) or "(empty body)"
        raise LLMError(f"HTTP {exc.code} from {host}: {shown}") from exc
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            raise LLMError(
                f"request to {host} timed out after {timeout} seconds"
            ) from exc
        raise LLMError(f"could not reach {host}: {exc.reason}") from exc
    except TimeoutError as exc:
        raise LLMError(f"request to {host} timed out after {timeout} seconds") from exc
    except (OSError, http.client.HTTPException) as exc:
        raise LLMError(f"connection to {host} failed: {exc}") from exc
    except ValueError as exc:
        raise LLMError(
            f"could not send the request to {host} ({type(exc).__name__}); "
            "check LLM_BASE_URL"
        ) from exc


def _extract(raw: bytes, host: str, api_key: str) -> str:
    """Return choices[0].message.content from a chat-completions reply."""
    try:
        content = json.loads(raw)["choices"][0]["message"]["content"]
    except (ValueError, LookupError, TypeError) as exc:
        raise LLMError(
            f"malformed response from {host}: expected JSON holding "
            f"choices[0].message.content. Body starts with: {_snippet(raw, api_key)}"
        ) from exc
    if not isinstance(content, str):
        raise LLMError(
            f"malformed response from {host}: choices[0].message.content is not text"
        )
    return content


def _openai_compatible(prompt: str, opts: dict[str, Any]) -> str:
    """Ask an OpenAI-compatible server for one completion."""
    base_url, model, api_key = _settings()
    url, host = _endpoint(base_url)
    request = _build_request(url, model, api_key, prompt, opts)
    timeout = opts.get("timeout")
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    return _extract(_send(request, host, timeout, api_key), host, api_key)


def complete(prompt: str, provider: str | None = None, **opts: Any) -> str:
    """Return one completion for the prompt.

    The provider is the argument if given, else the LLM_PROVIDER environment
    variable, else mock. Options are temperature, max_tokens and timeout (in
    seconds); anything else raises LLMError. Raises LLMError for every
    configuration, network, HTTP and response problem, and TypeError if the
    prompt is not a string.
    """
    if not isinstance(prompt, str):
        raise TypeError("prompt must be a string")
    _utf8(prompt)
    name = (
        (provider or "").strip()
        or os.environ.get(PROVIDER_ENV, "").strip()
        or DEFAULT_PROVIDER
    ).lower()
    if name not in PROVIDERS:
        raise LLMError(
            f"unknown provider {name!r}; choose one of {', '.join(PROVIDERS)}"
        )
    _validate_opts(opts)
    if name == "mock":
        return _mock(prompt)
    return _openai_compatible(prompt, opts)


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; prints the completion, returns an exit code."""
    parser = argparse.ArgumentParser(
        prog="llm_adapter.py",
        description=(
            "Print one completion for a prompt. Writes no files. "
            "Settings and keys come only from environment variables."
        ),
        epilog=(
            "environment variables: LLM_PROVIDER (mock or openai_compatible), "
            "LLM_BASE_URL, LLM_MODEL, LLM_API_KEY (optional). The "
            "openai_compatible provider follows the chat-completions "
            "convention; verify against your provider's current documentation."
        ),
    )
    parser.add_argument("--prompt", required=True, metavar="TEXT", help="prompt text")
    parser.add_argument(
        "--provider",
        metavar="NAME",
        help="mock or openai_compatible (default: LLM_PROVIDER, else mock)",
    )
    args = parser.parse_args(argv)
    try:
        text = complete(args.prompt, provider=args.provider)
    except LLMError as exc:
        print(f"llm_adapter.py: error: {exc}", file=sys.stderr)
        return 1
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
