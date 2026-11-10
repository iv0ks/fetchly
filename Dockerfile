# syntax=docker/dockerfile:1

# ---- Stage 1: build dependencies into a wheel cache ------------------------
FROM python:3.12-slim AS builder

# Apply available OS security patches before building dependencies.
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Install dependencies into a dedicated prefix we can copy into the runtime
# image. Keeping this in its own stage keeps the final image small.
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: minimal runtime ---------------------------------------------
FROM python:3.12-slim AS runtime

# Apply available OS security patches on top of the base image. This picks up
# fixes (e.g. zlib1g) that are released between base-image updates, keeping the
# scanned runtime image free of fixable OS CVEs. apt lists are removed to keep
# the image small.
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to run the app.
RUN useradd --create-home --uid 10001 appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/install/bin:${PATH}" \
    PYTHONPATH="/install/lib/python3.12/site-packages:/app" \
    DATA_ROOT="/app"

WORKDIR /app

# Bring in the pre-built dependencies from the builder stage.
COPY --from=builder /install /install

# Copy application code and the served documents.
COPY app ./app
COPY docs ./docs

# Bake the challenge flag INTO the image at build time, at /app/flag.txt —
# OUTSIDE the served docs/ directory on purpose, so path traversal has a target.
# The flag is intentionally NOT committed to the repo (it would spoil the lab).
#
# We create it here (rather than relying on the app's startup seed) because the
# container runs with a read-only root filesystem, so the app cannot write it
# at runtime. When running straight from Python the app seeds it itself; here
# it already exists, so that seed is a no-op. Override with --build-arg FLAG=...
ARG FLAG=FLAG{FETCHLY_UNLOCKED_THE_VAULT}
RUN printf '%s\n' "$FLAG" > /app/flag.txt

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://127.0.0.1:5000/healthz').read()==b'ok' else sys.exit(1)"

# Serve with gunicorn (production WSGI server) rather than Flask's dev server.
# --worker-tmp-dir /tmp keeps things working under a read-only root filesystem
# (see docker-compose.yml: read_only + tmpfs /tmp).
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", \
     "--worker-tmp-dir", "/tmp", "app.main:app"]
