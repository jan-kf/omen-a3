class Grid:
    def __init__(self, size):
        self.size = size
        self.tiles = [[None for _ in range(size)] for _ in range(size)]

    def update(self):
        # Stub method for future use
        pass

    def get_unit_at(self, position):
        x, y = position
        return self.tiles[y][x]

    def move_unit(self, unit, new_pos):
        old_x, old_y = unit.position
        new_x, new_y = new_pos
        self.tiles[old_y][old_x] = None
        self.tiles[new_y][new_x] = unit

    def remove_unit(self, unit):
        x, y = unit.position
        self.tiles[y][x] = None

    def get_best_adjacent_position(self, position, influence_map):
        x, y = position
        options = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and (dx != 0 or dy != 0):
                    score = influence_map.map[ny][nx]
                    options.append(((nx, ny), score))
        options.sort(key=lambda x: -x[1])
        return options[0][0] if options else position

    def display(self):
        for row in self.tiles:
            print(" ".join([u.agent_id if u else "." for u in row]))
        print()