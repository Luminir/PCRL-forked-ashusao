import pickle
import numpy as np
import pandas as pd
import sys
import os

# --- PATH FIX: Ensures it can find evaluation_framework.py ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import evaluation_framework as ef

n_x, n_y = 32, 32

def generate_mock_data(location):
    """Creates the necessary input files if they don't exist"""
    print(f"--- Generating Mock Data for {location} ---")
    os.makedirs("../Graph/Pickle", exist_ok=True)
    os.makedirs(f"../data/{location}", exist_ok=True)

    # 1. Load density from your previous load_graph run
    density_path = f"../Graph/{location}/grid_density_{location}.pkl"
    with open(density_path, "rb") as f:
        grid_density = pickle.load(f)

    # 2. Mock Demand
    demand = grid_density * np.random.uniform(0.8, 1.2, size=(n_x, n_y))
    pickle.dump(demand, open(f"../Graph/Pickle/demand_{location}.pkl", "wb"))

    # 3. Mock Estate Price (Center of grid is more expensive)
    estate_price = np.zeros((n_x, n_y))
    for i in range(n_x):
        for j in range(n_y):
            dist_to_center = np.sqrt((i - 16)**2 + (j - 16)**2)
            estate_price[i][j] = 1000 * (1 / (dist_to_center + 1)) 
    pickle.dump(estate_price, open(f"../Graph/Pickle/estateprice_{location}.pkl", "wb"))

    # 4. Mock Private Charging
    pickle.dump(np.zeros((n_x, n_y)), open(f"../Graph/Pickle/privCS_{location}.pkl", "wb"))

    # 5. Empty Existing Infrastructure CSV
    df = pd.DataFrame(columns=['nearest node', 'numberofpoints'])
    df.to_csv(f"../data/{location}/OCM_simple{location}.csv", index=False)
    print("--- Mock Data Ready ---")

def social_efficiency_upper_bound(my_node, my_node_list):
    priv_CS = my_node[1].get("private CS", 0)
    I1_max = 0
    for other_node in my_node_list:
        if ef.haversine(my_node, other_node) <= ef.RADIUS_MAX:
            I1_max += 1
    my_node[1]["I1_max"] = I1_max
    delta_benefit = I1_max * (1 - 0.1 * priv_CS)
    delta_benefit /= 100
    upper_bound = ef.my_lambda * delta_benefit / max(my_node[1]["estate price"], 0.01)
    return upper_bound

def charging_demand(my_node, demand_matrix):
    row, col = my_node[1]["row"], my_node[1]["column"]
    if row is None or col is None:
        my_node[1]["demand"] = np.mean(demand_matrix)
    else:
        my_node[1]["demand"] = demand_matrix[row][col]

def modify_demand_dict(my_demand_matrix, grid_density):
    demand_min = 0.05
    for i in range(n_x):
        for j in range(n_y):
            if grid_density[i][j] > 0:
                my_demand_matrix[i][j] = my_demand_matrix[i][j] / grid_density[i][j]
            else:
                my_demand_matrix[i][j] = 0
            my_demand_matrix[i][j] += demand_min
            if my_demand_matrix[i][j] >= 250:
                my_demand_matrix[i][j] = 250
    demand_max = np.amax(my_demand_matrix)
    if demand_max > 0:
        my_demand_matrix /= demand_max
    return my_demand_matrix

if __name__ == '__main__':
    location = "Hanoi"
    
    # Run mock data generation first
    generate_mock_data(location)

    graph_file = f"../Graph/{location}/{location}.graphml"
    node_file = f"../Graph/{location}/node_list_{location}.txt"
    
    print(f"Loading graph and node list for {location}...")
    graph, node_list = ef.prepare_graph(graph_file, node_file)

    # Load the newly created Pickle files
    objects = pickle.load(open(f"../Graph/Pickle/demand_{location}.pkl", "rb"))
    grid_density = pickle.load(open(f"../Graph/{location}/grid_density_{location}.pkl", "rb"))
    priv_matrix = pickle.load(open(f"../Graph/Pickle/privCS_{location}.pkl", "rb"))
    estate_matrix = pickle.load(open(f"../Graph/Pickle/estateprice_{location}.pkl", "rb"))

    demand_matrix = modify_demand_dict(objects, grid_density)

    print("Processing nodes...")
    for node in node_list:
        charging_demand(node, demand_matrix)
        row, col = node[1]["row"], node[1]["column"]
        if row is None or col is None:
            node[1]["estate price"] = np.mean(estate_matrix)
            node[1]["private CS"] = np.mean(priv_matrix)
        else:
            node[1]["estate price"] = estate_matrix[row][col]
            node[1]["private CS"] = priv_matrix[row][col]

    print("Calculating Social Efficiency (Upper Bounds)...")
    for node in node_list:
        node[1]["upper bound"] = social_efficiency_upper_bound(node, node_list)

    # Save final results
    with open(f"../Graph/nodes_extended_{location}.txt", 'w', encoding='utf-8') as file:
        file.write(str(node_list))
    
    pickle.dump([], open(f"../Graph/Pickle/existingplan_{location}.pkl", "wb"))
    print(f"✅ Success! File saved at: ../Graph/nodes_extended_{location}.txt")