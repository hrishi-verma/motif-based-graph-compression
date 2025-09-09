"""
Graph Motif Compression Server

A Flask backend that provides API endpoints for compressing large network graphs
through motif clustering using Wasserstein distance-based similarity measures.
The server performs agglomerative clustering to group structurally similar 
subgraphs (motifs) and provides various endpoints for visualization and analysis.

Key Features:
- Threshold-based compression using agglomerative clustering
- Motif expansion and subgraph extraction
- Compression statistics and unique motif identification
- Real-time clustering based on precomputed Wasserstein distances
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import networkx as nx
import json
import os
import numpy as np
from sklearn.cluster import AgglomerativeClustering

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests for frontend integration

# File paths for data loading - using absolute paths to ensure files are found
# regardless of where the script is executed from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "facebook_weighted_filtered.csv")
WASSERSTEIN_PATH = os.path.join(BASE_DIR, "wasserstein_distances.json")
MOTIF_PATH = os.path.join(BASE_DIR, "facebook_motifs.json")

# Load the main graph from CSV data
# Expected format: source_node, target_node, edge_weight
# Using NetworkX Graph (undirected) since social networks are typically bidirectional
df = pd.read_csv(CSV_PATH)
G = nx.Graph()
for _, row in df.iterrows():
    # Convert to int/float to ensure proper data types for graph algorithms
    G.add_edge(int(row[0]), int(row[1]), weight=float(row[2]))

# Load precomputed data files
# wasserstein_data: pairwise Wasserstein distances between motifs (format: "node1-node2": distance)
# motif_data: individual motif structures for each node
with open(WASSERSTEIN_PATH, 'r') as f:
    wasserstein_data = json.load(f)
with open(MOTIF_PATH, 'r') as f:
    motif_data = json.load(f)

# Build node indexing system for clustering algorithms
# Extract all unique nodes from the Wasserstein distance pairs
all_nodes = sorted(set(int(k.split("-")[0]) for k in wasserstein_data.keys()) |
                   set(int(k.split("-")[1]) for k in wasserstein_data.keys()))
node_index = {node: i for i, node in enumerate(all_nodes)}  # node_id -> matrix_index
index_node = {i: node for node, i in node_index.items()}    # matrix_index -> node_id

# Build symmetric distance matrix for agglomerative clustering
# Uses precomputed Wasserstein distances between motif structures
N = len(all_nodes)
# Initialize with large distances (100.0) to handle missing pairs - this ensures
# nodes without precomputed distances are treated as maximally dissimilar
dist_matrix = np.full((N, N), fill_value=100.0)
for pair, dist in wasserstein_data.items():
    n1, n2 = map(int, pair.split("-"))
    i, j = node_index[n1], node_index[n2]
    # Ensure symmetry since Wasserstein distance is symmetric but may only be
    # stored in one direction in the JSON file
    dist_matrix[i][j] = dist
    dist_matrix[j][i] = dist
np.fill_diagonal(dist_matrix, 0.0)  # Distance from node to itself is always 0

@app.route('/processed_edges')
def get_processed_graph():
    """
    Get compressed graph representation using agglomerative clustering.
    
    Performs motif-based clustering at the specified threshold and returns
    a simplified graph where similar motifs are grouped into supernodes.
    
    Query Parameters:
        threshold (float): Distance threshold for clustering (default: 0)
                          Lower values = more compression
    
    Returns:
        JSON: {
            "nodes": [{"id": int, "compressed": bool, "cluster_id": int, 
                      "nodes_in_cluster": [int]}],
            "links": [{"source": int, "target": int, "weight": float}]
        }
    """
    threshold = float(request.args.get("threshold", 0))

    # Perform agglomerative clustering based on Wasserstein distances
    # Using average linkage to balance cluster sizes and avoid chaining effects
    model = AgglomerativeClustering(
        metric='precomputed',        # Use our precomputed distance matrix
        distance_threshold=threshold, # Clustering threshold - lower = more compression
        n_clusters=None,             # Let threshold determine cluster count automatically
        linkage='average'            # Average linkage reduces sensitivity to outliers
    )
    labels = model.fit_predict(dist_matrix)

    # Group nodes by cluster labels
    cluster_map = {}
    for idx, label in enumerate(labels):
        cluster_map.setdefault(label, []).append(index_node[idx])
    
    # Split disconnected clusters into connected components
    # This ensures each cluster represents a connected subgraph
    connected_clusters = {}
    cluster_counter = 0
    
    for original_cluster_id, nodes in cluster_map.items():
        if len(nodes) == 1:
            # Single node clusters are always connected
            connected_clusters[cluster_counter] = nodes
            cluster_counter += 1
        else:
            # Check connectivity and split if necessary
            subgraph = G.subgraph(nodes)
            components = list(nx.connected_components(subgraph))
            
            for component in components:
                connected_clusters[cluster_counter] = list(component)
                cluster_counter += 1
    
    # Update cluster_map to use connected clusters
    cluster_map = connected_clusters

    # Create supernodes (cluster representatives) and mapping
    # Each cluster is represented by a single "supernode" for visualization
    cluster_id_map = {}  # original_node -> (cluster_id, representative_node)
    supernodes = []
    for cid, members in cluster_map.items():
        # Use smallest node ID as representative for consistency across runs
        rep = min(members)
        for m in members:
            cluster_id_map[m] = (cid, rep)
        # Store metadata needed for frontend visualization and expansion
        supernodes.append({
            "id": int(rep),
            "compressed": True,
            "cluster_id": int(cid),
            "nodes_in_cluster": [int(n) for n in members]
        })

    # Aggregate edges between clusters - combine multiple edges into single weighted edges
    edge_dict = {}
    for u, v, data in G.edges(data=True):
        # Map nodes to their cluster representatives (or themselves if not clustered)
        cu, ru = cluster_id_map.get(u, (None, u))
        cv, rv = cluster_id_map.get(v, (None, v))
        if ru != rv:  # Only keep inter-cluster edges (remove intra-cluster edges)
            # Sort edge endpoints to ensure consistent key regardless of direction
            key = tuple(sorted([ru, rv]))
            edge_dict.setdefault(key, []).append(data["weight"])

    # Create compressed edge list with averaged weights
    # Multiple edges between clusters are combined using mean weight to preserve
    # overall connectivity strength while simplifying the visualization
    links = [{"source": int(a), "target": int(b), "weight": float(np.mean(w))} 
             for (a, b), w in edge_dict.items()]

    return jsonify({"nodes": supernodes, "links": links})
@app.route('/cluster_subgraph/<int:cluster_id>')
def get_cluster_subgraph(cluster_id):
    """
    Get the internal structure of a specific cluster.
    
    Returns the subgraph containing all nodes within the specified cluster,
    including their internal connections and adjacency matrix representation.
    
    Path Parameters:
        cluster_id (int): The cluster ID to extract
        
    Query Parameters:
        threshold (float): Distance threshold used for clustering (default: 0)
    
    Returns:
        JSON: {
            "nodes": [int],  # List of node IDs in the cluster
            "adjacency_matrix": [[float]]  # Weighted adjacency matrix
        }
        
    Error Responses:
        404: Cluster not found at the specified threshold
    """
    threshold = float(request.args.get("threshold", 0))

    # Recreate clustering to find the specified cluster
    model = AgglomerativeClustering(
        metric='precomputed',
        distance_threshold=threshold,
        n_clusters=None,
        linkage='average'
    )
    labels = model.fit_predict(dist_matrix)

    # Build cluster mapping and ensure connectivity
    initial_cluster_map = {}
    for idx, label in enumerate(labels):
        initial_cluster_map.setdefault(label, []).append(index_node[idx])
    
    # Split disconnected clusters into connected components
    cluster_map = {}
    cluster_counter = 0
    
    for original_cluster_id, nodes in initial_cluster_map.items():
        if len(nodes) == 1:
            cluster_map[cluster_counter] = nodes
            cluster_counter += 1
        else:
            subgraph = G.subgraph(nodes)
            components = list(nx.connected_components(subgraph))
            
            for component in components:
                cluster_map[cluster_counter] = list(component)
                cluster_counter += 1

    if cluster_id not in cluster_map:
        return jsonify({"error": "Cluster not found"}), 404

    # Extract subgraph for the requested cluster
    nodes = cluster_map[cluster_id]
    subgraph = G.subgraph(nodes)
    # Convert to adjacency matrix preserving node order and edge weights
    # Using nodelist parameter ensures consistent matrix ordering for frontend
    adj_matrix = nx.to_numpy_array(subgraph, nodelist=nodes, weight='weight').tolist()

    return jsonify({
        "nodes": nodes,
        "adjacency_matrix": adj_matrix
    })



@app.route('/motif/<int:node_id>')
def get_motif(node_id):
    """
    Get motif data for a specific node, with optional cluster expansion.
    
    Can return either the individual motif structure or the full cluster
    that contains this node, depending on the full_cluster parameter.
    
    Path Parameters:
        node_id (int): The node ID to get motif data for
        
    Query Parameters:
        full_cluster (bool): If "true", return entire cluster containing this node
                           If "false", return individual motif data (default)
        threshold (float): Distance threshold for clustering (used with full_cluster)
    
    Returns:
        JSON: When full_cluster=true: {
            "nodes": [int],  # All nodes in the cluster
            "adjacency_matrix": [[float]]  # Cluster's adjacency matrix
        }
        JSON: When full_cluster=false: 
            Precomputed motif data from motif_data file
            
    Error Responses:
        404: Motif not found in precomputed data
    """
    full_cluster = request.args.get("full_cluster", "false").lower() == "true"
    threshold = float(request.args.get("threshold", 0))

    if full_cluster:
        # Return the entire cluster containing this node
        model = AgglomerativeClustering(
            metric='precomputed',
            distance_threshold=threshold,
            n_clusters=None,
            linkage='average'
        )
        labels = model.fit_predict(dist_matrix)

        cluster_map = {}
        for idx, label in enumerate(labels):
            cluster_map.setdefault(label, []).append(index_node[idx])

        # Find which cluster contains the requested node
        # Linear search through clusters - could be optimized with reverse mapping
        # but cluster count is typically small so performance impact is minimal
        cluster_nodes = []
        for group in cluster_map.values():
            if node_id in group:
                cluster_nodes = group
                break

        # Extract the cluster's subgraph and adjacency matrix
        subgraph = G.subgraph(cluster_nodes)
        adj_matrix = nx.to_numpy_array(subgraph, nodelist=cluster_nodes, weight='weight').tolist()

        return jsonify({
            "nodes": cluster_nodes,
            "adjacency_matrix": adj_matrix
        })
    else:
        # Return individual motif data from precomputed file
        data = motif_data.get(str(node_id))
        if not data:
            return jsonify({"error": "Motif not found"}), 404
        return jsonify(data)
@app.route('/unique_motifs')
def get_unique_motifs():
    """
    Identify and return unique motif patterns from clustering results.
    
    Performs clustering and then uses graph isomorphism to identify
    structurally identical clusters, counting their occurrences.
    
    Query Parameters:
        threshold (float): Distance threshold for clustering (default: 0)
    
    Returns:
        JSON: [
            {
                "nodes": [int],  # Sample nodes for layout (one representative cluster)
                "adjacency_matrix": [[float]],  # Adjacency matrix of the pattern
                "count": int,  # Number of clusters with this pattern
                "all_nodes": [int]  # All nodes across all matching clusters
            }
        ]
    """
    threshold = float(request.args.get("threshold", 0))

    # Perform clustering to get cluster groups
    model = AgglomerativeClustering(
        metric='precomputed',
        distance_threshold=threshold,
        n_clusters=None,
        linkage='average'
    )
    labels = model.fit_predict(dist_matrix)

    cluster_map = {}
    for idx, label in enumerate(labels):
        cluster_map.setdefault(label, []).append(index_node[idx])

    # Find unique structural patterns using graph isomorphism
    # This identifies clusters that have identical connectivity patterns
    seen_subgraphs = []  # Track unique patterns found so far

    for nodes in cluster_map.values():
        subgraph = G.subgraph(nodes)
        matched = None

        # Check if this subgraph matches any previously seen pattern
        # Graph isomorphism considers structure but not node labels or positions
        for motif in seen_subgraphs:
            if nx.is_isomorphic(subgraph, motif['graph']):
                motif['count'] += 1  # Increment count for this pattern
                motif['all_nodes'].extend(nodes)  # Add nodes to the pattern
                matched = True
                break

        if not matched:
            # New unique pattern found - store both the graph and its matrix representation
            seen_subgraphs.append({
                'graph': subgraph,  # Keep graph object for isomorphism testing
                'nodes': list(nodes),  # Representative nodes for visualization layout
                'all_nodes': list(nodes),  # All nodes with this pattern (grows as matches found)
                'adjacency_matrix': nx.to_numpy_array(subgraph, nodelist=nodes, weight='weight').tolist(),
                'count': 1
            })

    # Format output for frontend consumption
    # Remove internal graph objects and prepare data for JSON serialization
    result = []
    for motif in seen_subgraphs:
        result.append({
            "nodes": motif['nodes'],  # Representative cluster for D3.js layout
            "adjacency_matrix": motif['adjacency_matrix'],
            "count": motif['count'],  # How many clusters share this pattern
            "all_nodes": list(set(motif['all_nodes']))  # Deduplicated complete node list
        })

    return jsonify(result)
@app.route('/compression_stats')
def compression_stats():
    """
    Calculate and return compression statistics for the current threshold.
    
    Provides metrics about how much the graph has been compressed through
    motif clustering, useful for understanding the compression trade-offs.
    
    Query Parameters:
        threshold (float): Distance threshold for clustering (default: 0)
    
    Returns:
        JSON: {
            "original_motifs": int,  # Number of original nodes/motifs
            "supernodes": int,       # Number of clusters (compressed nodes)
            "compression_percent": float  # Percentage reduction (0-100)
        }
    """
    threshold = float(request.args.get("threshold", 0))

    # Perform clustering to calculate compression metrics
    model = AgglomerativeClustering(
        metric='precomputed',
        distance_threshold=threshold,
        n_clusters=None,
        linkage='average'
    )
    labels = model.fit_predict(dist_matrix)

    # Calculate compression statistics
    num_original = len(labels)  # Original number of motifs/nodes
    num_clusters = len(set(labels))  # Number of clusters after compression
    # Compression percentage: how much the graph was reduced (0% = no compression, 100% = maximum)
    compression = round((1 - num_clusters / num_original) * 100, 1)

    return jsonify({
        "original_motifs": num_original,
        "supernodes": num_clusters,
        "compression_percent": compression
    })


if __name__ == '__main__':
    # Run Flask development server with debug mode enabled
    # Server will be available at http://127.0.0.1:5000
    app.run(debug=True)
    
