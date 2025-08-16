"""
Comprehensive Timing and Clock Measurement Module
Provides high-precision timing for all system operations
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from contextlib import contextmanager
import statistics


@dataclass
class TimingMeasurement:
    """Individual timing measurement"""
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    thread_id: int = field(default_factory=lambda: threading.get_ident())


@dataclass
class OperationStats:
    """Statistics for a specific operation type"""
    operation_name: str
    total_calls: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    avg_duration: float = 0.0
    recent_durations: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def update(self, duration: float):
        """Update statistics with new measurement"""
        self.total_calls += 1
        self.total_duration += duration
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)
        self.avg_duration = self.total_duration / self.total_calls
        self.recent_durations.append(duration)


class HighPrecisionTimer:
    """High-precision timer using performance counter"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self) -> float:
        """Start timing"""
        self.start_time = time.perf_counter()
        return self.start_time
    
    def stop(self) -> float:
        """Stop timing and return duration"""
        self.end_time = time.perf_counter()
        if self.start_time is None:
            raise ValueError("Timer not started")
        return self.end_time - self.start_time
    
    def elapsed(self) -> float:
        """Get elapsed time without stopping"""
        if self.start_time is None:
            raise ValueError("Timer not started")
        return time.perf_counter() - self.start_time
    
    def reset(self):
        """Reset timer"""
        self.start_time = None
        self.end_time = None


