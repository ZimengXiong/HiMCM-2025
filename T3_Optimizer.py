# T3_Optimizer.py - Team Member 3

import time
# Mock T1 BuildingModel and T2 Classes for smoke test independence

class ACO_Pathfinder:
    """Implements the Ant Colony Optimization (ACO) for micro-scale sequencing."""
    def __init__(self, graph_g, initial_zones):
        self.graph = graph_g
        self.zones = initial_zones

    def find_optimal_sequence(self, responder_id, room_status):
        """
        Task: Run ACO on all 'Unchecked' rooms in the responder's current zone.
        """
        unchecked_rooms = [room for room in self.zones.get(responder_id, []) if room_status.get(room) == 'Unchecked']
        
        if not unchecked_rooms:
            return None, 0.0 # Sequence is complete

        # Placeholder: Just returns the remaining rooms in a fixed order.
        optimal_sequence = unchecked_rooms 
        estimated_time = len(unchecked_rooms) * 40.0 # Time = N_rooms * (T_CLEAR + travel)

        # OUTPUT 2: Optimal Sequence P*
        return optimal_sequence, estimated_time

class TimeAggregator:
    """Tracks cumulative time and determines the next waypoint for Layer 2."""
    def __init__(self, pathfinder: ACO_Pathfinder):
        self.pathfinder = pathfinder
        self.total_sweep_time = 0.0 # Total sweep time (T_sweep)

    def get_next_waypoint(self, responder_id, room_status):
        """
        Task: Get the optimal sequence and return the immediate next step.
        """
        optimal_sequence, _ = self.pathfinder.find_optimal_sequence(responder_id, room_status)
        
        if optimal_sequence:
            # OUTPUT 1: Next Waypoint x_next(t)
            next_waypoint = optimal_sequence[0] 
        else:
            next_waypoint = 'EXIT'

        return next_waypoint, optimal_sequence

    def update_sweep_time(self, current_time):
        """Task: Update the final total sweep time."""
        self.total_sweep_time = max(self.total_sweep_time, current_time)