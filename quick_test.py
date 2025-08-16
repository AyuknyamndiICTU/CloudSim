#!/usr/bin/env python3
"""
Quick Test Script for Cloud Storage System
Tests basic functionality without full demo
"""

import time
import os
import sys
import threading
from storage_virtual_node import StorageVirtualNode
from storage_virtual_network import StorageVirtualNetwork


def test_basic_functionality():
    """Test basic upload/download functionality"""
    print("🧪 Starting Quick Test of Cloud Storage System")
    print("=" * 50)
    
    # Start network controller
    print("1. 🌐 Starting network controller...")
    network = StorageVirtualNetwork(host='localhost', port=5000, grpc_port=50051)
    time.sleep(2)
    print("   ✅ Network controller started")
    
    # Create test nodes
    print("2. 🖥️  Creating test nodes...")
    try:
        node1 = StorageVirtualNode(
            node_id="test_node1",
            cpu_capacity=4,
            memory_capacity=16,
            storage_capacity=500,
            bandwidth=1000,
            network_host='localhost',
            network_port=5000
        )
        print("   ✅ Node 1 created and connected")
        
        node2 = StorageVirtualNode(
            node_id="test_node2", 
            cpu_capacity=4,
            memory_capacity=16,
            storage_capacity=500,
            bandwidth=1000,
            network_host='localhost',
            network_port=5000
        )
        print("   ✅ Node 2 created and connected")
        
        time.sleep(3)  # Allow nodes to register
        
        # Create test file
        print("3. 📝 Creating test file...")
        test_file = node1.create_test_file("test_upload.txt", 2.0)  # 2MB file
        print(f"   ✅ Test file created: {test_file}")
        
        # Test upload
        print("4. 📤 Testing file upload...")
        upload_success = node1.upload_file_to_controller(test_file, replication_factor=2)
        
        if upload_success:
            print("   ✅ File upload successful!")
        else:
            print("   ❌ File upload failed!")
            return False
        
        # Test concurrent uploads
        print("5. 🚀 Testing concurrent uploads...")
        
        # Create multiple test files
        test_files = []
        for i in range(3):
            file_name = f"concurrent_test_{i+1}.txt"
            file_path = node1.create_test_file(file_name, 1.0 + i * 0.5)
            test_files.append(file_path)
        
        def upload_worker(node, file_path):
            return node.upload_file_to_controller(file_path, replication_factor=2)
        
        # Start concurrent uploads
        threads = []
        results = []
        
        for file_path in test_files:
            def worker(fp=file_path):
                result = upload_worker(node1, fp)
                results.append(result)
            
            thread = threading.Thread(target=worker, daemon=True)
            threads.append(thread)
            thread.start()
            time.sleep(0.2)  # Stagger starts
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        successful_uploads = sum(results)
        print(f"   ✅ Concurrent uploads: {successful_uploads}/{len(test_files)} successful")
        
        # Show final statistics
        print("6. 📊 Final Statistics:")
        from statistics_manager import stats_manager
        
        print(f"   📁 Total files transferred: {stats_manager.total_files_transferred}")
        print(f"   📊 Total data transferred: {stats_manager.format_size(stats_manager.total_data_transferred)}")
        print(f"   🔄 Active transfers: {len(stats_manager.active_transfers)}")
        print(f"   📈 Completed transfers: {len(stats_manager.transfer_history)}")
        
        # Show node summaries
        for node in [node1, node2]:
            summary = stats_manager.generate_node_summary(
                node.node_id,
                node.total_storage,
                len(node.active_transfers),
                node.total_requests_processed
            )
            print(summary)
        
        print("\n🎉 Quick test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        try:
            if 'node1' in locals():
                node1.shutdown()
            if 'node2' in locals():
                node2.shutdown()
            if 'network' in locals():
                network.shutdown()
        except:
            pass
        print("✅ Cleanup completed")


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
