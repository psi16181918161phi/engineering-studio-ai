# deployment/ — Role 4 (Software Quality, Security & DevOps)

WHAT: Owned exclusively by Role 4. Container images, compose manifests,
and any deployment-target configuration used for the live demo.
WHY: Keeps deploy/infra config out of `src/` so a broken Dockerfile edit
never blocks Role 3's pipeline work — see `../SCAFFOLDING.md` §2.
HOW: Starter files below assume the CLI-based demo
(`python -m engineering_studio.cli "<brief>"`); adapt if Role 5 adds a web
service (see `../backend/README.md`).

## Files in this folder

| File | Purpose |
|---|---|
| `Dockerfile` | Builds a container that runs the CLI pipeline. |
| `docker-compose.yml` | Local multi-service compose (extend if a `backend/api/` service is added). |

## Also owned by Role 4 (outside this folder)

- `../.github/workflows/ci.yml` — lint/type-check/test pipeline; extend
  with a coverage gate and `pip-audit`/`bandit` per `../docs/TEAM_QA.md` §5.
- `../tests/` — test suites (Role 3 may add tests for code they write;
  Role 4 owns the coverage bar and CI enforcement).

## Security reminders

- Never bake a real `FIREWORKS_API_KEY` into an image layer or compose
  file — pass it at runtime via `--env-file .env` or your CI secret store.
- Pin base image tags (no `:latest`) for reproducible builds.
