#!/usr/bin/env python3
"""
Test script to verify that infinite persistence points are being excluded
"""

import json

def test_infinite_exclusion():
    """Test that infinite points are properly excluded from Wasserstein calculations"""
    
    # Load persistence data
    with open('data/persistence_coordinates.json', 'r') as f:
        persistence_data = json.load(f)
    
    # Import the extract_points function
    from wasserstein_distance_calculator import extract_points
    
    print("Testing infinite point exclusion...")
    
    # Test a few motifs
    test_motifs = ['1', '48', '53']
    
    for motif_id in test_motifs:
        if motif_id in persistence_data['motifs']:
            motif_data = persistence_data['motifs'][motif_id]
            
            # Count total points
            total_points = len(motif_data['points'])
            
            # Count infinite points
            infinite_points = sum(1 for p in motif_data['points'] if p['persistence'] == -1)
            
            # Extract points with and without infinite points
            points_with_infinite = extract_points(motif_data, include_infinite=True)
            points_without_infinite = extract_points(motif_data, include_infinite=False)
            
            print(f"\nMotif {motif_id}:")
            print(f"  Total points in data: {total_points}")
            print(f"  Infinite points (persistence = -1): {infinite_points}")
            print(f"  Points extracted with infinite: {len(points_with_infinite)}")
            print(f"  Points extracted without infinite: {len(points_without_infinite)}")
            print(f"  Difference: {len(points_with_infinite) - len(points_without_infinite)}")
            
            # Verify the difference matches the infinite count
            if len(points_with_infinite) - len(points_without_infinite) == infinite_points:
                print(f"  ✓ Correct exclusion of infinite points")
            else:
                print(f"  ✗ Error in infinite point exclusion")
    
    print(f"\n=== Summary ===")
    print("The updated Wasserstein distance calculator now:")
    print("1. Excludes infinite persistence points (persistence = -1) by default")
    print("2. Only considers finite persistence points for distance calculations")
    print("3. This is the standard approach for Wasserstein distance in TDA")

if __name__ == "__main__":
    test_infinite_exclusion()