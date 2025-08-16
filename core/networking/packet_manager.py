"""
Packet-based Socket Communication Module
Handles reliable packet transmission with headers, checksums, and timing
"""

import struct
import socket
import hashlib
import time
import threading
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum, auto


class PacketType(Enum):
    """Packet type enumeration"""
    HEARTBEAT = auto()
    FILE_UPLOAD = auto()
    FILE_DOWNLOAD = auto()
    FILE_CHUNK = auto()
    CONTROL = auto()
    ACK = auto()
    ERROR = auto()


@dataclass
class PacketHeader:
    """Packet header structure"""
    packet_type: PacketType
    sequence_number: int
    total_packets: int
    payload_size: int
    checksum: str
    timestamp: float
    source_id: str
    destination_id: str


@dataclass
class Packet:
    """Complete packet structure"""
    header: PacketHeader
    payload: bytes


class PacketManager:
    """Manages packet creation, transmission, and validation"""
    
    HEADER_SIZE = 128  # Fixed header size in bytes
    MAX_PAYLOAD_SIZE = 64 * 1024  # 64KB max payload
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.sequence_counter = 0
        self.lock = threading.Lock()
        
        # Timing measurements
        self.transmission_times = {}
        self.round_trip_times = {}
        
    def create_packet(self, packet_type: PacketType, payload: bytes, 
                     destination_id: str, sequence_num: int = None, 
                     total_packets: int = 1) -> Packet:
        """Create a packet with proper header and checksum"""
        with self.lock:
            if sequence_num is None:
                sequence_num = self.sequence_counter
                self.sequence_counter += 1
        
        # Calculate checksum
        checksum = hashlib.md5(payload).hexdigest()
        
        # Create header
        header = PacketHeader(
            packet_type=packet_type,
            sequence_number=sequence_num,
            total_packets=total_packets,
            payload_size=len(payload),
            checksum=checksum,
            timestamp=time.time(),
            source_id=self.node_id,
            destination_id=destination_id
        )
        
        return Packet(header=header, payload=payload)
    
    def serialize_packet(self, packet: Packet) -> bytes:
        """Serialize packet to bytes for transmission"""
        # Pack header into fixed-size binary format
        header_data = struct.pack(
            '!I I I I 32s d 32s 32s',
            packet.header.packet_type.value,
            packet.header.sequence_number,
            packet.header.total_packets,
            packet.header.payload_size,
            packet.header.checksum.encode('utf-8')[:32],
            packet.header.timestamp,
            packet.header.source_id.encode('utf-8')[:32],
            packet.header.destination_id.encode('utf-8')[:32]
        )
        
        # Pad header to fixed size
        header_data = header_data.ljust(self.HEADER_SIZE, b'\x00')
        
        return header_data + packet.payload
    
    def deserialize_packet(self, data: bytes) -> Optional[Packet]:
        """Deserialize bytes to packet"""
        if len(data) < self.HEADER_SIZE:
            return None
        
        try:
            # Unpack header
            header_data = data[:self.HEADER_SIZE]
            payload = data[self.HEADER_SIZE:]
            
            unpacked = struct.unpack('!I I I I 32s d 32s 32s', header_data[:struct.calcsize('!I I I I 32s d 32s 32s')])
            
            packet_type = PacketType(unpacked[0])
            sequence_number = unpacked[1]
            total_packets = unpacked[2]
            payload_size = unpacked[3]
            checksum = unpacked[4].decode('utf-8').rstrip('\x00')
            timestamp = unpacked[5]
            source_id = unpacked[6].decode('utf-8').rstrip('\x00')
            destination_id = unpacked[7].decode('utf-8').rstrip('\x00')
            
            # Validate payload size
            if len(payload) != payload_size:
                return None
            
            # Validate checksum
            calculated_checksum = hashlib.md5(payload).hexdigest()
            if calculated_checksum != checksum:
                return None
            
            header = PacketHeader(
                packet_type=packet_type,
                sequence_number=sequence_number,
                total_packets=total_packets,
                payload_size=payload_size,
                checksum=checksum,
                timestamp=timestamp,
                source_id=source_id,
                destination_id=destination_id
            )
            
            return Packet(header=header, payload=payload)
            
        except Exception as e:
            print(f"Packet deserialization error: {e}")
            return None
    
    def send_packet(self, sock: socket.socket, packet: Packet) -> bool:
        """Send packet with timing measurement"""
        try:
            start_time = time.perf_counter()
            
            serialized = self.serialize_packet(packet)
            
            # Send packet size first
            size_data = struct.pack('!I', len(serialized))
            sock.sendall(size_data)
            
            # Send packet data
            sock.sendall(serialized)
            
            end_time = time.perf_counter()
            transmission_time = end_time - start_time
            
            # Record timing
            self.transmission_times[packet.header.sequence_number] = {
                'start': start_time,
                'end': end_time,
                'duration': transmission_time,
                'size': len(serialized)
            }
            
            return True
            
        except Exception as e:
            print(f"Packet send error: {e}")
            return False
    
    def receive_packet(self, sock: socket.socket, timeout: float = 5.0) -> Optional[Packet]:
        """Receive packet with timing measurement"""
        try:
            start_time = time.perf_counter()
            sock.settimeout(timeout)
            
            # Receive packet size first
            size_data = sock.recv(4)
            if len(size_data) != 4:
                return None
            
            packet_size = struct.unpack('!I', size_data)[0]
            
            # Receive packet data
            received_data = b''
            while len(received_data) < packet_size:
                chunk = sock.recv(packet_size - len(received_data))
                if not chunk:
                    return None
                received_data += chunk
            
            end_time = time.perf_counter()
            
            # Deserialize packet
            packet = self.deserialize_packet(received_data)
            
            if packet:
                # Record round-trip time if this is an ACK
                if packet.header.packet_type == PacketType.ACK:
                    seq_num = packet.header.sequence_number
                    if seq_num in self.transmission_times:
                        original_time = self.transmission_times[seq_num]['start']
                        rtt = end_time - original_time
                        self.round_trip_times[seq_num] = rtt
                
                # Record receive timing
                receive_time = end_time - start_time
                packet.header.receive_time = receive_time
            
            return packet
            
        except socket.timeout:
            return None
        except Exception as e:
            print(f"Packet receive error: {e}")
            return None
    
    def create_ack_packet(self, original_packet: Packet) -> Packet:
        """Create acknowledgment packet"""
        ack_payload = struct.pack('!I d', original_packet.header.sequence_number, time.time())
        
        return self.create_packet(
            PacketType.ACK,
            ack_payload,
            original_packet.header.source_id,
            original_packet.header.sequence_number
        )
    
    def get_transmission_stats(self) -> Dict[str, Any]:
        """Get transmission statistics"""
        if not self.transmission_times:
            return {}
        
        times = [t['duration'] for t in self.transmission_times.values()]
        sizes = [t['size'] for t in self.transmission_times.values()]
        
        return {
            'total_packets': len(self.transmission_times),
            'avg_transmission_time': sum(times) / len(times),
            'min_transmission_time': min(times),
            'max_transmission_time': max(times),
            'total_bytes_sent': sum(sizes),
            'avg_packet_size': sum(sizes) / len(sizes),
            'throughput_bps': sum(sizes) / sum(times) if sum(times) > 0 else 0
        }
    
    def get_rtt_stats(self) -> Dict[str, Any]:
        """Get round-trip time statistics"""
        if not self.round_trip_times:
            return {}
        
        rtts = list(self.round_trip_times.values())
        
        return {
            'total_rtts': len(rtts),
            'avg_rtt': sum(rtts) / len(rtts),
            'min_rtt': min(rtts),
            'max_rtt': max(rtts),
            'rtt_variance': sum((rtt - sum(rtts)/len(rtts))**2 for rtt in rtts) / len(rtts)
        }


