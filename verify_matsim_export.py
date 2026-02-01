
import os
import sys

# Ensure current directory is in path
sys.path.append(os.getcwd())

try:
    import evaluation_framework as ef
    from Preprocessing import matsim_bridge
    print("Imports successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def test_export():
    print("Testing MATSim Export...")
    
    # Create mock data if real files aren't easy to load without full env setup
    # Mock Node List: [ [id, {data}], ... ]
    mock_nodes = [
        [1, {'x': 105.80, 'y': 21.00}],
        [2, {'x': 105.81, 'y': 21.01}],
        [3, {'x': 105.82, 'y': 21.02}]
    ]
    
    # Mock Plan: List of Stations
    # Station: [ [node_pos], [config], {stats} ]
    mock_station_1 = [
        mock_nodes[0],          # s_pos (Node)
        [1, 0, 0],              # s_x (1 charger of type 0)
        {'fee': 1000}           # s_dict
    ]
    
    mock_station_2 = [
        mock_nodes[2],
        [0, 2, 1],
        {'fee': 5000}
    ]
    
    mock_plan = [mock_station_1, mock_station_2]
    
    output_file = "test_facilities.xml"
    
    # Run Function
    ef.export_solution_to_matsim(mock_plan, mock_nodes, output_file)
    
    # Verify File Exists and Content
    if os.path.exists(output_file):
        print(f"SUCCESS: {output_file} created.")
        with open(output_file, 'r') as f:
            content = f.read()
            print("--- Content Snippet ---")
            print(content[:300])
            print("...")
            if 'cs_1' in content and 'cs_3' in content:
                print("Verification Passed: Station IDs found in XML.")
            else:
                print("Verification Failed: Station IDs missing.")
    else:
        print("FAILURE: File not created.")

if __name__ == "__main__":
    test_export()
