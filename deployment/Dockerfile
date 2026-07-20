# WHAT: Single container image for every Engineering Studio AI surface:
#       the dashboard (webapp + API, one FastAPI app), the CLI, the SDK
#       (used programmatically inside the image), and the `textual` GUI.
# WHY:  One reproducible image for the live hackathon demo instead of a
#       CLI-only image that didn't match the recorded dashboard demo
#       (see markdowns/investigations/INVESTIGATE_2026-07-10_...
#       gap G2). `python:3.14-slim` is a standard multi-arch Debian base
#       (linux/amd64 + linux/arm64), so this same image runs unmodified
#       under Docker Desktop on Windows and macOS (incl. Apple Silicon)
#       and native Docker Engine on Linux.
# HOW:  Installs the src-layout package + core deps + the lightweight
#       `gui` extra (textual). The Playwright `e2e` extra is
#       deliberately NOT installed here (dev/test-only, adds a large
#       browser download judges don't need to run the app).
#       `docker-compose.yml` picks which surface to run via `command:`.
#
# Build:  docker build -t engineering-studio-ai-openai -f deployment/Dockerfile .
# Multi-arch build (optional): docker buildx build --platform linux/amd64,linux/arm64 -t engineering-studio-ai-openai -f deployment/Dockerfile .
#
# Run examples (see docker-compose.yml for the packaged versions):
#   Dashboard (webapp + API):
#     docker run --env-file .env -p 8000:8000 engineering-studio-ai-openai \
#       uvicorn engineering_studio.webapp:app --host 0.0.0.0 --port 8000
#   CLI:
#     docker run --env-file .env engineering-studio-ai-openai \
#       python -m engineering_studio.cli run "Design a warehouse robot"
#   GUI (needs an interactive TTY):
#     docker run -it --env-file .env engineering-studio-ai-openai \
#       python -m engineering_studio.gui

FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml requirements.txt ./
COPY src/ ./src/

RUN pip install --no-cache-dir -e ".[gui]" -r requirements.txt

EXPOSE 8000

# No hard-coded ENTRYPOINT: each surface (dashboard/CLI/GUI) is chosen via
# `command:` in docker-compose.yml, or an explicit `docker run ... <cmd>`.
CMD ["uvicorn", "engineering_studio.webapp:app", "--host", "0.0.0.0", "--port", "8000"]
