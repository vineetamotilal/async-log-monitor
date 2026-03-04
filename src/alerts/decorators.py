from typing import Callable, Any
import time

def threshold_alert(limit: int, window_seconds: int = 60) -> Callable:
    """
    A complex functional decorator for tracking error events frequency within a sliding window.
    
    This metaprogramming pattern maintains state (event timestamps) to determine if a specific
    function is called too often within a timeframe, triggering a threshold-specific action.
    
    Args:
        limit: The maximum number of events allowed within the time window.
        window_seconds: The duration of the time window in seconds.
        
    Returns:
        The decorator function.
    """
    
    def decorator(func: Callable) -> Callable:
        # Closure variable to maintain state across function calls
        # A list to store the timestamps of occurrences
        event_timestamps: list[float] = []

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            now = time.time()
            
            # Prune old timestamps that fall outside the window
            # Filter keeps elements where the condition is true
            nonlocal event_timestamps
            event_timestamps = [t for t in event_timestamps if now - t <= window_seconds]
            
            # Record the new event
            event_timestamps.append(now)

            # Check if the limit has been exceeded
            if len(event_timestamps) > limit:
                print(f"🚨 [ALERT METADATA] Decorator Threshold Exceeded! > {limit} events in {window_seconds}s. 🚨")
                # When exceeded, we could optionally clear the timestamps to avoid alerting on every subsequent event
                # until the window resets, but for demonstration, we let it continue alerting.
                # event_timestamps.clear()

            # Finally, execute the underlying wrapped function (e.g., executing the actual alert callback)
            return func(*args, **kwargs)
            
        return wrapper
        
    return decorator
