# Why I Containerised Async Log Monitor with Docker 🐳

## The Project in One Line

**Async Log Monitor** is a long-running Python daemon that tails log files in real-time, detects errors, and fires throttled alerts. It was built to demonstrate expert-level Python patterns — async generators, abstract base classes, Pydantic models, and metaprogramming decorators.

---

## Why Docker — Not Just `python -m src.orchestrator`

The first time I ran this locally, it worked fine. Then I thought: *what happens when someone else clones this repo?* Or when I want to deploy it to a server? That's when the cracks appeared.

### 1. This is a Daemon, Not a Script

`orchestrator.py` is not a one-shot script. It's designed to run **forever**, tailing log files continuously — exactly like a production monitoring agent (Datadog, Filebeat, Fluentd). Daemons belong in containers. Containers are designed to:

- Run indefinitely (`restart: unless-stopped` in `docker-compose.yml`)
- Restart themselves on crash — no manual intervention needed
- Be stopped and started cleanly with a single command

Running a daemon directly with `python` means babysitting it manually.

---

### 2. Reproducibility Across Machines

When I built this project, I was on Python 3.13. The async features I used — `asyncio.TaskGroup` semantics, modern type hint syntax — behave differently on older versions. Without Docker:

- A teammate on Python 3.9 sees failures I never saw
- A CI server on a different OS gets different results
- "It worked on my machine" becomes the explanation

The `Dockerfile` pins `python:3.13-slim` as the base. Anyone who runs `docker compose up --build` gets **the exact same Python runtime I used** — on Windows, macOS, or Linux.

---

### 3. It Enforces the Architecture I Designed

The `orchestrator.py` is designed around a key idea: **the monitor reads logs, it does not own them**. It should watch files produced by other applications — it should never be writing into its own directory.

Docker enforces this cleanly:

```yaml
volumes:
  - ./logs:/logs:ro   # read-only mount — the container cannot modify your log files
```

The container also runs as a **non-root `monitor` user**. Here's what that actually means.

#### 🔐 Think of it like a job role at an office

Imagine you hire a **security guard** to watch CCTV footage. Their job is to **watch**, not to touch anything else.

- A **root user** = the guard has **master keys** to every room, every filing cabinet, every server. If they go rogue (or get hacked), they can delete files, steal data, break things.
- A **non-root `monitor` user** = the guard only has a key to **the CCTV room**. Even if they want to cause damage, they physically can't — they have no access anywhere else.

The `Dockerfile` enforces this:

```dockerfile
# Creates a restricted user called "monitor"
RUN useradd --create-home --shell /bin/bash monitor

# Switches to that user before the app starts — it never runs as root
USER monitor
```

#### What this protects against

Say there's a bug in `tailer.py` — the file-reading code. Instead of *reading* a line, it accidentally tries to *delete* a file or *write* somewhere unexpected.

| Scenario | Running as `root` | Running as `monitor` user |
|---|---|---|
| Bug tries to delete `/etc/passwd` | ✅ Succeeds — disaster | ❌ Permission denied — blocked |
| Bug tries to write to `/app/src/` | ✅ Succeeds — code corrupted | ❌ Permission denied — blocked |
| Bug tries to read `/logs` | ✅ Succeeds | ✅ Succeeds — this is the *only* thing it's allowed to do |

#### "Security in the infrastructure, not assumed in the code"

- **Assumed in the code** = you write careful code and *hope* it never does anything bad. You trust the developer.
- **Built into the infrastructure** = even if the code has a bug or gets compromised, the OS-level permissions **physically prevent** damage. You don't need to trust anyone — the system enforces it.

It's the same reason banks use **vaults**, not just trustworthy employees. The vault doesn't trust — it enforces.

> **The PermissionError you saw earlier was proof of this working.**
> When the container tried to write `test_app.jsonl` to `/app`, the OS said *no* — the `monitor` user has no write access there. That's the security model doing its job. It just happened to block our own legitimate code too, which is why we fixed it by pointing writes to `/logs` instead.

---

### 4. Clean Dependency Isolation

This project has one dependency today (`pydantic`). Tomorrow it might have ten. Without Docker:

- Every developer needs to `pip install` manually
- Dependencies land in their global Python environment
- Version conflicts with other projects are their problem to solve

With Docker, `pip install` runs inside the image during `docker compose build`. The developer's machine stays clean. The image always has exactly what `requirements.txt` specifies — nothing more, nothing less.

---

### 5. Closer to How It Would Run in Production

If Async Log Monitor were deployed to a real server — watching Nginx logs, application logs, database logs — it would run in a container. It wouldn't run as a bare Python process. By containerising it from day one:

- The `docker-compose.yml` models the production configuration (volume mounts, env vars, restart policy)
- I discovered the permission error between the non-root user and the `/app` directory **locally**, not on a production server at 2am
- The gap between "runs on my laptop" and "runs in prod" is as small as possible

---

## What I Learned From the Process

Containerising this project forced me to think about things that pure Python development lets you ignore:

| Question forced by Docker | Why it matters |
|---|---|
| *What user does my process run as?* | Security — non-root is the right default |
| *Which paths does my app write to?* | Separation of concerns — a monitor shouldn't write to its own code directory |
| *What is the exact Python version and set of packages this needs?* | Reproducibility |
| *How does this restart if it crashes?* | Reliability for a long-running daemon |
| *How do I pass configuration (like log directory) without hardcoding it?* | `LOG_DIR` env var instead of a magic relative path |

These are questions every production-grade system must answer. Docker made me answer them for a project that's still in development — which is exactly the point.

---

## Summary

> I didn't containerise Async Log Monitor because it was required.
> I did it because a log monitoring daemon **is the kind of workload Docker was built for** — and because building it this way forced me to treat a learning project with the same rigour I'd apply to a production system.
