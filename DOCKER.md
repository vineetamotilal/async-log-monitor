# 🐳 Docker Guide — Async Log Monitor

This guide walks through everything you need to get **Async Log Monitor** running inside Docker — from building the image to simulating log events.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and **running**
- Verify your installation:
  ```bash
  docker --version
  docker compose version
  ```

---

## Project Structure (Docker-relevant files)

```text
async-log-monitor/
├── Dockerfile            # Two-stage build: builder + slim runtime image
├── docker-compose.yml    # Orchestrates the container with volume mounts & env vars
├── .dockerignore         # Files excluded from the Docker build context
├── requirements.txt      # Python dependencies installed during build
└── logs/                 # 📂 Mount point — place your .jsonl log files here
    └── test_app.jsonl    # Example log file for testing
```

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/vineetamotilal/async-log-monitor.git
cd async-log-monitor
```

---

## Step 2 — Create the `logs/` Directory

The container reads log files from a mounted `./logs` directory on your machine.
Create it and add a starter log file:

**Linux / macOS / Git Bash:**
```bash
mkdir -p logs
echo '{"timestamp": "2024-01-01T00:00:00Z", "level": "INFO", "message": "App started"}' >> logs/test_app.jsonl
```

**Windows PowerShell:**
```powershell
mkdir logs
echo '{"timestamp": "2024-01-01T00:00:00Z", "level": "INFO", "message": "App started"}' >> logs\test_app.jsonl
```

> ⚠️ The container will crash if the `logs/` directory doesn't exist, because `docker-compose.yml` mounts it at startup.

---

## Step 3 — Build the Docker Image

This compiles your `Dockerfile` into a local image called `async-log-monitor:latest`.

```bash
docker compose build
```

What happens under the hood:
1. **Stage 1 (builder):** Installs Python dependencies from `requirements.txt`
2. **Stage 2 (runtime):** Copies only the installed packages + `src/` into a slim image, running as a non-root `monitor` user for security

> You only need to re-run `docker compose build` when you change `requirements.txt`, `Dockerfile`, or `src/` code.

---

## Step 4 — Start the Container

```bash
docker compose up
```

You should see output like:
```
async-log-monitor  | 🚀 Starting Async Log Monitor Orchestrator...
async-log-monitor  | 📂 Docker mode: watching log files in '/logs'
async-log-monitor  | 👀 Started monitoring: /logs/test_app.jsonl (Parser: JSONLogParser)
```

The monitor is now **tailing** every `.jsonl` file inside your local `logs/` folder in real time.

### Build + Start in one command (first-time or after code changes)

```bash
docker compose up --build
```

### Run in the background (detached mode)

```bash
docker compose up -d
```

---

## Step 5 — Simulate Log Events

Open a **second terminal** in the repo root and append JSON log lines to any file inside `logs/`.

**Append an INFO log:**

Linux/macOS:
```bash
echo '{"level": "INFO", "message": "User logged in"}' >> logs/test_app.jsonl
```
Windows PowerShell:
```powershell
echo '{"level": "INFO", "message": "User logged in"}' >> logs\test_app.jsonl
```

**Trigger the `@threshold_alert` decorator** (run this 3+ times rapidly):

Linux/macOS:
```bash
echo '{"level": "ERROR", "message": "Simulated failure"}' >> logs/test_app.jsonl
```
Windows PowerShell:
```powershell
echo '{"level": "ERROR", "message": "Simulated failure"}' >> logs\test_app.jsonl
```

You will see the alert fire in the container terminal:
```
🔥 [ALERT TIER 1] Error detected in /logs/test_app.jsonl! Log entry: ERROR - ...
```
After 3 errors within 10 seconds, the throttle kicks in and suppresses further spam.

---

## Step 6 — View Container Logs

If running detached (`-d`), stream logs with:

```bash
docker compose logs -f
```

Press `Ctrl+C` to stop streaming (the container keeps running).

---

## Step 7 — Stop the Container

```bash
docker compose down
```

This stops and removes the container (but **not** the image or your `logs/` files).

---

## Useful Docker Commands Cheat Sheet

| Command | Description |
|---|---|
| `docker compose build` | Build the image from `Dockerfile` |
| `docker compose up` | Start the container (foreground) |
| `docker compose up --build` | Rebuild image and start |
| `docker compose up -d` | Start in background (detached) |
| `docker compose down` | Stop and remove the container |
| `docker compose logs -f` | Stream live container logs |
| `docker compose ps` | Show running containers |
| `docker images` | List all local Docker images |
| `docker rmi async-log-monitor:latest` | Delete the built image |

---

## How the Volume Mount Works

```yaml
# From docker-compose.yml
volumes:
  - ./logs:/logs:ro   # your local ./logs → /logs inside container (read-only)
```

- Files you add to `./logs/` on your machine instantly appear at `/logs/` inside the container
- `:ro` means the container can **read** but not **modify** your log files (safe by default)
- The orchestrator is configured via `LOG_DIR=/logs` (set in `docker-compose.yml`) to watch this path

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `PermissionError: 'test_app.jsonl'` | Make sure `LOG_DIR=/logs` is in `docker-compose.yml` environment section |
| `logs/` volume not found | Run `mkdir logs` in the repo root before `docker compose up` |
| Container exits immediately | Check logs with `docker compose logs` for the Python traceback |
| Changes to `src/` not reflected | Run `docker compose up --build` to force a rebuild |
| `version` attribute warning in compose | Safe to ignore — it's a deprecated field in newer Docker versions |
