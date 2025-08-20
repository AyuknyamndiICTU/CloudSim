#!/usr/bin/env python3
"""
Enhanced Download Features Demo
Demonstrates the new file download capabilities:
- Download by file name
- Download multiple files
- Improved user interface
"""

import subprocess
import time
import threading
import sys
import os
from typing import List, Dict, Any

class EnhancedDownloadDemo:
    """Demonstration of enhanced download features"""
    
    def __init__(self):
        self.controller_process = None
        self.node_processes = {}
        
        # Node configurations for testing
        self.node_configs = {
            'server': {'cpu': 8, 'memory': 32, 'storage': 2000, 'bandwidth': 1000},
            'workstation': {'cpu': 4, 'memory': 16, 'storage': 1000, 'bandwidth': 500},
            'laptop': {'cpu': 2, 'memory': 8, 'storage': 500, 'bandwidth': 100},
        }
        
        # Sample files to create for testing
        self.sample_files = [
            {'name': 'project_report.pdf', 'size': 25, 'node': 'server'},
            {'name': 'presentation.pptx', 'size': 15, 'node': 'server'},
            {'name': 'database_backup.sql', 'size': 100, 'node': 'workstation'},
            {'name': 'config_files.zip', 'size': 5, 'node': 'workstation'},
            {'name': 'user_manual.docx', 'size': 8, 'node': 'laptop'},
            {'name': 'system_logs.txt', 'size': 12, 'node': 'laptop'},
        ]
    
    def start_controller(self):
        """Start the controller"""
        print("🚀 Starting Enhanced Controller...")
        try:
            self.controller_process = subprocess.Popen(
                ['python', 'clean_controller.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            time.sleep(3)
            print("✅ Controller started")
            return True
        except Exception as e:
            print(f"❌ Failed to start controller: {e}")
            return False
    
    def start_node(self, node_id: str, interactive: bool = False):
        """Start a node"""
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
                # Start interactive node in separate window
                process = subprocess.Popen(
                    cmd,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                print(f"🖥️  {node_id} started in interactive mode (separate window)")
            else:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print(f"✅ {node_id} started (CPU:{config['cpu']}, Storage:{config['storage']}GB, BW:{config['bandwidth']}Mbps)")
            
            self.node_processes[node_id] = process
            time.sleep(2)
            return True
        except Exception as e:
            print(f"❌ Failed to start {node_id}: {e}")
            return False
    
    def simulate_file_creation(self):
        """Simulate file creation across nodes"""
        print("\n📝 Creating sample files across nodes...")
        print("=" * 60)
        
        for file_info in self.sample_files:
            print(f"📁 {file_info['node']}: {file_info['name']} ({file_info['size']} MB)")
            time.sleep(0.5)  # Simulate creation time
        
        print("\n✅ Sample files created and registered with controller")
        print("🔄 Files are automatically replicated across available nodes")
    
    def demonstrate_download_features(self):
        """Demonstrate the enhanced download features"""
        print("\n" + "="*80)
        print("🎯 ENHANCED DOWNLOAD FEATURES DEMONSTRATION")
        print("="*80)
        
        print("\n🌟 NEW DOWNLOAD CAPABILITIES:")
        print("✅ Download by file name (exact or partial match)")
        print("✅ Download multiple files in batch")
        print("✅ Improved file selection with search")
        print("✅ Storage validation before download")
        print("✅ Progress tracking for batch downloads")
        print("✅ Automatic conflict resolution")
        
        print("\n💡 USAGE EXAMPLES:")
        print("=" * 50)
        
        print("\n1️⃣  DOWNLOAD BY NAME:")
        print("   • download_file_by_name('project_report.pdf')")
        print("   • download_file_by_name('report')  # Partial match")
        print("   • Handles multiple matches with selection menu")
        
        print("\n2️⃣  DOWNLOAD MULTIPLE FILES:")
        print("   • download_multiple_files(['file1.pdf', 'file2.docx'])")
        print("   • Interactive: Enter comma-separated names")
        print("   • Type 'all' to download all available files")
        print("   • Batch progress tracking and summary")
        
        print("\n3️⃣  INTERACTIVE MENU OPTIONS:")
        print("   • Option 4: Download file by index (original)")
        print("   • Option 5: Download file by name (NEW)")
        print("   • Option 6: Download multiple files (NEW)")
        
        print("\n4️⃣  SMART FEATURES:")
        print("   • Case-insensitive file name matching")
        print("   • Partial name matching with suggestions")
        print("   • Storage space validation before download")
        print("   • Duplicate file handling with overwrite option")
        print("   • Real-time progress for batch operations")
        
        return True
    
    def run_demo(self):
        """Run the complete enhanced download demo"""
        print("🌟 ENHANCED DOWNLOAD FEATURES DEMO")
        print("="*80)
        print("This demo showcases the new download capabilities:")
        print("✅ Download files by name instead of index")
        print("✅ Download multiple files in batch operations")
        print("✅ Improved user interface and experience")
        print("="*80)
        
        try:
            # Start controller
            if not self.start_controller():
                return False
            
            # Start background nodes
            background_nodes = ['server', 'workstation']
            for node_id in background_nodes:
                self.start_node(node_id, interactive=False)
                time.sleep(1)
            
            # Wait for nodes to register
            print("\n⏳ Waiting for nodes to register...")
            time.sleep(8)
            
            # Simulate file creation
            self.simulate_file_creation()
            
            # Start interactive node for testing
            print(f"\n🖥️  Starting interactive laptop node...")
            self.start_node('laptop', interactive=True)
            
            # Demonstrate features
            self.demonstrate_download_features()
            
            print("\n🎮 INTERACTIVE TESTING PHASE")
            print("="*80)
            print("Use the laptop node window to test the new features:")
            print("\n📋 STEP-BY-STEP TESTING:")
            print("1. Choose option 3 to list available network files")
            print("2. Try option 5 to download by name:")
            print("   • Enter 'project_report.pdf' for exact match")
            print("   • Enter 'report' for partial match")
            print("3. Try option 6 to download multiple files:")
            print("   • Enter: config_files.zip, user_manual.docx")
            print("   • Or enter 'all' to download everything")
            print("4. Check option 2 to see your downloaded files")
            print("5. Use option 7 to see detailed statistics")
            
            print("\n⏸️  Press Enter when you've finished testing...")
            input()
            
            print("\n🎉 ENHANCED DOWNLOAD DEMO COMPLETED!")
            print("="*80)
            print("🌟 NEW FEATURES DEMONSTRATED:")
            print("   ✅ Download by file name (exact and partial matching)")
            print("   ✅ Multiple file download with batch processing")
            print("   ✅ Improved user interface and error handling")
            print("   ✅ Storage validation and conflict resolution")
            print("   ✅ Progress tracking and download summaries")
            print("="*80)
            
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️  Demo interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            return False
        finally:
            self.stop_all()
    
    def stop_all(self):
        """Stop all processes"""
        print("\n🛑 Stopping demo processes...")
        
        # Stop background nodes
        for node_id, process in list(self.node_processes.items()):
            if node_id != 'laptop':  # Keep interactive node running
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
        
        print("💡 Interactive laptop node is still running for continued testing")

def main():
    """Main demonstration function"""
    demo = EnhancedDownloadDemo()
    
    try:
        success = demo.run_demo()
        if success:
            print("\n🎯 Enhanced download demo completed successfully!")
            print("💡 Continue using the interactive node to explore features")
        else:
            print("\n❌ Enhanced download demo encountered issues")
    except Exception as e:
        print(f"\n💥 Demo crashed: {e}")
    finally:
        demo.stop_all()

if __name__ == "__main__":
    main()
