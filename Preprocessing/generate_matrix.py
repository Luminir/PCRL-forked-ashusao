
import os
import osmnx as ox
import networkx as nx
import numpy as np
import pandas as pd
import pickle
import time
from multiprocessing import Pool, cpu_count

"""
Generate Pre-computed Distance Matrix
"""

location = "Hanoi"
GRAPH_FILE = f"../Graph/{location}/{location}.graphml"
OUTPUT_DIR = f"../Graph/{location}/Matrix"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def process_chunk(args):
    """
    Worker function to calculate distances for a chunk of source nodes.
    Using networkx.single_source_dijkstra_path_length is more efficient for sparse graphs
    than Floyd-Warshall, and easier to key by node ID.
    """
    G_chunk, source_nodes, all_nodes_list = args
    chunk_results = {}
    
    for src in source_nodes:
        # Compute shortest paths from src to ALL reachable nodes
        # weight='length' uses the physical distance
        lengths = nx.single_source_dijkstra_path_length(G_chunk, src, weight='length')
        chunk_results[src] = lengths
        
    return chunk_results

def generate_matrix():
    print(f"Loading graph from {GRAPH_FILE}...")
    G = ox.load_graphml(GRAPH_FILE)
    nodes = list(G.nodes())
    n = len(nodes)
    print(f"Graph loaded. Nodes: {n}, Edges: {len(G.edges())}")

    # Create mappings
    node_to_idx = {node: i for i, node in enumerate(nodes)}
    idx_to_node = {i: node for i, node in enumerate(nodes)}
    
    # Save mappings immediately
    mapping = {'node_to_idx': node_to_idx, 'idx_to_node': idx_to_node}
    with open(os.path.join(OUTPUT_DIR, 'node_mapping.pkl'), 'wb') as f:
        pickle.dump(mapping, f)
        
    # Save node metadata for KDTree
    print("Saving node metadata...")
    cols = ['node_id', 'x', 'y']
    data = []
    for node, attrs in G.nodes(data=True):
        data.append([node, attrs.get('x'), attrs.get('y')])
    
    df = pd.DataFrame(data, columns=cols)
    df.to_csv(os.path.join(OUTPUT_DIR, 'nodes_metadata.csv'), index=False)

    print("Calculating all-pairs shortest paths (this may take a while)...")
    start_time = time.time()
    
    # Initialize Matrix with Infinity
    # Using float32 to save RAM (4 bytes * 15000^2 ≈ 900MB)
    dist_matrix = np.full((n, n), np.inf, dtype=np.float32)
    
    # Fill diagonal with 0
    np.fill_diagonal(dist_matrix, 0)

    # Parallel Processing
    num_cores = max(1, cpu_count() - 2)
    print(f"Using {num_cores} cores for processing...")
    
    chunk_size = max(1, n // num_cores)
    chunks = [nodes[i:i + chunk_size] for i in range(0, n, chunk_size)]
    
    # We pass the graph copy to workers (expensive for RAM, but easiest for multiprocessing)
    # For very large graphs, shared memory would be better, but Hanoi 15k fits in RAM.
    worker_args = [(G, chunk, nodes) for chunk in chunks]
    
    with Pool(processes=num_cores) as pool:
        results = pool.map(process_chunk, worker_args)
        
    print("Merging results into matrix...")
    count = 0
    for chunk_res in results:
        for src, lengths in chunk_res.items():
            src_idx = node_to_idx[src]
            for target, dist in lengths.items():
                if target in node_to_idx:
                    tgt_idx = node_to_idx[target]
                    dist_matrix[src_idx, tgt_idx] = dist
            count += 1
            if count % 1000 == 0:
                print(f"Processed {count}/{n} rows...")

    print("Saving matrix to disk...")
    np.save(os.path.join(OUTPUT_DIR, 'dist_matrix.npy'), dist_matrix)
    
    duration = time.time() - start_time
    print(f"DONE! Time taken: {duration:.2f} seconds")
    print(f"Matrix shape: {dist_matrix.shape}")
    print(f"Saved to {OUTPUT_DIR}")

if __name__ == '__main__':
    generate_matrix()
