class VisibilityManager:
    def __init__(self, grid, visibility_range=3):
        self.grid = grid
        self.visibility_range = visibility_range
        self.visible_tiles = set()

    def update_visibility(self, units):
        self.visible_tiles.clear()
        for unit in units:
            x, y = unit.position
            for dx in range(-self.visibility_range, self.visibility_range + 1):
                for dy in range(-self.visibility_range, self.visibility_range + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid.size and 0 <= ny < self.grid.size:
                        self.visible_tiles.add((nx, ny))

    def is_visible(self, x, y):
        return (x, y) in self.visible_tiles
