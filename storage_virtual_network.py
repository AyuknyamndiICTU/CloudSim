import time
import socket
import threading
import pickle
import uuid
import grpc
import hashlib
from concurrent import futures
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict
from dataclasses import dataclass, field

import file_transfer_pb2
import file_transfer_pb2_grpc
from statistics_manager import stats_manager


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
class NodeFileInfo:
    node_id: str
    host: str
    port: int
    capacity: Dict
    last_heartbeat: float
    status: str = "active"
    stored_files: Set[str] = field(default_factory=set)
    active_transfers: Set[str] = field(default_factory=set)


class FileTransferService(file_transfer_pb2_grpc.FileTransferServiceServicer):
    def __init__(self, network_controller):
        self.controller = network_controller

    def UploadFile(self, request_iterator, context):
        """Handle file upload with streaming chunks"""
        file_metadata = None
        file_id = None
        chunks_received = 0
        total_size_received = 0
        transfer_id = str(uuid.uuid4())

        try:
            for request in request_iterator:
                if request.HasField('metadata'):
                    file_metadata = request.metadata
                    file_id = file_metadata.file_id

                    # Start tracking transfer
                    chunk_count = (file_metadata.file_size + 512*1024 - 1) // (512*1024)  # 512KB chunks
                    stats_manager.start_transfer(
                        transfer_id, file_metadata.file_name, file_metadata.file_size,
                        file_metadata.source_node_id, ["controller"], chunk_count
                    )

                    print(f"📤 Starting upload: {file_metadata.file_name} ({stats_manager.format_size(file_metadata.file_size)})")

                elif request.HasField('chunk'):
                    chunk = request.chunk
                    chunks_received += 1
                    total_size_received += len(chunk.data)

                    # Update progress
                    progress = (total_size_received / file_metadata.file_size) * 100 if file_metadata else 0
                    stats_manager.update_transfer_progress(transfer_id, chunks_received, progress)

                    # Simulate processing time
                    time.sleep(0.01)

            # Complete transfer
            if file_metadata:
                # Store file info
                file_info = FileInfo(
                    file_id=file_metadata.file_id,
                    file_name=file_metadata.file_name,
                    file_size=file_metadata.file_size,
                    upload_time=time.time(),
                    source_node=file_metadata.source_node_id,
                    chunk_count=chunks_received
                )

                # Select nodes for replication
                replica_nodes = self.controller._select_replica_nodes(
                    file_metadata.replication_factor,
                    exclude_node=file_metadata.source_node_id
                )

                file_info.replica_nodes.update(replica_nodes)
                self.controller.files[file_id] = file_info

                # Update storage usage
                for node_id in replica_nodes:
                    stats_manager.update_node_storage(node_id, file_metadata.file_size)

                # Complete transfer tracking
                transfer_stats = stats_manager.complete_transfer(transfer_id, True)
                if transfer_stats:
                    print(stats_manager.generate_transfer_report(transfer_stats))

                return file_transfer_pb2.FileUploadResponse(
                    success=True,
                    message="File uploaded successfully",
                    file_id=file_id,
                    replica_nodes=list(replica_nodes)
                )

        except Exception as e:
            stats_manager.complete_transfer(transfer_id, False)
            return file_transfer_pb2.FileUploadResponse(
                success=False,
                message=f"Upload failed: {str(e)}"
            )

    def DownloadFile(self, request, context):
        """Handle file download with streaming chunks"""
        file_id = request.file_id

        if file_id not in self.controller.files:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("File not found")
            return

        file_info = self.controller.files[file_id]
        transfer_id = str(uuid.uuid4())

        # Start tracking download
        chunk_count = file_info.chunk_count
        stats_manager.start_transfer(
            transfer_id, file_info.file_name, file_info.file_size,
            "controller", [request.requesting_node_id], chunk_count
        )

        print(f"📥 Starting download: {file_info.file_name} to {request.requesting_node_id}")

        try:
            # Send metadata first
            yield file_transfer_pb2.FileDownloadResponse(
                metadata=file_transfer_pb2.FileMetadata(
                    file_name=file_info.file_name,
                    file_size=file_info.file_size,
                    file_id=file_info.file_id
                )
            )

            # Send chunks
            chunk_size = 512 * 1024  # 512KB
            chunks_sent = 0

            for i in range(chunk_count):
                # Simulate chunk data
                chunk_data = b'0' * min(chunk_size, file_info.file_size - i * chunk_size)

                yield file_transfer_pb2.FileDownloadResponse(
                    chunk=file_transfer_pb2.FileChunk(
                        file_id=file_id,
                        chunk_id=i,
                        data=chunk_data,
                        chunk_size=len(chunk_data),
                        checksum=hashlib.md5(chunk_data).hexdigest()
                    )
                )

                chunks_sent += 1
                progress = (chunks_sent / chunk_count) * 100
                stats_manager.update_transfer_progress(transfer_id, chunks_sent, progress)

                time.sleep(0.01)  # Simulate network delay

            # Send completion
            transfer_stats = stats_manager.complete_transfer(transfer_id, True)
            if transfer_stats:
                print(stats_manager.generate_transfer_report(transfer_stats))

            yield file_transfer_pb2.FileDownloadResponse(
                complete=file_transfer_pb2.TransferComplete(
                    success=True,
                    message="Download completed successfully"
                )
            )

        except Exception as e:
            stats_manager.complete_transfer(transfer_id, False)
            yield file_transfer_pb2.FileDownloadResponse(
                complete=file_transfer_pb2.TransferComplete(
                    success=False,
                    message=f"Download failed: {str(e)}"
                )
            )


