"""Unit tests for scripts/common/llm_adapter.py.

Everything runs offline. The openai_compatible provider is exercised against a
throwaway HTTP server bound to 127.0.0.1 on an ephemeral port, so no request
ever leaves the machine.

Run all tests with: python3 -B scripts/tests/run_all.py
"""

import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import socket
import subprocess  # nosec B404
import sys
import tempfile
import threading
import traceback
import unittest
import urllib.request
from email.message import Message
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from types import ModuleType
from typing import Any, NamedTuple, cast
from unittest import mock

sys.dont_write_bytecode = True

ADAPTER_PATH = Path(__file__).resolve().parent.parent / "common" / "llm_adapter.py"
MODEL = "test-model"
FAKE_KEY = "unit-test-secret-value-0000"
CANNED_CONTENT = "canned completion text"


def load_adapter() -> ModuleType:
    """Import the adapter from its file, relative to this test file."""
    spec = importlib.util.spec_from_file_location("llm_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


adapter = load_adapter()


def sha12(prompt: str) -> str:
    """First 12 hex characters of the SHA-256 of the prompt."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]


class Recorded(NamedTuple):
    """One request seen by the local server."""

    method: str
    path: str
    headers: Message
    body: bytes


Reply = tuple[int, dict[str, str], bytes]


def ok_reply(content: Any = CANNED_CONTENT) -> Reply:
    """A canned chat-completions reply."""
    body = {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
    }
    return 200, {}, json.dumps(body).encode("utf-8")


class _Handler(BaseHTTPRequestHandler):
    """Record the request, then send the next scripted reply."""

    def _reply(self) -> None:
        server = cast("_RecordingServer", self.server)
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        server.requests.append(Recorded(self.command, self.path, self.headers, body))
        index = min(len(server.requests), len(server.replies)) - 1
        status, headers, payload = server.replies[index]
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        for name, value in headers.items():
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    do_GET = _reply
    do_POST = _reply

    def log_message(  # pylint: disable=redefined-builtin
        self, format: str, *args: Any
    ) -> None:
        """Keep the test output quiet."""


class _RecordingServer(HTTPServer):
    """HTTP server that keeps every request it receives."""

    def __init__(self, replies: list[Reply]) -> None:
        super().__init__(("127.0.0.1", 0), _Handler)
        self.replies = replies
        self.requests: list[Recorded] = []


class LocalServer:
    """A loopback server on an ephemeral port, run in a background thread."""

    def __init__(self, *replies: Reply) -> None:
        self._server = _RecordingServer(list(replies) or [ok_reply()])
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            kwargs={"poll_interval": 0.05},
            daemon=True,
        )

    @property
    def requests(self) -> list[Recorded]:
        """Requests received so far."""
        return self._server.requests

    @property
    def base_url(self) -> str:
        """The value to use for LLM_BASE_URL."""
        return f"http://127.0.0.1:{self._server.server_address[1]}/v1"

    def start(self) -> None:
        """Begin serving."""
        self._thread.start()

    def stop(self) -> None:
        """Stop serving and release the port."""
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)


def unused_port() -> int:
    """A loopback port on which nothing is listening."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def setUpModule() -> None:  # pylint: disable=invalid-name
    """Bypass any system proxy so loopback requests stay on this machine."""
    urllib.request.install_opener(
        urllib.request.build_opener(urllib.request.ProxyHandler({}))
    )


def tearDownModule() -> None:  # pylint: disable=invalid-name
    """Restore urllib's default opener."""
    urllib.request.install_opener(None)  # type: ignore[arg-type]


class EnvTestCase(unittest.TestCase):
    """Runs each test on a private copy of os.environ without LLM_ variables."""

    def setUp(self) -> None:
        patcher = mock.patch.dict(os.environ)
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in [name for name in os.environ if name.startswith("LLM_")]:
            del os.environ[name]


class ServerTestCase(EnvTestCase):
    """Adds a local server whose address and model go into the environment."""

    def start_server(self, *replies: Reply, key: str | None = None) -> LocalServer:
        """Start a server, point the environment at it, optionally set a key."""
        server = LocalServer(*replies)
        server.start()
        self.addCleanup(server.stop)
        os.environ["LLM_BASE_URL"] = server.base_url
        os.environ["LLM_MODEL"] = MODEL
        if key is not None:
            os.environ["LLM_API_KEY"] = key
        return server

    @staticmethod
    def ask(prompt: str = "Say hi", **opts: Any) -> str:
        """Call the openai_compatible provider."""
        return str(adapter.complete(prompt, provider="openai_compatible", **opts))


class MockProviderTests(EnvTestCase):
    """The offline provider."""

    def test_known_values(self) -> None:
        """MOCK: plus the first 12 hex characters of the SHA-256."""
        self.assertEqual(
            adapter.complete("hello", provider="mock"), "MOCK:2cf24dba5fb0"
        )
        self.assertEqual(adapter.complete("", provider="mock"), "MOCK:e3b0c44298fc")

    def test_format_and_digest(self) -> None:
        """The format is fixed and matches hashlib."""
        result = adapter.complete("Explain rebasing.", provider="mock")
        self.assertRegex(result, r"^MOCK:[0-9a-f]{12}$")
        self.assertEqual(result, "MOCK:" + sha12("Explain rebasing."))

    def test_deterministic(self) -> None:
        """The same prompt always gives the same text."""
        first = adapter.complete("same prompt", provider="mock")
        self.assertEqual(first, adapter.complete("same prompt", provider="mock"))

    def test_different_prompts_differ(self) -> None:
        """Different prompts give different text."""
        first = adapter.complete("prompt one", provider="mock")
        second = adapter.complete("prompt two", provider="mock")
        self.assertNotEqual(first, second)

    def test_unicode_prompt(self) -> None:
        """Non-ASCII text is hashed as UTF-8."""
        prompt = "caf\u00e9 \u2013 \u65e5\u672c\u8a9e \U0001f600"
        self.assertEqual(
            adapter.complete(prompt, provider="mock"), "MOCK:" + sha12(prompt)
        )

    def test_never_uses_the_network(self) -> None:
        """The mock provider does not open a connection, whatever is set."""
        os.environ["LLM_BASE_URL"] = f"http://127.0.0.1:{unused_port()}/v1"
        os.environ["LLM_MODEL"] = MODEL
        with mock.patch.object(
            urllib.request, "urlopen", side_effect=AssertionError("network used")
        ) as fake:
            adapter.complete("offline", provider="mock")
        fake.assert_not_called()

    def test_accepts_the_common_options(self) -> None:
        """Options are accepted, so providers can be swapped freely."""
        plain = adapter.complete("x", provider="mock")
        with_opts = adapter.complete(
            "x", provider="mock", temperature=0, max_tokens=5, timeout=1
        )
        self.assertEqual(plain, with_opts)

    def test_bad_options_are_rejected(self) -> None:
        """Unknown or badly typed options raise LLMError instead of vanishing."""
        cases: list[dict[str, Any]] = [
            {"max_token": 5},
            {"temperature": "hot"},
            {"temperature": True},
            {"temperature": float("nan")},
            {"max_tokens": 0},
            {"max_tokens": 1.5},
            {"max_tokens": True},
            {"timeout": 0},
            {"timeout": -1},
            {"timeout": float("inf")},
            {"timeout": "soon"},
        ]
        for opts in cases:
            with self.subTest(opts=opts), self.assertRaises(adapter.LLMError):
                adapter.complete("x", provider="mock", **opts)

    def test_prompt_must_be_text(self) -> None:
        """A non-string prompt is a programming error."""
        with self.assertRaises(TypeError):
            adapter.complete(42, provider="mock")

    def test_prompt_must_be_valid_unicode(self) -> None:
        """A lone surrogate cannot be encoded and is reported clearly."""
        with self.assertRaises(adapter.LLMError):
            adapter.complete("bad \ud800 text", provider="mock")


class ProviderSelectionTests(ServerTestCase):
    """Argument first, then LLM_PROVIDER, then mock."""

    def test_default_is_mock(self) -> None:
        """With no argument and no variable the provider is mock."""
        self.assertEqual(adapter.complete("hi"), "MOCK:" + sha12("hi"))

    def test_environment_selects_mock(self) -> None:
        """LLM_PROVIDER=mock works."""
        os.environ["LLM_PROVIDER"] = "mock"
        self.assertEqual(adapter.complete("hi"), "MOCK:" + sha12("hi"))

    def test_environment_selects_openai_compatible(self) -> None:
        """LLM_PROVIDER=openai_compatible reaches the server."""
        server = self.start_server()
        os.environ["LLM_PROVIDER"] = "openai_compatible"
        self.assertEqual(adapter.complete("hi"), CANNED_CONTENT)
        self.assertEqual(len(server.requests), 1)

    def test_argument_beats_environment(self) -> None:
        """An explicit provider overrides LLM_PROVIDER in both directions."""
        server = self.start_server()
        os.environ["LLM_PROVIDER"] = "openai_compatible"
        self.assertEqual(adapter.complete("hi", provider="mock"), "MOCK:" + sha12("hi"))
        self.assertEqual(server.requests, [])
        os.environ["LLM_PROVIDER"] = "mock"
        self.assertEqual(
            adapter.complete("hi", provider="openai_compatible"), CANNED_CONTENT
        )
        self.assertEqual(len(server.requests), 1)

    def test_empty_environment_value_means_mock(self) -> None:
        """An empty LLM_PROVIDER is treated as unset."""
        os.environ["LLM_PROVIDER"] = ""
        self.assertEqual(adapter.complete("hi"), "MOCK:" + sha12("hi"))

    def test_provider_name_is_trimmed_and_case_insensitive(self) -> None:
        """Stray spaces and capitals do not matter."""
        self.assertEqual(
            adapter.complete("hi", provider="  Mock "), "MOCK:" + sha12("hi")
        )

    def test_unknown_provider(self) -> None:
        """The message names the bad value and the valid choices."""
        with self.assertRaises(adapter.LLMError) as caught:
            adapter.complete("hi", provider="carrier-pigeon")
        message = str(caught.exception)
        self.assertIn("carrier-pigeon", message)
        self.assertIn("mock", message)
        self.assertIn("openai_compatible", message)

    def test_environment_is_restored_between_tests(self) -> None:
        """setUp starts every test without LLM_ variables."""
        self.assertEqual([n for n in os.environ if n.startswith("LLM_")], [])


class OpenAICompatibleTests(ServerTestCase):
    """The HTTP provider, against a local server."""

    def test_request_shape(self) -> None:
        """Method, path, headers and JSON body are exactly as documented."""
        server = self.start_server()
        self.assertEqual(self.ask("Say hi"), CANNED_CONTENT)
        self.assertEqual(len(server.requests), 1)
        request = server.requests[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.path, "/v1/chat/completions")
        self.assertEqual(request.headers.get("Content-Type"), "application/json")
        self.assertEqual(
            json.loads(request.body),
            {"model": MODEL, "messages": [{"role": "user", "content": "Say hi"}]},
        )

    def test_trailing_slash_in_base_url(self) -> None:
        """A trailing slash on LLM_BASE_URL does not double up."""
        server = self.start_server()
        os.environ["LLM_BASE_URL"] += "/"
        self.ask()
        self.assertEqual(server.requests[0].path, "/v1/chat/completions")

    def test_authorization_header_present_with_key(self) -> None:
        """A key is sent as a Bearer token."""
        server = self.start_server(key=FAKE_KEY)
        self.ask()
        headers = server.requests[0].headers
        self.assertEqual(headers.get("Authorization"), f"Bearer {FAKE_KEY}")

    def test_authorization_header_absent_without_key(self) -> None:
        """No key set: no Authorization header at all."""
        server = self.start_server()
        self.ask()
        self.assertNotIn("Authorization", server.requests[0].headers)

    def test_authorization_header_absent_with_empty_key(self) -> None:
        """An empty or blank key counts as no key."""
        for value in ("", "   "):
            with self.subTest(value=value):
                server = self.start_server(key=value)
                self.ask()
                self.assertNotIn("Authorization", server.requests[0].headers)

    def test_key_is_not_in_the_body(self) -> None:
        """The key travels only in the header."""
        server = self.start_server(key=FAKE_KEY)
        self.ask()
        self.assertNotIn(FAKE_KEY.encode("utf-8"), server.requests[0].body)

    def test_optional_parameters_sent_only_when_given(self) -> None:
        """temperature and max_tokens appear in the body only when given."""
        server = self.start_server()
        self.ask("p", temperature=0.2, max_tokens=50, timeout=5)
        self.ask("p", temperature=0)
        self.ask("p", temperature=None, max_tokens=None, timeout=None)
        first, second, third = (json.loads(r.body) for r in server.requests)
        self.assertEqual(first["temperature"], 0.2)
        self.assertEqual(first["max_tokens"], 50)
        self.assertNotIn("timeout", first)
        self.assertEqual(second["temperature"], 0)
        self.assertNotIn("max_tokens", second)
        self.assertNotIn("temperature", third)
        self.assertNotIn("max_tokens", third)

    def test_unicode_prompt_round_trip(self) -> None:
        """A non-ASCII prompt arrives intact."""
        server = self.start_server()
        prompt = "caf\u00e9 \u65e5\u672c\u8a9e \U0001f600"
        self.ask(prompt)
        body = json.loads(server.requests[0].body)
        self.assertEqual(body["messages"][0]["content"], prompt)

    def test_empty_completion_is_returned(self) -> None:
        """An empty string is a valid completion."""
        self.start_server(ok_reply(""))
        self.assertEqual(self.ask(), "")

    def test_redirect_does_not_forward_the_key(self) -> None:
        """If a server redirects, the Authorization header is not repeated."""
        server = self.start_server(
            (302, {"Location": "/elsewhere"}, b""), ok_reply(), key=FAKE_KEY
        )
        self.assertEqual(self.ask(), CANNED_CONTENT)
        first, second = server.requests
        self.assertEqual(first.headers.get("Authorization"), f"Bearer {FAKE_KEY}")
        self.assertEqual((second.method, second.path), ("GET", "/elsewhere"))
        self.assertNotIn("Authorization", second.headers)

    def test_timeout_option(self) -> None:
        """A server that never answers raises LLMError once the timeout passes."""
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen(1)
            port = listener.getsockname()[1]
            os.environ["LLM_BASE_URL"] = f"http://127.0.0.1:{port}/v1"
            os.environ["LLM_MODEL"] = MODEL
            with self.assertRaises(adapter.LLMError) as caught:
                self.ask(timeout=0.3)
        self.assertIn("timed out", str(caught.exception))

    def test_connection_refused(self) -> None:
        """Nothing listening: LLMError naming the host."""
        port = unused_port()
        os.environ["LLM_BASE_URL"] = f"http://127.0.0.1:{port}/v1"
        os.environ["LLM_MODEL"] = MODEL
        with self.assertRaises(adapter.LLMError) as caught:
            self.ask(timeout=5)
        self.assertIn(f"127.0.0.1:{port}", str(caught.exception))


class ErrorHandlingTests(ServerTestCase):
    """Every failure is an LLMError that says what happened, without the key."""

    def assert_no_key(self, caught: Any) -> None:
        """The key must not appear in the message, repr, or full traceback."""
        exc = caught.exception
        chain = "".join(traceback.format_exception(exc))
        for text in (str(exc), repr(exc), chain):
            self.assertNotIn(FAKE_KEY, text)

    def test_http_500_raises_without_leaking_the_key(self) -> None:
        """Status and body are reported; a key echoed by the server is hidden."""
        body = f'{{"error": "boom", "echo": "{FAKE_KEY}"}}'.encode("utf-8")
        self.start_server((500, {}, body), key=FAKE_KEY)
        with self.assertRaises(adapter.LLMError) as caught:
            self.ask()
        message = str(caught.exception)
        self.assertIn("500", message)
        self.assertIn("boom", message)
        self.assert_no_key(caught)

    def test_error_body_is_cut_to_200_characters(self) -> None:
        """Only the first 200 characters of the body are shown."""
        self.start_server((500, {}, b"x" * 500))
        with self.assertRaises(adapter.LLMError) as caught:
            self.ask()
        message = str(caught.exception)
        self.assertIn("x" * 200, message)
        self.assertNotIn("x" * 201, message)

    def test_other_http_statuses(self) -> None:
        """Client and server errors all carry their status code."""
        for status in (400, 401, 404, 429, 503):
            with self.subTest(status=status):
                self.start_server((status, {}, b'{"error": "nope"}'), key=FAKE_KEY)
                with self.assertRaises(adapter.LLMError) as caught:
                    self.ask()
                self.assertIn(str(status), str(caught.exception))
                self.assert_no_key(caught)

    def test_empty_error_body(self) -> None:
        """An empty error body still gives a readable message."""
        self.start_server((502, {}, b""))
        with self.assertRaises(adapter.LLMError) as caught:
            self.ask()
        self.assertIn("502", str(caught.exception))
        self.assertIn("empty", str(caught.exception))

    def test_malformed_responses(self) -> None:
        """Bad JSON or the wrong shape raises LLMError, never another type."""
        bodies = [
            b"not json at all",
            b"",
            b"[]",
            b"null",
            b'{"choices": "abc"}',
            b'{"choices": []}',
            b'{"choices": [{}]}',
            b'{"choices": [{"message": {}}]}',
            b'{"choices": [{"message": {"content": null}}]}',
            b'{"choices": [{"message": {"content": 42}}]}',
            b'{"choices": [{"message": {"content": ["a"]}}]}',
            b"\xff\xfe\xfd",
        ]
        for body in bodies:
            with self.subTest(body=body):
                self.start_server((200, {}, body), key=FAKE_KEY)
                with self.assertRaises(adapter.LLMError) as caught:
                    self.ask()
                self.assertIn("malformed", str(caught.exception))
                self.assert_no_key(caught)

    def test_malformed_response_hides_an_echoed_key(self) -> None:
        """The body excerpt in the message never contains the key."""
        self.start_server((200, {}, f"oops {FAKE_KEY}".encode("utf-8")), key=FAKE_KEY)
        with self.assertRaises(adapter.LLMError) as caught:
            self.ask()
        self.assertIn("oops", str(caught.exception))
        self.assert_no_key(caught)

    def test_missing_environment_variables(self) -> None:
        """Missing or empty LLM_BASE_URL or LLM_MODEL are named in the message."""
        cases = [
            ({}, ["LLM_BASE_URL", "LLM_MODEL"]),
            ({"LLM_BASE_URL": "http://127.0.0.1:1/v1"}, ["LLM_MODEL"]),
            ({"LLM_MODEL": MODEL}, ["LLM_BASE_URL"]),
            ({"LLM_BASE_URL": "", "LLM_MODEL": "  "}, ["LLM_BASE_URL", "LLM_MODEL"]),
        ]
        for env, expected in cases:
            with self.subTest(env=env):
                for name in ("LLM_BASE_URL", "LLM_MODEL"):
                    os.environ.pop(name, None)
                os.environ.update(env)
                with self.assertRaises(adapter.LLMError) as caught:
                    self.ask()
                for name in expected:
                    self.assertIn(name, str(caught.exception))

    def test_bad_base_urls(self) -> None:
        """Only plain http(s) URLs without credentials are accepted."""
        marker = "hunter2-not-a-real-password"
        urls = [
            "ftp://127.0.0.1/v1",
            "file://localhost/whatever",
            "localhost:8000/v1",
            "127.0.0.1:8000/v1",
            "http://",
            "http://127.0.0.1:notaport/v1",
            f"http://user:{marker}@127.0.0.1:1/v1",
            "http://127.0.0.1:1/v1?api_version=1",
            "http://127.0.0.1:1/v1#frag",
        ]
        os.environ["LLM_MODEL"] = MODEL
        for url in urls:
            with self.subTest(url=url):
                os.environ["LLM_BASE_URL"] = url
                with self.assertRaises(adapter.LLMError) as caught:
                    self.ask()
                self.assertIn("LLM_BASE_URL", str(caught.exception))
                self.assertNotIn(marker, str(caught.exception))

    def test_bad_api_key_is_rejected_and_not_shown(self) -> None:
        """A key that cannot go in a header fails before any request is sent."""
        for bad in ("abc\ndef", "abc\x1bdef", "caf\u00e9-key"):
            with self.subTest(bad=repr(bad)):
                server = self.start_server(key=bad)
                with self.assertRaises(adapter.LLMError) as caught:
                    self.ask()
                self.assertIn("LLM_API_KEY", str(caught.exception))
                self.assertNotIn("abc", str(caught.exception))
                self.assertNotIn("caf", str(caught.exception))
                self.assertEqual(server.requests, [])

    def test_key_with_surrounding_whitespace_is_trimmed(self) -> None:
        """A stray trailing newline from a shell is not an error."""
        server = self.start_server(key=f"  {FAKE_KEY}\n")
        self.ask()
        headers = server.requests[0].headers
        self.assertEqual(headers.get("Authorization"), f"Bearer {FAKE_KEY}")


class CommandLineTests(EnvTestCase):
    """The command line, run as a separate process."""

    def run_cli(
        self,
        *args: str,
        extra_env: dict[str, str] | None = None,
        cwd: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """Run llm_adapter.py with a clean LLM_ environment."""
        env = {k: v for k, v in os.environ.items() if not k.startswith("LLM_")}
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env.update(extra_env or {})
        return subprocess.run(  # nosec B603
            [sys.executable, "-B", str(ADAPTER_PATH), *args],
            capture_output=True,
            text=True,
            env=env,
            cwd=cwd,
            timeout=60,
            check=False,
        )

    def test_help_exits_zero(self) -> None:
        """--help works and documents the options."""
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--prompt", result.stdout)
        self.assertIn("--provider", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_prints_the_mock_completion(self) -> None:
        """--prompt with the default provider prints MOCK: and the digest."""
        result = self.run_cli("--prompt", "hello")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "MOCK:2cf24dba5fb0\n")
        self.assertEqual(result.stderr, "")

    def test_provider_option_and_environment(self) -> None:
        """--provider and LLM_PROVIDER both select the mock provider."""
        by_option = self.run_cli("--prompt", "hello", "--provider", "mock")
        by_env = self.run_cli("--prompt", "hello", extra_env={"LLM_PROVIDER": "mock"})
        self.assertEqual(by_option.stdout, by_env.stdout)
        self.assertEqual(by_option.returncode, 0)

    def test_configuration_error_exits_one_without_traceback(self) -> None:
        """A missing setting is reported on stderr, not as a traceback."""
        result = self.run_cli("--prompt", "hello", "--provider", "openai_compatible")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("LLM_BASE_URL", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_missing_prompt_is_a_usage_error(self) -> None:
        """No --prompt exits with argparse's usage code."""
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn("--prompt", result.stderr)

    def test_writes_no_files(self) -> None:
        """Running in an empty folder leaves it empty."""
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        self.run_cli("--prompt", "hello", cwd=folder)
        self.run_cli("--prompt", "hello", "--provider", "nope", cwd=folder)
        self.assertEqual(os.listdir(folder), [])


class CommandLineServerTests(ServerTestCase):
    """main() called in-process against the local server."""

    def test_prints_the_server_completion(self) -> None:
        """The completion is printed on stdout and the exit code is 0."""
        self.start_server(key=FAKE_KEY)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = adapter.main(["--prompt", "hi", "--provider", "openai_compatible"])
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue(), CANNED_CONTENT + "\n")

    def test_http_error_exits_one_and_hides_the_key(self) -> None:
        """A server error becomes exit code 1 and a message on stderr."""
        self.start_server((500, {}, FAKE_KEY.encode("utf-8")), key=FAKE_KEY)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = adapter.main(["--prompt", "hi", "--provider", "openai_compatible"])
        self.assertEqual(code, 1)
        self.assertEqual(out.getvalue(), "")
        self.assertIn("500", err.getvalue())
        self.assertNotIn(FAKE_KEY, err.getvalue())


KEY_LINE = re.compile(r"^([A-Za-z][A-Za-z ]*):[ \t]*(.*)$")
REQUIRED_KEYS = ("ID", "Purpose", "Usage", "Dependencies", "Writes files", "License")


class HeaderTests(unittest.TestCase):
    """The module docstring is a valid script header."""

    source = ADAPTER_PATH.read_text(encoding="utf-8")
    docstring = ast.get_docstring(ast.parse(source)) or ""

    def parse_header(self) -> tuple[dict[str, str], list[str]]:
        """Split the docstring into Key: value fields and the prose after them."""
        fields: dict[str, str] = {}
        current = ""
        lines = self.docstring.splitlines()
        for number, line in enumerate(lines):
            if not line.strip():
                rest = number + 1
                return fields, lines[rest:]
            if line[0] in " \t":
                if not current:
                    self.fail(f"continuation line before any key: {line!r}")
                fields[current] += " " + line.strip()
                continue
            match = KEY_LINE.match(line)
            if match is None:
                self.fail(f"header line is not 'Key: value': {line!r}")
            current = match.group(1)
            fields[current] = match.group(2).strip()
        return fields, []

    def test_required_fields_and_values(self) -> None:
        """Every required key is present with the expected value."""
        fields, _ = self.parse_header()
        for key in REQUIRED_KEYS:
            self.assertTrue(fields.get(key), f"missing header field {key}")
        self.assertEqual(fields["ID"], "X-OP-01")
        self.assertEqual(fields["Stage"], "OP")
        self.assertTrue(fields["Title"])
        self.assertEqual(fields["Dependencies"], "stdlib")
        self.assertEqual(fields["Writes files"], "no")
        self.assertEqual(fields["License"], "CC0-1.0")
        self.assertTrue(fields["Usage"].startswith("python3 "))

    def test_prose_after_the_header_never_looks_like_a_field(self) -> None:
        """No flush-left prose line could be mistaken for 'Key: value'."""
        _, prose = self.parse_header()
        self.assertTrue(prose, "expected explanatory text after the header")
        for line in prose:
            self.assertIsNone(KEY_LINE.match(line), line)

    def test_states_the_verification_caveat(self) -> None:
        """The docstring carries the required provider-documentation caveat."""
        flat = " ".join(self.docstring.split())
        self.assertIn(
            "Request and response shapes follow the widely implemented "
            "chat-completions convention; verify against your provider's "
            "current documentation.",
            flat,
        )

    def test_only_standard_library_imports(self) -> None:
        """Every import resolves to a standard-library module."""
        names: set[str] = set()
        for node in ast.walk(ast.parse(self.source)):
            if isinstance(node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                names.add(node.module.split(".")[0])
        self.assertTrue(names)
        self.assertEqual(names - set(sys.stdlib_module_names), set())

    def test_disables_bytecode_writing(self) -> None:
        """The module sets sys.dont_write_bytecode."""
        self.assertIn("sys.dont_write_bytecode = True", self.source)


if __name__ == "__main__":
    unittest.main()
