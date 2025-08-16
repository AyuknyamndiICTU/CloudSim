#!/usr/bin/env python3
"""
Interactive Cloud Storage Client
Allows manual testing of file operations
"""

import os
import sys
import time
from storage_virtual_node import StorageVirtualNode
from statistics_manager import stats_manager


class InteractiveClient:
    def __init__(self, node_id: str = "client_node"):
        self.node_id = node_id
        self.node = None
        self.setup_node()
    
    def setup_node(self):
        """Setup the client node"""
        try:
            print(f"🔧 Setting up client node: {self.node_id}")
            self.node = StorageVirtualNode(
                node_id=self.node_id,
                cpu_capacity=4,
                memory_capacity=16,
                storage_capacity=500,
                bandwidth=1000,
                network_host='localhost',
                network_port=5000
            )
            print(f"✅ Client node {self.node_id} connected to network")
            time.sleep(2)  # Allow connection to stabilize
        except Exception as e:
            print(f"❌ Failed to setup client node: {e}")
            sys.exit(1)
    
    def show_menu(self):
        """Display the interactive menu"""
        print("\n" + "="*60)
        print("🌟 CLOUD STORAGE INTERACTIVE CLIENT")
        print("="*60)
        print("1. 📤 Upload a file")
        print("2. 📥 Download a file")
        print("3. 📝 Create test file")
        print("4. 📊 Show node statistics")
        print("5. 🔄 Upload multiple files concurrently")
        print("6. 📋 List local files")
        print("7. 🧪 Run quick test")
        print("8. ❌ Exit")
        print("-" * 60)
    
    def create_test_file(self):
        """Create a test file interactively"""
        print("\n📝 Create Test File")
        print("-" * 30)
        
        file_name = input("Enter file name (e.g., test.txt): ").strip()
        if not file_name:
            file_name = "test_file.txt"
        
        try:
            size_mb = float(input("Enter file size in MB (e.g., 2.5): ").strip())
        except ValueError:
            size_mb = 1.0
            print(f"Using default size: {size_mb} MB")
        
        try:
            file_path = self.node.create_test_file(file_name, size_mb)
            print(f"✅ Test file created: {file_path}")
            return file_path
        except Exception as e:
            print(f"❌ Failed to create test file: {e}")
            return None
    
    def upload_file(self):
        """Upload a file interactively"""
        print("\n📤 Upload File")
        print("-" * 20)
        
        # List available files
        storage_dir = self.node.storage_dir
        if os.path.exists(storage_dir):
            files = [f for f in os.listdir(storage_dir) if os.path.isfile(os.path.join(storage_dir, f))]
            if files:
                print("Available files:")
                for i, file in enumerate(files, 1):
                    file_path = os.path.join(storage_dir, file)
                    size = os.path.getsize(file_path)
                    print(f"  {i}. {file} ({stats_manager.format_size(size)})")
                
                try:
                    choice = int(input("Select file number (or 0 to enter custom path): ").strip())
                    if 1 <= choice <= len(files):
                        file_path = os.path.join(storage_dir, files[choice - 1])
                    elif choice == 0:
                        file_path = input("Enter full file path: ").strip()
                    else:
                        print("❌ Invalid choice")
                        return
                except ValueError:
                    print("❌ Invalid input")
                    return
            else:
                file_path = input("Enter file path: ").strip()
        else:
            file_path = input("Enter file path: ").strip()
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return
        
        try:
            replication = int(input("Enter replication factor (default 2): ").strip() or "2")
        except ValueError:
            replication = 2
        
        print(f"\n🚀 Starting upload...")
        success = self.node.upload_file_to_controller(file_path, replication)
        
        if success:
            print("🎉 Upload completed successfully!")
        else:
            print("❌ Upload failed!")
    
    def download_file(self):
        """Download a file interactively"""
        print("\n📥 Download File")
        print("-" * 20)
        
        file_id = input("Enter file ID to download: ").strip()
        if not file_id:
            print("❌ File ID is required")
            return
        
        save_path = input("Enter save path (optional): ").strip()
        if not save_path:
            save_path = None
        
        print(f"\n🚀 Starting download...")
        success = self.node.download_file_from_controller(file_id, save_path)
        
        if success:
            print("🎉 Download completed successfully!")
        else:
            print("❌ Download failed!")
    
    def show_statistics(self):
        """Show node statistics"""
        print("\n📊 Node Statistics")
        print("-" * 30)
        
        summary = stats_manager.generate_node_summary(
            self.node.node_id,
            self.node.total_storage,
            len(self.node.active_transfers),
            self.node.total_requests_processed
        )
        print(summary)
        
        # Show active transfers
        if stats_manager.active_transfers:
            print("\n🔄 Active Transfers:")
            for transfer_id, transfer in stats_manager.active_transfers.items():
                print(f"  📁 {transfer.file_name}: {transfer.progress:.1f}% complete")
        
        # Show recent transfers
        if stats_manager.transfer_history:
            print("\n📈 Recent Transfers:")
            for transfer in list(stats_manager.transfer_history)[-5:]:
                status = "✅" if transfer.state == "COMPLETED" else "❌"
                print(f"  {status} {transfer.file_name}: {transfer.transfer_rate:.2f} MB/s")
    
    def upload_multiple_files(self):
        """Upload multiple files concurrently"""
        print("\n🔄 Concurrent Upload")
        print("-" * 25)
        
        try:
            count = int(input("How many test files to create and upload? (default 3): ").strip() or "3")
        except ValueError:
            count = 3
        
        print(f"📝 Creating {count} test files...")
        
        # Create test files
        test_files = []
        for i in range(count):
            file_name = f"concurrent{i+1}.txt"
            size_mb = 2.0 + i * 0.5  # Varying sizes
            file_path = self.node.create_test_file(file_name, size_mb)
            if file_path:
                test_files.append(file_path)
        
        if not test_files:
            print("❌ No test files created")
            return
        
        print(f"🚀 Starting concurrent upload of {len(test_files)} files...")
        
        import threading
        
        def upload_worker(file_path):
            file_name = os.path.basename(file_path)
            print(f"🔄 Starting upload: {file_name}")
            success = self.node.upload_file_to_controller(file_path, replication_factor=2)
            if success:
                print(f"✅ Completed upload: {file_name}")
            else:
                print(f"❌ Failed upload: {file_name}")
        
        # Start concurrent uploads
        threads = []
        for file_path in test_files:
            thread = threading.Thread(target=upload_worker, args=(file_path,), daemon=True)
            threads.append(thread)
            thread.start()
            time.sleep(0.2)  # Small delay between starts
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        print("🎉 Concurrent upload demonstration completed!")
    
    def list_local_files(self):
        """List local files in storage directory"""
        print("\n📋 Local Files")
        print("-" * 20)
        
        storage_dir = self.node.storage_dir
        if os.path.exists(storage_dir):
            files = [f for f in os.listdir(storage_dir) if os.path.isfile(os.path.join(storage_dir, f))]
            if files:
                total_size = 0
                for file in files:
                    file_path = os.path.join(storage_dir, file)
                    size = os.path.getsize(file_path)
                    total_size += size
                    print(f"  📁 {file} ({stats_manager.format_size(size)})")
                print(f"\n📊 Total: {len(files)} files, {stats_manager.format_size(total_size)}")
            else:
                print("📭 No files found in storage directory")
        else:
            print("📭 Storage directory not found")
    
    def run_quick_test(self):
        """Run a quick test of the system"""
        print("\n🧪 Quick Test")
        print("-" * 15)
        
        # Create a test file
        print("1. Creating test file...")
        file_path = self.node.create_test_file("quick_test.txt", 1.5)
        
        if file_path:
            # Upload it
            print("2. Uploading file...")
            success = self.node.upload_file_to_controller(file_path, replication_factor=2)
            
            if success:
                print("✅ Quick test completed successfully!")
            else:
                print("❌ Quick test failed during upload!")
        else:
            print("❌ Quick test failed during file creation!")
    
    def run(self):
        """Run the interactive client"""
        print("🌟 Welcome to Cloud Storage Interactive Client!")
        print("Make sure the network controller is running first.")
        
        try:
            while True:
                self.show_menu()
                choice = input("Enter your choice (1-8): ").strip()
                
                if choice == '1':
                    self.upload_file()
                elif choice == '2':
                    self.download_file()
                elif choice == '3':
                    self.create_test_file()
                elif choice == '4':
                    self.show_statistics()
                elif choice == '5':
                    self.upload_multiple_files()
                elif choice == '6':
                    self.list_local_files()
                elif choice == '7':
                    self.run_quick_test()
                elif choice == '8':
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
                
                input("\nPress Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        finally:
            if self.node:
                self.node.shutdown()


if __name__ == "__main__":
    client = InteractiveClient()
    client.run()