class ClockManager:
    """Comprehensive timing and clock management system"""
    
    def __init__(self):
        self.active_measurements: Dict[str, TimingMeasurement] = {}
        self.completed_measurements: List[TimingMeasurement] = []
        self.operation_stats: Dict[str, OperationStats] = defaultdict(OperationStats)
        self.lock = threading.RLock()
        
        # System timing
        self.system_start_time = time.time()
        self.system_start_perf = time.perf_counter()
        
        # Network timing
        self.network_latencies: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.packet_timings: Dict[int, Dict[str, float]] = {}
        
        # File operation timing
        self.file_operation_times: Dict[str, List[float]] = defaultdict(list)
        
        # CPU and resource timing
        self.cpu_measurement_intervals: List[Tuple[float, float]] = []
    
    def start_measurement(self, operation_name: str, metadata: Dict[str, Any] = None) -> str:
        """Start timing an operation"""
        measurement_id = f"{operation_name}_{threading.get_ident()}_{time.perf_counter()}"
        
        measurement = TimingMeasurement(
            operation_name=operation_name,
            start_time=time.perf_counter(),
            metadata=metadata or {}
        )
        
        with self.lock:
            self.active_measurements[measurement_id] = measurement
        
        return measurement_id
    
    def end_measurement(self, measurement_id: str) -> Optional[float]:
        """End timing an operation"""
        end_time = time.perf_counter()
        
        with self.lock:
            if measurement_id not in self.active_measurements:
                return None
            
            measurement = self.active_measurements[measurement_id]
            measurement.end_time = end_time
            measurement.duration = end_time - measurement.start_time
            
            # Move to completed measurements
            self.completed_measurements.append(measurement)
            del self.active_measurements[measurement_id]
            
            # Update operation statistics
            op_name = measurement.operation_name
            if op_name not in self.operation_stats:
                self.operation_stats[op_name] = OperationStats(operation_name=op_name)
            
            self.operation_stats[op_name].update(measurement.duration)
            
            return measurement.duration
    
    @contextmanager
    def measure_operation(self, operation_name: str, metadata: Dict[str, Any] = None):
        """Context manager for timing operations"""
        measurement_id = self.start_measurement(operation_name, metadata)
        try:
            yield measurement_id
        finally:
            self.end_measurement(measurement_id)
    
    def measure_function(self, operation_name: str = None):
        """Decorator for timing functions"""
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                with self.measure_operation(op_name):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def record_network_latency(self, peer_id: str, latency: float):
        """Record network latency to a peer"""
        with self.lock:
            self.network_latencies[peer_id].append(latency)
    
    def record_packet_timing(self, packet_id: int, event: str, timestamp: float = None):
        """Record packet timing events"""
        if timestamp is None:
            timestamp = time.perf_counter()
        
        with self.lock:
            if packet_id not in self.packet_timings:
                self.packet_timings[packet_id] = {}
            self.packet_timings[packet_id][event] = timestamp
    
    def record_file_operation(self, operation_type: str, duration: float):
        """Record file operation timing"""
        with self.lock:
            self.file_operation_times[operation_type].append(duration)
    
    def get_operation_stats(self, operation_name: str) -> Optional[OperationStats]:
        """Get statistics for a specific operation"""
        with self.lock:
            return self.operation_stats.get(operation_name)
    
    def get_all_operation_stats(self) -> Dict[str, OperationStats]:
        """Get statistics for all operations"""
        with self.lock:
            return dict(self.operation_stats)
    
    def get_network_latency_stats(self, peer_id: str) -> Dict[str, float]:
        """Get network latency statistics for a peer"""
        with self.lock:
            latencies = list(self.network_latencies.get(peer_id, []))
            
            if not latencies:
                return {}
            
            return {
                'count': len(latencies),
                'avg_latency': statistics.mean(latencies),
                'min_latency': min(latencies),
                'max_latency': max(latencies),
                'median_latency': statistics.median(latencies),
                'std_dev': statistics.stdev(latencies) if len(latencies) > 1 else 0.0
            }
    
    def get_packet_timing_analysis(self, packet_id: int) -> Dict[str, Any]:
        """Analyze timing for a specific packet"""
        with self.lock:
            if packet_id not in self.packet_timings:
                return {}
            
            timings = self.packet_timings[packet_id]
            analysis = {'events': timings}
            
            # Calculate intervals between events
            if 'sent' in timings and 'ack_received' in timings:
                analysis['round_trip_time'] = timings['ack_received'] - timings['sent']
            
            if 'processing_start' in timings and 'processing_end' in timings:
                analysis['processing_time'] = timings['processing_end'] - timings['processing_start']
            
            if 'transmission_start' in timings and 'transmission_end' in timings:
                analysis['transmission_time'] = timings['transmission_end'] - timings['transmission_start']
            
            return analysis
    
    def get_file_operation_stats(self, operation_type: str) -> Dict[str, float]:
        """Get file operation statistics"""
        with self.lock:
            times = self.file_operation_times.get(operation_type, [])
            
            if not times:
                return {}
            
            return {
                'count': len(times),
                'total_time': sum(times),
                'avg_time': statistics.mean(times),
                'min_time': min(times),
                'max_time': max(times),
                'median_time': statistics.median(times),
                'std_dev': statistics.stdev(times) if len(times) > 1 else 0.0
            }
    
    def get_system_uptime(self) -> Dict[str, float]:
        """Get system uptime information"""
        current_time = time.time()
        current_perf = time.perf_counter()
        
        return {
            'uptime_seconds': current_time - self.system_start_time,
            'uptime_perf_seconds': current_perf - self.system_start_perf,
            'start_time': self.system_start_time,
            'current_time': current_time
        }
    
    def generate_timing_report(self) -> str:
        """Generate essential timing report"""
        report = []
        report.append("⏱️  PERFORMANCE SUMMARY")
        report.append("=" * 40)

        # System uptime
        uptime = self.get_system_uptime()
        report.append(f"🕐 System Uptime: {uptime['uptime_seconds']:.1f}s")

        # Key performance metrics only
        with self.lock:
            # Count file operations
            file_ops = [op for op in self.operation_stats.keys() if 'file_upload' in op]
            total_file_ops = len(file_ops)

            if total_file_ops > 0:
                # Calculate average file upload time
                upload_times = [self.operation_stats[op].avg_duration for op in file_ops]
                avg_upload_time = sum(upload_times) / len(upload_times)
                report.append(f"📤 File Uploads: {total_file_ops} completed")
                report.append(f"⚡ Avg Upload Time: {avg_upload_time:.2f}s")

            # Network performance summary
            if self.network_latencies:
                total_latency_samples = sum(len(latencies) for latencies in self.network_latencies.values())
                report.append(f"🌐 Network Samples: {total_latency_samples}")

                # Calculate overall average latency
                all_latencies = []
                for latencies in self.network_latencies.values():
                    all_latencies.extend(latencies)

                if all_latencies:
                    avg_latency = sum(all_latencies) / len(all_latencies)
                    report.append(f"📡 Avg Network Latency: {avg_latency*1000:.1f}ms")

            # File operation summary
            if self.file_operation_times:
                total_chunk_ops = sum(len(times) for times in self.file_operation_times.values())
                report.append(f"🧩 Chunks Processed: {total_chunk_ops}")

                # Calculate average chunk processing time
                all_chunk_times = []
                for times in self.file_operation_times.values():
                    all_chunk_times.extend(times)

                if all_chunk_times:
                    avg_chunk_time = sum(all_chunk_times) / len(all_chunk_times)
                    report.append(f"⚙️  Avg Chunk Time: {avg_chunk_time:.3f}s")

        return "\n".join(report)
    
    def cleanup_old_measurements(self, max_age_seconds: float = 3600):
        """Clean up old measurements to prevent memory leaks"""
        cutoff_time = time.perf_counter() - max_age_seconds
        
        with self.lock:
            # Clean completed measurements
            self.completed_measurements = [
                m for m in self.completed_measurements 
                if m.start_time > cutoff_time
            ]
            
            # Clean packet timings
            old_packet_ids = [
                pid for pid, timings in self.packet_timings.items()
                if min(timings.values()) < cutoff_time
            ]
            for pid in old_packet_ids:
                del self.packet_timings[pid]


# Global clock manager instance
clock_manager = ClockManager()
