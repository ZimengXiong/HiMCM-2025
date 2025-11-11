# T1_Strategist.py - Team Member 1

import numpy as np

class BuildingModel:
    """Manages the static building structure and global parameters."""
    def __init__(self, layout_data):
        self.V_WALK = 1.5  # m/s
        self.T_CLEAR = 30  # seconds per standard office room
        self.graph = self._initialize_graph(layout_data)
        self.risk_factors = self._calculate_risk(layout_data) 

    def _initialize_graph(self, layout_data):
        # Placeholder: Returns a simple graph with rooms A, B, C, D.
        # Rooms A & B connected to H1 (Hallway node)
        return {
            'A': {'neighbors': ['H1'], 'cost_to_H1': 10.0},
            'B': {'neighbors': ['H1'], 'cost_to_H1': 10.0},
            'H1': {'neighbors': ['A', 'B'], 'cost_to_A': 10.0, 'cost_to_B': 10.0}
        }

    def _calculate_risk(self, layout_data):
        # Placeholder: Uniform risk for all rooms.
        return {'A': 1.0, 'B': 1.0, 'H1': 0.0}

class ZoneAllocator:
    """Implements Poisson's Equation and Clustering for zone assignment."""
    def __init__(self, building_model: BuildingModel):
        self.building = building_model

    def solve_poisson_demand(self):
        # Placeholder: Simple dummy demand.
        return {'A': 100, 'B': 100, 'H1': 10}

    def initial_partition(self, N_responders: int):
        """
        Task: Partition the building based on the demand field.
        OUTPUT 2: Zonal Assignment Z_i(t0)
        OUTPUT 3: P_coord
        """
        # Placeholder: Assigns room A to R1, room B to R2.
        initial_zones = {'R1': ['A', 'H1'], 'R2': ['B']}
        P_coord = 50.0 # Placeholder for initial repulsion strength

        return initial_zones, P_coord

    def re_partition(self, N_responders: int, compromised_rooms: list):
        # Placeholder: Simple logic to reassign remaining rooms.
        return {'R1': ['H1'], 'R2': ['B']} # Example if 'A' is compromised