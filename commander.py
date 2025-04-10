from unit import Unit
from settings import START_POSITIONS

class Commander:
    def __init__(self, agent_id, grid, visibility):
        self.agent_id = agent_id
        self.grid = grid
        self.visibility = visibility
        self.units = [Unit(agent_id, position=START_POSITIONS[agent_id], infantry=1, has_transport=False, armor_rating=0)]

    def take_turn(self, influence_map):
        for unit in self.units:
            ...

    def add_unit(self, position):
        self.units.append(Unit(self.agent_id, position=position, infantry=1, has_transport=False, armor_rating=0))