class NetworkController(threading.Thread):
    def __init__(self, host: str = '0.0.0.0', port: int = 5000, grpc_port: int = 50051):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.grpc_port = grpc_port
        self.nodes = {}
        self.files: Dict[str, FileInfo] = {}
        self.lock = threading.Lock()
        self.running = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.heartbeat_timeout = 5
        self.transfer_operations = defaultdict(dict)

        # gRPC server for file transfers
        self.grpc_server = None
        self._start_grpc_server()

    def _start_grpc_server(self):
        """Start gRPC server for file transfer operations"""
        try:
            self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            file_transfer_service = FileTransferService(self)
            file_transfer_pb2_grpc.add_FileTransferServiceServicer_to_server(
                file_transfer_service, self.grpc_server
            )
            self.grpc_server.add_insecure_port(f'[::]:{self.grpc_port}')
            self.grpc_server.start()
            print(f"[Network] gRPC File Transfer Service started on port {self.grpc_port}")
        except Exception as e:
            print(f"[Network] Failed to start gRPC server: {e}")

    def _select_replica_nodes(self, replication_factor: int, exclude_node: str = None) -> List[str]:
        """Select nodes for file replication"""
        with self.lock:
            available_nodes = [
                node_id for node_id in self.nodes.keys()
                if node_id != exclude_node and self.nodes[node_id]['status'] == 'active'
            ]

            # Select up to replication_factor nodes
            selected = available_nodes[:min(replication_factor, len(available_nodes))]
            return selected

    def run(self):
        self.running = True
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen()
            print(f"[Network] Controller started on {self.host}:{self.port}")
            
            while self.running:
                try:
                    conn, addr = self.socket.accept()
                    threading.Thread(
                        target=self._handle_connection,
                        args=(conn,),
                        daemon=True
                    ).start()
                except OSError as e:
                    if self.running:
                        print(f"[Network] Accept error: {e}")
                    break
        except OSError as e:
            print(f"[Network] Failed to start: {e}")
        finally:
            self.socket.close()
            
    def _handle_connection(self, conn):
        try:
            data = conn.recv(4096)
            if not data:
                return

            message = pickle.loads(data)
            with self.lock:
                if message['action'] == 'REGISTER':
                    node_id = message['node_id']
                    if node_id not in self.nodes:
                        print(f"[Network] Node {node_id} registered (came ONLINE)")
                    self.nodes[node_id] = {
                        'host': message['host'],
                        'port': message['port'],
                        'capacity': message['capacity'],
                        'last_seen': 0,  # 0 means registered but not yet active
                        'status': 'registered'
                    }
                    conn.sendall(pickle.dumps({'status': 'OK'}))

                elif message['action'] == 'ACTIVE_NOTIFICATION':
                    node_id = message['node_id']
                    if node_id in self.nodes:
                        if self.nodes[node_id]['status'] != 'active':
                            print(f"[Network] Node {node_id} is now ACTIVE")
                        self.nodes[node_id]['status'] = 'active'
                        self.nodes[node_id]['last_seen'] = time.time()
                        conn.sendall(pickle.dumps({'status': 'ACK'}))

                elif message['action'] == 'HEARTBEAT':
                    node_id = message['node_id']
                    if node_id in self.nodes:
                        if self.nodes[node_id]['status'] == 'registered':
                            print(f"[Network] Node {node_id} is now ACTIVE")
                            self.nodes[node_id]['status'] = 'active'
                        self.nodes[node_id]['last_seen'] = time.time()
                        conn.sendall(pickle.dumps({'status': 'ACK'}))

                        # Print node summary periodically
                        if hasattr(self, '_last_summary_time'):
                            if time.time() - self._last_summary_time > 30:  # Every 30 seconds
                                self._print_node_summary(node_id)
                                self._last_summary_time = time.time()
                        else:
                            self._last_summary_time = time.time()
                    else:
                        conn.sendall(pickle.dumps({
                            'status': 'ERROR',
                            'error': 'Node not registered'
                        }))

                elif message['action'] == 'FILE_UPLOAD_REQUEST':
                    # Handle file upload request
                    file_info = message.get('file_info', {})
                    response = self._handle_file_upload_request(file_info)
                    conn.sendall(pickle.dumps(response))

                elif message['action'] == 'FILE_DOWNLOAD_REQUEST':
                    # Handle file download request
                    file_id = message.get('file_id')
                    requesting_node = message.get('node_id')
                    response = self._handle_file_download_request(file_id, requesting_node)
                    conn.sendall(pickle.dumps(response))
        except Exception as e:
            print(f"[Network] Connection error: {e}")
        finally:
            conn.close()

    def _handle_file_upload_request(self, file_info: Dict) -> Dict:
        """Handle file upload request from node"""
        try:
            file_id = file_info.get('file_id', str(uuid.uuid4()))
            file_name = file_info.get('file_name', 'unknown')
            file_size = file_info.get('file_size', 0)
            source_node = file_info.get('source_node', 'unknown')
            replication_factor = file_info.get('replication_factor', 2)

            # Select replica nodes
            replica_nodes = self._select_replica_nodes(replication_factor, exclude_node=source_node)

            if not replica_nodes:
                return {
                    'status': 'ERROR',
                    'message': 'No available nodes for replication'
                }

            # Store file info
            file_record = FileInfo(
                file_id=file_id,
                file_name=file_name,
                file_size=file_size,
                upload_time=time.time(),
                source_node=source_node
            )
            file_record.replica_nodes.update(replica_nodes)

            with self.lock:
                self.files[file_id] = file_record

                # Update node storage tracking
                for node_id in replica_nodes:
                    stats_manager.update_node_storage(node_id, file_size)

            print(f"📁 File registered: {file_name} -> replicas: {replica_nodes}")

            return {
                'status': 'SUCCESS',
                'file_id': file_id,
                'replica_nodes': replica_nodes,
                'message': f'File will be replicated to {len(replica_nodes)} nodes'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'message': f'Upload request failed: {str(e)}'
            }

    def _handle_file_download_request(self, file_id: str, requesting_node: str) -> Dict:
        """Handle file download request from node"""
        try:
            with self.lock:
                if file_id not in self.files:
                    return {
                        'status': 'ERROR',
                        'message': 'File not found'
                    }

                file_info = self.files[file_id]
                available_nodes = [
                    node_id for node_id in file_info.replica_nodes
                    if node_id in self.nodes and self.nodes[node_id]['status'] == 'active'
                ]

                if not available_nodes:
                    return {
                        'status': 'ERROR',
                        'message': 'No available replicas for download'
                    }

                # Select best node (for now, just pick the first available)
                source_node = available_nodes[0]

                return {
                    'status': 'SUCCESS',
                    'file_info': {
                        'file_id': file_id,
                        'file_name': file_info.file_name,
                        'file_size': file_info.file_size,
                        'source_node': source_node
                    },
                    'source_nodes': available_nodes,
                    'message': f'File available from {len(available_nodes)} nodes'
                }

        except Exception as e:
            return {
                'status': 'ERROR',
                'message': f'Download request failed: {str(e)}'
            }

    def _print_node_summary(self, node_id: str):
        """Print node summary with current statistics"""
        if node_id in self.nodes:
            node_info = self.nodes[node_id]
            total_storage = node_info['capacity'].get('storage', 0)

            # Count active and completed transfers for this node
            active_transfers = len([
                t for t in stats_manager.active_transfers.values()
                if node_id in t.destination_nodes
            ])

            completed_transfers = len([
                t for t in stats_manager.transfer_history
                if node_id in t.destination_nodes and t.state == "COMPLETED"
            ])

            summary = stats_manager.generate_node_summary(
                node_id, total_storage, active_transfers, completed_transfers
            )
            print(summary)

    def check_node_status(self):
        """Check which nodes are offline"""
        current_time = time.time()
        offline_nodes = []

        with self.lock:
            for node_id, info in list(self.nodes.items()):
                if info['status'] == 'registered':
                    continue  # New node not yet active
                    
                if current_time - info['last_seen'] > self.heartbeat_timeout:
                    offline_nodes.append(node_id)
                    print(f"[Network] Node {node_id} went OFFLINE")
                    del self.nodes[node_id]

        return offline_nodes

    def stop(self):
        self.running = False

        # Stop gRPC server
        if self.grpc_server:
            print("[Network] Stopping gRPC server...")
            self.grpc_server.stop(grace=5)

        # Create temporary connection to unblock accept()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
        except:
            pass

