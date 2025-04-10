from tile import Tile
from a_star import AStar
from unit import Unit
import json
import string

import random

import math
from typing import List, Tuple, Set

Position = Tuple[int, int]


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
    
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'
    GREY = '\033[90m'
    BLACK = '\033[90m'
    DEFAULT = '\033[99m'


class GameMap:
    def __init__(self, size, map_encoding=None, random_map=(0, 0.1)):
        self.size = size
        if map_encoding:
            self.load_map(map_encoding, size)
        else:
            self.tiles = [[Tile((x, y)) for y in range(size)] for x in range(size)]
            if random_map[0] != 0:
                coords = generate_maze_pattern(
                    size, density=random_map[1], seed=random_map[0]
                )
                self.tiles = [[Tile((x, y)) for y in range(size)] for x in range(size)]
                for x, y in coords:
                    maneuver_score = random.randint(-10, -2)
                    if x == 25:
                        maneuver_score = 1
                    if y == 25:
                        maneuver_score = 1
                    self.tiles[x][y].maneuver_score = maneuver_score

    def get_tile(self, position):
        x, y = position
        return self.tiles[x][y]

    def find_path(self, unit_weight, start, goal):
        planner = AStar(self, start, goal, unit_weight)
        return planner.find_path()

    # def get_visible_tiles(self, unit: Unit):
    #     visible_tiles = set()
    #     for dx in range(-1, 2):
    #         for dy in range(-1, 2):
    #             x = unit.position[0] + dx
    #             y = unit.position[1] + dy
    #             if 0 <= x < self.size and 0 <= y < self.size:
    #                 visible_tiles.add((x, y))
    #     return visible_tiles

    def get_visible_tiles(
        self,
        unit_pos: Position,
        direction_deg: int,
        vision_cone_deg: int,
        vision_range: int,
    ) -> Set[Position]:
        
        visible = set()
        direction_rad = math.radians(direction_deg)
        half_cone = math.radians(vision_cone_deg / 2)

        for dx in range(-vision_range, vision_range + 1):
            for dy in range(-vision_range, vision_range + 1):
                if dx == 0 and dy == 0:
                    continue

                tx, ty = unit_pos[0] + dx, unit_pos[1] + dy
                rel_dx, rel_dy = tx - unit_pos[0], ty - unit_pos[1]

                dist = math.hypot(rel_dx, rel_dy)
                if dist > vision_range:
                    continue

                angle_to_tile = math.atan2(rel_dy, rel_dx)
                angle_diff = (angle_to_tile - direction_rad + math.pi * 2) % (
                    math.pi * 2
                )
                if angle_diff > math.pi:
                    angle_diff -= math.pi * 2

                if abs(angle_diff) > half_cone:
                    continue

                # Elevation and concealment/cover blocking
                steps = int(dist)
                unit_elev = self.tiles[unit_pos[0]][unit_pos[1]].elevation
                blocked = False
                occlusion_score = 0

                for step in range(1, steps + 1):
                    ix = unit_pos[0] + int(round(rel_dx * step / dist))
                    iy = unit_pos[1] + int(round(rel_dy * step / dist))
                    if ix < 0 or ix >= self.size or iy < 0 or iy >= self.size:
                        continue

                    tile = self.tiles[ix][iy]
                    if tile.elevation - unit_elev > 5:
                        blocked = True
                        break

                    occlusion_score += (tile.concealment_score + tile.cover_score)
                    if occlusion_score >= 100:
                        blocked = True
                        break

                if not blocked:
                    visible.add((tx, ty))

        return visible

    def save_map(self, filename):
        with open(filename, "w") as f:
            for row in self.tiles:
                for tile in row:
                    data = {
                        "x": tile.x,
                        "y": tile.y,
                        "maneuver": tile.maneuver_score,
                        "elevation": tile.elevation,
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
                tile.elevation = data["elevation"]
                tile.concealment_score = data["concealment"]
                tile.fuel = data["fuel"]
                tile.manpower = data["manpower"]
                tile.resources = data["resources"]
                tiles[tile.x][tile.y] = tile

        self.tiles = tiles

    def print_maneuver_map(self, unit: Unit, path=None, vision=None):
        digits = string.digits + string.ascii_lowercase
        endured_cost = 0

        def to_base36(val):
            val = max(min(val, 35), -35)  # clamp to range
            if val < 0:
                return "-" + digits[abs(val)]
            return digits[val]

        for y in reversed(range(self.size)):
            row = ""
            for x in range(self.size):
                val = self.tiles[x][y].maneuver_score + self.tiles[x][y].elevation
                sym = to_base36(val).rjust(2)

                if unit and (x, y) == unit.position:
                    endured_cost += val
                    sym = bcolors.BOLD + bcolors.OKBLUE + " @" + bcolors.ENDC
                elif path and (x, y) in path:
                    endured_cost += val
                    if val > 0:
                        sym = bcolors.OKGREEN + " •" + bcolors.ENDC
                    elif val < -1:
                        sym = bcolors.FAIL + sym + bcolors.ENDC
                    else:
                        sym = bcolors.OKCYAN + " •" + bcolors.ENDC
                elif vision and (x, y) in vision:
                    sym = bcolors.WHITE + " ▩" + bcolors.ENDC
                elif val < -1:
                    sym = bcolors.WARNING + sym + bcolors.ENDC
                elif val > 0:
                    sym = bcolors.HEADER + sym + bcolors.ENDC
                elif val == 0 or val == -1:
                    sym = "  "

                if x == 49 and y == 49:
                    sym = bcolors.OKGREEN + sym + bcolors.ENDC

                row += sym
            print(row)
        print("Endured cost: ", endured_cost)
