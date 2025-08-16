"""
File Management Module - Core File Operations
Handles file upload, download, chunking, and replication
"""

import os
import hashlib
import uuid
import threading
import time
from typing import Dict, List, Optional, Set, Tuple, BinaryIO
from dataclasses import dataclass, field
from enum import Enum, auto
import math

from ..timing.clock_manager import clock_manager


class FileOperationType(Enum):
    """File operation types"""
    UPLOAD = auto()
    DOWNLOAD = auto()
    REPLICATION = auto()
    DELETION = auto()


class FileStatus(Enum):
    """File status enumeration"""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class FileChunk:
    """File chunk information"""
    chunk_id: int
    offset: int
    size: int
    checksum: str
    data: Optional[bytes] = None
    status: FileStatus = FileStatus.PENDING
    transfer_time: Optional[float] = None


@dataclass
class FileMetadata:
    """File metadata information"""
    file_id: str
    file_name: str
    file_path: str
    file_size: int
    checksum: str
    chunk_size: int
    total_chunks: int
    created_at: float
    modified_at: float
    mime_type: Optional[str] = None
    compression: bool = False
    encryption: bool = False


@dataclass
class FileOperation:
    """File operation tracking"""
    operation_id: str
    operation_type: FileOperationType
    file_metadata: FileMetadata
    source_node: str
    target_nodes: Set[str] = field(default_factory=set)
    status: FileStatus = FileStatus.PENDING
    progress: float = 0.0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    chunks_completed: int = 0


