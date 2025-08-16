"""
Core Networking Module - Connection Management
Handles network connections, protocols, and communication
"""

import socket
import threading
import time
import pickle
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum, auto

from .packet_manager import PacketManager, PacketType, ReliableSocketManager
from ..timing.clock_manager import clock_manager


class ConnectionState(Enum):
    """Connection state enumeration"""
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    RECONNECTING = auto()
    FAILED = auto()


@dataclass
class ConnectionInfo:
    """Information about a network connection"""
    peer_id: str
    host: str
    port: int
    state: ConnectionState
    connected_at: Optional[float] = None
    last_activity: Optional[float] = None
    reconnect_attempts: int = 0
    max_reconnect_attempts: int = 5


class NetworkProtocol:
    """Network protocol handler"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.message_handlers: Dict[str, Callable] = {}
        
    def register_handler(self, message_type: str, handler: Callable):
        """Register message handler"""
        self.message_handlers[message_type] = handler
    
    def handle_message(self, message: Dict[str, Any], sender_id: str) -> Optional[Dict[str, Any]]:
        """Handle incoming message"""
        message_type = message.get('type', 'unknown')
        
        if message_type in self.message_handlers:
            try:
                with clock_manager.measure_operation(f"handle_{message_type}"):
                    return self.message_handlers[message_type](message, sender_id)
            except Exception as e:
                print(f"Error handling {message_type} from {sender_id}: {e}")
                return {'type': 'error', 'message': str(e)}
        else:
            print(f"Unknown message type: {message_type} from {sender_id}")
            return {'type': 'error', 'message': f'Unknown message type: {message_type}'}
    
    def create_message(self, message_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create protocol message"""
        return {
            'type': message_type,
            'sender': self.node_id,
            'timestamp': time.time(),
            'data': data
        }


