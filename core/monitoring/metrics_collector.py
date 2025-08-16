"""
Monitoring and Metrics Module
Comprehensive performance tracking, statistics collection, and reporting
"""

import time
import threading
import psutil
import os
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import deque, defaultdict
from enum import Enum, auto

from ..timing.clock_manager import clock_manager


class MetricType(Enum):
    """Metric type enumeration"""
    COUNTER = auto()
    GAUGE = auto()
    HISTOGRAM = auto()
    TIMER = auto()


@dataclass
class Metric:
    """Individual metric data point"""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    memory_used: int
    memory_total: int
    disk_usage_percent: float
    disk_used: int
    disk_total: int
    network_bytes_sent: int
    network_bytes_recv: int
    load_average: List[float]
    timestamp: float


@dataclass
class TransferMetrics:
    """File transfer metrics"""
    transfer_id: str
    file_name: str
    file_size: int
    bytes_transferred: int
    transfer_rate: float
    progress_percent: float
    chunks_completed: int
    total_chunks: int
    start_time: float
    estimated_completion: Optional[float] = None


class MetricsCollector:
    """Collects and manages system and application metrics"""
    
    def __init__(self, collection_interval: float = 1.0):
        self.collection_interval = collection_interval
        self.running = False
        
        # Metric storage
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        
        # System metrics
        self.system_metrics_history: deque = deque(maxlen=300)  # 5 minutes at 1s intervals
        
        # Transfer metrics
        self.active_transfers: Dict[str, TransferMetrics] = {}
        self.completed_transfers: deque = deque(maxlen=100)
        
        # Threading
        self.lock = threading.RLock()
        self.collection_thread: Optional[threading.Thread] = None
        
        # Callbacks for custom metrics
        self.metric_callbacks: Dict[str, Callable] = {}
        
        # Initialize system monitoring
        self.process = psutil.Process()
        self.initial_net_io = psutil.net_io_counters()
    
    def start_collection(self):
        """Start metrics collection"""
        if self.running:
            return
        
        self.running = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        print("📊 Metrics collection started")
    
    def stop_collection(self):
        """Stop metrics collection"""
        self.running = False
        if self.collection_thread and self.collection_thread.is_alive():
            self.collection_thread.join(timeout=2)
        print("📊 Metrics collection stopped")
    
    def _collection_loop(self):
        """Main metrics collection loop"""
        while self.running:
            try:
                with clock_manager.measure_operation("metrics_collection"):
                    self._collect_system_metrics()
                    self._collect_custom_metrics()
                    self._update_transfer_metrics()
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                print(f"Error in metrics collection: {e}")
                time.sleep(self.collection_interval)
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            net_io = psutil.net_io_counters()
            
            # Load average (Unix-like systems)
            try:
                load_avg = list(os.getloadavg())
            except (OSError, AttributeError):
                load_avg = [0.0, 0.0, 0.0]
            
            # Create system metrics object
            sys_metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used=memory.used,
                memory_total=memory.total,
                disk_usage_percent=disk.percent,
                disk_used=disk.used,
                disk_total=disk.total,
                network_bytes_sent=net_io.bytes_sent - self.initial_net_io.bytes_sent,
                network_bytes_recv=net_io.bytes_recv - self.initial_net_io.bytes_recv,
                load_average=load_avg,
                timestamp=time.time()
            )
            
            with self.lock:
                self.system_metrics_history.append(sys_metrics)
                
                # Update individual metrics
                self.gauges['system.cpu.percent'] = cpu_percent
                self.gauges['system.memory.percent'] = memory.percent
                self.gauges['system.memory.used'] = memory.used
                self.gauges['system.disk.percent'] = disk.percent
                self.gauges['system.network.bytes_sent'] = sys_metrics.network_bytes_sent
                self.gauges['system.network.bytes_recv'] = sys_metrics.network_bytes_recv
                
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
    
    def _collect_custom_metrics(self):
        """Collect custom metrics from callbacks"""
        for metric_name, callback in self.metric_callbacks.items():
            try:
                value = callback()
                if value is not None:
                    self.record_gauge(metric_name, value)
            except Exception as e:
                print(f"Error collecting custom metric {metric_name}: {e}")
    
    def _update_transfer_metrics(self):
        """Update transfer metrics"""
        current_time = time.time()
        
        with self.lock:
            for transfer_id, metrics in self.active_transfers.items():
                # Calculate current transfer rate
                elapsed = current_time - metrics.start_time
                if elapsed > 0:
                    metrics.transfer_rate = metrics.bytes_transferred / elapsed
                
                # Estimate completion time
                if metrics.transfer_rate > 0:
                    remaining_bytes = metrics.file_size - metrics.bytes_transferred
                    eta_seconds = remaining_bytes / metrics.transfer_rate
                    metrics.estimated_completion = current_time + eta_seconds
    
    def record_counter(self, name: str, value: float = 1.0, tags: Dict[str, str] = None):
        """Record counter metric"""
        with self.lock:
            self.counters[name] += value
            self._record_metric(name, value, MetricType.COUNTER, tags)
    
    def record_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record gauge metric"""
        with self.lock:
            self.gauges[name] = value
            self._record_metric(name, value, MetricType.GAUGE, tags)
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record histogram metric"""
        with self.lock:
            self.histograms[name].append(value)
            # Keep only recent values
            if len(self.histograms[name]) > 1000:
                self.histograms[name] = self.histograms[name][-1000:]
            self._record_metric(name, value, MetricType.HISTOGRAM, tags)
    
    def record_timer(self, name: str, duration: float, tags: Dict[str, str] = None):
        """Record timer metric"""
        self.record_histogram(f"{name}.duration", duration, tags)
    
    def _record_metric(self, name: str, value: float, metric_type: MetricType, tags: Dict[str, str] = None):
        """Record metric to history"""
        metric = Metric(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {},
            metric_type=metric_type
        )
        self.metrics[name].append(metric)
    
    def start_transfer_tracking(self, transfer_id: str, file_name: str, file_size: int, total_chunks: int):
        """Start tracking a file transfer"""
        with self.lock:
            self.active_transfers[transfer_id] = TransferMetrics(
                transfer_id=transfer_id,
                file_name=file_name,
                file_size=file_size,
                bytes_transferred=0,
                transfer_rate=0.0,
                progress_percent=0.0,
                chunks_completed=0,
                total_chunks=total_chunks,
                start_time=time.time()
            )
    
    def update_transfer_progress(self, transfer_id: str, bytes_transferred: int, chunks_completed: int):
        """Update transfer progress"""
        with self.lock:
            if transfer_id in self.active_transfers:
                metrics = self.active_transfers[transfer_id]
                metrics.bytes_transferred = bytes_transferred
                metrics.chunks_completed = chunks_completed
                metrics.progress_percent = (bytes_transferred / metrics.file_size) * 100
                
                # Record metrics
                self.record_gauge(f"transfer.{transfer_id}.progress", metrics.progress_percent)
                self.record_gauge(f"transfer.{transfer_id}.rate", metrics.transfer_rate)
    
    def complete_transfer(self, transfer_id: str, success: bool = True):
        """Complete transfer tracking"""
        with self.lock:
            if transfer_id in self.active_transfers:
                metrics = self.active_transfers[transfer_id]
                metrics.progress_percent = 100.0 if success else metrics.progress_percent
                
                # Move to completed transfers
                self.completed_transfers.append(metrics)
                del self.active_transfers[transfer_id]
                
                # Record completion
                self.record_counter("transfers.completed" if success else "transfers.failed")
    
    def register_metric_callback(self, metric_name: str, callback: Callable[[], float]):
        """Register callback for custom metric collection"""
        self.metric_callbacks[metric_name] = callback
    
    def get_current_system_metrics(self) -> Optional[SystemMetrics]:
        """Get current system metrics"""
        with self.lock:
            return self.system_metrics_history[-1] if self.system_metrics_history else None
    
    def get_metric_history(self, metric_name: str, limit: int = 100) -> List[Metric]:
        """Get metric history"""
        with self.lock:
            return list(self.metrics[metric_name])[-limit:]
    
    def get_transfer_metrics(self, transfer_id: str) -> Optional[TransferMetrics]:
        """Get transfer metrics"""
        with self.lock:
            return self.active_transfers.get(transfer_id)
    
    def get_all_active_transfers(self) -> Dict[str, TransferMetrics]:
        """Get all active transfer metrics"""
        with self.lock:
            return self.active_transfers.copy()
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get comprehensive statistics summary"""
        with self.lock:
            current_sys = self.get_current_system_metrics()
            
            summary = {
                'timestamp': time.time(),
                'system': {
                    'cpu_percent': current_sys.cpu_percent if current_sys else 0,
                    'memory_percent': current_sys.memory_percent if current_sys else 0,
                    'disk_percent': current_sys.disk_usage_percent if current_sys else 0,
                    'load_average': current_sys.load_average if current_sys else [0, 0, 0]
                },
                'transfers': {
                    'active_count': len(self.active_transfers),
                    'completed_count': len(self.completed_transfers),
                    'total_active_bytes': sum(t.file_size for t in self.active_transfers.values()),
                    'avg_transfer_rate': sum(t.transfer_rate for t in self.active_transfers.values()) / max(1, len(self.active_transfers))
                },
                'counters': dict(self.counters),
                'gauges': dict(self.gauges)
            }
            
            return summary


class PerformanceReporter:
    """Generates performance reports with emoji formatting"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def generate_system_report(self) -> str:
        """Generate system performance report"""
        current_metrics = self.metrics.get_current_system_metrics()
        if not current_metrics:
            return "❌ No system metrics available"
        
        report = []
        report.append("🖥️  SYSTEM PERFORMANCE REPORT")
        report.append("=" * 40)
        
        # CPU
        cpu_emoji = "🔥" if current_metrics.cpu_percent > 80 else "⚡" if current_metrics.cpu_percent > 50 else "😴"
        report.append(f"{cpu_emoji} CPU Usage: {current_metrics.cpu_percent:.1f}%")
        
        # Memory
        mem_emoji = "🔴" if current_metrics.memory_percent > 90 else "🟡" if current_metrics.memory_percent > 70 else "🟢"
        report.append(f"{mem_emoji} Memory: {current_metrics.memory_percent:.1f}% ({self._format_bytes(current_metrics.memory_used)}/{self._format_bytes(current_metrics.memory_total)})")
        
        # Disk
        disk_emoji = "💾" if current_metrics.disk_usage_percent > 90 else "💿"
        report.append(f"{disk_emoji} Disk: {current_metrics.disk_usage_percent:.1f}% ({self._format_bytes(current_metrics.disk_used)}/{self._format_bytes(current_metrics.disk_total)})")
        
        # Network
        report.append(f"🌐 Network: ↑{self._format_bytes(current_metrics.network_bytes_sent)} ↓{self._format_bytes(current_metrics.network_bytes_recv)}")
        
        # Load average
        report.append(f"⚖️  Load: {current_metrics.load_average[0]:.2f}, {current_metrics.load_average[1]:.2f}, {current_metrics.load_average[2]:.2f}")
        
        return "\n".join(report)
    
    def generate_transfer_report(self) -> str:
        """Generate transfer performance report"""
        active_transfers = self.metrics.get_all_active_transfers()
        
        report = []
        report.append("📊 TRANSFER PERFORMANCE REPORT")
        report.append("=" * 40)
        
        if not active_transfers:
            report.append("📭 No active transfers")
            return "\n".join(report)
        
        total_rate = 0
        for transfer_id, metrics in active_transfers.items():
            progress_bar = self._create_progress_bar(metrics.progress_percent)
            rate_emoji = "🚀" if metrics.transfer_rate > 10*1024*1024 else "🏃" if metrics.transfer_rate > 1024*1024 else "🚶"
            
            report.append(f"📁 {metrics.file_name}")
            report.append(f"   {progress_bar} {metrics.progress_percent:.1f}%")
            report.append(f"   {rate_emoji} Rate: {self._format_bytes(metrics.transfer_rate)}/s")
            report.append(f"   🧩 Chunks: {metrics.chunks_completed}/{metrics.total_chunks}")
            
            if metrics.estimated_completion:
                eta = metrics.estimated_completion - time.time()
                report.append(f"   ⏱️  ETA: {eta:.0f}s")
            
            report.append("")
            total_rate += metrics.transfer_rate
        
        report.append(f"📈 Total Transfer Rate: {self._format_bytes(total_rate)}/s")
        
        return "\n".join(report)
    
    def _format_bytes(self, bytes_value: float) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def _create_progress_bar(self, progress: float, width: int = 20) -> str:
        """Create progress bar"""
        filled = int(width * progress / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"


# Global metrics collector instance
metrics_collector = MetricsCollector()
performance_reporter = PerformanceReporter(metrics_collector)
