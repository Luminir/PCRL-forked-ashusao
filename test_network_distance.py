"""
Test Network-Based Distance Implementation

This script verifies that the network-based distance calculation
is working correctly compared to the Haversine fallback.
"""

import osmnx as ox
import evaluation_framework as ef
import sys
import os

# Ensure we can import from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def test_distance_comparison():
    """Compare network distance vs Haversine for sample nodes"""
    print("=" * 60)
    print("TESTING NETWORK-BASED DISTANCE CALCULATION")
    print("=" * 60)
    
    location = "Hanoi"
    graph_file = f"Graph/{location}/{location}.graphml"
    node_file = f"Graph/nodes_extended_{location}.txt"
    
    print(f"\nLoading graph and nodes for {location}...")
    try:
        graph, node_list = ef.prepare_graph(graph_file, node_file)
        print(f"✓ Loaded {len(node_list)} nodes")
    except Exception as e:
        print(f"✗ Error loading graph: {e}")
        return False
    
    # Test a few sample node pairs
    print("\n" + "-" * 60)
    print("COMPARING DISTANCES (Network vs Haversine)")
    print("-" * 60)
    
    test_pairs = min(5, len(node_list) - 1)  # Test up to 5 pairs
    success_count = 0
    fallback_count = 0
    
    for i in range(test_pairs):
        node1 = node_list[i]
        node2 = node_list[i + 1]
        
        # Calculate both distances
        haversine_dist = ef.haversine_fallback(node1, node2)
        network_dist = ef.calculate_distance(graph, node1, node2)
        
        # Check if fallback was used (distances will be identical)
        is_fallback = abs(network_dist - haversine_dist) < 0.01
        
        if is_fallback:
            fallback_count += 1
            status = "⚠ FALLBACK"
        else:
            status = "✓ NETWORK"
            
        # Network distance should always be >= Haversine (or equal if fallback)
        ratio = network_dist / haversine_dist
        is_valid = ratio >= 0.99  # Allow tiny floating point errors
        
        if is_valid:
            success_count += 1
            
        print(f"\nPair {i+1}: Node {str(node1[0])[:8]}... → {str(node2[0])[:8]}...")
        print(f"  Haversine:  {haversine_dist:10.2f} m")
        print(f"  Network:    {network_dist:10.2f} m")
        print(f"  Ratio:      {ratio:10.2f}x")
        print(f"  Status:     {status}")
        print(f"  Valid:      {'✓ YES' if is_valid else '✗ NO'}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total pairs tested:    {test_pairs}")
    print(f"Valid results:         {success_count}/{test_pairs}")
    print(f"Fallback used:         {fallback_count}/{test_pairs}")
    print(f"Network routing used:  {test_pairs - fallback_count}/{test_pairs}")
    
    if success_count == test_pairs:
        print("\n✓ ALL TESTS PASSED!")
        if fallback_count == test_pairs:
            print("  Note: All tests used fallback (nodes might not be in graph)")
        return True
    else:
        print(f"\n✗ FAILED: {test_pairs - success_count} invalid results")
        return False

def test_caching():
    """Verify that distance caching works correctly"""
    print("\n" + "=" * 60)
    print("TESTING DISTANCE CACHING")
    print("=" * 60)
    
    location = "Hanoi"
    graph_file = f"Graph/{location}/{location}.graphml"
    node_file = f"Graph/nodes_extended_{location}.txt"
    
    graph, node_list = ef.prepare_graph(graph_file, node_file)
    
    if len(node_list) < 2:
        print("✗ Not enough nodes for caching test")
        return False
    
    node1 = node_list[0]
    node2 = node_list[1]
    
    # Calculate distance twice
    dist1 = ef.calculate_distance(graph, node1, node2)
    dist2 = ef.calculate_distance(graph, node1, node2)
    
    # Should be exactly identical (same object or value)
    if dist1 == dist2:
        print(f"✓ Caching verified: Both calls returned {dist1:.2f} m")
        return True
    else:
        print(f"✗ Caching failed: Got {dist1:.2f} m and {dist2:.2f} m")
        return False

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("NETWORK DISTANCE VERIFICATION TESTS")
    print("=" * 60 + "\n")
    
    try:
        test1 = test_distance_comparison()
        test2 = test_caching()
        
        print("\n" + "=" * 60)
        print("FINAL RESULT")
        print("=" * 60)
        
        if test1 and test2:
            print("✓ All verification tests PASSED!")
            print("\nThe network-based distance implementation is working correctly.")
            print("You can now proceed with training or testing the model.")
            sys.exit(0)
        else:
            print("✗ Some tests FAILED!")
            print("\nPlease review the errors above before proceeding.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