class ConnectionManager:
    """Manages network connections and communication"""
    
    def __init__(self, node_id: str, host: str = 'localhost', port: int = 0):
        self.node_id = node_id
        self.host = host
        self.port = port
        
        # Connection management
        self.connections: Dict[str, ConnectionInfo] = {}
        self.sockets: Dict[str, socket.socket] = {}
        self.lock = threading.RLock()
        
        # Protocol and packet management
        self.protocol = NetworkProtocol(node_id)
        self.packet_manager = PacketManager(node_id)
        self.reliable_manager = ReliableSocketManager(node_id)
        
        # Server socket for incoming connections
        self.server_socket: Optional[socket.socket] = None
        self.server_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Heartbeat management
        self.heartbeat_interval = 5.0
        self.heartbeat_timeout = 15.0
        self.heartbeat_thread: Optional[threading.Thread] = None
        
        # Statistics
        self.connection_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'failed_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'bytes_sent': 0,
            'bytes_received': 0
        }
    
    def start_server(self, port: int = None) -> bool:
        """Start server to accept incoming connections"""
        if port:
            self.port = port
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            
            # Update port if it was auto-assigned
            if self.port == 0:
                self.port = self.server_socket.getsockname()[1]
            
            self.running = True
            
            # Start server thread
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            
            # Start heartbeat thread
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self.heartbeat_thread.start()
            
            print(f"[{self.node_id}] Server started on {self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"[{self.node_id}] Failed to start server: {e}")
            return False
    
    def _server_loop(self):
        """Main server loop for accepting connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                
                # Handle new connection in separate thread
                connection_thread = threading.Thread(
                    target=self._handle_client_connection,
                    args=(client_socket, address),
                    daemon=True
                )
                connection_thread.start()
                
            except OSError:
                if self.running:
                    print(f"[{self.node_id}] Server socket error")
                break
            except Exception as e:
                print(f"[{self.node_id}] Server error: {e}")
    
    def _handle_client_connection(self, client_socket: socket.socket, address: tuple):
        """Handle incoming client connection"""
        peer_id = None
        
        try:
            # Receive initial handshake
            with clock_manager.measure_operation("connection_handshake"):
                data = client_socket.recv(4096)
                if data:
                    message = pickle.loads(data)
                    if message.get('type') == 'handshake':
                        peer_id = message.get('sender')
                        
                        # Store connection
                        with self.lock:
                            self.connections[peer_id] = ConnectionInfo(
                                peer_id=peer_id,
                                host=address[0],
                                port=address[1],
                                state=ConnectionState.CONNECTED,
                                connected_at=time.time(),
                                last_activity=time.time()
                            )
                            self.sockets[peer_id] = client_socket
                            self.connection_stats['total_connections'] += 1
                            self.connection_stats['active_connections'] += 1
                        
                        # Send handshake response
                        response = self.protocol.create_message('handshake_ack', {
                            'node_id': self.node_id,
                            'timestamp': time.time()
                        })
                        client_socket.sendall(pickle.dumps(response))
                        
                        print(f"[{self.node_id}] Connected to {peer_id} from {address}")
            
            # Handle messages from this connection
            while self.running and peer_id:
                try:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    
                    with clock_manager.measure_operation("message_processing"):
                        message = pickle.loads(data)
                        
                        # Update activity timestamp
                        with self.lock:
                            if peer_id in self.connections:
                                self.connections[peer_id].last_activity = time.time()
                        
                        # Process message
                        response = self.protocol.handle_message(message, peer_id)
                        
                        # Send response if any
                        if response:
                            client_socket.sendall(pickle.dumps(response))
                        
                        # Update statistics
                        with self.lock:
                            self.connection_stats['messages_received'] += 1
                            self.connection_stats['bytes_received'] += len(data)
                
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[{self.node_id}] Error handling message from {peer_id}: {e}")
                    break
        
        except Exception as e:
            print(f"[{self.node_id}] Connection error: {e}")
        
        finally:
            # Clean up connection
            if peer_id:
                self.disconnect_peer(peer_id)
            else:
                try:
                    client_socket.close()
                except:
                    pass
    
    def connect_to_peer(self, peer_id: str, host: str, port: int) -> bool:
        """Connect to a peer"""
        try:
            with clock_manager.measure_operation(f"connect_to_{peer_id}"):
                # Create socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10.0)
                sock.connect((host, port))
                
                # Send handshake
                handshake = self.protocol.create_message('handshake', {
                    'node_id': self.node_id
                })
                sock.sendall(pickle.dumps(handshake))
                
                # Wait for handshake response
                response_data = sock.recv(4096)
                response = pickle.loads(response_data)
                
                if response.get('type') == 'handshake_ack':
                    # Store connection
                    with self.lock:
                        self.connections[peer_id] = ConnectionInfo(
                            peer_id=peer_id,
                            host=host,
                            port=port,
                            state=ConnectionState.CONNECTED,
                            connected_at=time.time(),
                            last_activity=time.time()
                        )
                        self.sockets[peer_id] = sock
                        self.connection_stats['total_connections'] += 1
                        self.connection_stats['active_connections'] += 1
                    
                    print(f"[{self.node_id}] Connected to {peer_id} at {host}:{port}")
                    return True
                else:
                    sock.close()
                    return False
        
        except Exception as e:
            print(f"[{self.node_id}] Failed to connect to {peer_id}: {e}")
            with self.lock:
                self.connection_stats['failed_connections'] += 1
            return False
    
    def send_message(self, peer_id: str, message_type: str, data: Dict[str, Any]) -> bool:
        """Send message to peer"""
        if peer_id not in self.sockets:
            return False
        
        try:
            with clock_manager.measure_operation(f"send_{message_type}"):
                message = self.protocol.create_message(message_type, data)
                serialized = pickle.dumps(message)
                
                sock = self.sockets[peer_id]
                sock.sendall(serialized)
                
                # Update statistics
                with self.lock:
                    self.connection_stats['messages_sent'] += 1
                    self.connection_stats['bytes_sent'] += len(serialized)
                    
                    if peer_id in self.connections:
                        self.connections[peer_id].last_activity = time.time()
                
                return True
        
        except Exception as e:
            print(f"[{self.node_id}] Failed to send message to {peer_id}: {e}")
            self.disconnect_peer(peer_id)
            return False
    
    def disconnect_peer(self, peer_id: str):
        """Disconnect from peer"""
        with self.lock:
            if peer_id in self.sockets:
                try:
                    self.sockets[peer_id].close()
                except:
                    pass
                del self.sockets[peer_id]
            
            if peer_id in self.connections:
                self.connections[peer_id].state = ConnectionState.DISCONNECTED
                self.connection_stats['active_connections'] -= 1
                print(f"[{self.node_id}] Disconnected from {peer_id}")
    
    def _heartbeat_loop(self):
        """Heartbeat monitoring loop"""
        while self.running:
            current_time = time.time()
            
            with self.lock:
                # Check for inactive connections
                inactive_peers = []
                for peer_id, conn_info in self.connections.items():
                    if (conn_info.state == ConnectionState.CONNECTED and
                        conn_info.last_activity and
                        current_time - conn_info.last_activity > self.heartbeat_timeout):
                        inactive_peers.append(peer_id)
                
                # Disconnect inactive peers
                for peer_id in inactive_peers:
                    print(f"[{self.node_id}] Peer {peer_id} timed out")
                    self.disconnect_peer(peer_id)
            
            time.sleep(self.heartbeat_interval)
    
    def get_connection_info(self, peer_id: str) -> Optional[ConnectionInfo]:
        """Get connection information for peer"""
        with self.lock:
            return self.connections.get(peer_id)
    
    def get_all_connections(self) -> Dict[str, ConnectionInfo]:
        """Get all connection information"""
        with self.lock:
            return self.connections.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get connection statistics"""
        with self.lock:
            stats = self.connection_stats.copy()
            stats['active_peers'] = list(self.connections.keys())
            stats['server_port'] = self.port
            return stats
    
    def shutdown(self):
        """Shutdown connection manager"""
        print(f"[{self.node_id}] Shutting down connection manager...")
        
        self.running = False
        
        # Close all peer connections
        with self.lock:
            for peer_id in list(self.sockets.keys()):
                self.disconnect_peer(peer_id)
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        # Wait for threads to finish
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=2)
        
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=2)
        
        # Cleanup reliable manager
        self.reliable_manager.cleanup()
        
        print(f"[{self.node_id}] Connection manager shutdown complete")
