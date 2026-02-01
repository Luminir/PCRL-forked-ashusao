
import os
import pickle
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

"""
Distance Matrix Loader for RL Environment
"""

class DistanceMatrixLoader:
    """
    Loader class to lookup distances from a pre-computed matrix.
    Replaces real-time OSMnx shortest path calculation with O(1) table lookup.
    """

    def __init__(self, data_dir: str):
        """
        Initialize loader and load data into memory.
        
        Args:
            data_dir: Directory containing dist_matrix.npy and node_mapping.pkl
        """
        self.data_dir = data_dir
        
        print(f"Loading distance matrix from {data_dir}...")
        
        # Load distance matrix
        matrix_file = os.path.join(data_dir, 'dist_matrix.npy')
        if not os.path.exists(matrix_file):
            raise FileNotFoundError(f"Matrix file not found: {matrix_file}. Please run generate_matrix.py first.")
            
        self.dist_matrix = np.load(matrix_file)
        
        # Load node mapping
        mapping_file = os.path.join(data_dir, 'node_mapping.pkl')
        if not os.path.exists(mapping_file):
            raise FileNotFoundError(f"Mapping file not found: {mapping_file}")
            
        with open(mapping_file, 'rb') as f:
            mapping = pickle.load(f)
            
        self.node_to_idx = mapping['node_to_idx']
        self.idx_to_node = mapping['idx_to_node']
        
        # Load nodes metadata for KDTree (GPS to Node ID lookup)
        metadata_file = os.path.join(data_dir, 'nodes_metadata.csv')
        if os.path.exists(metadata_file):
            self.nodes_df = pd.read_csv(metadata_file)
            coords = self.nodes_df[['y', 'x']].values # y=lat, x=lon
            self.kdtree = cKDTree(coords)
            self.node_ids = self.nodes_df['node_id'].values
        else:
            print("Warning: nodes_metadata.csv not found. GPS-to-Node lookup will be disabled.")
            self.kdtree = None

        print(f"Distance Matrix Loaded: {self.dist_matrix.shape}")

    def get_distance(self, node_from_id, node_to_id):
        """
        Get network distance between two node IDs (straight from OSMnx graph).
        Returns distance in meters.
        """
        try:
            idx_from = self.node_to_idx[node_from_id]
            idx_to = self.node_to_idx[node_to_id]
            return float(self.dist_matrix[idx_from, idx_to])
        except KeyError:
            # Fallback if node not found in matrix (should rarely happen if graph is consistent)
            return float('inf')

    def find_nearest_node(self, lat, lon):
        """
        Find nearest graph node to a GPS coordinate.
        """
        if self.kdtree is None:
            raise ValueError("KDTree not initialized. Missing nodes_metadata.csv")
            
        # Query KDTree
        _, idx = self.kdtree.query([lat, lon], k=1)
        # Return the actual OSM node ID
        return self.node_ids[idx]
