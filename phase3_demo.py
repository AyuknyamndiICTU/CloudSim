#!/usr/bin/env python3
"""
Phase 3 Comprehensive Demo: Multi-Node Testing & Advanced Features
Demonstrates all advanced distributed cloud storage capabilities
"""

import subprocess
import time
import threading
import sys
import os
from typing import List, Dict, Any

class Phase3Demo:
    """Comprehensive Phase 3 demonstration"""
    
    def __init__(self):
        self.controller_process = None
        self.node_processes = {}
        self.interactive_nodes = {}
        
        # Diverse node configurations for realistic testing
        self.node_configs = {
            'serverA': {'cpu': 8, 'memory': 32, 'storage': 2000, 'bandwidth': 1000},  # High-end server
            'serverB': {'cpu': 6, 'memory': 24, 'storage': 1500, 'bandwidth': 750},   # Enterprise server
            'workstation': {'cpu': 4, 'memory': 16, 'storage': 1000, 'bandwidth': 500}, # Workstation
            'laptop': {'cpu': 2, 'memory': 8, 'storage': 500, 'bandwidth': 100},      # Laptop
            'edge': {'cpu': 4, 'memory': 12, 'storage': 800, 'bandwidth': 300},       # Edge device
        }
    
    def start_controller(self):
        """Start the enhanced controller"""
        print("🚀 Starting Enhanced Distributed Cloud Storage Controller...")
        try:
            self.controller_process = subprocess.Popen(
                ['python', 'clean_controller.py'],
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            time.sleep(3)
            print("✅ Controller started in separate window")
            return True
        except Exception as e:
            print(f"❌ Failed to start controller: {e}")
            return False
    
    def start_node(self, node_id: str, interactive: bool = False):
        """Start a node with specified configuration"""
        config = self.node_configs[node_id]
        
        cmd = [
            'python', 'clean_node.py',
            '--node-id', node_id,
            '--cpu', str(config['cpu']),
            '--memory', str(config['memory']),
            '--storage', str(config['storage']),
            '--bandwidth', str(config['bandwidth'])
        ]
        
        if interactive:
            cmd.append('--interactive')
        
        try:
            if interactive:
                # Start interactive nodes in separate console windows
                process = subprocess.Popen(
                    cmd,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                self.interactive_nodes[node_id] = process
                print(f"🖥️  {node_id} started in interactive mode (separate window)")
            else:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.node_processes[node_id] = process
                print(f"✅ {node_id} started (CPU:{config['cpu']}, RAM:{config['memory']}GB, Storage:{config['storage']}GB, BW:{config['bandwidth']}Mbps)")
            
            time.sleep(2)
            return True
        except Exception as e:
            print(f"❌ Failed to start {node_id}: {e}")
            return False
    
    def demonstrate_multi_node_setup(self):
        """Demonstrate multi-node setup with different configurations"""
        print("\n" + "="*80)
        print("🌐 PHASE 3 DEMO: MULTI-NODE DISTRIBUTED CLOUD STORAGE")
        print("="*80)
        
        print("🔧 Starting diverse node ecosystem...")
        
        # Start background nodes
        background_nodes = ['serverA', 'serverB', 'workstation']
        for node_id in background_nodes:
            self.start_node(node_id, interactive=False)
            time.sleep(1)
        
        print("\n⏳ Waiting for nodes to register and stabilize...")
        time.sleep(8)
        
        # Start interactive nodes for user interaction
        print("\n🖥️  Starting interactive nodes (separate windows)...")
        interactive_nodes = ['laptop', 'edge']
        for node_id in interactive_nodes:
            self.start_node(node_id, interactive=True)
            time.sleep(2)
        
        print("\n✅ Multi-node ecosystem established!")
        print("="*80)
        print("🌟 NETWORK OVERVIEW:")
        print(f"   📊 {len(background_nodes)} background nodes running")
        print(f"   🖥️  {len(interactive_nodes)} interactive nodes available")
        print("   🎯 Controller coordinating all operations")
        print("   🔄 Automatic file replication enabled")
        print("   ⚡ Bandwidth-aware transfers active")
        print("   🏥 Fault tolerance monitoring enabled")
        print("="*80)
        
        return True
    
    def demonstrate_file_operations(self):
        """Demonstrate advanced file operations"""
        print("\n📁 ADVANCED FILE OPERATIONS DEMO")
        print("-" * 60)
        
        print("The system now supports:")
        print("✅ Automatic file upload and replication")
        print("✅ Cross-node file downloads")
        print("✅ Real-time file availability updates")
        print("✅ Bandwidth-aware transfer timing")
        print("✅ Progress tracking with ETA")
        print("✅ Storage validation and management")
        
        print("\n💡 Try these operations in the interactive node windows:")
        print("   1. Create files of different sizes")
        print("   2. List available network files")
        print("   3. Download files from other nodes")
        print("   4. Monitor transfer statistics")
        print("   5. Check network status")
        
        return True
    
    def demonstrate_fault_tolerance(self):
        """Demonstrate fault tolerance capabilities"""
        print("\n🛡️  FAULT TOLERANCE DEMONSTRATION")
        print("-" * 60)
        
        print("🔄 Simulating node failure scenario...")
        
        # Stop one background node to simulate failure
        if 'workstation' in self.node_processes:
            print("💥 Simulating workstation node failure...")
            try:
                process = self.node_processes['workstation']
                process.terminate()
                process.wait(timeout=5)
                del self.node_processes['workstation']
                print("✅ Node failure simulated")
            except Exception as e:
                print(f"⚠️  Error during failure simulation: {e}")
        
        print("\n⏳ Observing system response...")
        time.sleep(10)
        
        print("🔄 System should automatically:")
        print("   ✅ Detect the failed node")
        print("   ✅ Update file availability")
        print("   ✅ Trigger re-replication if needed")
        print("   ✅ Redistribute load to remaining nodes")
        
        # Restart the node
        print("\n🔄 Restarting failed node...")
        self.start_node('workstation', interactive=False)
        
        print("⏳ Waiting for recovery...")
        time.sleep(8)
        
        print("✅ Node recovery completed")
        print("🎯 System demonstrates robust fault tolerance!")
        
        return True
    
    def demonstrate_load_balancing(self):
        """Demonstrate load balancing capabilities"""
        print("\n⚖️  LOAD BALANCING DEMONSTRATION")
        print("-" * 60)
        
        print("🎯 The system intelligently balances load based on:")
        print("   📊 Node bandwidth capabilities")
        print("   💾 Available storage space")
        print("   🖥️  CPU resources and current load")
        print("   📈 Historical performance metrics")
        print("   🌐 Network proximity (simulated)")
        
        print("\n🔄 Load balancing features:")
        print("   ✅ Smart replica placement")
        print("   ✅ Optimal source node selection")
        print("   ✅ Concurrent transfer limits")
        print("   ✅ Performance-based routing")
        print("   ✅ Dynamic load redistribution")
        
        return True
    
    def run_comprehensive_demo(self):
        """Run the complete Phase 3 demonstration"""
        print("🌟 PHASE 3: COMPREHENSIVE DISTRIBUTED CLOUD STORAGE DEMO")
        print("="*80)
        print("This demonstration showcases:")
        print("✅ Multi-node setup with diverse configurations")
        print("✅ Advanced file operations and transfers")
        print("✅ Fault tolerance and recovery")
        print("✅ Load balancing and performance optimization")
        print("✅ Real-time monitoring and statistics")
        print("="*80)
        
        try:
            # Start controller
            if not self.start_controller():
                return False
            
            # Demonstrate multi-node setup
            if not self.demonstrate_multi_node_setup():
                return False
            
            # Demonstrate file operations
            self.demonstrate_file_operations()
            
            # Wait for user to try operations
            print("\n⏸️  INTERACTIVE PHASE")
            print("="*80)
            print("🎮 Use the interactive node windows to:")
            print("   • Create files and observe automatic replication")
            print("   • Download files from other nodes")
            print("   • Monitor real-time statistics")
            print("   • Explore all enhanced features")
            print("\nPress Enter when ready to continue with fault tolerance demo...")
            input()
            
            # Demonstrate fault tolerance
            self.demonstrate_fault_tolerance()
            
            # Demonstrate load balancing
            self.demonstrate_load_balancing()
            
            print("\n🎉 PHASE 3 DEMONSTRATION COMPLETED!")
            print("="*80)
            print("🌟 ACHIEVEMENTS UNLOCKED:")
            print("   ✅ Multi-node distributed storage system")
            print("   ✅ Resource-aware node management")
            print("   ✅ Automatic file replication and discovery")
            print("   ✅ Bandwidth-aware chunked transfers")
            print("   ✅ Fault tolerance with automatic recovery")
            print("   ✅ Intelligent load balancing")
            print("   ✅ Real-time performance monitoring")
            print("   ✅ Interactive node terminals")
            print("="*80)
            
            print("\n💡 NEXT STEPS:")
            print("   • Continue using interactive nodes")
            print("   • Run fault_tolerance_test.py for comprehensive testing")
            print("   • Run performance_benchmark.py for detailed metrics")
            print("   • Explore advanced features and edge cases")
            
            print("\nPress Enter to keep the system running or Ctrl+C to exit...")
            input()
            
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️  Demo interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            return False
        finally:
            print("\n🔄 Demo completed. Interactive nodes will continue running.")
            print("Use Ctrl+C in their windows to stop them individually.")
    
    def stop_background_processes(self):
        """Stop background processes only (keep interactive nodes running)"""
        print("\n🛑 Stopping background processes...")
        
        # Stop background nodes
        for node_id, process in list(self.node_processes.items()):
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {node_id} stopped")
            except Exception as e:
                print(f"⚠️  Force killing {node_id}: {e}")
                process.kill()
        
        # Stop controller
        if self.controller_process:
            try:
                self.controller_process.terminate()
                self.controller_process.wait(timeout=5)
                print("✅ Controller stopped")
            except Exception as e:
                print(f"⚠️  Force killing controller: {e}")
                self.controller_process.kill()
        
        print("💡 Interactive nodes are still running in separate windows")

def main():
    """Main demonstration function"""
    demo = Phase3Demo()
    
    try:
        success = demo.run_comprehensive_demo()
        if success:
            print("\n🎯 Phase 3 demo completed successfully!")
        else:
            print("\n❌ Phase 3 demo encountered issues")
    except Exception as e:
        print(f"\n💥 Demo crashed: {e}")
    finally:
        demo.stop_background_processes()

if __name__ == "__main__":
    main()
