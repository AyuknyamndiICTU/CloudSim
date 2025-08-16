#!/usr/bin/env python3
"""
File Sharing Demo
Demonstrates the new file sharing features with clean emoji status updates
"""

import os
import sys
import time
import threading
import subprocess

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from storage_virtual_node import StorageVirtualNode


def main():
    """Run file sharing demonstration"""
    print("🌟 FILE SHARING SYSTEM DEMONSTRATION")
    print("=" * 60)
    print("Features:")
    print("✅ Clean emoji status updates")
    print("📂 Real-time file listing")
    print("📁 File creation notifications")
    print("📥 Cross-node file downloads")
    print("🔄 Dynamic file list updates")
    print("=" * 60)
    
    nodes = []
    
    try:
        print("\n🔧 Setting up demonstration...")
        
        # Create test nodes
        node_configs = [
            {"node_id": "fileNodeA", "cpu": 4, "memory": 16, "storage": 1000, "bandwidth": 1000},
            {"node_id": "fileNodeB", "cpu": 8, "memory": 32, "storage": 2000, "bandwidth": 1500},
            {"node_id": "fileNodeC", "cpu": 6, "memory": 24, "storage": 1500, "bandwidth": 1200}
        ]
        
        for config in node_configs:
            try:
                print(f"🔧 Creating {config['node_id']}...")
                
                node = StorageVirtualNode(
                    node_id=config["node_id"],
                    cpu_capacity=config["cpu"],
                    memory_capacity=config["memory"],
                    storage_capacity=config["storage"],
                    bandwidth=config["bandwidth"],
                    network_host='localhost',
                    network_port=5000
                )
                
                nodes.append(node)
                print(f"✅ {config['node_id']} created")
                time.sleep(2)  # Allow connection to establish
                
            except Exception as e:
                print(f"❌ Failed to create {config['node_id']}: {e}")
        
        if not nodes:
            print("❌ No nodes created, exiting demo")
            return
        
        print(f"\n✅ Created {len(nodes)} nodes successfully")
        print("⏳ Waiting for system to stabilize...")
        time.sleep(3)
        
        # Demonstrate file creation and listing
        print("\n" + "="*60)
        print("📝 DEMONSTRATION: File Creation & Real-time Listing")
        print("="*60)
        
        # Create files on different nodes
        test_files = [
            (nodes[0], "document1.txt", 2.5),
            (nodes[1], "image_data.bin", 5.0),
            (nodes[0], "config.json", 0.5),
            (nodes[2], "dataset.csv", 3.2),
            (nodes[1], "backup.zip", 8.1)
        ]
        
        print("📁 Creating files on different nodes...")
        print("(Watch the controller terminal for real-time updates)")
        
        created_files = []
        for node, file_name, size_mb in test_files:
            print(f"\n📝 Creating {file_name} ({size_mb} MB) on {node.node_id}...")
            file_path = node.create_test_file(file_name, size_mb)
            created_files.append((node, file_path, file_name))
            
            # Wait a bit to see the real-time updates
            time.sleep(2)
        
        # Demonstrate file listing
        print("\n" + "="*60)
        print("📂 DEMONSTRATION: File Listing from All Nodes")
        print("="*60)
        
        print("📋 Listing available files from first node...")
        available_files = nodes[0].list_available_files()
        
        # Demonstrate cross-node file download
        if available_files:
            print("\n" + "="*60)
            print("📥 DEMONSTRATION: Cross-Node File Download")
            print("="*60)
            
            # Find a file from a different node
            target_file = None
            for file_info in available_files:
                if file_info['owner_node'] != nodes[0].node_id:
                    target_file = file_info
                    break
            
            if target_file:
                print(f"📥 {nodes[0].node_id} downloading {target_file['name']} from {target_file['owner_node']}...")
                success = nodes[0].download_file_by_id(target_file['file_id'], f"downloaded_{target_file['name']}")
                
                if success:
                    print("✅ Cross-node download completed!")
                else:
                    print("❌ Cross-node download failed!")
            else:
                print("ℹ️  All files are on the same node, cannot demonstrate cross-node download")
        
        # Demonstrate node disconnection and file cleanup
        print("\n" + "="*60)
        print("🔌 DEMONSTRATION: Node Disconnection & File Cleanup")
        print("="*60)
        
        if len(nodes) > 1:
            print(f"🔌 Disconnecting {nodes[-1].node_id}...")
            print("(Watch the controller terminal for offline status and file cleanup)")
            
            nodes[-1].shutdown()
            nodes.pop()
            
            # Wait for cleanup to be visible
            time.sleep(5)
            
            print("📋 Listing files after node disconnection...")
            remaining_files = nodes[0].list_available_files()
            print(f"📊 Files remaining: {len(remaining_files)}")
        
        print("\n" + "="*60)
        print("🎉 FILE SHARING DEMONSTRATION COMPLETED!")
        print("="*60)
        print("✨ Features Demonstrated:")
        print("   🔗 Clean emoji connection status")
        print("   📁 Real-time file creation notifications")
        print("   📂 Dynamic file listing updates")
        print("   📥 Cross-node file downloads")
        print("   🗑️  Automatic file cleanup on node disconnect")
        print("   📊 Live file availability tracking")
        
        print("\n💡 Next Steps:")
        print("   1. Start the controller: python main.py --network --host 0.0.0.0 --network-port 5000")
        print("   2. Start nodes: python main.py --node --node-id nodeX --storage 1000")
        print("   3. Use interactive client: python interactive_client.py")
        print("   4. Try option 7 to list available files from all nodes")
        print("   5. Try option 2 to download files by ID")
        
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


