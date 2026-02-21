# Sentinel-Py 🛡️

**Sentinel-Py** is a distributed log monitoring engine built with expert-level Python design patterns. It efficiently tracks application log files in real-time, extracts structured data, and triggers alerts when error rates exceed customizable thresholds.

This project was built to demonstrate an understanding of **Clean Architecture**, **Concurrency**, and **Advanced Metaprogramming** in Python, acting as a lightweight version of enterprise tools like Datadog or Filebeat.

## ✨ Core Features & Architecture

*   **Memory-Efficient Log Tailing (Generators & Context Managers)**  
    Uses an asynchronous generator to `yield` one line of a log file at a time, just like the Unix `tail -f` command. It relies on `asynccontextmanager` to guarantee safe file handle closure even if exceptions occur. No matter how large the log file gets, Sentinel-Py's memory footprint remains tiny.
*   **Event-Driven Concurrency (AsyncIO)**  
    Built entirely on `asyncio`, the orchestrator can simultaneously monitor dozens of separate log files without the heavy overhead of threading or multiprocessing by utilizing an asynchronous event loop (`asyncio.gather`).
*   **Dependency Inversion Principle (ABC & Pydantic)**  
    The core engine relies entirely on an `Abstract Base Class` (`LogParserABC`). The engine does not need to know if it is parsing Nginx, Apache, or JSON logs—it simply passes raw strings to the parser, which validates and structures the output into strict **Pydantic** models (`LogEntry`).
*   **Stateful Metaprogramming (Complex Decorators)**  
    Alert logic is throttled using a custom functional decorator: `@threshold_alert(limit=3, window_seconds=10)`. This metaprogramming pattern harnesses Python closures to track alert timestamps across memory scopes and suppress alert spam during "error storms."

## 📂 Project Structure

```text
sentinel-py/
├── pyproject.toml              # Project metadata and dependencies
├── README.md                   
├── src/
│   └── sentinel_py/
│       ├── __init__.py
│       ├── reader/
│       │   └── tailer.py       # AsyncGenerator and ContextManager for file tailing
│       ├── parser/
│       │   ├── base.py         # LogParserABC and Pydantic LogEntry model
│       │   └── json_parser.py  # Concrete implementation for JSON testing
│       ├── alerts/
│       │   └── decorators.py   # Metaprogramming @threshold_alert
│       └── orchestrator.py     # Main AsyncIO concurrency engine
└── tests/
    └── ...                     # Test suite
```

## 🚀 Getting Started

### Prerequisites
*   Python 3.10+ (for modern type hinting and asyncio features)
*   `pydantic` (`pip install pydantic`)

### Running the Orchestrator

1.  Clone the repository and install dependencies.
2.  Start the **Sentinel-Py Orchestrator** in your terminal. This will spin up the daemon and create a dummy `test_app.jsonl` file to monitor:
    ```bash
    python -m src.sentinel_py.orchestrator
    ```
3.  Open a **second terminal** and simulate an application writing an error to the log file:
    ```bash
    echo '{"level": "ERROR", "message": "Simulated failure"}' >> test_app.jsonl
    ```
    *(Run the above command several times in quick succession to trigger the Decorator Alert Threshold!)*

## 🛠️ Future Roadmap

*   Implement concrete Parsers for standard NGINX and Apache access logs.
*   Integrate actual alerting endpoints (e.g., Slack Webhooks, SMTP Email).
*   Add integration tests using `pytest` and `pytest-asyncio`.
