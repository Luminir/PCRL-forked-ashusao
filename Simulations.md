# Simulation Integration Plan for PCRL

## 1. Simulation Framework Comparison

An analysis of MATSim, GAMA, and Current Static Formulas for Charging Station (CS) optimization.

| Feature | MATSim | GAMA | Current (Static Formula) |
| --- | --- | --- | --- |
| **Focus** | Large-scale transport, daily activity plans, congestion, routing. | Generic agent-based modeling (ABM), GIS, visualization. | Simple mathematical approximations. |
| **Strengths** | Industry standard for transport realism; handles spillover effects and queuing. | Flexible, uses GAML language, excellent for custom behavioral rules. | Maximum speed;  lookup. Ideal for initial RL training. |
| **Weaknesses** | High computational overhead; Java-based; slow for RL loops. | Slower than pure Python; less specialized for traffic than MATSim. | Ignores dynamic interactions (e.g., waiting-line traffic blocks). |
| **Verdict** | **Standard for Validation.** Best for physically consistent results in research. | **Behavioral Alternative.** Good for visualizing specific agent logic. | **Training Baseline.** Use for pre-training; transition to MATSim for fine-tuning. |

---

## 2. Integration Architecture

Because MATSim is Java-based and RL environments are typically Python-based, integration requires a pipeline-based approach.

### Option A: Online Learning (Gym-MATSim Wrapper)

The RL agent learns directly from simulation feedback.

1. **Action:** Agent decides CS locations.
2. **Wrapper (`env.step`):** * Generates a `facilities.xml` file with new CS coordinates.
* Updates `config.xml` to reference the new facilities.


3. **Execution:** Python triggers MATSim via CLI: `subprocess.run(["java", "-jar", "matsim.jar", "config.xml"])`.
4. **Optimization:** Run only the "Mobsim" (Mobility Simulation) and minimal iterations to reduce latency.
5. **Reward:** Python parses `scorestats.txt` or `events.xml` to extract travel and queuing times.

### Option B: Offline Validation

MATSim acts as a high-fidelity benchmark for a pre-trained agent.

1. Train the RL agent using the fast `evaluation_framework.py`.
2. Export the final solution to MATSim for a single execution.
3. Compare performance: Use MATSim to identify failure cases where static formulas underestimated congestion.

---

## 3. Implementation Steps

### Step 1: Network Preparation

Convert existing **OSMnx** graphs to MATSim `network.xml`.

* **Tools:** `matsim-tools`, `pt2matsim`, or JOSM.

### Step 2: Bridge Function

Add a utility to `evaluation_framework.py` to export agent decisions into the required XML format.

```python
def export_solution_to_matsim(my_plan, filename="output_facilities.xml"):
    # Generates MATSim facilities XML structure
    # Example: <facility id="cs_1" x="x_coord" y="y_coord"><activity type="charging" /></facility>
    pass

```

### Step 3: Reward Parsing

Add a utility to extract simulation metrics for the RL reward function.

```python
def get_matsim_reward(matsim_output_dir):
    # Parses scorestats.txt or events.xml
    # Returns: average_trip_duration + average_waiting_time
    pass

```

---

## 4. Reward Function Integration

### Transitioning from Static to Dynamic

**Current Static Reward:**


**MATSim Integrated Reward:**
The reward incorporates real measured data and captures "Congestion Externalities" (e.g., road blockages caused by station placement).

* : Average trip duration from `matsim_data`.
* : Real waiting time at facilities.
* : Count of "stuck" agents or flow reduction.
