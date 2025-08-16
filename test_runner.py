#!/usr/bin/env python3
"""
Test Runner for Cloud Storage System
Simple interface to run different tests and demos
"""

import sys
import os
import subprocess
import time

def print_banner():
    """Print test runner banner"""
    print("🧪 CLOUD STORAGE SYSTEM TEST RUNNER")
    print("=" * 50)
    print("Choose a test to run:")
    print()

def print_menu():
    """Print test menu"""
    print("1. 🧪 Comprehensive Test Suite (All Features)")
    print("2. 🌟 Enhanced Demo (Modular Architecture)")
    print("3. ✨ Final Demo (Clean Statistics)")
    print("4. 📂 File Sharing Demo (NEW!) - RECOMMENDED")
    print("5. 🎬 Original Demo (Legacy System)")
    print("6. 🎮 Interactive Client")
    print("7. ⚡ Quick Test")
    print("8. 📊 Statistics Test Only")
    print("9. 🔧 Module Test (Individual Components)")
    print("10. ❌ Exit")
    print()

def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("🚀 Starting Comprehensive Test Suite...")
    print("This will test all functionalities with proper statistics")
    print("-" * 50)
    
    try:
        import comprehensive_test
        test_suite = comprehensive_test.ComprehensiveTest()
        test_suite.run_comprehensive_test()
    except Exception as e:
        print(f"❌ Error running comprehensive test: {e}")
        import traceback
        traceback.print_exc()

def run_enhanced_demo():
    """Run enhanced demo"""
    print("🌟 Starting Enhanced Demo...")
    print("This showcases the new modular architecture")
    print("-" * 50)

    try:
        import enhanced_demo
        demo = enhanced_demo.EnhancedCloudDemo()
        demo.run_comprehensive_demo()
    except Exception as e:
        print(f"❌ Error running enhanced demo: {e}")
        import traceback
        traceback.print_exc()

def run_final_demo():
    """Run final demo with clean statistics"""
    print("✨ Starting Final Demo...")
    print("This showcases clean, essential statistics display")
    print("-" * 50)

    try:
        import final_demo
        final_demo.main()
    except Exception as e:
        print(f"❌ Error running final demo: {e}")
        import traceback
        traceback.print_exc()

def run_file_sharing_demo():
    """Run file sharing demo"""
    print("📂 Starting File Sharing Demo...")
    print("This showcases the new file sharing features")
    print("-" * 50)

    try:
        import file_sharing_demo
        file_sharing_demo.main()
    except Exception as e:
        print(f"❌ Error running file sharing demo: {e}")
        import traceback
        traceback.print_exc()

def run_original_demo():
    """Run original demo"""
    print("🎬 Starting Original Demo...")
    print("This runs the legacy system demo")
    print("-" * 50)
    
    try:
        import demo_cloud_system
        demo = demo_cloud_system.CloudStorageDemo()
        demo.run_complete_demo()
    except Exception as e:
        print(f"❌ Error running original demo: {e}")
        import traceback
        traceback.print_exc()

def run_interactive_client():
    """Run interactive client"""
    print("🎮 Starting Interactive Client...")
    print("This allows manual testing of features")
    print("-" * 50)
    
    try:
        import interactive_client
        client = interactive_client.InteractiveClient()
        client.run()
    except Exception as e:
        print(f"❌ Error running interactive client: {e}")
        import traceback
        traceback.print_exc()

def run_quick_test():
    """Run quick test"""
    print("⚡ Starting Quick Test...")
    print("This runs a basic functionality test")
    print("-" * 50)
    
    try:
        import quick_test
        success = quick_test.test_basic_functionality()
        if success:
            print("✅ Quick test completed successfully!")
        else:
            print("❌ Quick test failed!")
    except Exception as e:
        print(f"❌ Error running quick test: {e}")
        import traceback
        traceback.print_exc()

