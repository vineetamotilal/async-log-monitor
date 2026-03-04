# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /app

# Install dependencies into a separate layer for caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.13-slim AS runtime

# Non-root user for security
RUN useradd --create-home --shell /bin/bash monitor

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# Copy application source code
COPY src/ ./src/

# Directory where real log files can be mounted at runtime
RUN mkdir -p /logs && chown monitor:monitor /logs

USER monitor

# The container monitors log files mounted into /logs.
# Override CMD or set LOG_DIR env var to point at your real logs.
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "src.orchestrator"]
