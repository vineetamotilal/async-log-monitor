# Async Log Monitor 🛡️

**Async Log Monitor** is a distributed log monitoring engine built with expert-level Python design patterns. It efficiently tracks application log files in real-time, extracts structured data, and triggers alerts when error rates exceed customizable thresholds.

This project demonstrates **Clean Architecture**, **Concurrency**, and **Advanced Metaprogramming** in Python — a lightweight version of enterprise tools like Datadog or Filebeat.

---

## ✨ Core Features & Architecture

- **Memory-Efficient Log Tailing (Generators & Context Managers)**
  Uses an asynchronous generator to `yield` one line at a time — just like `tail -f`. Relies on `asynccontextmanager` to guarantee safe file handle closure even on exceptions. Memory footprint stays tiny no matter how large the log file grows.

- **Event-Driven Concurrency (AsyncIO)**
  Built entirely on `asyncio`. The orchestrator simultaneously monitors dozens of log files without the overhead of threading or multiprocessing, using `asyncio.gather` to fan out tasks across an async event loop.

- **Dependency Inversion Principle (ABC & Pydantic)**
  The core engine depends only on a `LogParserABC` abstract interface. It doesn't care whether it's parsing Nginx, Apache, or JSON logs — it passes raw strings to whichever parser is injected, which validates and structures the output into strict **Pydantic** `LogEntry` models.

- **Stateful Metaprogramming (Complex Decorators)**
  Alert logic is throttled via a custom functional decorator: `@threshold_alert(limit=3, window_seconds=10)`. This harnesses Python closures to track alert timestamps across memory scopes and suppress alert spam during "error storms."

---

## 📂 Project Structure

```text
async-log-monitor/
├── Dockerfile              # Two-stage build: builder + slim runtime image
├── docker-compose.yml      # Container orchestration with volume mounts & env vars
├── .dockerignore           # Files excluded from the Docker build context
├── requirements.txt        # Python dependencies
├── DOCKER.md               # Full step-by-step Docker guide
├── README.md
├── logs/                   # 📂 Mount this directory into Docker for log monitoring
│   └── test_app.jsonl      # Example log file
└── src/
    ├── reader/
    │   └── tailer.py       # AsyncGenerator & ContextManager for file tailing
    ├── parser/
    │   ├── base.py         # LogParserABC + Pydantic LogEntry model
    │   └── json_parser.py  # Concrete JSON log parser implementation
    ├── alerts/
    │   └── decorators.py   # Metaprogramming @threshold_alert decorator
    └── orchestrator.py     # Main AsyncIO concurrency engine
```

---

## 🚀 Getting Started

### Prerequisites

- **Docker** — [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended), or Docker Engine on Linux
- **Python 3.10+** — only needed if running locally without Docker

Verify Docker is installed and running:
```bash
docker --version
docker compose version
```

---

## 🐳 Running with Docker (Recommended)

Docker is the easiest way to run this project. No Python setup required.

### 1. Clone the repository

```bash
git clone https://github.com/vineetamotilal/async-log-monitor.git
cd async-log-monitor
```

### 2. Create the `logs/` directory and seed a log file

The container reads from your local `./logs/` directory via a volume mount.

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

### 3. Build and start the container

```bash
docker compose up --build
```

You should see:
```
async-log-monitor  | 🚀 Starting Async Log Monitor Orchestrator...
async-log-monitor  | 📂 Docker mode: watching log files in '/logs'
async-log-monitor  | 👀 Started monitoring: /logs/test_app.jsonl (Parser: JSONLogParser)
```

### 4. Simulate log events (second terminal)

Open a new terminal in the repo root and append log lines:

**Linux / macOS:**
```bash
# INFO event
echo '{"level": "INFO", "message": "User logged in"}' >> logs/test_app.jsonl

# ERROR event — run 3+ times quickly to trigger the @threshold_alert decorator!
echo '{"level": "ERROR", "message": "Simulated failure"}' >> logs/test_app.jsonl
```

**Windows PowerShell:**
```powershell
echo '{"level": "INFO", "message": "User logged in"}' >> logs\test_app.jsonl
echo '{"level": "ERROR", "message": "Simulated failure"}' >> logs\test_app.jsonl
```

After 3 errors within 10 seconds, you'll see the alert fire:
```
🔥 [ALERT TIER 1] Error detected in /logs/test_app.jsonl! Log entry: ERROR - ...
```

### 5. Stop the container

```bash
docker compose down
```

> 📖 For a full Docker reference (detached mode, rebuild, troubleshooting, cheat sheet), see [DOCKER.md](./DOCKER.md).

---

## 🖥️ Running Locally (without Docker)

If you prefer to run without Docker:

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the orchestrator

```bash
python -m src.orchestrator
```

This creates a `test_app.jsonl` in the current directory and starts tailing it.

### 3. Append log lines to trigger the monitor

**Linux / macOS:**
```bash
echo '{"level": "ERROR", "message": "Simulated failure"}' >> test_app.jsonl
```

**Windows PowerShell:**
```powershell
echo '{"level": "ERROR", "message": "Simulated failure"}' >> test_app.jsonl
```

*(Run the error command 3+ times quickly to trigger the decorator alert threshold!)*

---

## ⚡ Docker Quick Reference

| Command | Description |
|---|---|
| `docker compose up --build` | Build image and start container |
| `docker compose up` | Start without rebuilding |
| `docker compose up -d` | Start in background (detached) |
| `docker compose down` | Stop and remove the container |
| `docker compose logs -f` | Stream live container output |
| `docker compose ps` | Show running containers |

---

## 🛠️ Future Roadmap

- Implement concrete parsers for NGINX and Apache access log formats
- Integrate real alerting endpoints (Slack Webhooks, SMTP Email)
- Add integration tests using `pytest` and `pytest-asyncio`
- Support dynamic file discovery (watch the `logs/` directory for new files at runtime)
