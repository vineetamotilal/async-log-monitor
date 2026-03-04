import asyncio
import os
from src.sentinel_py.reader.tailer import tail_file
from src.sentinel_py.parser.base import LogParserABC, LogEntry
from src.sentinel_py.alerts.decorators import threshold_alert

class SentinelOrchestrator:
    """
    The main monitoring engine that ties everything together.
    Uses AsyncIO to concurrently tail multiple log files.
    """
    
    def __init__(self):
        self.tasks: list[asyncio.Task] = []

    @threshold_alert(limit=3, window_seconds=10)
    def trigger_error_alert(self, file_path: str, log_entry: LogEntry):
        """
        The method that handles alerting when an error is detected.
        Decorated to prevent alert spam if an error storm occurs.
        """
        print(f"\n🔥 [ALERT TIER 1] Error detected in {file_path}! Log entry: {log_entry.level} - {log_entry.raw_content}")

    async def monitor_file(self, file_path: str, parser: LogParserABC):
        """
        Monitors a single file asynchronously.
        Calls the generator to yield lines and the parser to extract data.
        """
        print(f"👀 Started monitoring: {file_path} (Parser: {parser.__class__.__name__})")
        try:
            async for line in tail_file(file_path):
                # Using the Dependency Inverted parser
                entry = parser.parse(line)
                
                if entry:
                    if entry.is_error:
                        self.trigger_error_alert(file_path, entry)
                    else:
                        print(f"✅ [INFO] {file_path}: Processed line -> {entry.level}")
                else:
                    print(f"⚠️ [WARNING] Failed to parse line or irrelevant format in {file_path}: {line}")
        except asyncio.CancelledError:
            print(f"🛑 Stopped monitoring {file_path}.")
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
        except Exception as e:
            print(f"❌ Exception in monitoring {file_path}: {e}")

    async def run(self, files_to_monitor: dict[str, LogParserABC]):
        """
        Main entry point to start monitoring multiple files concurrently.
        
        Args:
            files_to_monitor: A dictionary mapping file paths to their specific Parser objects.
        """
        print("🚀 Starting Sentinel-Py Orchestrator...\n")
        
        # Create an asyncio Task for each file to monitor
        for file_path, parser in files_to_monitor.items():
            task = asyncio.create_task(self.monitor_file(file_path, parser))
            self.tasks.append(task)
            
        # Run all monitoring tasks concurrently
        # gather blocks here, running until cancelled
        await asyncio.gather(*self.tasks)


async def main():
    """
    Example runner for local testing.
    """
    from src.sentinel_py.parser.json_parser import JSONLogParser
    
    # 1. Setup a test log file
    test_log = "test_app.jsonl"
    with open(test_log, "w", encoding="utf-8") as f:
        f.write('{"timestamp": "2023-10-27T10:00:00Z", "level": "INFO", "message": "App started"}\n')
        
    print(f"Created test log file: {test_log}")
    print("Please manually append JSON lines to this file to see Sentinel-Py in action.")
    print("Example: echo '{\"level\": \"ERROR\", \"message\": \"Failed!\"}' >> test_app.jsonl\n")

    # 2. Initialize the orchestrator & parser
    json_parser = JSONLogParser()
    orchestrator = SentinelOrchestrator()
    
    # 3. Define the monitoring mapping
    # Maps absolute paths to concrete parser instances
    files_to_monitor = {
        os.path.abspath(test_log): json_parser
    }
    
    # 4. Boot the engine
    try:
        await orchestrator.run(files_to_monitor)
    except KeyboardInterrupt:
        print("\nShutting down Sentinel-Py...")

if __name__ == "__main__":
    # Ensure asyncio.run is called on the main coroutine
    asyncio.run(main())
