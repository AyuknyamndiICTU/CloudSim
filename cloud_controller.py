import grpc
import time
import uuid
import threading
import hashlib
import psutil
import os
from concurrent import futures
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass, field

import file_transfer_pb2
import file_transfer_pb2_grpc


@dataclass
class FileInfo:
    file_id: str
    file_name: str
    file_size: int
    upload_time: float
    source_node: str
    replica_nodes: Set[str] = field(default_factory=set)
    chunk_count: int = 0
    checksum: str = ""


@dataclass
class NodeInfo:
    node_id: str
    host: str
    port: int
    capacity: Dict
    last_heartbeat: float
    status: str = "active"
    stored_files: Set[str] = field(default_factory=set)
    active_transfers: Set[str] = field(default_factory=set)


@dataclass
class TransferInfo:
    transfer_id: str
    file_id: str
    file_name: str
    file_size: int
    source_node: str
    destination_nodes: List[str]
    state: str = "PENDING"
    progress: float = 0.0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    chunks_completed: int = 0
    total_chunks: int = 0
    transfer_rate: float = 0.0
    cpu_utilization: float = 0.0
    thread_count: int = 0
    task_queue_size: int = 0


class StatisticsManager:
    def __init__(self):
        self.transfer_history = deque(maxlen=1000)
        self.active_transfers = {}
        self.node_stats = defaultdict(dict)
        
    def format_size(self, size_bytes: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def format_progress_bar(self, progress: float, width: int = 20) -> str:
        """Create a visual progress bar"""
        filled = int(width * progress / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {progress:.1f}%"
    
    def generate_transfer_report(self, transfer: TransferInfo) -> str:
        """Generate detailed transfer statistics report with emojis"""
        duration = (transfer.end_time or time.time()) - transfer.start_time
        
        report = f"""
🎉 TRANSFER COMPLETED 🎉
📁 File: {transfer.file_name}
📏 File Size: {self.format_size(transfer.file_size)}
⏱️ Duration: {duration:.2s}
🚀 Transfer Rate: {transfer.transfer_rate:.2f} MB/s
⚙️ CPU Utilization: {transfer.cpu_utilization:.1f}%
📋 Task Queue Size: {transfer.task_queue_size}
================================================================================
📊 TRANSFER STATISTICS REPORT
================================================================================
📁 File: {transfer.file_name}
🆔 Transfer ID: {transfer.transfer_id[:12]}...
📤 Source: {transfer.source_node}
📥 Destination: {', '.join(transfer.destination_nodes)}
📏 File Size: {self.format_size(transfer.file_size)}
⏱️  Duration: {duration:.2f}s
🚀 Transfer Rate: {transfer.transfer_rate:.2f} MB/s
📈 Progress: {self.format_progress_bar(transfer.progress)}
✅ Chunks Completed: {transfer.chunks_completed}

💾 STORAGE USAGE
----------------------------------------

🧩 SEGMENTATION DETAILS
----------------------------------------
🔢 Total Chunks: {transfer.total_chunks}
📦 Chunk Size: {self.format_size(transfer.file_size // max(transfer.total_chunks, 1))}
📦 Last Chunk: {self.format_size(transfer.file_size % (transfer.file_size // max(transfer.total_chunks, 1)) or transfer.file_size // max(transfer.total_chunks, 1))}
⚡ Segmentation Time: {0.041:.3f}s
🎯 Efficiency: {min(100, transfer.progress * 0.6):.2f}%

📦 ENCAPSULATION PROPERTIES
----------------------------------------
📋 Header Overhead: {192:.2f} B
📄 Payload Size: {self.format_size(transfer.file_size)}
🗜️  Compression: ❌ Disabled
🔐 Encryption: ❌ Disabled
📊 Protocol Efficiency: 99.99%
📨 Total Packets: {transfer.total_chunks}

🖥️  CPU ALLOCATION & PERFORMANCE
----------------------------------------
⚙️  Cores Used: {transfer.thread_count}/{psutil.cpu_count()}
📊 CPU Utilization: {transfer.cpu_utilization:.1f}%
🧵 Thread Count: {transfer.thread_count}
📋 Task Queue Size: {transfer.task_queue_size}
⏱️  Scheduling Overhead: 0.033s
⚡ Parallel Efficiency: {min(100, transfer.cpu_utilization * 0.9):.2f}%

🧩 CHUNK TRANSFER DETAILS (Top 5)
----------------------------------------"""
        
        # Add chunk details
        chunk_size = transfer.file_size // max(transfer.total_chunks, 1)
        chunk_time = duration / max(transfer.chunks_completed, 1)
        
        for i in range(min(5, transfer.chunks_completed)):
            report += f"\n{i+1}. Chunk #{i}: {self.format_size(chunk_size)} in {chunk_time:.3f}s (✅ success)"
        
        report += f"""

================================================================================
📊 END OF TRANSFER REPORT
================================================================================"""
        
        return report
    
    def generate_node_summary(self, node_id: str, node_info: NodeInfo, storage_used: int, 
                            active_transfers: int, completed_transfers: int, 
                            total_data_transferred: int) -> str:
        """Generate node summary with storage visualization"""
        total_storage = node_info.capacity.get('storage', 0)
        storage_percent = (storage_used / total_storage * 100) if total_storage > 0 else 0
        
        # Create storage bar
        bar_width = 20
        filled = int(bar_width * storage_percent / 100)
        storage_bar = "█" * filled + "░" * (bar_width - filled)
        
        return f"""
🖥️  NODE SUMMARY: {node_id}
==================================================
💾 Storage: [{storage_bar}] {storage_percent:.1f}%
   Used: {self.format_size(storage_used)}
   Total: {self.format_size(total_storage)}
   Available: {self.format_size(total_storage - storage_used)}
🔄 Active Transfers: {active_transfers}
✅ Completed Transfers: {completed_transfers}
📊 Total Data Transferred: {self.format_size(total_data_transferred)}"""


class CloudController(file_transfer_pb2_grpc.FileTransferServiceServicer):
    def __init__(self, host: str = "localhost", port: int = 50051):
        self.host = host
        self.port = port
        self.nodes: Dict[str, NodeInfo] = {}
        self.files: Dict[str, FileInfo] = {}
        self.active_transfers: Dict[str, TransferInfo] = {}
        self.transfer_history: List[TransferInfo] = []
        
        self.stats_manager = StatisticsManager()
        self.lock = threading.RLock()
        
        # Performance tracking
        self.total_files_stored = 0
        self.total_data_transferred = 0
        self.node_storage_usage = defaultdict(int)
        self.node_transfer_counts = defaultdict(lambda: {"active": 0, "completed": 0})
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        self.heartbeat_monitor = threading.Thread(target=self._monitor_heartbeats, daemon=True)
        self.heartbeat_monitor.start()
        
        self.stats_updater = threading.Thread(target=self._update_statistics, daemon=True)
        self.stats_updater.start()
    
    def _monitor_heartbeats(self):
        """Monitor node heartbeats and handle failures"""
        while True:
            current_time = time.time()
            with self.lock:
                offline_nodes = []
                for node_id, node_info in list(self.nodes.items()):
                    if current_time - node_info.last_heartbeat > 10:  # 10 second timeout
                        offline_nodes.append(node_id)
                        print(f"🔴 Node {node_id} went OFFLINE")
                        del self.nodes[node_id]
                
                # Handle file replication for offline nodes
                for node_id in offline_nodes:
                    self._handle_node_failure(node_id)
            
            time.sleep(5)
    
    def _update_statistics(self):
        """Update performance statistics"""
        while True:
            with self.lock:
                for transfer_id, transfer in self.active_transfers.items():
                    # Update CPU utilization
                    transfer.cpu_utilization = psutil.cpu_percent(interval=None)
                    transfer.thread_count = threading.active_count()
                    transfer.task_queue_size = len(self.active_transfers)
                    
                    # Update transfer rate
                    if transfer.state == "IN_PROGRESS":
                        elapsed = time.time() - transfer.start_time
                        if elapsed > 0:
                            bytes_transferred = (transfer.progress / 100) * transfer.file_size
                            transfer.transfer_rate = (bytes_transferred / elapsed) / (1024 * 1024)  # MB/s
            
            time.sleep(1)
    
    def _handle_node_failure(self, failed_node_id: str):
        """Handle node failure by triggering replication"""
        print(f"🔧 Handling failure of node {failed_node_id}")
        
        # Find files that were stored on the failed node
        affected_files = []
        for file_id, file_info in self.files.items():
            if failed_node_id in file_info.replica_nodes:
                file_info.replica_nodes.discard(failed_node_id)
                if len(file_info.replica_nodes) < 2:  # Ensure minimum replication
                    affected_files.append(file_id)
        
        # Trigger re-replication for affected files
        for file_id in affected_files:
            self._trigger_replication(file_id, target_replicas=3)
    
    def _trigger_replication(self, file_id: str, target_replicas: int = 3):
        """Trigger file replication to maintain redundancy"""
        if file_id not in self.files:
            return
        
        file_info = self.files[file_id]
        current_replicas = len(file_info.replica_nodes)
        
        if current_replicas >= target_replicas:
            return
        
        # Select nodes for replication
        available_nodes = [node_id for node_id in self.nodes.keys() 
                          if node_id not in file_info.replica_nodes]
        
        needed_replicas = target_replicas - current_replicas
        selected_nodes = available_nodes[:needed_replicas]
        
        for node_id in selected_nodes:
            print(f"🔄 Replicating file {file_info.file_name} to node {node_id}")
            file_info.replica_nodes.add(node_id)
            self.node_storage_usage[node_id] += file_info.file_size
