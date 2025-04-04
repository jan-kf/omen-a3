
class Tile:
    def __init__(self, position, data=None):
        self.position = position
        self.x = position[0]
        self.y = position[1]
        self.data = data

        self.maneuver_score = -1
        # self.create_test_score()
        self.concealment_score = 0
        self.altitude = 0

        self.fuel = 0
        self.manpower = 0
        self.resources = 0

    def calculate_tile_values(self):
        # Placeholder for tile value calculation logic
        # not to be done yet
        pass

    def create_test_score(self):
        if self.x == 25:
            self.maneuver_score = 1
        
        if self.y == 25:
            self.maneuver_score = 1
        
        # elif self.x == 25 and self.y > 25:
        #     self.maneuver_score = -36
        # elif self.x == 40 and self.y > 25:
        #     self.maneuver_score = 5
        # elif 15 > self.x > 5 and self.y == 7:
        #     self.maneuver_score = -36
        # elif self.x == 9 and (5 >= self.y >= 2):
        #     self.maneuver_score = -36
        # elif self.x == 5 and (9 >= self.y >= 5):
        #     self.maneuver_score = -36
