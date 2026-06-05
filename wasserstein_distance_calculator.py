#!/usr/bin/env python3
"""
Wasserstein Distance Calculator for Persistence Diagrams
Computes pairwise Wasserstein distances between motif persistence diagrams
Simple implementation without external dependencies
"""

import json
import math
import time
import argparse
from itertools import combinations

def load_persistence_data(filename):
    """Load persistence coordinates from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def extract_points(motif_data, include_infinite=False):
    """
    Extract persistence points as (birth, death) coordinates
    
    Args:
        motif_data: Motif persistence data
        include_infinite: Whether to include infinite persistence points (default: False)
    
    Returns:
        List of [birth, death] coordinates
    """
    points = []
    
    for point in motif_data['points']:
        # Skip infinite points if not requested (standard for Wasserstein distance)
        if not include_infinite and point['persistence'] == -1:
            continue
            
        birth = point['x']
        death = point['y']
        
        # Handle infinite persistence points (only if include_infinite=True)
        if point['persistence'] == -1:
            # For infinite points, use a large death value
            death = max(death, birth + 1000)
        
        points.append([birth, death])
    
    return points

def point_distance(p1, p2):
    """Compute L-infinity distance between two points"""
    return max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))

def simple_wasserstein_distance(diagram1, diagram2):
    """
    Compute a simplified Wasserstein distance between two persistence diagrams
    Uses a greedy matching approach for simplicity
    
    Args:
        diagram1, diagram2: Lists of [birth, death] coordinates
    
    Returns:
        float: Approximate Wasserstein distance
    """
    
    # Handle empty diagrams
    if len(diagram1) == 0 and len(diagram2) == 0:
        return 0.0
    
    if len(diagram1) == 0:
        # All points in diagram2 match to diagonal
        return sum(abs(d - b) / 2 for b, d in diagram2)
    
    if len(diagram2) == 0:
        # All points in diagram1 match to diagonal
        return sum(abs(d - b) / 2 for b, d in diagram1)
    
    # Simple greedy matching (not optimal but fast)
    d1_copy = diagram1.copy()
    d2_copy = diagram2.copy()
    total_cost = 0.0
    
    # Match points greedily
    while d1_copy and d2_copy:
        min_cost = float('inf')
        best_i, best_j = 0, 0
        
        # Find closest pair
        for i, p1 in enumerate(d1_copy):
            for j, p2 in enumerate(d2_copy):
                cost = point_distance(p1, p2)
                if cost < min_cost:
                    min_cost = cost
                    best_i, best_j = i, j
        
        total_cost += min_cost
        d1_copy.pop(best_i)
        d2_copy.pop(best_j)
    
    # Match remaining points to diagonal
    for b, d in d1_copy:
        total_cost += abs(d - b) / 2
    
    for b, d in d2_copy:
        total_cost += abs(d - b) / 2
    
    return total_cost

def compute_all_wasserstein_distances(persistence_data, p=2, include_infinite=False):
    """
    Compute pairwise Wasserstein distances between all motifs
    
    Args:
        persistence_data: Dictionary containing motif persistence data
        p: Order of Wasserstein distance
        include_infinite: Whether to include infinite persistence points
    
    Returns:
        Dictionary with pairwise distances
    """
    
    motif_ids = list(persistence_data['motifs'].keys())
    distances = {}
    
    print(f"Computing Wasserstein distances for {len(motif_ids)} motifs...")
    print(f"Excluding infinite persistence points (persistence = -1)")
    print(f"Total pairs to compute: {len(motif_ids) * (len(motif_ids) - 1) // 2}")
    
    start_time = time.time()
    computed = 0
    
    # Compute pairwise distances
    for i, motif1 in enumerate(motif_ids):
        for j, motif2 in enumerate(motif_ids):
            if i <= j:  # Only compute upper triangle (symmetric matrix)
                continue
                
            # Extract persistence points
            points1 = extract_points(persistence_data['motifs'][motif1], include_infinite)
            points2 = extract_points(persistence_data['motifs'][motif2], include_infinite)
            
            # Compute Wasserstein distance
            distance = simple_wasserstein_distance(points1, points2)
            
            # Store both directions for easy lookup
            distances[f"{motif1}-{motif2}"] = distance
            distances[f"{motif2}-{motif1}"] = distance
            
            computed += 1
            
            # Progress update
            if computed % 1000 == 0:
                elapsed = time.time() - start_time
                rate = computed / elapsed
                remaining = (len(motif_ids) * (len(motif_ids) - 1) // 2) - computed
                eta = remaining / rate if rate > 0 else 0
                print(f"Computed {computed} distances ({rate:.1f} pairs/sec, ETA: {eta:.1f}s)")
    
    # Add self-distances (always 0)
    for motif_id in motif_ids:
        distances[f"{motif_id}-{motif_id}"] = 0.0
    
    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.2f} seconds")
    
    return distances

def analyze_distances(distances):
    """Analyze the computed distances and provide statistics"""
    
    # Get all distance values (excluding self-distances)
    distance_values = [d for key, d in distances.items() if d > 0]
    
    if not distance_values:
        print("No distances computed!")
        return
    
    print("\n=== Wasserstein Distance Analysis ===")
    print(f"Total pairs: {len(distance_values)}")
    print(f"Mean distance: {sum(distance_values) / len(distance_values):.4f}")
    
    # Calculate standard deviation manually
    mean_dist = sum(distance_values) / len(distance_values)
    variance = sum((d - mean_dist) ** 2 for d in distance_values) / len(distance_values)
    std_dev = math.sqrt(variance)
    print(f"Std deviation: {std_dev:.4f}")
    
    print(f"Min distance: {min(distance_values):.4f}")
    print(f"Max distance: {max(distance_values):.4f}")
    
    # Calculate median manually
    sorted_distances = sorted(distance_values)
    n = len(sorted_distances)
    if n % 2 == 0:
        median = (sorted_distances[n//2 - 1] + sorted_distances[n//2]) / 2
    else:
        median = sorted_distances[n//2]
    print(f"Median distance: {median:.4f}")
    
    # Find most similar and most different pairs
    min_dist = min(distance_values)
    max_dist = max(distance_values)
    
    most_similar = [key for key, d in distances.items() if abs(d - min_dist) < 1e-10 and d > 0]
    most_different = [key for key, d in distances.items() if abs(d - max_dist) < 1e-10]
    
    print(f"\nMost similar motifs (distance = {min_dist:.4f}):")
    for pair in most_similar[:5]:  # Show first 5
        print(f"  {pair}")
    
    print(f"\nMost different motifs (distance = {max_dist:.4f}):")
    for pair in most_different[:5]:  # Show first 5
        print(f"  {pair}")

def save_distance_matrix(distances, motif_ids, filename):
    """Save distances as a matrix format for analysis"""
    
    n = len(motif_ids)
    matrix = []
    
    for i, motif1 in enumerate(motif_ids):
        row = []
        for j, motif2 in enumerate(motif_ids):
            key = f"{motif1}-{motif2}"
            row.append(distances.get(key, 0.0))
        matrix.append(row)
    
    # Save as JSON matrix
    matrix_data = {
        'matrix': matrix,
        'motif_ids': motif_ids,
        'size': n
    }
    
    matrix_filename = filename.replace('.json', '_matrix.json')
    with open(matrix_filename, 'w') as f:
        json.dump(matrix_data, f, indent=2)
    
    print(f"Distance matrix saved to {matrix_filename}")

def main(hop_distance=1):
    """Main function to compute Wasserstein distances"""

    # Determine input/output filenames based on hop distance
    if hop_distance == 1:
        persistence_file = 'data/persistence_coordinates.json'
        output_file = 'data/wasserstein_distances.json'
    else:
        persistence_file = f'data/persistence_coordinates_{hop_distance}hop.json'
        output_file = f'data/wasserstein_distances_{hop_distance}hop.json'

    # Load persistence data
    print(f"Loading persistence data from {persistence_file}...")
    persistence_data = load_persistence_data(persistence_file)

    print(f"Loaded data for {persistence_data['metadata']['total_motifs']} {hop_distance}-hop motifs")

    # Compute Wasserstein distances (excluding infinite persistence points)
    distances = compute_all_wasserstein_distances(
        persistence_data,
        p=2,  # Not used in simple version
        include_infinite=False  # Exclude infinite persistence points for proper Wasserstein distance
    )

    # Analyze results
    analyze_distances(distances)

    # Save results
    with open(output_file, 'w') as f:
        json.dump(distances, f, indent=2)

    print(f"\nWasserstein distances saved to {output_file}")

    # Save distance matrix for further analysis
    motif_ids = list(persistence_data['motifs'].keys())
    save_distance_matrix(distances, motif_ids, output_file)

    return distances

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Compute Wasserstein distances between persistence diagrams')
    parser.add_argument('--hop', type=int, default=1, choices=[1, 2, 3],
                        help='Hop distance (default: 1)')
    args = parser.parse_args()

    distances = main(hop_distance=args.hop)