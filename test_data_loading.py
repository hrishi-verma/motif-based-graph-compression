#!/usr/bin/env python3
"""
Test script to verify the persistence coordinates data can be loaded properly
"""
import json
import os

def test_data_loading():
    """Test loading the persistence coordinates data"""
    
    data_file = 'data/persistence_coordinates.json'
    
    # Check if file exists
    if not os.path.exists(data_file):
        print(f"❌ File not found: {data_file}")
        return False
    
    print(f"✅ File exists: {data_file}")
    
    # Try to load JSON
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
        print("✅ JSON loaded successfully")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return False
    
    # Check data structure
    if 'points' not in data:
        print("❌ Missing 'points' key in data")
        return False
    
    if 'metadata' not in data:
        print("❌ Missing 'metadata' key in data")
        return False
    
    print("✅ Data structure is valid")
    
    # Print summary
    points = data['points']
    metadata = data['metadata']
    
    print(f"\n📊 Data Summary:")
    print(f"   Total points: {len(points)}")
    print(f"   Metadata total: {metadata.get('total_points', 'N/A')}")
    print(f"   Component points: {metadata.get('component_points', 'N/A')}")
    print(f"   Cycle points: {metadata.get('cycle_points', 'N/A')}")
    print(f"   Motif count: {metadata.get('motif_count', 'N/A')}")
    
    # Check first few points
    if points:
        print(f"\n🔍 Sample points:")
        for i, point in enumerate(points[:3]):
            print(f"   Point {i+1}: x={point.get('x')}, y={point.get('y')}, "
                  f"dim={point.get('dimension')}, motif={point.get('motif_id')}")
    
    print("\n✅ All tests passed! Data is ready for visualization.")
    return True

if __name__ == "__main__":
    test_data_loading()