# T2_Navigator.py - Team Member 2

import numpy as np

# Mock T1 BuildingModel class for smoke test independence
# In the actual run, you would import T1_Strategist.BuildingModel
class MockBuildingModel:
    def __init__(self):
        self.V_WALK = 1.5
        self.T_CLEAR = 30

class DynamicEnvironment:
    """Manages the CA for hazards and the SFM for occupants."""
    def __init__(self, graph):
        self.graph = graph
        self.hazard_map = {} 

    def update_hazard(self, time_step):
        """Task: Run one step of the CA model. OUTPUT: Hazard Map H(x, t)"""
        # Placeholder: Hazard at (1, 1) is increasing.
        if 'R1' not in self.hazard_map:
             self.hazard_map = {'R1': 0.0, 'R2': 0.0}
        
        self.hazard_map['R1'] += 0.05 # R1's path gets a bit riskier
        return self.hazard_map

    def update_occupants(self, time_step):
        """Task: Run one step of the SFM. Returns attractive force U_moving."""
        # Placeholder: No significant occupant attraction force.
        return 0.0

class MovementSimulator:
    """Calculates movement based on the Total Potential Field U_i."""
    def __init__(self, initial_zones, P_coord, env: DynamicEnvironment):
        self.zones = initial_zones
        self.P_coord = P_coord
        self.env = env
        self.responder_pos = {'R1': (0.0, 0.0), 'R2': (5.0, 0.0)} # Start points
        self.room_status = self._initialize_status(initial_zones) # OUTPUT 2: S(t)
        self.total_time = 0.0

    def _initialize_status(self, zones):
        status = {}
        for r_list in zones.values():
            for room in r_list:
                status[room] = 'Unchecked'
        return status

    def update_position(self, time_step, next_waypoint):
        """
        Task: Calculate total potential U_i and update position via gradient descent.
        """
        self.total_time += time_step
        
        # Placeholder for movement: R1 just moves a little toward (1, 0)
        self.responder_pos['R1'] = (self.responder_pos['R1'][0] + 0.1, self.responder_pos['R1'][1])
        
        # Placeholder for status update: After 3 steps, R1 clears 'A'
        if self.total_time > 10.0:
            self.room_status['A'] = 'Cleared'

        # Placeholder for Re-Zoning Trigger: Set to 1 if hazard is high
        T_rezone = 1 if self.env.hazard_map.get('R1', 0) > 0.1 else 0

        # OUTPUT 1: Current Responder Position x_i(t)
        return T_rezone, self.responder_pos

# T2 OUTPUTS: T_rezone (to T1), self.responder_pos, self.room_status (to T3)