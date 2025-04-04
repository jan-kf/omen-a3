from tile import Tile
from d_star_lite import DStarLite
import json
import string

import random


def generate_maze_pattern(size, density=0.1, seed=None):
    if seed is not None:
        random.seed(seed)

    maze_coords = set()
    wall_count = int(size * size * density)

    for _ in range(wall_count):
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        if (x, y) != (0, 0) and (x, y) != (size - 1, size - 1):
            # Avoid placing walls at the start and goal positions
            maze_coords.add((x, y))

    return maze_coords


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class GameMap:
    def __init__(self, size, map_encoding=None, random_map=(0, 0.1)):
        self.size = size
        if map_encoding:
            self.load_map(map_encoding, size)
        else:
            self.tiles = [[Tile((x, y)) for y in range(size)] for x in range(size)]
            if random_map[0] != 0:
                coords = generate_maze_pattern(size, density=random_map[1], seed=random_map[0])
                self.tiles = [[Tile((x, y)) for y in range(size)] for x in range(size)]
                for x, y in coords:
                    self.tiles[x][y].maneuver_score = random.randint(-50, 10)

    def get_tile(self, position):
        x, y = position
        return self.tiles[x][y]

    def find_path(self, unit_weight, start, goal):
        planner = DStarLite(self, start, goal, unit_weight)
        planner.compute_shortest_path()
        return planner.get_path()

    def save_map(self, filename):
        with open(filename, "w") as f:
            for row in self.tiles:
                for tile in row:
                    data = {
                        "x": tile.x,
                        "y": tile.y,
                        "maneuver": tile.maneuver_score,
                        "altitude": tile.altitude,
                        "concealment": tile.concealment_score,
                        "fuel": tile.fuel,
                        "manpower": tile.manpower,
                        "resources": tile.resources,
                    }
                    f.write(json.dumps(data) + "\n")

    def load_map(self, filename, size):
        tiles = [[Tile((x, y)) for y in range(size)] for x in range(size)]
        with open(filename) as f:
            for line in f:
                data = json.loads(line)
                tile = Tile((data["x"], data["y"]))
                tile.maneuver_score = data["maneuver"]
                tile.altitude = data["altitude"]
                tile.concealment_score = data["concealment"]
                tile.fuel = data["fuel"]
                tile.manpower = data["manpower"]
                tile.resources = data["resources"]
                tiles[tile.x][tile.y] = tile

        self.tiles = tiles

    def print_maneuver_map(self, path=None):
        digits = string.digits + string.ascii_lowercase

        def to_base36(val):
            val = max(min(val, 35), -35)  # clamp to range
            if val < 0:
                return "-" + digits[abs(val)]
            return digits[val]

        for y in reversed(range(self.size)):
            row = ""
            for x in range(self.size):
                val = self.tiles[x][y].maneuver_score
                sym = to_base36(val).rjust(2)
                    
                if path and (x, y) in path:
                    if val > 0:
                        sym = bcolors.OKGREEN + sym + bcolors.ENDC
                    elif val < 0:
                        sym = bcolors.FAIL + sym + bcolors.ENDC
                    else:
                        sym = bcolors.OKCYAN + sym + bcolors.ENDC
                elif val < 0:
                    sym = bcolors.WARNING + sym + bcolors.ENDC
                elif val > 0:
                    sym = bcolors.HEADER + sym + bcolors.ENDC
                elif val == 0:
                    sym = "  "

                if x == 49 and y == 49:
                    sym = bcolors.OKGREEN + sym + bcolors.ENDC

                row += sym
            print(row)
