#!/usr/bin/env python3
"""
Enhanced Cloud Storage Demo
Demonstrates the new modular architecture with comprehensive features
"""

import time
import threading
import sys
import os
from typing import List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nodes.enhanced_storage_node import EnhancedStorageNode
from core import clock_manager, metrics_collector, performance_reporter


class EnhancedCloudDemo:
    """Enhanced demonstration of the modular cloud storage system"""
    
    def __init__(self):
        self.nodes: List[EnhancedStorageNode] = []
        self.demo_running = False
    
    def create_enhanced_nodes(self, count: int = 3):
        """Create enhanced storage nodes with different configurations"""
        print("🏗️  Creating Enhanced Storage Nodes")
        print("=" * 50)
        
        node_configs = [
            {
                "node_id": "enhanced_nodeA",
                "cpu": 8,
                "memory": 32,
                "storage": 2000,
                "bandwidth": 1500,
                "listen_port": 6001
            },
            {
                "node_id": "enhanced_nodeB", 
                "cpu": 16,
                "memory": 64,
                "storage": 4000,
                "bandwidth": 2000,
                "listen_port": 6002
            },
            {
                "node_id": "enhanced_nodeC",
                "cpu": 12,
                "memory": 48,
                "storage": 3000,
                "bandwidth": 1800,
                "listen_port": 6003
            }
        ]
        
        for i in range(min(count, len(node_configs))):
            config = node_configs[i]
            
            try:
                print(f"🔧 Creating {config['node_id']}...")
                
                node = EnhancedStorageNode(
                    node_id=config["node_id"],
                    cpu_capacity=config["cpu"],
                    memory_capacity=config["memory"],
                    storage_capacity=config["storage"],
                    bandwidth=config["bandwidth"],
                    network_host='localhost',
                    network_port=5000,  # Controller port
                    listen_port=config["listen_port"]
                )
                
                if node.start():
                    self.nodes.append(node)
                    print(f"✅ {config['node_id']} created successfully")
                else:
                    print(f"❌ Failed to create {config['node_id']}")
                
                time.sleep(2)  # Allow node to initialize
                
            except Exception as e:
                print(f"❌ Error creating {config['node_id']}: {e}")
        
        print(f"\n🎉 Successfully created {len(self.nodes)} enhanced nodes")
    
    def demonstrate_packet_communication(self):
        """Demonstrate packet-based communication"""
        print("\n" + "="*60)
        print("📡 DEMONSTRATION: Packet-Based Communication")
        print("="*60)
        
        if len(self.nodes) < 2:
            print("❌ Need at least 2 nodes for communication demo")
            return
        
        node1, node2 = self.nodes[0], self.nodes[1]
        
        print(f"🔗 Testing communication between {node1.node_id} and {node2.node_id}")
        
        # Test connection establishment
        with clock_manager.measure_operation("node_to_node_connection"):
            success = node1.connection_manager.connect_to_peer(
                node2.node_id, 'localhost', node2.connection_manager.port
            )
        
        if success:
            print("✅ Packet-based connection established")
            
            # Test message exchange
            with clock_manager.measure_operation("message_exchange"):
                response = node1.connection_manager.send_message(
                    node2.node_id, 'health_check', {'test': True}
                )
            
            if response:
                print("✅ Packet-based message exchange successful")
            else:
                print("❌ Message exchange failed")
        else:
            print("❌ Packet-based connection failed")
    
    def demonstrate_timing_measurements(self):
        """Demonstrate comprehensive timing measurements"""
        print("\n" + "="*60)
        print("⏱️  DEMONSTRATION: Comprehensive Timing Measurements")
        print("="*60)
        
        if not self.nodes:
            print("❌ No nodes available for timing demo")
            return
        
        node = self.nodes[0]
        
        # Create test files with timing
        print("📝 Creating test files with timing measurements...")
        
        test_files = []
        for i in range(3):
            file_name = f"timing_test_{i+1}.dat"
            size_mb = 1.0 + i * 0.5
            
            with clock_manager.measure_operation(f"create_test_file_{i+1}"):
                file_path = node.create_test_file(file_name, size_mb)
                test_files.append(file_path)
        
        # Upload files with timing
        print("📤 Uploading files with detailed timing...")
        
        for file_path in test_files:
            with clock_manager.measure_operation("enhanced_file_upload"):
                success = node.upload_file(file_path, replication_factor=2)
                if success:
                    print(f"✅ Timed upload: {os.path.basename(file_path)}")
                else:
                    print(f"❌ Timed upload failed: {os.path.basename(file_path)}")
        
        # Generate timing report
        print("\n📊 TIMING ANALYSIS REPORT:")
        print(clock_manager.generate_timing_report())
    
    def demonstrate_metrics_collection(self):
        """Demonstrate comprehensive metrics collection"""
        print("\n" + "="*60)
        print("📊 DEMONSTRATION: Comprehensive Metrics Collection")
        print("="*60)
        
        if not self.nodes:
            print("❌ No nodes available for metrics demo")
            return
        
        # Let metrics collect for a while
        print("📈 Collecting metrics for 10 seconds...")
        time.sleep(10)
        
        # Generate comprehensive reports
        for node in self.nodes:
            print(f"\n🖥️  METRICS REPORT FOR {node.node_id}:")
            print("-" * 40)
            
            # System performance report
            system_report = performance_reporter.generate_system_report()
            print(system_report)
            
            # Transfer performance report
            transfer_report = performance_reporter.generate_transfer_report()
            if transfer_report:
                print(transfer_report)
            
            # Custom node metrics
            stats = node._get_comprehensive_stats()
            print(f"\n📋 Node-Specific Metrics:")
            print(f"   💾 Storage Used: {node._format_bytes(stats['basic']['storage_used'])}")
            print(f"   📁 Files Stored: {stats['basic']['files_stored']}")
            print(f"   🔗 Active Connections: {stats['basic']['active_connections']}")
            print(f"   ⏱️  Uptime: {stats['basic']['uptime']:.1f}s")
    
    def demonstrate_modular_architecture(self):
        """Demonstrate the benefits of modular architecture"""
        print("\n" + "="*60)
        print("🏗️  DEMONSTRATION: Modular Architecture Benefits")
        print("="*60)
        
        print("✨ Modular Components Demonstrated:")
        print("   📡 Networking Module:")
        print("      - Packet-based communication with checksums")
        print("      - Reliable socket management")
        print("      - Connection state tracking")
        print("      - Protocol message handling")
        
        print("   ⏱️  Timing Module:")
        print("      - High-precision performance counters")
        print("      - Operation-specific timing")
        print("      - Network latency measurements")
        print("      - Comprehensive timing reports")
        
        print("   📁 File Management Module:")
        print("      - Intelligent file chunking")
        print("      - Operation tracking")
        print("      - Replication management")
        print("      - Metadata handling")
        
        print("   📊 Monitoring Module:")
        print("      - Real-time metrics collection")
        print("      - System performance tracking")
        print("      - Transfer progress monitoring")
        print("      - Emoji-rich reporting")
        
        print("\n🎯 Architecture Benefits:")
        print("   ✅ Separation of Concerns")
        print("   ✅ Easy Testing and Debugging")
        print("   ✅ Modular Extensibility")
        print("   ✅ Code Reusability")
        print("   ✅ Maintainable Codebase")
    
    def demonstrate_concurrent_operations(self):
        """Demonstrate concurrent file operations"""
        print("\n" + "="*60)
        print("🚀 DEMONSTRATION: Concurrent Operations with Timing")
        print("="*60)
        
        if not self.nodes:
            print("❌ No nodes available for concurrent demo")
            return
        
        # Create multiple test files
        print("📝 Creating multiple test files...")
        test_files = []
        
        for i in range(4):
            node = self.nodes[i % len(self.nodes)]
            file_name = f"concurrent_enhanced_{i+1}.dat"
            size_mb = 2.0 + i * 0.3
            
            file_path = node.create_test_file(file_name, size_mb)
            test_files.append((node, file_path))
        
        # Start concurrent uploads
        print("🚀 Starting concurrent uploads with comprehensive tracking...")
        
        def upload_worker(node, file_path):
            with clock_manager.measure_operation(f"concurrent_upload_{os.path.basename(file_path)}"):
                success = node.upload_file(file_path, replication_factor=2)
                if success:
                    print(f"✅ Concurrent upload completed: {os.path.basename(file_path)} on {node.node_id}")
                else:
                    print(f"❌ Concurrent upload failed: {os.path.basename(file_path)} on {node.node_id}")
        
        # Start threads
        threads = []
        for node, file_path in test_files:
            thread = threading.Thread(target=upload_worker, args=(node, file_path), daemon=True)
            threads.append(thread)
            thread.start()
            time.sleep(0.2)  # Stagger starts
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        print("🎉 Concurrent operations demonstration completed!")
    
    def run_comprehensive_demo(self):
        """Run the complete enhanced demonstration"""
        try:
            print("🌟 ENHANCED CLOUD STORAGE DEMONSTRATION")
            print("🏗️  Featuring Modular Architecture & Advanced Monitoring")
            print("="*70)
            
            self.demo_running = True
            
            # Create enhanced nodes
            self.create_enhanced_nodes(3)
            
            if not self.nodes:
                print("❌ No nodes created, cannot continue demo")
                return
            
            # Wait for system stabilization
            print("\n⏳ Allowing system to stabilize...")
            time.sleep(5)
            
            # Run demonstrations
            self.demonstrate_modular_architecture()
            self.demonstrate_packet_communication()
            self.demonstrate_timing_measurements()
            self.demonstrate_concurrent_operations()
            self.demonstrate_metrics_collection()
            
            # Final comprehensive report
            print("\n" + "="*70)
            print("📊 FINAL COMPREHENSIVE SYSTEM REPORT")
            print("="*70)
            
            # Global timing report
            print(clock_manager.generate_timing_report())
            
            # Global metrics summary
            metrics_summary = metrics_collector.get_statistics_summary()
            print(f"\n🌐 GLOBAL METRICS SUMMARY:")
            print(f"   🖥️  System CPU: {metrics_summary['system']['cpu_percent']:.1f}%")
            print(f"   💾 System Memory: {metrics_summary['system']['memory_percent']:.1f}%")
            print(f"   📊 Active Transfers: {metrics_summary['transfers']['active_count']}")
            print(f"   ✅ Completed Transfers: {metrics_summary['transfers']['completed_count']}")
            
            print("\n🎉 ENHANCED DEMONSTRATION COMPLETED SUCCESSFULLY!")
            print("✨ Features Successfully Demonstrated:")
            print("   📦 Packet-based socket communication")
            print("   ⏱️  High-precision timing measurements")
            print("   🏗️  Modular architecture design")
            print("   📊 Comprehensive metrics collection")
            print("   🚀 Concurrent operations")
            print("   🔧 Easy extensibility and maintenance")
            
        except KeyboardInterrupt:
            print("\n⏹️  Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up enhanced demo resources...")
        
        self.demo_running = False
        
        # Shutdown all nodes
        for node in self.nodes:
            try:
                node.shutdown()
            except Exception as e:
                print(f"Error shutting down {node.node_id}: {e}")
        
        # Stop global metrics collection
        try:
            metrics_collector.stop_collection()
        except:
            pass
        
        print("✅ Enhanced demo cleanup completed")


if __name__ == "__main__":
    print("🚀 Starting Enhanced Cloud Storage Demo...")
    print("📋 Make sure no other instances are running on the same ports")
    print("⚠️  This demo showcases the new modular architecture")
    
    demo = EnhancedCloudDemo()
    demo.run_comprehensive_demo()
