from typing import Tuple, Optional
import random


class Tile:
    def __init__(self, position, data=None):
        self.position = position
        self.x = position[0]
        self.y = position[1]
        self.data = data

        self.occupation: Tuple[Optional[str], Optional[str]] = (None, None)

        self.maneuver_score = -1
        # self.create_test_score()
        # 0 - 100 where 0 is exposed, 100 is completely concealed
        self.concealment_score = 0
        # 0 - 100 where 0 is no cover, 100 is full cover
        self.cover_score = 0

        self.elevation = 0

        self.fuel = 0
        self.manpower = 0
        self.resources = 0
        self.isWater = False
        self.make_test_elevation()
        self.make_test_concealment()
        self.make_test_cover()

    def calculate_tile_values(self):
        # Placeholder for tile value calculation logic
        # not to be done yet
        pass

    def make_test_elevation(self):
        self.elevation = random.randint(0, 36)

    def make_test_concealment(self):
        if self.y == 12:
            self.cover_score = 10

    def make_test_cover(self):
        if self.y == 12:
            self.cover_score = 10
        if self.y < 12 and self.x > 14:
            self.cover_score = 50

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
