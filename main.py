# main.py - The Integration Engine

from T1_Strategist import BuildingModel, ZoneAllocator
from T2_Navigator import DynamicEnvironment, MovementSimulator
from T3_Optimizer import ACO_Pathfinder, TimeAggregator

# --- 1. SETUP PHASE (T1's Initial Work) ---
print("--- 1. Setup Phase: T1 Runs Initial Allocation ---")
N_RESPONDERS = 2
TIME_STEP = 5.0 # seconds per step (for simulation granularity)

# Define a simple floor plan for the smoke test
layout_data = {'A': {'type': 'Office'}, 'B': {'type': 'Office'}} 

# T1: Initialize Building and Zones
building = BuildingModel(layout_data)
allocator = ZoneAllocator(building)
initial_zones, P_coord = allocator.initial_partition(N_RESPONDERS)

print(f"Initial Zones: {initial_zones}")
print(f"P_coord: {P_coord}")

# --- 2. INITIALIZE SIMULATORS (T2 & T3 Setup) ---
print("\n--- 2. Initialization ---")

# T2: Initialize Environment and Movement
env = DynamicEnvironment(building.graph)
simulator = MovementSimulator(initial_zones, P_coord, env)

# T3: Initialize Optimizer and Aggregator
pathfinder = ACO_Pathfinder(building.graph, simulator.zones)
aggregator = TimeAggregator(pathfinder)

# --- 3. SIMULATION LOOP (Main Execution) ---
print("\n--- 3. Running Simulation Loop (Smoke Test) ---")
MAX_STEPS = 5 # Run for 5 steps only for smoke test

current_time = 0.0
is_complete = False
all_responders = list(initial_zones.keys())

for step in range(MAX_STEPS):
    if is_complete:
        break

    current_time += TIME_STEP
    print(f"\n[STEP {step+1}] Time: {current_time:.1f}s")
    
    # T2: Update hazards and environment
    env.update_hazard(TIME_STEP)

    # Main Loop Logic for Each Responder
    for responder_id in all_responders:
        # T3: Get the optimal next step
        next_waypoint, sequence = aggregator.get_next_waypoint(responder_id, simulator.room_status)
        
        print(f"  > R-{responder_id}: Next Waypoint: {next_waypoint} | Sequence: {sequence}")
        
        # T2: Update responder position based on the waypoint
        T_rezone, current_pos = simulator.update_position(TIME_STEP, next_waypoint)
        
        # T1 Check: Re-Zoning Trigger (The T2 -> T1 feedback loop)
        if T_rezone == 1:
            print(f"  !!! Re-Zone Triggered by R-{responder_id} !!!")
            # T1 re-runs allocation
            simulator.zones = allocator.re_partition(N_RESPONDERS, ['A']) # Mock compromised room
            pathfinder.zones = simulator.zones # Update T3's zones

    # T3: Update max sweep time
    aggregator.update_sweep_time(current_time)

    # Check for completion
    if all(status == 'Cleared' for status in simulator.room_status.values()):
        is_complete = True

# --- 4. RESULTS ---
print("\n--- 4. Results ---")
print(f"Final Room Status: {simulator.room_status}")
print(f"Total Sweep Time (Placeholder Max): {aggregator.total_sweep_time:.1f}s")
print("Smoke Test Complete: All modules communicated successfully!")