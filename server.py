# server.py to return full cluster on motif expansion request
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import networkx as nx
import json
import os
import numpy as np
from sklearn.cluster import AgglomerativeClustering

app = Flask(__name__)
CORS(app)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "facebook_weighted_filtered.csv")
WASSERSTEIN_PATH = os.path.join(BASE_DIR, "wasserstein_distances.json")
MOTIF_PATH = os.path.join(BASE_DIR, "facebook_motifs.json")

# Load graph
df = pd.read_csv(CSV_PATH)
G = nx.Graph()
for _, row in df.iterrows():
    G.add_edge(int(row[0]), int(row[1]), weight=float(row[2]))

# Load JSONs
with open(WASSERSTEIN_PATH, 'r') as f:
    wasserstein_data = json.load(f)
with open(MOTIF_PATH, 'r') as f:
    motif_data = json.load(f)

# Build node index for clustering
all_nodes = sorted(set(int(k.split("-")[0]) for k in wasserstein_data.keys()) |
                   set(int(k.split("-")[1]) for k in wasserstein_data.keys()))
node_index = {node: i for i, node in enumerate(all_nodes)}
index_node = {i: node for node, i in node_index.items()}

# Build distance matrix
N = len(all_nodes)
dist_matrix = np.full((N, N), fill_value=100.0)
for pair, dist in wasserstein_data.items():
    n1, n2 = map(int, pair.split("-"))
    i, j = node_index[n1], node_index[n2]
    dist_matrix[i][j] = dist
    dist_matrix[j][i] = dist
np.fill_diagonal(dist_matrix, 0.0)

@app.route('/processed_edges')
def get_processed_graph():
    threshold = float(request.args.get("threshold", 0))

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

    cluster_id_map = {}
    supernodes = []
    for cid, members in cluster_map.items():
        rep = min(members)
        for m in members:
            cluster_id_map[m] = (cid, rep)
        supernodes.append({
            "id": int(rep),
            "compressed": True,
            "cluster_id": int(cid),
            "nodes_in_cluster": [int(n) for n in members]
        })

    edge_dict = {}
    for u, v, data in G.edges(data=True):
        cu, ru = cluster_id_map.get(u, (None, u))
        cv, rv = cluster_id_map.get(v, (None, v))
        if ru != rv:
            key = tuple(sorted([ru, rv]))
            edge_dict.setdefault(key, []).append(data["weight"])

    links = [{"source": int(a), "target": int(b), "weight": float(np.mean(w))} for (a, b), w in edge_dict.items()]

    return jsonify({"nodes": supernodes, "links": links})
@app.route('/cluster_subgraph/<int:cluster_id>')
def get_cluster_subgraph(cluster_id):
    threshold = float(request.args.get("threshold", 0))

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

    if cluster_id not in cluster_map:
        return jsonify({"error": "Cluster not found"}), 404

    nodes = cluster_map[cluster_id]
    subgraph = G.subgraph(nodes)
    adj_matrix = nx.to_numpy_array(subgraph, nodelist=nodes, weight='weight').tolist()

    return jsonify({
        "nodes": nodes,
        "adjacency_matrix": adj_matrix
    })



@app.route('/motif/<int:node_id>')
def get_motif(node_id):
    full_cluster = request.args.get("full_cluster", "false").lower() == "true"
    threshold = float(request.args.get("threshold", 0))

    if full_cluster:
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

        # Find the cluster this node belongs to
        cluster_nodes = []
        for group in cluster_map.values():
            if node_id in group:
                cluster_nodes = group
                break

        subgraph = G.subgraph(cluster_nodes)
        adj_matrix = nx.to_numpy_array(subgraph, nodelist=cluster_nodes, weight='weight').tolist()

        return jsonify({
            "nodes": cluster_nodes,
            "adjacency_matrix": adj_matrix
        })
    else:
        data = motif_data.get(str(node_id))
        if not data:
            return jsonify({"error": "Motif not found"}), 404
        return jsonify(data)
@app.route('/unique_motifs')
def get_unique_motifs():
    threshold = float(request.args.get("threshold", 0))

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

    seen_subgraphs = []
    unique_motifs = []

    for nodes in cluster_map.values():
        subgraph = G.subgraph(nodes)
        matched = None

        for motif in seen_subgraphs:
            if nx.is_isomorphic(subgraph, motif['graph']):
                motif['count'] += 1
                motif['all_nodes'].extend(nodes)
                matched = True
                break

        if not matched:
            seen_subgraphs.append({
                'graph': subgraph,
                'nodes': list(nodes),
                'all_nodes': list(nodes),  # to collect all matching clusters
                'adjacency_matrix': nx.to_numpy_array(subgraph, nodelist=nodes, weight='weight').tolist(),
                'count': 1
            })

    # Clean output
    result = []
    for motif in seen_subgraphs:
        result.append({
            "nodes": motif['nodes'],  # just one sample for layout
            "adjacency_matrix": motif['adjacency_matrix'],
            "count": motif['count'],
            "all_nodes": list(set(motif['all_nodes']))  # remove duplicates
        })

    return jsonify(result)
@app.route('/compression_stats')
def compression_stats():
    threshold = float(request.args.get("threshold", 0))

    model = AgglomerativeClustering(
        metric='precomputed',
        distance_threshold=threshold,
        n_clusters=None,
        linkage='average'
    )
    labels = model.fit_predict(dist_matrix)

    num_original = len(labels)
    num_clusters = len(set(labels))
    compression = round((1 - num_clusters / num_original) * 100, 1)

    return jsonify({
        "original_motifs": num_original,
        "supernodes": num_clusters,
        "compression_percent": compression
    })


if __name__ == '__main__':
    app.run(debug=True)
    
