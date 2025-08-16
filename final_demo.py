#!/usr/bin/env python3
"""
Final Demo - Clean Statistics Display
Shows the improved, essential statistics without verbose operation details
"""

import os
import sys
import time
import threading

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nodes.enhanced_storage_node import EnhancedStorageNode
from core import clock_manager, performance_reporter
from statistics_manager import stats_manager


def main():
    """Run final demo with clean statistics"""
    print("🌟 FINAL DEMO - CLEAN STATISTICS DISPLAY")
    print("=" * 60)
    print("Showcasing essential statistics without verbose details")
    print("=" * 60)
    
    nodes = []
    
    try:
        # Create test nodes
        print("🔧 Creating test nodes...")
        
        node_configs = [
            {"node_id": "demo_nodeA", "cpu": 4, "memory": 16, "storage": 1000, "bandwidth": 1000, "port": 9001},
            {"node_id": "demo_nodeB", "cpu": 8, "memory": 32, "storage": 2000, "bandwidth": 1500, "port": 9002}
        ]
        
        for config in node_configs:
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
                nodes.append(node)
                print(f"✅ {config['node_id']} started successfully")
            else:
                print(f"❌ Failed to start {config['node_id']}")
            
            time.sleep(1)
        
        if not nodes:
            print("❌ No nodes started, exiting demo")
            return
        
        # Wait for system stabilization
        print("\n⏳ System stabilizing...")
        time.sleep(3)
        
        # Create and upload test files
        print("\n📝 Creating test files...")
        test_files = []
        
        for i, node in enumerate(nodes):
            for j in range(2):
                file_name = f"demo_file_{node.node_id}_{j+1}.dat"
                size_mb = 1.5 + j * 0.5
                file_path = node.create_test_file(file_name, size_mb)
                test_files.append((node, file_path))
                print(f"   📁 Created {file_name} ({size_mb:.1f} MB) on {node.node_id}")
        
        # Upload files sequentially first
        print("\n📤 Sequential file uploads...")
        for i, (node, file_path) in enumerate(test_files[:2]):
            print(f"   📤 Uploading {os.path.basename(file_path)} from {node.node_id}...")
            success = node.upload_file(file_path, replication_factor=2)
            if success:
                print(f"   ✅ Upload completed")
            else:
                print(f"   ❌ Upload failed")
        
        # Then do concurrent uploads
        print("\n🚀 Concurrent file uploads...")
        
        def upload_worker(node, file_path):
            print(f"   🔄 Starting concurrent upload: {os.path.basename(file_path)} from {node.node_id}")
            success = node.upload_file(file_path, replication_factor=2)
            if success:
                print(f"   ✅ Concurrent upload completed: {os.path.basename(file_path)}")
            else:
                print(f"   ❌ Concurrent upload failed: {os.path.basename(file_path)}")
        
        # Start concurrent uploads for remaining files
        threads = []
        for node, file_path in test_files[2:]:
            thread = threading.Thread(target=upload_worker, args=(node, file_path), daemon=True)
            threads.append(thread)
            thread.start()
            time.sleep(0.2)  # Stagger starts
        
        # Wait for concurrent uploads to complete
        for thread in threads:
            thread.join()
        
        # Wait for all operations to complete
        print("\n⏳ Waiting for all operations to complete...")
        time.sleep(3)
        
        # Display clean statistics
        print("\n" + "=" * 60)
        print("📊 FINAL CLEAN STATISTICS DISPLAY")
        print("=" * 60)
        
        # System performance
        print("🖥️  SYSTEM PERFORMANCE:")
        system_report = performance_reporter.generate_system_report()
        print(system_report)
        
        # Essential performance summary (cleaned up)
        timing_report = clock_manager.generate_timing_report()
        print(f"\n{timing_report}")
        
        # Node summaries
        print("\n🖥️  NODE SUMMARIES:")
        for node in nodes:
            summary = stats_manager.generate_node_summary(
                node.node_id,
                node.storage_capacity,
                len(stats_manager.active_transfers),
                node.node_stats['files_uploaded']
            )
            print(summary)
        
        # Global statistics summary
        print(f"\n🌐 GLOBAL SUMMARY:")
        print(f"   📁 Total Files Transferred: {stats_manager.total_files_transferred}")
        print(f"   📊 Total Data Transferred: {stats_manager.format_size(stats_manager.total_data_transferred)}")
        print(f"   🔄 Active Transfers: {len(stats_manager.active_transfers)}")
        print(f"   📈 Completed Transfers: {len(stats_manager.transfer_history)}")
        
        print("\n" + "=" * 60)
        print("✅ FINAL DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("🎯 Key Improvements Made:")
        print("   ✅ Removed verbose operation statistics")
        print("   ✅ Showing only essential performance metrics")
        print("   ✅ Clean, readable summary format")
        print("   ✅ Focus on user-relevant information")
        print("   ✅ Maintained detailed transfer reports")
        print("   ✅ Kept emoji-rich visual indicators")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        for node in nodes:
            try:
                node.shutdown()
            except:
                pass
        print("✅ Cleanup completed")


if __name__ == "__main__":
    print("🚀 Starting Final Demo with Clean Statistics")
    print("📋 This demo shows the improved statistics display")
    print("⚠️  Make sure no other instances are running on ports 9001-9002")
    print()
    
    main()
