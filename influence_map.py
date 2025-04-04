class InfluenceMap:
    def __init__(self, grid, units, visibility):
        self.grid = grid
        self.units = units
        self.visibility = visibility
        self.map = [[0 for _ in range(grid.size)] for _ in range(grid.size)]

    def generate(self):
        for unit in self.units:
            x, y = unit.position
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid.size and 0 <= ny < self.grid.size:
                        self.map[ny][nx] += max(0, 5 - abs(dx) - abs(dy))