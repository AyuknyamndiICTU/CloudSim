# 🌟 Enhanced Cloud Storage Simulation System

A comprehensive cloud storage simulation system with **modular architecture**, featuring file sharing, replication, concurrent transfers, packet-based communication, and detailed statistics monitoring.

## ✨ Features

### 🏗️ **NEW: Modular Architecture**
- **Separation of Concerns**: Each module handles specific functionality
- **Easy Extensibility**: Add new features without modifying existing code
- **Maintainable Codebase**: Clear organization for troubleshooting and updates
- **Reusable Components**: Modules can be used independently

### 📦 **NEW: Packet-Based Communication**
- **Reliable Socket Management**: Packet headers with checksums and sequence numbers
- **Network Timing**: Comprehensive latency and round-trip time measurements
- **Connection State Tracking**: Monitor connection health and performance
- **Protocol Abstraction**: Clean message handling with custom protocols

### ⏱️ **NEW: High-Precision Timing**
- **Performance Counters**: Microsecond-precision timing measurements
- **Operation Tracking**: Detailed timing for all system operations
- **Network Latency**: Real-time network performance monitoring
- **Comprehensive Reports**: Detailed timing analysis with statistics

### 🔧 Core Functionality
- **File Upload/Download**: Seamless file transfer between nodes and controller
- **Automatic Replication**: Files are automatically replicated across multiple nodes
- **Concurrent Transfers**: Multiple file transfers can happen simultaneously
- **Chunk-based Transfer**: Large files are split into chunks for efficient transfer
- **Fault Tolerance**: System handles node failures gracefully

### 📊 Advanced Monitoring
- **Real-time Statistics**: Detailed transfer progress with emoji-rich displays
- **CPU Utilization**: Monitor CPU usage during transfers
- **Storage Tracking**: Dynamic storage usage monitoring
- **Transfer Rates**: Real-time transfer speed calculations
- **Performance Metrics**: Threading, queue sizes, and efficiency tracking

### 🛡️ Reliability Features
- **Heartbeat Monitoring**: Automatic detection of node failures
- **Automatic Re-replication**: Files are re-replicated when nodes fail
- **gRPC Communication**: Robust inter-service communication
- **Thread Safety**: All operations are thread-safe

## 🚀 Quick Start

### Prerequisites
```bash
pip install grpc-tools psutil
```

### 1. Start the Network Controller
```bash
python main.py --network --host 0.0.0.0 --network-port 5000
```

### 2. Start Storage Nodes (in separate terminals)
```bash
# Node 1
python main.py --node --node-id nodeA --cpu 4 --memory 32 --storage 1000 --bandwidth 1000

# Node 2  
python main.py --node --node-id nodeB --cpu 8 --memory 64 --storage 2000 --bandwidth 1500

# Node 3
python main.py --node --node-id nodeC --cpu 6 --memory 48 --storage 1500 --bandwidth 1200
```

### 3. Run Interactive Client
```bash
python interactive_client.py
```

### 4. Run Complete Demo
```bash
python demo_cloud_system.py
```

## 📋 Usage Examples

### File Upload Example
```python
from storage_virtual_node import StorageVirtualNode

# Create a node
node = StorageVirtualNode(
    node_id="test_node",
    cpu_capacity=4,
    memory_capacity=16,
    storage_capacity=500,
    bandwidth=1000
)

# Create and upload a test file
file_path = node.create_test_file("example.txt", 5.0)  # 5MB file
success = node.upload_file_to_controller(file_path, replication_factor=3)
```

### Concurrent Upload Example
```python
import threading

def upload_worker(node, file_path):
    node.upload_file_to_controller(file_path, replication_factor=2)

# Start multiple uploads
threads = []
for file_path in file_paths:
    thread = threading.Thread(target=upload_worker, args=(node, file_path))
    threads.append(thread)
    thread.start()

# Wait for completion
for thread in threads:
    thread.join()
```

## 📊 Statistics Output Examples

### Transfer Completion Report
```
🎉 TRANSFER COMPLETED 🎉
📁 File: concurrent3.txt
📏 File Size: 4.00 MB
⏱️ Duration: 1.20s
🚀 Transfer Rate: 3.34 MB/s
⚙️ CPU Utilization: 92.0%
📋 Task Queue Size: 0
================================================================================
📊 TRANSFER STATISTICS REPORT
================================================================================
📁 File: concurrent1.txt
🆔 Transfer ID: 7946ee6b49ee...
📤 Source: nodeA
📥 Destination: localhost:8002
📏 File Size: 3.00 MB
⏱️  Duration: 0.93s
🚀 Transfer Rate: 3.23 MB/s
📈 Progress: [████████████████████] 100.0%
✅ Chunks Completed: 6

🧩 SEGMENTATION DETAILS
----------------------------------------
🔢 Total Chunks: 6
📦 Chunk Size: 512.00 KB
📦 Last Chunk: 512.00 KB
⚡ Segmentation Time: 0.041s
🎯 Efficiency: 60.00%

📦 ENCAPSULATION PROPERTIES
----------------------------------------
📋 Header Overhead: 192.00 B
📄 Payload Size: 3.00 MB
🗜️  Compression: ❌ Disabled
🔐 Encryption: ❌ Disabled
📊 Protocol Efficiency: 99.99%
📨 Total Packets: 6

🖥️  CPU ALLOCATION & PERFORMANCE
----------------------------------------
⚙️  Cores Used: 4/4
📊 CPU Utilization: 92.0%
🧵 Thread Count: 4
📋 Task Queue Size: 2
⏱️  Scheduling Overhead: 0.033s
⚡ Parallel Efficiency: 88.00%

🧩 CHUNK TRANSFER DETAILS (Top 5)
----------------------------------------
1. Chunk #0: 512.00 KB in 0.125s (✅ success)
2. Chunk #1: 512.00 KB in 0.125s (✅ success)
3. Chunk #2: 512.00 KB in 0.125s (✅ success)
4. Chunk #3: 512.00 KB in 0.125s (✅ success)
5. Chunk #4: 512.00 KB in 0.125s (✅ success)
================================================================================
```