def show_usage_instructions():
    """Show detailed usage instructions"""
    print("\n📋 DETAILED USAGE INSTRUCTIONS")
    print("=" * 50)
    
    print("\n1️⃣  START THE CONTROLLER:")
    print("   python main.py --network --host 0.0.0.0 --network-port 5000")
    print("   👀 Watch for clean emoji status updates:")
    print("      🔗 nodeX connected")
    print("      ✅ nodeX online")
    print("      📁 filename.txt (2.5 MB) created on nodeX")
    print("      📂 Available Files list")
    print("      ❌ nodeX offline")
    print("      🗑️  filename.txt removed (owner offline)")
    
    print("\n2️⃣  START NODES (separate terminals):")
    print("   python main.py --node --node-id nodeA --storage 1000")
    print("   python main.py --node --node-id nodeB --storage 2000")
    print("   python main.py --node --node-id nodeC --storage 1500")
    
    print("\n3️⃣  USE INTERACTIVE CLIENT:")
    print("   python interactive_client.py")
    print("   📝 Option 3: Create test files (auto-notifies controller)")
    print("   📂 Option 7: List available files from all nodes")
    print("   📥 Option 2: Download files by ID from other nodes")
    
    print("\n4️⃣  FEATURES TO TRY:")
    print("   • Create files on different nodes")
    print("   • Watch real-time file list updates on controller")
    print("   • Download files from other nodes")
    print("   • Disconnect a node and see file cleanup")
    print("   • Reconnect and create more files")
    
    print("\n🎯 WHAT YOU'LL SEE:")
    print("   Controller Terminal:")
    print("   🔗 nodeA connected")
    print("   ✅ nodeA online")
    print("   📁 test.txt (2.5 MB) created on nodeA")
    print("   📂 Available Files (1 total):")
    print("   📄 test.txt (2.5 MB) - nodeA")
    print("   ❌ nodeA offline")
    print("   🗑️  test.txt removed (owner offline)")


if __name__ == "__main__":
    print("🚀 File Sharing System Demo")
    print("📋 Make sure the controller is running first!")
    print("   Command: python main.py --network --host 0.0.0.0 --network-port 5000")
    
    choice = input("\nChoose option:\n1. Run demo\n2. Show usage instructions\nEnter choice (1-2): ").strip()
    
    if choice == '1':
        main()
    elif choice == '2':
        show_usage_instructions()
    else:
        print("❌ Invalid choice")
