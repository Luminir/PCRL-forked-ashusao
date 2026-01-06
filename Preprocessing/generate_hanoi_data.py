# Save as Preprocessing/generate_hanoi_data.py
import pickle
import numpy as np
import pandas as pd
import os

location = "Hanoi"
n_x, n_y = 32, 32

# Create directories
os.makedirs("../Graph/Pickle", exist_ok=True)
os.makedirs(f"../data/{location}", exist_ok=True)

# 1. Load the density we got from load_graph.py
density_path = f"../Graph/{location}/grid_density_{location}.pkl"
with open(density_path, "rb") as f:
    grid_density = pickle.load(f)

# 2. Create Demand: High where road density is high + some randomness
demand = grid_density * np.random.uniform(0.8, 1.2, size=(n_x, n_y))
pickle.dump(demand, open(f"../Graph/Pickle/demand_{location}.pkl", "wb"))

# 3. Estate Price: In Hanoi, prices are higher in the center (approx. center of grid)
estate_price = np.zeros((n_x, n_y))
for i in range(n_x):
    for j in range(n_y):
        dist_to_center = np.sqrt((i - 16)**2 + (j - 16)**2)
        estate_price[i][j] = 1000 * (1 / (dist_to_center + 1)) 
pickle.dump(estate_price, open(f"../Graph/Pickle/estateprice_{location}.pkl", "wb"))

# 4. Private Charging: Set to 0 for now (new market)
priv_cs = np.zeros((n_x, n_y))
pickle.dump(priv_cs, open(f"../Graph/Pickle/privCS_{location}.pkl", "wb"))

# 5. Existing Infrastructure: Empty CSV with required columns
df = pd.DataFrame(columns=['nearest node', 'numberofpoints'])
df.to_csv(f"../data/{location}/OCM_simple{location}.csv", index=False)

print("✅ All required Pickle and CSV files for Hanoi are ready.")