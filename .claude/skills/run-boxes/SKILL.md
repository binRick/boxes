---
name: run-boxes
description: Build, run, and drive Boxes.py. Use when asked to start the web server, run a box generator, render an SVG, test a generator change, or run the test suite.
---

Boxes.py is a Python box-generator framework with two entry points: a
web server (`scripts/boxesserver`, plain WSGI on `wsgiref`) and a CLI
(`scripts/boxes`). Both run straight from the repo — no build step.
Drive the server with `curl`; the smoke driver at
`.claude/skills/run-boxes/smoke.sh` does launch → drive → teardown in
one shot.

All paths below are relative to the repo root.

## Setup

One-time: create a venv and install deps (system Python lacks `qrcode`
and friends — `import boxes` fails without this).

```bash
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
.venv/bin/python -c "import boxes"   # should print nothing
```

Verified with Python 3.14 (Homebrew) on macOS.

## Run (agent path)

Smoke test — creates the venv if missing, starts the server on port
8765, hits the homepage, a generator page, and renders an SVG, then
kills the server. Prints `PASS` on success:

```bash
.claude/skills/run-boxes/smoke.sh          # optional arg: port
```

To keep a server running and poke it by hand:

```bash
.venv/bin/python scripts/boxesserver --port 8000 &
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/          # 200
curl -s "http://localhost:8000/UniversalBox?x=100&y=100&h=100&render=1" \
  -o /tmp/box.svg                          # ~33 KB SVG
```

URL shape: `/<GeneratorName>` is the parameter form,
`&render=1` plus the generator's args returns the rendered file.
`--help` shows `--host`, `--port`, `--url_prefix`, `--static_path`.

CLI path — render a box without the server:

```bash
.venv/bin/python scripts/boxes --list                # all generators
.venv/bin/python scripts/boxes UniversalBox --x 100 --y 100 --h 100 \
  --output /tmp/cli_box.svg
```

## Run (human path)

```bash
.venv/bin/python scripts/boxesserver   # serves http://localhost:8000, Ctrl-C to stop
```

## Test

`pytest` and `lxml` are needed but are NOT in `requirements.txt`:

```bash
.venv/bin/pip install -q pytest lxml
.venv/bin/python -m pytest tests/ -q   # 193 passed, 9 skipped in ~4s
```

## Gotchas

- **`import boxes` fails on system Python** with
  `ModuleNotFoundError: No module named 'qrcode'` — the package
  imports its full dependency tree at import time. Always use the
  venv.
- **Test deps are undeclared** — `tests/test_svg.py` needs `lxml`,
  and `pytest` itself isn't in `requirements.txt`. Install both
  before running the suite.
- **Server logs to stderr** — request lines
  (`127.0.0.1 - - [...] "GET / ..."`) appear on stderr, which is
  normal, not an error.
- **`curl ... | grep -q` under `set -o pipefail` false-fails** —
  `grep -q` exits at first match, curl gets SIGPIPE, the pipeline
  reports failure on a successful match. Capture into a variable
  first (the smoke script does this).