class FileChunker:
    """Handles file chunking operations"""
    
    DEFAULT_CHUNK_SIZE = 512 * 1024  # 512KB
    
    def __init__(self, chunk_size: int = None):
        self.chunk_size = chunk_size or self.DEFAULT_CHUNK_SIZE
    
    def calculate_optimal_chunk_size(self, file_size: int) -> int:
        """Calculate optimal chunk size based on file size"""
        if file_size < 10 * 1024 * 1024:  # < 10MB
            return 256 * 1024  # 256KB
        elif file_size < 100 * 1024 * 1024:  # < 100MB
            return 512 * 1024  # 512KB
        elif file_size < 1024 * 1024 * 1024:  # < 1GB
            return 2 * 1024 * 1024  # 2MB
        else:
            return 10 * 1024 * 1024  # 10MB
    
    def create_chunks(self, file_path: str, chunk_size: int = None) -> List[FileChunk]:
        """Create chunks from file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_size = os.path.getsize(file_path)
        actual_chunk_size = chunk_size or self.calculate_optimal_chunk_size(file_size)
        
        chunks = []
        chunk_id = 0
        
        with clock_manager.measure_operation("file_chunking"):
            with open(file_path, 'rb') as file:
                while True:
                    offset = file.tell()
                    chunk_data = file.read(actual_chunk_size)
                    
                    if not chunk_data:
                        break
                    
                    # Calculate checksum
                    checksum = hashlib.md5(chunk_data).hexdigest()
                    
                    chunk = FileChunk(
                        chunk_id=chunk_id,
                        offset=offset,
                        size=len(chunk_data),
                        checksum=checksum,
                        data=chunk_data
                    )
                    
                    chunks.append(chunk)
                    chunk_id += 1
        
        return chunks
    
    def reassemble_chunks(self, chunks: List[FileChunk], output_path: str) -> bool:
        """Reassemble chunks into file"""
        try:
            with clock_manager.measure_operation("file_reassembly"):
                # Sort chunks by chunk_id
                sorted_chunks = sorted(chunks, key=lambda c: c.chunk_id)
                
                with open(output_path, 'wb') as output_file:
                    for chunk in sorted_chunks:
                        if chunk.data is None:
                            raise ValueError(f"Chunk {chunk.chunk_id} has no data")
                        
                        # Verify checksum
                        calculated_checksum = hashlib.md5(chunk.data).hexdigest()
                        if calculated_checksum != chunk.checksum:
                            raise ValueError(f"Checksum mismatch for chunk {chunk.chunk_id}")
                        
                        output_file.write(chunk.data)
            
            return True
            
        except Exception as e:
            print(f"Error reassembling chunks: {e}")
            return False


class FileManager:
    """Manages file operations and metadata"""
    
    def __init__(self, storage_directory: str):
        self.storage_directory = storage_directory
        self.chunker = FileChunker()
        
        # File tracking
        self.files: Dict[str, FileMetadata] = {}
        self.operations: Dict[str, FileOperation] = {}
        self.lock = threading.RLock()
        
        # Statistics
        self.stats = {
            'files_uploaded': 0,
            'files_downloaded': 0,
            'bytes_uploaded': 0,
            'bytes_downloaded': 0,
            'chunks_processed': 0,
            'operations_completed': 0,
            'operations_failed': 0
        }
        
        # Ensure storage directory exists
        os.makedirs(storage_directory, exist_ok=True)
    
    def create_file_metadata(self, file_path: str, chunk_size: int = None) -> FileMetadata:
        """Create metadata for a file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_stat = os.stat(file_path)
        file_size = file_stat.st_size
        
        # Calculate file checksum
        with clock_manager.measure_operation("file_checksum_calculation"):
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5()
                while chunk := f.read(8192):
                    file_hash.update(chunk)
                file_checksum = file_hash.hexdigest()
        
        # Determine chunk size and count
        actual_chunk_size = chunk_size or self.chunker.calculate_optimal_chunk_size(file_size)
        total_chunks = math.ceil(file_size / actual_chunk_size)
        
        metadata = FileMetadata(
            file_id=str(uuid.uuid4()),
            file_name=os.path.basename(file_path),
            file_path=file_path,
            file_size=file_size,
            checksum=file_checksum,
            chunk_size=actual_chunk_size,
            total_chunks=total_chunks,
            created_at=file_stat.st_ctime,
            modified_at=file_stat.st_mtime
        )
        
        return metadata
    
    def start_upload_operation(self, file_path: str, target_nodes: Set[str], 
                              source_node: str) -> str:
        """Start file upload operation"""
        try:
            # Create metadata
            metadata = self.create_file_metadata(file_path)
            
            # Create operation
            operation = FileOperation(
                operation_id=str(uuid.uuid4()),
                operation_type=FileOperationType.UPLOAD,
                file_metadata=metadata,
                source_node=source_node,
                target_nodes=target_nodes,
                start_time=time.time()
            )
            
            with self.lock:
                self.files[metadata.file_id] = metadata
                self.operations[operation.operation_id] = operation
            
            print(f"📤 Started upload operation: {metadata.file_name} ({self._format_size(metadata.file_size)})")
            return operation.operation_id
            
        except Exception as e:
            print(f"Failed to start upload operation: {e}")
            raise
    
    def start_download_operation(self, file_id: str, target_path: str, 
                                source_node: str) -> str:
        """Start file download operation"""
        try:
            if file_id not in self.files:
                raise ValueError(f"File not found: {file_id}")
            
            metadata = self.files[file_id]
            
            # Create operation
            operation = FileOperation(
                operation_id=str(uuid.uuid4()),
                operation_type=FileOperationType.DOWNLOAD,
                file_metadata=metadata,
                source_node=source_node,
                start_time=time.time()
            )
            
            with self.lock:
                self.operations[operation.operation_id] = operation
            
            print(f"📥 Started download operation: {metadata.file_name}")
            return operation.operation_id
            
        except Exception as e:
            print(f"Failed to start download operation: {e}")
            raise
    
    def process_chunk_upload(self, operation_id: str, chunk: FileChunk) -> bool:
        """Process chunk upload"""
        with self.lock:
            if operation_id not in self.operations:
                return False
            
            operation = self.operations[operation_id]
            
            try:
                with clock_manager.measure_operation("chunk_upload_processing"):
                    # Verify chunk
                    if chunk.data:
                        calculated_checksum = hashlib.md5(chunk.data).hexdigest()
                        if calculated_checksum != chunk.checksum:
                            raise ValueError(f"Checksum mismatch for chunk {chunk.chunk_id}")
                    
                    # Store chunk (in real implementation, this would save to disk)
                    chunk.status = FileStatus.COMPLETED
                    chunk.transfer_time = time.time()
                    
                    # Update operation progress
                    operation.chunks_completed += 1
                    operation.progress = (operation.chunks_completed / operation.file_metadata.total_chunks) * 100
                    
                    # Update statistics
                    self.stats['chunks_processed'] += 1
                    
                    # Check if operation is complete
                    if operation.chunks_completed >= operation.file_metadata.total_chunks:
                        operation.status = FileStatus.COMPLETED
                        operation.end_time = time.time()
                        self.stats['files_uploaded'] += 1
                        self.stats['bytes_uploaded'] += operation.file_metadata.file_size
                        self.stats['operations_completed'] += 1
                        
                        print(f"✅ Upload completed: {operation.file_metadata.file_name}")
                
                return True
                
            except Exception as e:
                print(f"Error processing chunk upload: {e}")
                operation.status = FileStatus.FAILED
                operation.error_message = str(e)
                self.stats['operations_failed'] += 1
                return False
    
    def get_operation_status(self, operation_id: str) -> Optional[FileOperation]:
        """Get operation status"""
        with self.lock:
            return self.operations.get(operation_id)
    
    def get_file_metadata(self, file_id: str) -> Optional[FileMetadata]:
        """Get file metadata"""
        with self.lock:
            return self.files.get(file_id)
    
    def list_files(self) -> List[FileMetadata]:
        """List all files"""
        with self.lock:
            return list(self.files.values())
    
    def get_statistics(self) -> Dict[str, any]:
        """Get file management statistics"""
        with self.lock:
            stats = self.stats.copy()
            stats['total_files'] = len(self.files)
            stats['active_operations'] = len([op for op in self.operations.values() 
                                            if op.status == FileStatus.IN_PROGRESS])
            return stats
    
    def cleanup_completed_operations(self, max_age_hours: int = 24):
        """Clean up old completed operations"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        with self.lock:
            completed_ops = [
                op_id for op_id, op in self.operations.items()
                if op.status in [FileStatus.COMPLETED, FileStatus.FAILED, FileStatus.CANCELLED]
                and op.end_time and op.end_time < cutoff_time
            ]
            
            for op_id in completed_ops:
                del self.operations[op_id]
            
            if completed_ops:
                print(f"🧹 Cleaned up {len(completed_ops)} old operations")
    
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"


class ReplicationManager:
    """Manages file replication across nodes"""
    
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        self.replication_policies: Dict[str, Dict] = {}
        self.replica_locations: Dict[str, Set[str]] = {}  # file_id -> set of node_ids
        self.lock = threading.RLock()
    
    def set_replication_policy(self, file_pattern: str, min_replicas: int, 
                              preferred_nodes: List[str] = None):
        """Set replication policy for files matching pattern"""
        with self.lock:
            self.replication_policies[file_pattern] = {
                'min_replicas': min_replicas,
                'preferred_nodes': preferred_nodes or []
            }
    
    def add_replica_location(self, file_id: str, node_id: str):
        """Add replica location for file"""
        with self.lock:
            if file_id not in self.replica_locations:
                self.replica_locations[file_id] = set()
            self.replica_locations[file_id].add(node_id)
    
    def remove_replica_location(self, file_id: str, node_id: str):
        """Remove replica location for file"""
        with self.lock:
            if file_id in self.replica_locations:
                self.replica_locations[file_id].discard(node_id)
                if not self.replica_locations[file_id]:
                    del self.replica_locations[file_id]
    
    def get_replica_locations(self, file_id: str) -> Set[str]:
        """Get replica locations for file"""
        with self.lock:
            return self.replica_locations.get(file_id, set()).copy()
    
    def check_replication_health(self) -> Dict[str, Dict]:
        """Check replication health for all files"""
        health_report = {}
        
        with self.lock:
            for file_id, metadata in self.file_manager.files.items():
                replicas = self.replica_locations.get(file_id, set())
                
                # Find applicable policy
                min_replicas = 2  # Default
                for pattern, policy in self.replication_policies.items():
                    if pattern in metadata.file_name:
                        min_replicas = policy['min_replicas']
                        break
                
                health_report[file_id] = {
                    'file_name': metadata.file_name,
                    'current_replicas': len(replicas),
                    'required_replicas': min_replicas,
                    'replica_nodes': list(replicas),
                    'healthy': len(replicas) >= min_replicas
                }
        
        return health_report
