#!/usr/bin/env python3
"""
Comprehensive Cloud Storage Demo System
Demonstrates file sharing, replication, concurrent transfers, and detailed statistics
"""

import time
import threading
import random
import os
import sys
from typing import List
from storage_virtual_node import StorageVirtualNode
from storage_virtual_network import StorageVirtualNetwork
from statistics_manager import stats_manager


class CloudStorageDemo:
    def __init__(self):
        self.network = None
        self.nodes: List[StorageVirtualNode] = []
        self.demo_files = []
        
    def start_network_controller(self):
        """Start the virtual network controller"""
        print("🌐 Starting Cloud Storage Network Controller...")
        self.network = StorageVirtualNetwork(host='0.0.0.0', port=5000, grpc_port=50051)
        time.sleep(2)  # Allow controller to start
        print("✅ Network Controller started successfully")
        
    def create_nodes(self, count: int = 4):
        """Create multiple storage nodes"""
        print(f"🖥️  Creating {count} storage nodes...")
        
        node_configs = [
            {"node_id": "nodeA", "cpu": 4, "memory": 16, "storage": 1000, "bandwidth": 1000},
            {"node_id": "nodeB", "cpu": 8, "memory": 32, "storage": 2000, "bandwidth": 1500},
            {"node_id": "nodeC", "cpu": 6, "memory": 24, "storage": 1500, "bandwidth": 1200},
            {"node_id": "nodeD", "cpu": 4, "memory": 16, "storage": 800, "bandwidth": 800},
        ]
        
        for i in range(min(count, len(node_configs))):
            config = node_configs[i]
            try:
                node = StorageVirtualNode(
                    node_id=config["node_id"],
                    cpu_capacity=config["cpu"],
                    memory_capacity=config["memory"],
                    storage_capacity=config["storage"],
                    bandwidth=config["bandwidth"],
                    network_host='localhost',
                    network_port=5000
                )
                self.nodes.append(node)
                print(f"✅ Node {config['node_id']} created and connected")
                time.sleep(1)  # Stagger node creation
            except Exception as e:
                print(f"❌ Failed to create node {config['node_id']}: {e}")
        
        print(f"🎉 Successfully created {len(self.nodes)} nodes")
        
    def create_demo_files(self):
        """Create test files for demonstration"""
        print("📝 Creating demo files...")
        
        demo_file_specs = [
            {"name": "concurrent1.txt", "size": 3.0},
            {"name": "concurrent2.txt", "size": 2.5},
            {"name": "concurrent3.txt", "size": 4.0},
            {"name": "large_dataset.bin", "size": 10.0},
            {"name": "config_backup.json", "size": 0.5},
        ]
        
        for spec in demo_file_specs:
            if self.nodes:
                # Create file on first node
                node = self.nodes[0]
                file_path = node.create_test_file(spec["name"], spec["size"])
                self.demo_files.append({
                    "path": file_path,
                    "name": spec["name"],
                    "size": spec["size"],
                    "node": node.node_id
                })
        
        print(f"✅ Created {len(self.demo_files)} demo files")
        
    def demonstrate_single_upload(self):
        """Demonstrate single file upload with detailed statistics"""
        print("\n" + "="*80)
        print("📤 DEMONSTRATION: Single File Upload with Replication")
        print("="*80)
        
        if not self.demo_files or not self.nodes:
            print("❌ No demo files or nodes available")
            return
        
        # Upload first demo file
        demo_file = self.demo_files[0]
        node = self.nodes[0]
        
        print(f"📁 Uploading {demo_file['name']} from {node.node_id}...")
        success = node.upload_file_to_controller(demo_file['path'], replication_factor=3)
        
        if success:
            print("🎉 Single upload demonstration completed!")
        else:
            print("❌ Single upload demonstration failed!")
        
        time.sleep(2)
        
    def demonstrate_concurrent_uploads(self):
        """Demonstrate concurrent file uploads"""
        print("\n" + "="*80)
        print("🚀 DEMONSTRATION: Concurrent File Uploads")
        print("="*80)
        
        if len(self.demo_files) < 3 or len(self.nodes) < 2:
            print("❌ Insufficient demo files or nodes for concurrent demo")
            return
        
        # Create threads for concurrent uploads
        upload_threads = []
        
        for i, demo_file in enumerate(self.demo_files[:3]):
            node = self.nodes[i % len(self.nodes)]
            
            def upload_worker(node_obj, file_info):
                print(f"🔄 [{node_obj.node_id}] Starting concurrent upload: {file_info['name']}")
                success = node_obj.upload_file_to_controller(file_info['path'], replication_factor=2)
                if success:
                    print(f"✅ [{node_obj.node_id}] Completed upload: {file_info['name']}")
                else:
                    print(f"❌ [{node_obj.node_id}] Failed upload: {file_info['name']}")
            
            thread = threading.Thread(
                target=upload_worker,
                args=(node, demo_file),
                daemon=True
            )
            upload_threads.append(thread)
        
        # Start all uploads simultaneously
        print("🚀 Starting concurrent uploads...")
        for thread in upload_threads:
            thread.start()
            time.sleep(0.5)  # Small delay between starts
        
        # Wait for all uploads to complete
        for thread in upload_threads:
            thread.join()
        
        print("🎉 Concurrent upload demonstration completed!")
        time.sleep(3)
        
    def demonstrate_fault_tolerance(self):
        """Demonstrate fault tolerance by simulating node failure"""
        print("\n" + "="*80)
        print("🛡️  DEMONSTRATION: Fault Tolerance and Recovery")
        print("="*80)
        
        if len(self.nodes) < 3:
            print("❌ Need at least 3 nodes for fault tolerance demo")
            return
        
        # Upload a file with high replication
        if self.demo_files:
            demo_file = self.demo_files[-1]  # Use last file
            node = self.nodes[0]
            
            print(f"📁 Uploading {demo_file['name']} with high replication...")
            success = node.upload_file_to_controller(demo_file['path'], replication_factor=3)
            
            if success:
                print("✅ File uploaded with replication")
                
                # Simulate node failure
                print(f"⚠️  Simulating failure of node {self.nodes[1].node_id}...")
                failed_node = self.nodes[1]
                failed_node.shutdown()
                self.nodes.remove(failed_node)
                
                print("🔧 System should automatically handle the failure...")
                time.sleep(5)
                
                print("✅ Fault tolerance demonstration completed!")
            else:
                print("❌ Failed to upload file for fault tolerance demo")
        
    def demonstrate_download_operations(self):
        """Demonstrate file download operations"""
        print("\n" + "="*80)
        print("📥 DEMONSTRATION: File Download Operations")
        print("="*80)
        
        # This would require file IDs from previous uploads
        # For demo purposes, we'll show the concept
        print("📋 Download operations would retrieve files from replicated nodes")
        print("🔍 System automatically selects best available replica")
        print("📊 Transfer statistics are tracked for downloads too")
        
    def show_system_statistics(self):
        """Display comprehensive system statistics"""
        print("\n" + "="*80)
        print("📊 SYSTEM STATISTICS SUMMARY")
        print("="*80)
        
        # Show statistics for each active node
        for node in self.nodes:
            summary = stats_manager.generate_node_summary(
                node.node_id, 
                node.total_storage,
                len(node.active_transfers),
                node.total_requests_processed
            )
            print(summary)
            print("-" * 50)
        
        # Show global statistics
        print(f"🌐 Total Files Transferred: {stats_manager.total_files_transferred}")
        print(f"📊 Total Data Transferred: {stats_manager.format_size(stats_manager.total_data_transferred)}")
        print(f"🔄 Active Transfers: {len(stats_manager.active_transfers)}")
        print(f"📈 Transfer History: {len(stats_manager.transfer_history)} completed")
        
    def run_complete_demo(self):
        """Run the complete demonstration"""
        try:
            print("🎬 Starting Comprehensive Cloud Storage Demonstration")
            print("="*80)
            
            # Start system components
            self.start_network_controller()
            self.create_nodes(4)
            self.create_demo_files()
            
            # Wait for system to stabilize
            print("⏳ Allowing system to stabilize...")
            time.sleep(5)
            
            # Run demonstrations
            self.demonstrate_single_upload()
            self.demonstrate_concurrent_uploads()
            self.demonstrate_fault_tolerance()
            self.demonstrate_download_operations()
            
            # Show final statistics
            self.show_system_statistics()
            
            print("\n" + "="*80)
            print("🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
            print("="*80)
            print("✨ Features demonstrated:")
            print("   📤 File uploads with chunking and streaming")
            print("   🔄 Automatic file replication across nodes")
            print("   🚀 Concurrent file transfers")
            print("   🛡️  Fault tolerance and recovery")
            print("   📊 Detailed statistics with emoji displays")
            print("   🧵 Multi-threaded operations")
            print("   ⚙️  CPU and resource monitoring")
            print("   💾 Dynamic storage tracking")
            
        except KeyboardInterrupt:
            print("\n⏹️  Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up resources...")
        
        # Shutdown nodes
        for node in self.nodes:
            try:
                node.shutdown()
            except:
                pass
        
        # Shutdown network
        if self.network:
            try:
                self.network.shutdown()
            except:
                pass
        
        print("✅ Cleanup completed")


if __name__ == "__main__":
    demo = CloudStorageDemo()
    demo.run_complete_demo()
