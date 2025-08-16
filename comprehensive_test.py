#!/usr/bin/env python3
"""
Comprehensive Test Script for Enhanced Cloud Storage System
Tests all functionalities with proper statistics display
"""

import os
import sys
import time
import threading
import traceback
from typing import List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nodes.enhanced_storage_node import EnhancedStorageNode
from core import clock_manager, metrics_collector, performance_reporter
from statistics_manager import stats_manager


class ComprehensiveTest:
    """Comprehensive test suite for the cloud storage system"""
    
    def __init__(self):
        self.nodes: List[EnhancedStorageNode] = []
        self.test_files = []
        self.test_results = {
            'packet_communication': False,
            'timing_measurements': False,
            'file_operations': False,
            'concurrent_transfers': False,
            'statistics_display': False,
            'modular_architecture': False
        }
    
    def setup_test_environment(self):
        """Setup test environment with nodes"""
        print("🔧 SETTING UP TEST ENVIRONMENT")
        print("=" * 50)
        
        # Create test nodes
        node_configs = [
            {"node_id": "test_nodeA", "cpu": 4, "memory": 16, "storage": 1000, "bandwidth": 1000, "port": 7001},
            {"node_id": "test_nodeB", "cpu": 8, "memory": 32, "storage": 2000, "bandwidth": 1500, "port": 7002},
            {"node_id": "test_nodeC", "cpu": 6, "memory": 24, "storage": 1500, "bandwidth": 1200, "port": 7003}
        ]
        
        for config in node_configs:
            try:
                print(f"🔧 Creating {config['node_id']}...")
                
                node = EnhancedStorageNode(
                    node_id=config["node_id"],
                    cpu_capacity=config["cpu"],
                    memory_capacity=config["memory"],
                    storage_capacity=config["storage"],
                    bandwidth=config["bandwidth"],
                    network_host='localhost',
                    network_port=5000,
                    listen_port=config["port"]
                )
                
                if node.start():
                    self.nodes.append(node)
                    print(f"✅ {config['node_id']} started successfully")
                else:
                    print(f"❌ Failed to start {config['node_id']}")
                
                time.sleep(1)  # Allow node to initialize
                
            except Exception as e:
                print(f"❌ Error creating {config['node_id']}: {e}")
                traceback.print_exc()
        
        print(f"✅ Test environment setup complete: {len(self.nodes)} nodes created")
        return len(self.nodes) > 0
    
    def test_packet_communication(self):
        """Test packet-based communication"""
        print("\n🧪 TEST 1: Packet-Based Communication")
        print("-" * 40)
        
        try:
            if len(self.nodes) < 2:
                print("❌ Need at least 2 nodes for communication test")
                return False
            
            node1, node2 = self.nodes[0], self.nodes[1]
            
            # Test connection establishment
            print(f"🔗 Testing connection between {node1.node_id} and {node2.node_id}")
            
            with clock_manager.measure_operation("packet_communication_test"):
                success = node1.connection_manager.connect_to_peer(
                    node2.node_id, 'localhost', node2.connection_manager.port
                )
            
            if success:
                print("✅ Packet-based connection established")
                
                # Test message exchange
                response = node1.connection_manager.send_message(
                    node2.node_id, 'health_check', {'test_data': 'packet_test'}
                )
                
                if response:
                    print("✅ Packet-based message exchange successful")
                    self.test_results['packet_communication'] = True
                    return True
                else:
                    print("❌ Message exchange failed")
            else:
                print("❌ Packet-based connection failed")
            
            return False
            
        except Exception as e:
            print(f"❌ Packet communication test failed: {e}")
            traceback.print_exc()
            return False
    
    def test_timing_measurements(self):
        """Test comprehensive timing measurements"""
        print("\n🧪 TEST 2: High-Precision Timing Measurements")
        print("-" * 40)
        
        try:
            if not self.nodes:
                print("❌ No nodes available for timing test")
                return False
            
            node = self.nodes[0]
            
            # Test file creation timing
            print("⏱️  Testing file creation timing...")
            with clock_manager.measure_operation("test_file_creation_timing"):
                file_path = node.create_test_file("timing_test.dat", 2.0)
                self.test_files.append(file_path)
            
            # Test multiple operations with timing
            operations = ['operation_1', 'operation_2', 'operation_3']
            for op in operations:
                with clock_manager.measure_operation(f"test_{op}"):
                    time.sleep(0.1)  # Simulate work
            
            # Generate timing report
            timing_stats = clock_manager.get_all_operation_stats()
            
            if timing_stats:
                print("✅ Timing measurements working correctly")
                print(f"📊 Captured {len(timing_stats)} operation types")
                
                # Show sample timing data
                for op_name, stats in list(timing_stats.items())[:3]:
                    print(f"   ⏱️  {op_name}: {stats.avg_duration:.4f}s avg, {stats.total_calls} calls")
                
                self.test_results['timing_measurements'] = True
                return True
            else:
                print("❌ No timing data captured")
                return False
                
        except Exception as e:
            print(f"❌ Timing measurements test failed: {e}")
            traceback.print_exc()
            return False
    
    def test_file_operations(self):
        """Test file operations with statistics"""
        print("\n🧪 TEST 3: File Operations with Statistics")
        print("-" * 40)
        
        try:
            if not self.nodes:
                print("❌ No nodes available for file operations test")
                return False
            
            node = self.nodes[0]
            
            # Create test files
            print("📝 Creating test files...")
            test_files = []
            for i in range(3):
                file_name = f"test_file_{i+1}.dat"
                size_mb = 1.0 + i * 0.5
                file_path = node.create_test_file(file_name, size_mb)
                test_files.append(file_path)
                print(f"   ✅ Created {file_name} ({size_mb:.1f} MB)")
            
            # Test file uploads
            print("📤 Testing file uploads...")
            upload_success = 0
            
            for file_path in test_files:
                print(f"   📤 Uploading {os.path.basename(file_path)}...")
                success = node.upload_file(file_path, replication_factor=2)
                if success:
                    upload_success += 1
                    print(f"   ✅ Upload successful")
                else:
                    print(f"   ❌ Upload failed")
            
            # Check statistics
            print("📊 Checking statistics...")
            node_stats = node._get_node_stats()
            
            print(f"   📁 Files uploaded: {node_stats['files_uploaded']}")
            print(f"   📊 Bytes transferred: {node._format_bytes(node_stats['bytes_transferred'])}")
            print(f"   💾 Storage used: {node._format_bytes(node_stats['storage_used'])}")
            
            if upload_success > 0 and node_stats['files_uploaded'] > 0:
                print("✅ File operations and statistics working correctly")
                self.test_results['file_operations'] = True
                return True
            else:
                print("❌ File operations or statistics not working")
                return False
                
        except Exception as e:
            print(f"❌ File operations test failed: {e}")
            traceback.print_exc()
            return False
    
    def test_concurrent_transfers(self):
        """Test concurrent file transfers"""
        print("\n🧪 TEST 4: Concurrent File Transfers")
        print("-" * 40)
        
        try:
            if not self.nodes:
                print("❌ No nodes available for concurrent test")
                return False
            
            # Create multiple test files
            print("📝 Creating files for concurrent transfer...")
            concurrent_files = []
            
            for i in range(4):
                node = self.nodes[i % len(self.nodes)]
                file_name = f"concurrent_test_{i+1}.dat"
                size_mb = 1.5 + i * 0.2
                file_path = node.create_test_file(file_name, size_mb)
                concurrent_files.append((node, file_path))
                print(f"   ✅ Created {file_name} on {node.node_id}")
            
            # Start concurrent uploads
            print("🚀 Starting concurrent uploads...")
            
            def upload_worker(node, file_path):
                try:
                    success = node.upload_file(file_path, replication_factor=2)
                    return success
                except Exception as e:
                    print(f"❌ Upload worker error: {e}")
                    return False
            
            # Start threads
            threads = []
            results = []
            
            for node, file_path in concurrent_files:
                def worker(n=node, fp=file_path):
                    result = upload_worker(n, fp)
                    results.append(result)
                
                thread = threading.Thread(target=worker, daemon=True)
                threads.append(thread)
                thread.start()
                time.sleep(0.1)  # Stagger starts
            
            # Wait for completion
            for thread in threads:
                thread.join(timeout=30)
            
            successful_transfers = sum(results)
            print(f"📊 Concurrent transfers completed: {successful_transfers}/{len(concurrent_files)} successful")
            
            if successful_transfers > 0:
                print("✅ Concurrent transfers working correctly")
                self.test_results['concurrent_transfers'] = True
                return True
            else:
                print("❌ Concurrent transfers failed")
                return False
                
        except Exception as e:
            print(f"❌ Concurrent transfers test failed: {e}")
            traceback.print_exc()
            return False
    
    def test_statistics_display(self):
        """Test comprehensive statistics display"""
        print("\n🧪 TEST 5: Statistics Display")
        print("-" * 40)
        
        try:
            # Wait for metrics to accumulate
            print("📊 Collecting metrics for analysis...")
            time.sleep(3)
            
            # Test system metrics
            system_report = performance_reporter.generate_system_report()
            print("✅ System performance report generated")
            print(system_report)
            
            # Test transfer metrics
            transfer_report = performance_reporter.generate_transfer_report()
            if transfer_report and "No active transfers" not in transfer_report:
                print("✅ Transfer performance report generated")
                print(transfer_report)
            
            # Test node summaries
            print("\n📋 Node Summaries:")
            for node in self.nodes:
                summary = stats_manager.generate_node_summary(
                    node.node_id,
                    node.storage_capacity,
                    len(stats_manager.active_transfers),
                    node.node_stats['files_uploaded']
                )
                print(summary)
            
            # Test timing report
            timing_report = clock_manager.generate_timing_report()
            print("\n⏱️  Performance Summary:")
            print(timing_report)
            
            print("✅ Statistics display working correctly")
            self.test_results['statistics_display'] = True
            return True
            
        except Exception as e:
            print(f"❌ Statistics display test failed: {e}")
            traceback.print_exc()
            return False
    
    def test_modular_architecture(self):
        """Test modular architecture components"""
        print("\n🧪 TEST 6: Modular Architecture")
        print("-" * 40)
        
        try:
            # Test individual modules
            print("🔧 Testing individual modules...")
            
            # Test packet manager
            from core.networking.packet_manager import PacketManager
            packet_mgr = PacketManager("test_node")
            print("✅ PacketManager module loaded")
            
            # Test clock manager
            from core.timing.clock_manager import ClockManager
            clock_mgr = ClockManager()
            print("✅ ClockManager module loaded")
            
            # Test file manager
            from core.file_management.file_operations import FileManager
            file_mgr = FileManager("./test_storage")
            print("✅ FileManager module loaded")
            
            # Test metrics collector
            from core.monitoring.metrics_collector import MetricsCollector
            metrics_mgr = MetricsCollector()
            print("✅ MetricsCollector module loaded")
            
            print("✅ Modular architecture working correctly")
            self.test_results['modular_architecture'] = True
            return True
            
        except Exception as e:
            print(f"❌ Modular architecture test failed: {e}")
            traceback.print_exc()
            return False
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🧪 COMPREHENSIVE CLOUD STORAGE SYSTEM TEST")
        print("=" * 60)
        print("Testing all functionalities with proper statistics display")
        print("=" * 60)
        
        try:
            # Setup environment
            if not self.setup_test_environment():
                print("❌ Failed to setup test environment")
                return False
            
            # Wait for system stabilization
            print("\n⏳ Allowing system to stabilize...")
            time.sleep(3)
            
            # Run all tests
            tests = [
                ("Packet Communication", self.test_packet_communication),
                ("Timing Measurements", self.test_timing_measurements),
                ("File Operations", self.test_file_operations),
                ("Concurrent Transfers", self.test_concurrent_transfers),
                ("Statistics Display", self.test_statistics_display),
                ("Modular Architecture", self.test_modular_architecture)
            ]
            
            for test_name, test_func in tests:
                try:
                    print(f"\n{'='*60}")
                    success = test_func()
                    if success:
                        print(f"✅ {test_name}: PASSED")
                    else:
                        print(f"❌ {test_name}: FAILED")
                except Exception as e:
                    print(f"❌ {test_name}: ERROR - {e}")
                    traceback.print_exc()
            
            # Final results
            self.display_final_results()
            
        except KeyboardInterrupt:
            print("\n⏹️  Test interrupted by user")
        except Exception as e:
            print(f"\n❌ Test suite failed: {e}")
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def display_final_results(self):
        """Display final test results"""
        print("\n" + "=" * 60)
        print("📊 FINAL TEST RESULTS")
        print("=" * 60)
        
        passed = sum(self.test_results.values())
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\n📈 Overall Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! System is working correctly.")
        else:
            print(f"⚠️  {total - passed} tests failed. Please check the issues above.")
        
        # Display comprehensive statistics
        print("\n📊 FINAL SYSTEM STATISTICS:")
        print("-" * 40)
        
        # Global statistics
        print(f"🌐 Total Files Transferred: {stats_manager.total_files_transferred}")
        print(f"📊 Total Data Transferred: {stats_manager.format_size(stats_manager.total_data_transferred)}")
        print(f"🔄 Active Transfers: {len(stats_manager.active_transfers)}")
        print(f"📈 Transfer History: {len(stats_manager.transfer_history)} completed")
        
        # Node statistics
        for node in self.nodes:
            node_stats = node._get_node_stats()
            print(f"\n🖥️  {node.node_id}:")
            print(f"   📁 Files: {node_stats['files_stored']}")
            print(f"   💾 Storage: {node._format_bytes(node_stats['storage_used'])}/{node._format_bytes(node.storage_capacity)}")
            print(f"   📤 Uploads: {node_stats['files_uploaded']}")
            print(f"   ⏱️  Uptime: {node_stats['uptime']:.1f}s")
    
    def cleanup(self):
        """Clean up test resources"""
        print("\n🧹 Cleaning up test resources...")
        
        # Shutdown nodes
        for node in self.nodes:
            try:
                node.shutdown()
            except Exception as e:
                print(f"Error shutting down {node.node_id}: {e}")
        
        # Stop metrics collection
        try:
            metrics_collector.stop_collection()
        except:
            pass
        
        print("✅ Test cleanup completed")


if __name__ == "__main__":
    print("🚀 Starting Comprehensive Cloud Storage System Test")
    print("📋 This will test all functionalities and display proper statistics")
    print("⚠️  Make sure no other instances are running on ports 7001-7003")
    
    test_suite = ComprehensiveTest()
    test_suite.run_comprehensive_test()
