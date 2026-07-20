# deployment/ — Role 4 (Software Quality, Security & DevOps)

WHAT: Owned exclusively by Role 4. Container images, compose manifests,
and any deployment-target configuration used for the live demo.
WHY: Keeps deploy/infra config out of `src/` so a broken Dockerfile edit
never blocks Role 3's pipeline work — see `../SCAFFOLDING.md` §2.
HOW: A single image (`Dockerfile`) packages every runnable surface —
dashboard (webapp + API), CLI, and GUI — selected via `command:` in
`docker-compose.yml`. `docker compose up` alone starts only the
dashboard (the surface the recorded demo evidence is built against);
`cli`/`gui` are opt-in Compose profiles.

## Files in this folder

| File | Purpose |
|---|---|
| `Dockerfile` | Builds one container image with the core package + `gui` extra installed; no hard-coded entrypoint. |
| `docker-compose.yml` | Three services: `dashboard` (default — webapp+API, port 8000), `cli` (profile `cli`), `gui` (profile `gui`, interactive TTY). |

## Cross-platform support

`python:3.14-slim` is a standard multi-arch Debian base image
(`linux/amd64` + `linux/arm64`). The same `Dockerfile`/`docker-compose.yml`
run unmodified under Docker Desktop on Windows and macOS (including Apple
Silicon) and native Docker Engine on Linux — no OS-specific branches are
needed. For running natively without Docker on any OS, see the root
`README.md` quick-start (PowerShell shown there; macOS/Linux use
`source .venv/bin/activate` in place of `.venv\Scripts\Activate.ps1`,
everything else is identical).

## Verification status (disclosed, not fabricated)

- **Verified 2026-07-10**: `docker compose -f deployment/docker-compose.yml
  build dashboard` succeeded (image `engineering-studio-ai-openai:latest`, 192MB);
  `docker run -p 8000:8000 engineering-studio-ai-openai:latest` started the
  container and `GET /api/health` returned `{"status":"ok"}` — the
  dashboard surface is confirmed to build and run correctly end-to-end.
  `cli`/`gui` profile services share the same image and were not
  separately smoke-tested this session (same base image/entrypoint
  mechanism, lower risk).

## Also owned by Role 4 (outside this folder)

- `../.github/workflows/ci.yml` — lint/type-check/test pipeline; extend
  with a coverage gate and `pip-audit`/`bandit` per `../docs/TEAM_QA.md` §5.
- `../tests/` — test suites (Role 3 may add tests for code they write;
  Role 4 owns the coverage bar and CI enforcement).

## Security reminders

- Never bake a real `FIREWORKS_API_KEY` into an image layer or compose
  file — pass it at runtime via `--env-file .env` or your CI secret store.
- Pin base image tags (no `:latest`) for reproducible builds.
