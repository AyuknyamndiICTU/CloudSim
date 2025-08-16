import argparse
import time
from storage_virtual_node import StorageVirtualNode
from storage_virtual_network import StorageVirtualNetwork

def run_node(node_id, cpu, memory, storage, bandwidth, network_host, network_port):
    try:
        print(f"Starting node {node_id}...")
        node = StorageVirtualNode(
            node_id=node_id,
            cpu_capacity=cpu,
            memory_capacity=memory,
            storage_capacity=storage,
            bandwidth=bandwidth,
            network_host=network_host,
            network_port=network_port
        )
        
        print(f"Node {node_id} running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        node.shutdown()
    except Exception as e:
        print(f"Node startup failed: {e}")

def run_network(host, port, grpc_port=50051):
    try:
        print("Starting network controller...")
        network = StorageVirtualNetwork(host=host, port=port, grpc_port=grpc_port)
        
        print(f"Network controller running on {host}:{port}. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        network.shutdown()
    except Exception as e:
        print(f"Network startup failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cloud Storage Simulation')
    parser.add_argument('--node', action='store_true', help='Run as a node')
    parser.add_argument('--network', action='store_true', help='Run as network controller')
    parser.add_argument('--node-id', type=str, help='Node ID')
    parser.add_argument('--cpu', type=int, default=4, help='CPU capacity')
    parser.add_argument('--memory', type=int, default=16, help='Memory capacity (GB)')
    parser.add_argument('--storage', type=int, default=500, help='Storage capacity (GB)')
    parser.add_argument('--bandwidth', type=int, default=1000, help='Bandwidth (Mbps)')
    parser.add_argument('--network-host', type=str, default='localhost', help='Network controller host')
    parser.add_argument('--network-port', type=int, default=5000, help='Network controller port')
    parser.add_argument('--grpc-port', type=int, default=50051, help='gRPC service port')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to (for network)')
    
    args = parser.parse_args()
    
    if args.network:
        run_network(args.host, args.network_port, args.grpc_port)
    elif args.node and args.node_id:
        run_node(
            args.node_id, 
            args.cpu, 
            args.memory, 
            args.storage, 
            args.bandwidth,
            args.network_host,
            args.network_port
        )
    else:
        print("Please specify either --network or --node with --node-id")