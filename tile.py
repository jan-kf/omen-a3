class Tile:
    def __init__(self, position, data=None):
        self.position = position
        self.x = position[0]
        self.y = position[1]
        self.data = data

        self.manuever_score = 0
        self.concealment_score = 0
        self.altitude = 0

        self.fuel = 0
        self.manpower = 0
        self.resources = 0

    def calculate_tile_values(self): 
        # Placeholder for tile value calculation logic
        # not to be done yet
        pass