class StorageVirtualNetwork:
    def __init__(self, host: str = '0.0.0.0', port: int = 5000, grpc_port: int = 50051):
        self.controller = NetworkController(host, port, grpc_port)
        self.controller.start()
        self.heartbeat_checker = threading.Thread(
            target=self._check_heartbeats,
            daemon=True
        )
        self.heartbeat_checker.start()
        
    def _check_heartbeats(self):
        while self.controller.running:
            self.controller.check_node_status()
            time.sleep(1)
            
    def add_node(self, node_id: str, host: str, port: int, capacity: Dict):
        """Manually add a node"""
        with self.controller.lock:
            self.controller.nodes[node_id] = {
                'host': host,
                'port': port,
                'capacity': capacity,
                'last_seen': time.time(),
                'status': 'active'
            }
            print(f"[Network] Manually added node {node_id}")
            
    def connect_nodes(self, node1_id: str, node2_id: str, bandwidth: int):
        """Connect two nodes with specified bandwidth"""
        if node1_id in self.controller.nodes and node2_id in self.controller.nodes:
            self._send_connection_info(node1_id, node2_id, bandwidth)
            self._send_connection_info(node2_id, node1_id, bandwidth)
            return True
        return False
        
    def _send_connection_info(self, target_node: str, peer_node: str, bandwidth: int):
        """Send connection information to a node"""
        peer_info = self.controller.nodes[peer_node]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(2)
                s.connect((peer_info['host'], peer_info['port']))
                s.sendall(pickle.dumps({
                    'action': 'CONNECT',
                    'node_id': peer_node,
                    'host': peer_info['host'],
                    'port': peer_info['port'],
                    'bandwidth': bandwidth
                }))
            except ConnectionRefusedError:
                print(f"[Network] Could not connect to node {peer_node}")

    def get_network_stats(self) -> Dict[str, float]:
        """Get overall network statistics"""
        with self.controller.lock:
            total_bandwidth = sum(n['capacity']['bandwidth'] for n in self.controller.nodes.values())
            used_bandwidth = sum(n['capacity']['bandwidth'] * 0.5 for n in self.controller.nodes.values())  # Simulated
            total_storage = sum(n['capacity']['storage'] for n in self.controller.nodes.values())
            used_storage = sum(n['capacity']['storage'] * 0.3 for n in self.controller.nodes.values())  # Simulated
            
            return {
                "total_nodes": len(self.controller.nodes),
                "active_nodes": sum(1 for n in self.controller.nodes.values() if n['status'] == 'active'),
                "total_bandwidth_bps": total_bandwidth,
                "used_bandwidth_bps": used_bandwidth,
                "bandwidth_utilization": (used_bandwidth / total_bandwidth) * 100 if total_bandwidth > 0 else 0,
                "total_storage_bytes": total_storage,
                "used_storage_bytes": used_storage,
                "storage_utilization": (used_storage / total_storage) * 100 if total_storage > 0 else 0,
                "active_transfers": sum(len(t) for t in self.controller.transfer_operations.values())
            }

    def shutdown(self):
        """Graceful shutdown"""
        print("[Network] Shutting down controller...")
        self.controller.stop()
        self.controller.join()
        print("[Network] Controller shutdown complete")