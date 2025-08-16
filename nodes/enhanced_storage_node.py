"""
Enhanced Storage Node Implementation
Uses modular architecture with proper separation of concerns
"""

import os
import time
import threading
import uuid
import psutil
from typing import Dict, List, Optional, Set

from core import (
    ConnectionManager,
    FileManager,
    ReplicationManager,
    metrics_collector,
    performance_reporter,
    clock_manager
)
from statistics_manager import stats_manager


class EnhancedStorageNode:
    """Enhanced storage node with modular architecture"""
    
    def __init__(self, node_id: str, cpu_capacity: int, memory_capacity: int,
                 storage_capacity: int, bandwidth: int, network_host: str = 'localhost',
                 network_port: int = 5000, listen_port: int = 0):
        
        self.node_id = node_id
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.storage_capacity = storage_capacity * 1024 ** 3  # Convert GB to bytes
        self.bandwidth = bandwidth * 1000000  # Convert Mbps to bps
        self.network_host = network_host
        self.network_port = network_port
        
        # Create storage directory
        self.storage_dir = f"enhanced_node_storage_{node_id}"
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize core modules
        self.connection_manager = ConnectionManager(node_id, 'localhost', listen_port)
        self.file_manager = FileManager(self.storage_dir)
        self.replication_manager = ReplicationManager(self.file_manager)
        
        # Node state
        self.running = False
        self.connected_to_controller = False
        
        # Statistics tracking
        self.node_stats = {
            'files_uploaded': 0,
            'files_downloaded': 0,
            'bytes_transferred': 0,
            'uptime_start': time.time()
        }
        
        # Setup message handlers
        self._setup_message_handlers()
        
        # Start metrics collection
        metrics_collector.start_collection()
        
        # Register custom metrics
        self._register_custom_metrics()
    
    def _setup_message_handlers(self):
        """Setup message handlers for different operations"""
        protocol = self.connection_manager.protocol
        
        protocol.register_handler('file_upload_request', self._handle_file_upload_request)
        protocol.register_handler('file_download_request', self._handle_file_download_request)
        protocol.register_handler('file_chunk', self._handle_file_chunk)
        protocol.register_handler('replication_request', self._handle_replication_request)
        protocol.register_handler('health_check', self._handle_health_check)
        protocol.register_handler('stats_request', self._handle_stats_request)
    
    def _register_custom_metrics(self):
        """Register custom metrics for collection"""
        metrics_collector.register_metric_callback(
            f'node.{self.node_id}.storage_usage',
            lambda: (self.file_manager.get_statistics()['bytes_uploaded'] / self.storage_capacity) * 100
        )
        
        metrics_collector.register_metric_callback(
            f'node.{self.node_id}.active_connections',
            lambda: len(self.connection_manager.get_all_connections())
        )
        
        metrics_collector.register_metric_callback(
            f'node.{self.node_id}.files_stored',
            lambda: len(self.file_manager.list_files())
        )
    
    def start(self) -> bool:
        """Start the enhanced storage node"""
        try:
            print(f"🚀 Starting enhanced storage node: {self.node_id}")
            
            # Start connection manager
            if not self.connection_manager.start_server():
                raise RuntimeError("Failed to start connection manager")
            
            # Connect to network controller
            if not self._connect_to_controller():
                print(f"⚠️  Failed to connect to controller, running in standalone mode")
            
            self.running = True
            
            # Start background tasks
            self._start_background_tasks()
            
            print(f"✅ Enhanced storage node {self.node_id} started successfully")
            print(f"   📡 Listening on port: {self.connection_manager.port}")
            print(f"   💾 Storage capacity: {self._format_bytes(self.storage_capacity)}")
            print(f"   🔗 Network bandwidth: {self.bandwidth / 1000000:.0f} Mbps")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start node {self.node_id}: {e}")
            return False
    
    def _connect_to_controller(self) -> bool:
        """Connect to the network controller"""
        try:
            with clock_manager.measure_operation("controller_connection"):
                success = self.connection_manager.connect_to_peer(
                    'controller', self.network_host, self.network_port
                )
                
                if success:
                    # Send registration message
                    registration_data = {
                        'node_id': self.node_id,
                        'capacity': {
                            'cpu': self.cpu_capacity,
                            'memory': self.memory_capacity,
                            'storage': self.storage_capacity,
                            'bandwidth': self.bandwidth
                        },
                        'listen_port': self.connection_manager.port
                    }
                    
                    self.connection_manager.send_message(
                        'controller', 'node_registration', registration_data
                    )
                    
                    self.connected_to_controller = True
                    print(f"✅ Connected to controller at {self.network_host}:{self.network_port}")
                    
                return success
                
        except Exception as e:
            print(f"❌ Controller connection failed: {e}")
            return False
    
    def _start_background_tasks(self):
        """Start background monitoring and maintenance tasks"""
        # Heartbeat thread
        heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        heartbeat_thread.start()
        
        # Cleanup thread
        cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        cleanup_thread.start()
        
        # Statistics reporting thread
        stats_thread = threading.Thread(target=self._stats_reporting_loop, daemon=True)
        stats_thread.start()
    
    def _heartbeat_loop(self):
        """Send periodic heartbeats to controller"""
        while self.running:
            if self.connected_to_controller:
                try:
                    heartbeat_data = {
                        'timestamp': time.time(),
                        'status': 'healthy',
                        'stats': self._get_node_stats()
                    }
                    
                    success = self.connection_manager.send_message(
                        'controller', 'heartbeat', heartbeat_data
                    )
                    
                    if not success:
                        print(f"⚠️  Heartbeat failed, attempting reconnection...")
                        self.connected_to_controller = False
                        self._connect_to_controller()
                
                except Exception as e:
                    print(f"❌ Heartbeat error: {e}")
            
            time.sleep(5)  # 5-second heartbeat interval
    
    def _cleanup_loop(self):
        """Periodic cleanup of old data"""
        while self.running:
            try:
                # Cleanup old file operations
                self.file_manager.cleanup_completed_operations()
                
                # Cleanup old timing measurements
                clock_manager.cleanup_old_measurements()
                
            except Exception as e:
                print(f"❌ Cleanup error: {e}")
            
            time.sleep(300)  # 5-minute cleanup interval
    
    def _stats_reporting_loop(self):
        """Periodic statistics reporting"""
        while self.running:
            try:
                # Generate and print performance report
                system_report = performance_reporter.generate_system_report()
                transfer_report = performance_reporter.generate_transfer_report()

                print(f"\n📊 Node {self.node_id} Performance Report:")
                print(system_report)
                if transfer_report:
                    print(transfer_report)

                # Show node summary with actual statistics
                node_summary = stats_manager.generate_node_summary(
                    self.node_id,
                    self.storage_capacity,
                    len(stats_manager.active_transfers),
                    self.node_stats['files_uploaded']
                )
                print(node_summary)
                print("-" * 50)

            except Exception as e:
                print(f"❌ Stats reporting error: {e}")

            time.sleep(30)  # 30-second reporting interval
    
    def upload_file(self, file_path: str, replication_factor: int = 2) -> bool:
        """Upload file using enhanced file management with proper statistics"""
        try:
            with clock_manager.measure_operation(f"file_upload_{os.path.basename(file_path)}"):
                print(f"📤 Starting enhanced upload: {os.path.basename(file_path)}")

                # Start upload operation
                operation_id = self.file_manager.start_upload_operation(
                    file_path, {'controller'}, self.node_id
                )

                # Get file metadata
                operation = self.file_manager.get_operation_status(operation_id)
                if not operation:
                    return False

                metadata = operation.file_metadata

                # Start transfer tracking in both systems
                metrics_collector.start_transfer_tracking(
                    operation_id, metadata.file_name, metadata.file_size, metadata.total_chunks
                )

                stats_transfer = stats_manager.start_transfer(
                    operation_id, metadata.file_name, metadata.file_size,
                    self.node_id, ['controller'], metadata.total_chunks
                )

                # Create chunks
                chunks = self.file_manager.chunker.create_chunks(file_path)

                # Process chunks with realistic timing and progress updates
                for i, chunk in enumerate(chunks):
                    # Simulate realistic chunk processing time
                    chunk_start_time = time.time()
                    time.sleep(0.05 + (chunk.size / (10 * 1024 * 1024)))  # Realistic processing time

                    # Process chunk
                    success = self.file_manager.process_chunk_upload(operation_id, chunk)

                    if success:
                        # Calculate progress
                        bytes_transferred = sum(c.size for c in chunks[:i+1])
                        progress = (bytes_transferred / metadata.file_size) * 100

                        # Update both metrics systems
                        metrics_collector.update_transfer_progress(
                            operation_id, bytes_transferred, i + 1
                        )

                        stats_manager.update_transfer_progress(
                            operation_id, i + 1, progress, psutil.cpu_percent(interval=None)
                        )

                        # Record timing
                        chunk_time = time.time() - chunk_start_time
                        clock_manager.record_file_operation("chunk_upload", chunk_time)

                        # Show progress
                        if (i + 1) % max(1, len(chunks) // 10) == 0 or i == len(chunks) - 1:
                            print(f"   📈 Progress: {progress:.1f}% ({i+1}/{len(chunks)} chunks)")
                    else:
                        metrics_collector.complete_transfer(operation_id, False)
                        stats_manager.complete_transfer(operation_id, False)
                        return False

                # Complete transfer
                transfer_stats = stats_manager.complete_transfer(operation_id, True)
                metrics_collector.complete_transfer(operation_id, True)

                # Update node statistics
                self.node_stats['files_uploaded'] += 1
                self.node_stats['bytes_transferred'] += metadata.file_size

                # Update storage usage
                stats_manager.update_node_storage(self.node_id, metadata.file_size)

                # Display transfer completion report
                if transfer_stats:
                    print(stats_manager.generate_transfer_report(transfer_stats))

                print(f"✅ Enhanced upload completed: {metadata.file_name}")
                return True

        except Exception as e:
            print(f"❌ Enhanced upload failed: {e}")
            return False
    
    def create_test_file(self, file_name: str, size_mb: float) -> str:
        """Create test file for demonstration"""
        file_path = os.path.join(self.storage_dir, file_name)
        size_bytes = int(size_mb * 1024 * 1024)
        
        with clock_manager.measure_operation("test_file_creation"):
            print(f"📝 Creating test file: {file_name} ({self._format_bytes(size_bytes)})")
            
            with open(file_path, 'wb') as f:
                chunk_size = 1024 * 1024  # 1MB chunks
                remaining = size_bytes
                
                while remaining > 0:
                    write_size = min(chunk_size, remaining)
                    data = os.urandom(write_size)
                    f.write(data)
                    remaining -= write_size
        
        print(f"✅ Test file created: {file_path}")
        return file_path
    
    def _handle_file_upload_request(self, message: Dict, sender_id: str) -> Dict:
        """Handle file upload request"""
        try:
            file_info = message['data']
            # Process upload request
            return {'status': 'accepted', 'message': 'Upload request accepted'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _handle_file_download_request(self, message: Dict, sender_id: str) -> Dict:
        """Handle file download request"""
        try:
            file_id = message['data']['file_id']
            # Process download request
            return {'status': 'accepted', 'message': 'Download request accepted'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _handle_file_chunk(self, message: Dict, sender_id: str) -> Dict:
        """Handle file chunk"""
        try:
            chunk_data = message['data']
            # Process chunk
            return {'status': 'received', 'message': 'Chunk received'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _handle_replication_request(self, message: Dict, sender_id: str) -> Dict:
        """Handle replication request"""
        try:
            replication_info = message['data']
            # Process replication
            return {'status': 'accepted', 'message': 'Replication accepted'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _handle_health_check(self, message: Dict, sender_id: str) -> Dict:
        """Handle health check"""
        return {
            'status': 'healthy',
            'stats': self._get_node_stats(),
            'timestamp': time.time()
        }
    
    def _handle_stats_request(self, message: Dict, sender_id: str) -> Dict:
        """Handle statistics request"""
        return {
            'stats': self._get_comprehensive_stats(),
            'timestamp': time.time()
        }
    
    def _get_node_stats(self) -> Dict:
        """Get basic node statistics"""
        file_stats = self.file_manager.get_statistics()
        connection_stats = self.connection_manager.get_statistics()
        
        return {
            'uptime': time.time() - self.node_stats['uptime_start'],
            'files_stored': file_stats['total_files'],
            'storage_used': file_stats['bytes_uploaded'],
            'storage_capacity': self.storage_capacity,
            'active_connections': connection_stats['active_connections'],
            'files_uploaded': self.node_stats['files_uploaded'],
            'files_downloaded': self.node_stats['files_downloaded'],
            'bytes_transferred': self.node_stats['bytes_transferred']
        }
    
    def _get_comprehensive_stats(self) -> Dict:
        """Get comprehensive statistics"""
        basic_stats = self._get_node_stats()
        metrics_summary = metrics_collector.get_statistics_summary()
        timing_report = clock_manager.get_all_operation_stats()
        
        return {
            'basic': basic_stats,
            'metrics': metrics_summary,
            'timing': {name: {
                'total_calls': stats.total_calls,
                'avg_duration': stats.avg_duration,
                'min_duration': stats.min_duration,
                'max_duration': stats.max_duration
            } for name, stats in timing_report.items()}
        }
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def shutdown(self):
        """Graceful shutdown"""
        print(f"🛑 Shutting down enhanced storage node: {self.node_id}")
        
        self.running = False
        
        # Stop metrics collection
        metrics_collector.stop_collection()
        
        # Shutdown connection manager
        self.connection_manager.shutdown()
        
        # Generate final report
        print(f"\n📊 Final Statistics for {self.node_id}:")
        print(performance_reporter.generate_system_report())
        print(clock_manager.generate_timing_report())
        
        print(f"✅ Enhanced storage node {self.node_id} shutdown complete")
