# WHAT: Container image for the Engineering Studio AI CLI pipeline.
# WHY:  Reproducible run environment for the live hackathon demo.
# HOW:  Installs the src-layout package + runtime deps, runs the CLI.
#
# Build:  docker build -t engineering-studio-ai -f deployment/Dockerfile .
# Run:    docker run --env-file .env engineering-studio-ai "Design a warehouse robot"

FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml requirements.txt ./
COPY src/ ./src/

RUN pip install --no-cache-dir -e . -r requirements.txt

ENTRYPOINT ["python", "-m", "engineering_studio.cli"]
