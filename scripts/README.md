# scripts

Small tools for the Rapid Upskilling Pipeline. They use only the Python standard library (or plain shell), and need Python 3.10 or newer. They run offline by default, and are released under [CC0 1.0](../LICENSE.md). Check your version with `python3 --version`. On an older Python, the site tools and `run_all.py` stop with one line on standard error and exit with status 2.

## Folder layout

| Folder | What it holds |
|---|---|
| `s1/` to `s5/` | Scripts for pipeline stages 1 to 5, one folder per stage |
| `ca/` | Certification alignment scripts |
| `dl/` | Delivery scripts |
| `op/` | Operating-practice scripts |
| `common/` | Shared helpers such as `llm_adapter.py`, published with the operating-practice scripts |
| `sample_data/` | The fictional running example, "Git Basics for New Team Members" |
| `site/` | Tools that build and check the documentation site (`sitelib.py`, `sync.py`, `check.py`) |
| `tests/` | Offline unit tests and the runner `run_all.py` |

Stage folders are added as scripts arrive, so not all of them may exist yet.

## Run the tests

```bash
python3 -B scripts/tests/run_all.py
```

The command works from any directory. It needs no network, no API key and no installs, prints one summary line, and exits 1 on any failure or error. On macOS, one skipped test is normal, because it needs a case-sensitive file system. The `-B` flag stops Python from writing `__pycache__` folders.

## Script header

Every script opens with a header: the module docstring in Python, or leading `# Key: value` comment lines in shell. Each field is written `Key: value`, and an indented line continues the value. Required fields are `ID` (`X-<stage code>-<nn>`, for example `X-OP-01`), `Purpose`, `Usage`, `Dependencies` (`stdlib` or a list), `Writes files` (`yes` or `no`) and `License` (`CC0-1.0`). `Title`, `Stage`, `Inputs` and `Outputs` are optional. The site tools turn the header into a page for the script, so keep it accurate. The full rules are in [Authoring conventions](../docs/contributing/authoring-conventions.md).

## Safety defaults

- Anything that writes or deletes files is a dry run unless `--write` is passed.
- Keys and other settings come only from environment variables, never from files, arguments or logs.

## LLM adapter

`common/llm_adapter.py` gives every script one function, `complete(prompt)`. The default `mock` provider is deterministic and offline. To reach a real model, set `LLM_PROVIDER=openai_compatible`, `LLM_BASE_URL`, `LLM_MODEL` and, if the server needs one, `LLM_API_KEY`. Try the mock provider:

```bash
python3 -B scripts/common/llm_adapter.py --prompt "Hello"
```