def run_statistics_test():
    """Run statistics-focused test"""
    print("📊 Starting Statistics Test...")
    print("This focuses on testing statistics display")
    print("-" * 50)
    
    try:
        from nodes.enhanced_storage_node import EnhancedStorageNode
        from statistics_manager import stats_manager
        from core import performance_reporter, clock_manager
        
        print("🔧 Creating test node...")
        node = EnhancedStorageNode(
            node_id="stats_test_node",
            cpu_capacity=4,
            memory_capacity=16,
            storage_capacity=500,
            bandwidth=1000,
            listen_port=8001
        )
        
        if node.start():
            print("✅ Node started successfully")
            
            # Create and upload test files
            print("📝 Creating test files...")
            test_files = []
            for i in range(3):
                file_name = f"stats_test_{i+1}.dat"
                size_mb = 1.0 + i * 0.5
                file_path = node.create_test_file(file_name, size_mb)
                test_files.append(file_path)
            
            print("📤 Uploading files to generate statistics...")
            for file_path in test_files:
                success = node.upload_file(file_path, replication_factor=2)
                if success:
                    print(f"   ✅ Uploaded {os.path.basename(file_path)}")
                else:
                    print(f"   ❌ Failed to upload {os.path.basename(file_path)}")
            
            # Wait for statistics to accumulate
            print("⏳ Waiting for statistics to accumulate...")
            time.sleep(3)
            
            # Display comprehensive statistics
            print("\n📊 COMPREHENSIVE STATISTICS DISPLAY:")
            print("=" * 60)
            
            # System performance report
            system_report = performance_reporter.generate_system_report()
            print("🖥️  SYSTEM PERFORMANCE:")
            print(system_report)
            
            # Node summary
            node_summary = stats_manager.generate_node_summary(
                node.node_id,
                node.storage_capacity,
                len(stats_manager.active_transfers),
                node.node_stats['files_uploaded']
            )
            print("\n🖥️  NODE SUMMARY:")
            print(node_summary)
            
            # Performance summary
            timing_report = clock_manager.generate_timing_report()
            print("\n⏱️  PERFORMANCE SUMMARY:")
            print(timing_report)
            
            # Global statistics
            print(f"\n🌐 GLOBAL STATISTICS:")
            print(f"   📁 Total Files Transferred: {stats_manager.total_files_transferred}")
            print(f"   📊 Total Data Transferred: {stats_manager.format_size(stats_manager.total_data_transferred)}")
            print(f"   🔄 Active Transfers: {len(stats_manager.active_transfers)}")
            print(f"   📈 Transfer History: {len(stats_manager.transfer_history)} completed")
            
            print("\n✅ Statistics test completed successfully!")
            
            # Cleanup
            node.shutdown()
        else:
            print("❌ Failed to start test node")
            
    except Exception as e:
        print(f"❌ Error running statistics test: {e}")
        import traceback
        traceback.print_exc()

def run_module_test():
    """Test individual modules"""
    print("🔧 Starting Module Test...")
    print("This tests individual modular components")
    print("-" * 50)
    
    try:
        # Test packet manager
        print("📦 Testing PacketManager...")
        from core.networking.packet_manager import PacketManager, PacketType
        packet_mgr = PacketManager("test_node")
        print("   ✅ PacketManager loaded successfully")
        
        # Test clock manager
        print("⏱️  Testing ClockManager...")
        from core.timing.clock_manager import ClockManager, clock_manager
        with clock_manager.measure_operation("test_operation"):
            time.sleep(0.1)
        print("   ✅ ClockManager working correctly")
        
        # Test file manager
        print("📁 Testing FileManager...")
        from core.file_management.file_operations import FileManager
        file_mgr = FileManager("./test_module_storage")
        print("   ✅ FileManager loaded successfully")
        
        # Test metrics collector
        print("📊 Testing MetricsCollector...")
        from core.monitoring.metrics_collector import MetricsCollector
        metrics_mgr = MetricsCollector()
        metrics_mgr.record_gauge("test_metric", 42.0)
        print("   ✅ MetricsCollector working correctly")
        
        # Test connection manager
        print("🔗 Testing ConnectionManager...")
        from core.networking.connection_manager import ConnectionManager
        conn_mgr = ConnectionManager("test_node")
        print("   ✅ ConnectionManager loaded successfully")
        
        print("\n✅ All modules tested successfully!")
        print("🏗️  Modular architecture is working correctly")
        
    except Exception as e:
        print(f"❌ Error running module test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test runner"""
    while True:
        print_banner()
        print_menu()
        
        try:
            choice = input("Enter your choice (1-10): ").strip()

            if choice == '1':
                run_comprehensive_test()
            elif choice == '2':
                run_enhanced_demo()
            elif choice == '3':
                run_final_demo()
            elif choice == '4':
                run_file_sharing_demo()
            elif choice == '5':
                run_original_demo()
            elif choice == '6':
                run_interactive_client()
            elif choice == '7':
                run_quick_test()
            elif choice == '8':
                run_statistics_test()
            elif choice == '9':
                run_module_test()
            elif choice == '10':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
            
            print("\n" + "="*50)
            input("Press Enter to continue...")
            print("\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Cloud Storage System Test Runner")
    print("📋 Make sure no other instances are running")
    print()
    main()