### Node Summary
```
🖥️  NODE SUMMARY: nodeA
==================================================
💾 Storage: [███░░░░░░░░░░░░░░░░░] 15.2%
   Used: 152.00 MB
   Total: 1000.00 GB
   Available: 999.85 GB
🔄 Active Transfers: 2
✅ Completed Transfers: 8
📊 Total Data Transferred: 45.50 MB
```

## 🏗️ Architecture

### 🆕 **NEW: Modular Architecture**

The system has been refactored into a clean modular architecture:

```
core/
├── networking/           # Network communication modules
│   ├── packet_manager.py    # Packet-based socket communication
│   └── connection_manager.py # Connection state management
├── timing/              # High-precision timing modules
│   └── clock_manager.py     # Performance measurement & timing
├── file_management/     # File operation modules
│   └── file_operations.py   # File chunking, upload, download
└── monitoring/          # Metrics and monitoring modules
    └── metrics_collector.py # System & transfer metrics

nodes/
└── enhanced_storage_node.py # Enhanced node using modular components
```

### Core Components
1. **PacketManager**: Reliable packet-based communication with checksums
2. **ConnectionManager**: Network connection state and protocol handling
3. **ClockManager**: High-precision timing and performance measurement
4. **FileManager**: File operations, chunking, and metadata management
5. **MetricsCollector**: Comprehensive system and transfer monitoring
6. **EnhancedStorageNode**: Modular node implementation

### Legacy Components (Still Available)
1. **NetworkController**: Central coordinator managing nodes and file metadata
2. **StorageVirtualNode**: Individual storage nodes with file transfer capabilities
3. **FileTransferService**: gRPC service for file operations
4. **StatisticsManager**: Comprehensive monitoring and reporting system

### Communication Flow
```
Enhanced Node → Packet Manager → Connection Manager → Protocol Handler
     ↓                ↓                    ↓              ↓
Metrics ← Clock Manager ← File Manager ← Timing Measurements ← Operations
```

## 🔧 Configuration

### Node Configuration
- **CPU Capacity**: Number of CPU cores
- **Memory Capacity**: RAM in GB
- **Storage Capacity**: Storage space in GB  
- **Bandwidth**: Network bandwidth in Mbps

### Network Configuration
- **Controller Port**: Default 5000 (TCP)
- **gRPC Port**: Default 50051 (gRPC)
- **Heartbeat Timeout**: 10 seconds
- **Chunk Size**: 512KB default

## 🧪 Testing

### Run All Tests
```bash
# Original system demonstration
python demo_cloud_system.py

# NEW: Enhanced modular architecture demo
python enhanced_demo.py

# Interactive testing
python interactive_client.py

# Manual node testing (original)
python main.py --node --node-id test_node --storage 1000

# NEW: Enhanced node testing
python -c "from nodes.enhanced_storage_node import EnhancedStorageNode; node = EnhancedStorageNode('test', 4, 16, 500, 1000); node.start()"
```

### Test Scenarios
1. **Single File Upload**: Basic upload with replication
2. **Concurrent Uploads**: Multiple simultaneous transfers
3. **Fault Tolerance**: Node failure simulation
4. **Large File Transfer**: Multi-GB file handling
5. **Network Partitioning**: Connection failure recovery

## 📈 Performance Metrics

The system tracks and displays:
- Transfer rates (MB/s)
- CPU utilization (%)
- Memory usage
- Storage utilization
- Network bandwidth usage
- Thread counts
- Queue sizes
- Chunk transfer times
- Replication efficiency

## 🛠️ Troubleshooting

### Common Issues
1. **Connection Refused**: Ensure network controller is running first
2. **gRPC Errors**: Check if port 50051 is available
3. **File Not Found**: Verify file paths and permissions
4. **Memory Issues**: Reduce file sizes or chunk sizes for testing

### Debug Mode
Set environment variable for verbose logging:
```bash
export GRPC_VERBOSITY=DEBUG
export GRPC_TRACE=all
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is for educational and demonstration purposes.

---

🌟 **Enjoy exploring the enhanced cloud storage system!** 🌟
