import time
import psutil
import numpy as np
from collections import deque

class PerformanceMonitor:
    """Monitor and analyze application performance metrics"""
    
    def __init__(self, max_samples=1000):
        self.processing_times = deque(maxlen=max_samples)
        self.ui_update_times = deque(maxlen=max_samples)
        self.memory_usage = deque(maxlen=max_samples)
        self.process = psutil.Process()
    
    def record_processing_time(self, time_ms):
        """Record orderbook processing time"""
        self.processing_times.append(time_ms)
    
    def record_ui_update_time(self):
        """Measure and record UI update time"""
        start = time.time()
        yield  # This makes this a context manager
        elapsed = (time.time() - start) * 1000
        self.ui_update_times.append(elapsed)
    
    def record_memory_usage(self):
        """Record current memory usage"""
        mem_info = self.process.memory_info()
        self.memory_usage.append(mem_info.rss / 1024 / 1024)  # MB
    
    def get_processing_stats(self):
        """Get statistics about processing times"""
        if not self.processing_times:
            return {"min": 0, "max": 0, "avg": 0, "p95": 0, "p99": 0}
        
        times = np.array(self.processing_times)
        return {
            "min": np.min(times),
            "max": np.max(times),
            "avg": np.mean(times),
            "p95": np.percentile(times, 95),
            "p99": np.percentile(times, 99)
        }
    
    def get_ui_update_stats(self):
        """Get statistics about UI update times"""
        if not self.ui_update_times:
            return {"min": 0, "max": 0, "avg": 0, "p95": 0, "p99": 0}
        
        times = np.array(self.ui_update_times)
        return {
            "min": np.min(times),
            "max": np.max(times),
            "avg": np.mean(times),
            "p95": np.percentile(times, 95),
            "p99": np.percentile(times, 99)
        }
    
    def get_memory_stats(self):
        """Get statistics about memory usage"""
        if not self.memory_usage:
            return {"current": 0, "peak": 0, "avg": 0}
        
        usage = np.array(self.memory_usage)
        return {
            "current": usage[-1] if len(usage) > 0 else 0,
            "peak": np.max(usage),
            "avg": np.mean(usage)
        }
    
    def generate_report(self):
        """Generate a comprehensive performance report"""
        return {
            "processing": self.get_processing_stats(),
            "ui_update": self.get_ui_update_stats(),
            "memory": self.get_memory_stats(),
            "samples": {
                "processing": len(self.processing_times),
                "ui_update": len(self.ui_update_times),
                "memory": len(self.memory_usage)
            }
        }