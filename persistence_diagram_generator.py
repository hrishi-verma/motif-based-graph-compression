import json
from collections import defaultdict

def load_mst_data(filename):
    """Load MST data from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)



def find_path_bfs(graph, start, end):
    """Find path between two nodes using BFS"""
    if start == end:
        return [start]
    
    visited = set()
    queue = [(start, [start])]
    
    while queue:
        node, path = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor == end:
                return path + [neighbor]
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))
    
    return None



def compute_single_motif_persistence(motif_id, motif_data):
    """
    Compute persistence diagram for a single motif using Maximum Spanning Tree approach
    Each H0 point should be at coordinates (0, weight) where:
    - x = 0 (all components born at time 0)
    - y = weight (component dies when edge is added at that weight)
    """
    
    # Get MST edges (these create H0 death events)
    mst_edges = [(edge['from'], edge['to'], edge['weight']) for edge in motif_data['mst_edges']]
    
    persistence_points = []
    
    # Each MST edge creates one H0 death event
    # Coordinates: (0, edge_weight)
    for from_node, to_node, weight in mst_edges:
        persistence_points.append({
            'birth': 0.0,  # All components born at time 0
            'death': weight,  # Component dies when this edge is added
            'dimension': 0,
            'persistence': weight  # Persistence = death - birth = weight - 0
        })
    
    # Add one infinite persistence point for the final surviving component
    # This represents the connected component that survives the entire filtration
    if mst_edges:
        # Use the minimum edge weight as birth time for the infinite component
        min_weight = min(edge[2] for edge in mst_edges)
        persistence_points.append({
            'birth': 0.0,
            'death': min_weight - 10,  # Place below the finite points for visualization
            'dimension': 0,
            'persistence': -1  # Infinite persistence marker
        })
    
    # Compute cycles (1-dimensional features) - should be empty for spanning trees
    cycle_points = compute_single_motif_cycles(motif_data)
    
    return persistence_points + cycle_points

def compute_single_motif_cycles(motif_data):
    """Compute 1-dimensional persistence (cycles) for a single motif"""
    cycle_points = []
    
    # Build MST graph as adjacency list
    mst_graph = defaultdict(list)
    edge_weights = {}
    
    for edge in motif_data['mst_edges']:
        from_node, to_node, weight = edge['from'], edge['to'], edge['weight']
        mst_graph[from_node].append(to_node)
        mst_graph[to_node].append(from_node)
        edge_weights[(min(from_node, to_node), max(from_node, to_node))] = weight
    
    # For each excluded edge, it would create a cycle
    for edge in motif_data['excluded_edges']:
        from_node, to_node, weight = edge['from'], edge['to'], edge['weight']
        
        if from_node in mst_graph and to_node in mst_graph:
            # Find path between nodes in MST
            path = find_path_bfs(mst_graph, from_node, to_node)
            
            if path and len(path) > 1:
                # Get weights of edges in the path
                path_weights = []
                for i in range(len(path) - 1):
                    edge_key = (min(path[i], path[i+1]), max(path[i], path[i+1]))
                    if edge_key in edge_weights:
                        path_weights.append(edge_weights[edge_key])
                
                if path_weights:
                    # Birth time is when the cycle could first form (max weight in MST path)
                    birth_time = max(path_weights)
                    death_time = weight  # Death time is when we add the excluded edge
                    
                    if death_time > birth_time:
                        cycle_points.append({
                            'birth': birth_time,
                            'death': death_time,
                            'dimension': 1,  # 1-dimensional (cycles)
                            'persistence': death_time - birth_time
                        })
    
    return cycle_points

def generate_persistence_coordinates(mst_filename):
    """Generate persistence diagram coordinates organized by motif and save to JSON"""
    
    # Load MST data
    mst_data = load_mst_data(mst_filename)
    
    # Prepare coordinates organized by motif
    coordinates = {
        'motifs': {},
        'metadata': {
            'total_motifs': len(mst_data),
            'total_points': 0,
            'component_points': 0,
            'cycle_points': 0
        }
    }
    
    total_points = 0
    total_component_points = 0
    total_cycle_points = 0
    
    # Compute persistence for each motif individually
    for motif_id, motif_data in mst_data.items():
        print(f"Computing persistence for motif {motif_id}...")
        
        # Compute persistence points for this motif
        persistence_points = compute_single_motif_persistence(motif_id, motif_data)
        
        # Separate by dimension
        component_points = [p for p in persistence_points if p['dimension'] == 0]
        cycle_points = [p for p in persistence_points if p['dimension'] == 1]
        
        # Store motif-specific data
        coordinates['motifs'][motif_id] = {
            'source_node': motif_data['source_node'],
            'points': [
                {
                    'x': point['birth'],
                    'y': point['death'],
                    'dimension': point['dimension'],
                    'persistence': point['persistence']
                }
                for point in persistence_points
            ],
            'statistics': {
                'total_points': len(persistence_points),
                'component_points': len(component_points),
                'cycle_points': len(cycle_points),
                'mst_edges': motif_data['num_mst_edges'],
                'excluded_edges': motif_data['num_excluded_edges'],
                'total_weight': motif_data['total_weight']
            }
        }
        
        total_points += len(persistence_points)
        total_component_points += len(component_points)
        total_cycle_points += len(cycle_points)
    
    # Update global metadata
    coordinates['metadata']['total_points'] = total_points
    coordinates['metadata']['component_points'] = total_component_points
    coordinates['metadata']['cycle_points'] = total_cycle_points
    
    # Save coordinates to JSON
    output_filename = 'data/persistence_coordinates.json'
    with open(output_filename, 'w') as f:
        json.dump(coordinates, f, indent=2)
    
    print(f"Generated persistence data for {len(mst_data)} motifs")
    print(f"Total persistence points: {total_points}")
    print(f"Saved coordinates to {output_filename}")
    
    return coordinates

def plot_persistence_diagram(coordinates):
    """Print summary of persistence diagram data"""
    
    # Collect all points from all motifs
    all_points = []
    for motif_id, motif_data in coordinates['motifs'].items():
        for point in motif_data['points']:
            all_points.append(point)
    
    # Separate by dimension
    dim0_points = [p for p in all_points if p['dimension'] == 0 and p['persistence'] != -1]
    dim1_points = [p for p in all_points if p['dimension'] == 1]
    infinite_points = [p for p in all_points if p['persistence'] == -1]
    
    print("\n=== Persistence Diagram Summary ===")
    print(f"Total motifs: {coordinates['metadata']['total_motifs']}")
    print(f"H₀ (Components): {len(dim0_points)} points")
    print(f"H₁ (Cycles): {len(dim1_points)} points")
    print(f"Infinite persistence: {len(infinite_points)} points")
    
    if dim0_points:
        persistences = [p['persistence'] for p in dim0_points]
        print(f"H₀ persistence range: {min(persistences):.2f} - {max(persistences):.2f}")
    
    if dim1_points:
        persistences = [p['persistence'] for p in dim1_points]
        print(f"H₁ persistence range: {min(persistences):.2f} - {max(persistences):.2f}")
    
    print("\nUse the HTML visualizer to see motif-specific persistence diagrams.")

if __name__ == "__main__":
    # Generate persistence coordinates
    coordinates = generate_persistence_coordinates('data/facebook_msts.json')
    
    # Plot the diagram
    plot_persistence_diagram(coordinates)