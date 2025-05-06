from tile import Tile
from a_star import AStar
import json
import string

import random

import math
from typing import List, Tuple, Set, TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from unit import Unit
    from region_logic import RegionControl

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

    RED = "\033[91m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    GREY = "\033[90m"
    BLACK = "\033[90m"
    DEFAULT = "\033[99m"


def unit_vector_from_angle(degrees: int) -> Tuple[float, float]:
    radians = math.radians(degrees)
    return math.cos(radians), math.sin(radians)


def apply_elevation_function(tiles: List[List["Tile"]], size, height_func):
    for x in range(size):
        for y in range(size):
            elevation = int(height_func(x, y))
            tiles[x][y].elevation = elevation
            tiles[x][y].maneuver_score = 0 if elevation > 0 else 5
            tiles[x][y].concealment_score = 50
            tiles[x][y].cover_score = 50
            tiles[x][y].fuel = random.randint(0, 1) if elevation < 10 else 0
            tiles[x][y].manpower = random.randint(0, 1) if elevation < 10 else 0
            tiles[x][y].resources = random.randint(0, 1) if elevation < 10 else 0


class GameMap:
    def __init__(self, size, map_encoding=None, generation_funct=None):
        self.size = size
        if map_encoding:
            self.load_map(map_encoding, size)
        else:
            self.tiles = [[Tile((x, y)) for y in range(size)] for x in range(size)]
            apply_elevation_function(self.tiles, self.size, generation_funct)

    def get_tile(self, position) -> "Tile":
        x, y = position
        return self.tiles[x][y]

    def find_path(self, unit_weight, start, goal):
        planner = AStar(self, start, goal, unit_weight)
        return planner.find_path()

    def get_adjacent(self, position: Tuple[int, int]) -> List[Tile]:
        x, y = position
        adj = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                adj.append(self.tiles[nx][ny])
        return adj

    def get_visible_tiles(
        self,
        unit_pos: Position,
        direction_deg: int,
        vision_cone_deg: int,
        vision_range: int,
        max_occlusion: int = 100,
        elevation_threshold: int = 5,
    ) -> Set[Position]:

        visible = set()
        direction_deg = direction_deg % 360
        start_elev = self.tiles[unit_pos[0]][unit_pos[1]].elevation

        half_cone = vision_cone_deg // 2
        for angle in range(
            direction_deg - half_cone, direction_deg + half_cone + 1, 10
        ):
            dx, dy = unit_vector_from_angle(angle)
            occlusion = 0
            for r in range(1, vision_range + 1):
                tx = unit_pos[0] + round(dx * r)
                ty = unit_pos[1] + round(dy * r)

                if tx < 0 or tx >= self.size or ty < 0 or ty >= self.size:
                    break

                tile = self.tiles[tx][ty]
                if tile.elevation - start_elev > elevation_threshold:
                    break

                occlusion += tile.concealment_score + tile.cover_score
                if occlusion >= max_occlusion:
                    break

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

    def print_maneuver_map(
        self,
        regions: List["RegionControl"],
    ):
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
                # val = self.tiles[x][y].maneuver_score + self.tiles[x][y].elevation
                val = self.tiles[x][y].elevation
                sym = to_base36(val).rjust(2)
                has_changed = False

                # elif unit.get_visible_tiles(self) and (x, y) in unit.get_visible_tiles(self):
                #     sym = bcolors.WHITE + " ▩" + bcolors.ENDC

                for region in regions:

                    # if (x, y) in region.get_frontier_tiles():
                    #     sym = bcolors.YELLOW + " ◌" + bcolors.ENDC
                    if has_changed:
                        continue

                    if (x, y) in region.controlled_tiles:
                        if region.side == "A":
                            sym = bcolors.OKGREEN + "░░" + bcolors.ENDC
                            # sym = bcolors.OKGREEN + sym + bcolors.ENDC
                            has_changed = True
                        elif region.side == "B":
                            sym = bcolors.YELLOW + "░░" + bcolors.ENDC
                            # sym = bcolors.YELLOW + sym + bcolors.ENDC
                            has_changed = True
                            # print("FOO")
                    # elif (x, y) in region.find_expansion_targets():
                    #     if region.side == "A":
                    #         sym = bcolors.OKCYAN + sym + bcolors.ENDC
                    #         # sym = bcolors.OKCYAN + " ◍" + bcolors.ENDC
                    #         has_changed = True
                    #     elif region.side == "B":
                    #         sym = bcolors.HEADER + sym + bcolors.ENDC
                    #         has_changed = True
                    #         # print("BAR")
                    tile_weight = 0
                    for unit in region.units:
                        if (x, y) == unit.position:
                            endured_cost += val
                            tile_weight += 1
                            match unit.direction:
                                case 90:
                                    sym = " ↑"
                                case 45:
                                    sym = " ↗"
                                case 0:
                                    sym = " →"
                                case 315:
                                    sym = " ↘"
                                case 180:
                                    sym = " ↓"
                                case 225:
                                    sym = " ↙"
                                case 270:
                                    sym = " ←"
                                case 135:
                                    sym = " ↖"
                            sym = "██"
                            # sym = to_base36(tile_weight).rjust(2)
                            if unit.side == "A":
                                sym = bcolors.CYAN + sym + bcolors.ENDC
                                has_changed = True
                            elif unit.side == "B":
                                sym = bcolors.FAIL + sym + bcolors.ENDC
                                has_changed = True
                        # elif unit.assigned_path and (x, y) in unit.assigned_path:
                        #     endured_cost += val
                        #     if unit.side == "A":
                        #         sym = bcolors.CYAN + " •" + bcolors.ENDC
                        #         has_changed = True
                        #     elif unit.side == "B":
                        #         sym = bcolors.YELLOW + " •" + bcolors.ENDC
                        #         has_changed = True

                if not has_changed:
                    sym = bcolors.WHITE + sym + bcolors.ENDC

                row += sym
            print(row)
        # print("Endured cost: ", endured_cost)
        # print("Unit task: ", unit.current_tasking)