class ReliableSocketManager:
    """Manages reliable socket connections with packet-based communication"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.packet_manager = PacketManager(node_id)
        self.connections: Dict[str, socket.socket] = {}
        self.connection_stats: Dict[str, Dict] = {}
        self.lock = threading.Lock()
    
    def create_connection(self, host: str, port: int, peer_id: str) -> bool:
        """Create reliable connection to peer"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((host, port))
            
            with self.lock:
                self.connections[peer_id] = sock
                self.connection_stats[peer_id] = {
                    'connected_at': time.time(),
                    'packets_sent': 0,
                    'packets_received': 0,
                    'bytes_sent': 0,
                    'bytes_received': 0,
                    'errors': 0
                }
            
            return True
            
        except Exception as e:
            print(f"Connection failed to {peer_id} at {host}:{port}: {e}")
            return False
    
    def send_reliable(self, peer_id: str, packet_type: PacketType, 
                     payload: bytes, retries: int = 3) -> bool:
        """Send packet with reliability (ACK/retry mechanism)"""
        if peer_id not in self.connections:
            return False
        
        sock = self.connections[peer_id]
        packet = self.packet_manager.create_packet(packet_type, payload, peer_id)
        
        for attempt in range(retries):
            if self.packet_manager.send_packet(sock, packet):
                # Wait for ACK if not a control packet
                if packet_type != PacketType.ACK:
                    ack = self.packet_manager.receive_packet(sock, timeout=2.0)
                    if ack and ack.header.packet_type == PacketType.ACK:
                        with self.lock:
                            self.connection_stats[peer_id]['packets_sent'] += 1
                            self.connection_stats[peer_id]['bytes_sent'] += len(payload)
                        return True
                else:
                    return True
            
            print(f"Retry {attempt + 1}/{retries} for packet to {peer_id}")
        
        with self.lock:
            self.connection_stats[peer_id]['errors'] += 1
        
        return False
    
    def close_connection(self, peer_id: str):
        """Close connection to peer"""
        with self.lock:
            if peer_id in self.connections:
                try:
                    self.connections[peer_id].close()
                except:
                    pass
                del self.connections[peer_id]
                
                if peer_id in self.connection_stats:
                    self.connection_stats[peer_id]['disconnected_at'] = time.time()
    
    def get_connection_stats(self, peer_id: str) -> Optional[Dict]:
        """Get connection statistics for peer"""
        with self.lock:
            return self.connection_stats.get(peer_id, {}).copy()
    
    def cleanup(self):
        """Clean up all connections"""
        with self.lock:
            for peer_id in list(self.connections.keys()):
                self.close_connection(peer_id)
