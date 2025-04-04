from combat import resolve_combat

class Unit:
    def __init__(self, agent_id, position, grid, visibility):
        self.agent_id = agent_id
        self.position = position
        self.grid = grid
        self.visibility = visibility
        self.count = 1
        self.is_dead = False

    def act(self, influence_map):
        best_pos = self.grid.get_best_adjacent_position(self.position, influence_map)
        occupant = self.grid.get_unit_at(best_pos)
        if occupant and occupant.agent_id != self.agent_id:
            winner = resolve_combat(self, occupant)
            if winner is self:
                self.position = best_pos
                self.grid.move_unit(self, best_pos)
            elif winner is None:
                self.grid.remove_unit(self)
                self.grid.remove_unit(occupant)
        else:
            self.position = best_pos
            self.grid.move_unit(self, best_pos)