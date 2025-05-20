from typing import List, Set, Tuple, Optional, TYPE_CHECKING
import math
from collections import Counter

if TYPE_CHECKING:
    from game_map import GameMap
    from unit import Unit
    from tile import Tile


def max_range(tile_cap: int) -> int:
    # estimate for max range given tile capacity
    return int(math.sqrt(tile_cap / 3.14))


def estimated_center(coords):
    x_avg = sum(x for x, _ in coords) // len(coords)
    y_avg = sum(y for _, y in coords) // len(coords)
    return (x_avg, y_avg)


class RegionControl:
    def __init__(
        self,
        region_id: str,
        side: str,
        tile_cap: int,
        game_map: "GameMap",
        list_of_positions: List[Tuple[int, int]],
    ):
        self.region_id = region_id
        self.side = side  # "A" or "B"
        self.tile_cap = tile_cap
        self.estimated_max_range = max_range(tile_cap)

        self.map = game_map
        self.units: List["Unit"] = []
        self.commander: Optional[str] = None  # Could be a unit_id or name

        self.controlled_tiles: Set[Tuple[int, int]] = set()

        self.assigned_positions: Set[Tuple[int, int]] = set()
        self.guarded_positions: Set[Tuple[int, int]] = set()

        for pos in list_of_positions:
            tile = self.map.get_tile(pos)
            self.add_tile(tile)
        self.calibrate_tasking()

    def calibrate_tasking(self):
        self.center = estimated_center(self.controlled_tiles)
        self.potential_points_of_interest = self.get_nearest_points_of_interest()
        self.local_direction_weights = self.get_local_direction_weights()
        self.local_paths = list(self.local_direction_weights.keys())

    def get_nearest_points_of_interest(self):
        map_points_of_interest = self.map.points_of_interest
        reachable_points = []
        for point in map_points_of_interest:
            tile = self.map.get_tile(point)
            if (
                tile.occupation
                and tile.occupation[0] == self.side
                and tile.occupation[1] != self.region_id
            ):
                continue
            distance = self.manhattan_distance(self.center, point) / 2
            if distance <= self.estimated_max_range:
                reachable_points.append(point)

        return reachable_points

    def get_local_direction_weights(self):
        path_coords = Counter()
        for point in self.potential_points_of_interest:
            for other_point in self.potential_points_of_interest:
                if point == other_point:
                    continue
                path = self.map.find_path(
                    unit_weight=1.0,
                    start=point,
                    goal=other_point,
                )
                path_coords.update(path)
        return dict(path_coords)

    def can_expand(self) -> bool:
        return len(self.controlled_tiles) < self.tile_cap

    def add_tile(self, tile: "Tile"):
        if (
            self.tile_cap > len(self.controlled_tiles)
            and tile.position not in self.controlled_tiles
        ):
            self.controlled_tiles.add(tile.position)
            tile.occupation = (self.side, self.region_id)
            if tile.position in self.assigned_positions:
                self.assigned_positions.remove(tile.position)

    def remove_tile(self, tile: "Tile"):
        self.controlled_tiles.discard(tile.position)

    def assign_unit(self, unit: "Unit"):
        if unit not in self.units:
            unit.assign_region(self.region_id)
            self.units.append(unit)

    ## not sure if useful anymore, gets the border tiles of the region
    # def get_frontier_tiles(self) -> List[Tuple[int, int]]:
    #     frontier = []
    #     for pos in self.controlled_tiles:
    #         tile = self.map.get_tile(pos)  # tile is a controlled tile
    #         for adj in self.map.get_adjacent(tile.position):
    #             if adj.position not in self.controlled_tiles:
    #                 frontier.append(tile.position)
    #                 break
    #     return frontier

    def get_expansion_targets(self) -> List[Tuple[int, int]]:
        frontier = []
        for pos in self.controlled_tiles:
            tile = self.map.get_tile(pos)  # tile is a controlled tile
            for adj in self.map.get_adjacent(tile.position):
                if adj.position not in self.controlled_tiles:
                    frontier.append(adj.position)
                    break
        return frontier

    def is_coord_bound(self, coord):
        x, y = coord

        # Cast rays in four directions
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Right  # Left  # Down  # Up

        for dx, dy in directions:
            found_boundary = False
            for step in range(1, self.estimated_max_range + 1):
                nx, ny = x + dx * step, y + dy * step
                if (nx, ny) in self.controlled_tiles:
                    found_boundary = True
                    break

            if not found_boundary:
                return False  # If any ray does not hit a boundary, it's not bound

        return True

    def is_near_point_of_interest(self, coord):
        for point in self.potential_points_of_interest:
            if self.manhattan_distance(coord, point) / 2 <= 2:
                return True
        return False

    def find_expansion_targets(self) -> List[Tuple[float, Tuple[int, int]]]:
        if self.can_expand() is False:
            return []
        frontier = self.get_expansion_targets()
        candidates: List[Tuple[float, Tuple[int, int]]] = []
        for position in [
            *frontier,
            *self.potential_points_of_interest,
            *self.local_paths,
        ]:
            tile = self.map.tiles[position[0]][position[1]]

            if tile.isWater:
                continue
            if tile.position in self.controlled_tiles:
                continue
            if tile.position in self.assigned_positions:
                continue
            if tile.occupation and tile.occupation[0] == self.side:
                continue

            score = 0
            ## needs more work:
            if self.is_coord_bound(tile.position):
                score += 10
                # self.add_tile(tile)
                # continue

            if self.is_near_point_of_interest(tile.position):
                score += 20

            score += tile.fuel + tile.resources + tile.manpower

            local_weight = self.local_direction_weights.get(tile.position, 0) * 10

            priority = (
                5
                if tile.occupation and tile.occupation[0] != self.side
                else local_weight
            )

            tile_cap_modifier = (self.tile_cap // len(self.controlled_tiles)) * 100

            maneuver = tile.maneuver_score
            elevation_difference = tile.elevation - tile.elevation

            # if elevation_difference > 200:
            #     continue  # not even allowed to move there
            # else:
            elevation_penalty = (
                abs(elevation_difference) * 1.5
                if elevation_difference > 0
                else abs(elevation_difference)
            )

            value = (priority + score + tile_cap_modifier) + (
                maneuver - elevation_penalty
            )

            candidates.append((value, tile.position))

        candidates.sort(reverse=True, key=lambda x: x[0])
        return candidates

    def find_guard_targets(self) -> List[Tuple[float, Tuple[int, int]]]:
        """
        Identify high-value tiles already under control that should be guarded.
        Scores tiles based on resource value, elevation, proximity to enemy, etc.
        Returns a list of (score, position) tuples sorted by score descending.
        """
        candidates = []
        for pos in self.controlled_tiles:
            tile = self.map.get_tile(pos)
            score = 0

            if self.is_near_point_of_interest(tile.position):
                score += 20

            # Example scoring logic
            score += tile.fuel + tile.resources + tile.manpower  # value of the tile
            score += (
                tile.concealment_score / 20
            )  # harder to detect unit = better guard post
            # for adj in self.map.get_adjacent(pos):
            #     if adj.occupation and adj.occupation[0] != self.side:
            #         score += 10  # near enemy = important

            if pos not in self.guarded_positions:
                candidates.append((score, pos))

        candidates.sort(reverse=True, key=lambda x: x[0])
        return candidates

    def manhattan_distance(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # def assign_units_to_expand(self):
    #     if not self.can_expand():
    #         print("Region is at capacity, cannot expand.", self.region_id)
    #         return

    #     expansion_targets = self.find_expansion_targets()
    #     guard_targets = self.find_guard_targets()
    #     available_units = [u for u in self.units if u.is_idle()]
    #     print(
    #         self.region_id,
    #         len(available_units),
    #         len(self.assigned_positions),
    #         len(self.guarded_positions),
    #         f"{(len(self.controlled_tiles)/self.tile_cap)*100:.2f}% capacity",
    #         [x[0] for x in expansion_targets[:5]],
    #         [x[0] for x in guard_targets[:5]],
    #     )
    #     for unit in available_units:
    #         if len(expansion_targets) == 0 and len(guard_targets) == 0:
    #             print("No targets available for expansion or guarding", self.region_id)
    #             break

    #         best_expansion_value = float("-inf")
    #         best_guard_value = float("-inf")
    #         if expansion_targets:
    #             best_expansion_value = expansion_targets[0][0]
    #         if guard_targets:
    #             best_guard_value = guard_targets[0][0]

    #         if best_expansion_value > best_guard_value:

    #             best_expansive_position = expansion_targets.pop(0)[1]

    #             best_expansive = self.map.tiles[best_expansive_position[0]][
    #                 best_expansive_position[1]
    #             ]
    #             unit.handle_assigned_location(best_expansive.position)
    #             self.assigned_positions.add(best_expansive.position)

    #         else:
    #             best_guard_position = guard_targets.pop(0)[1]

    #             best_guard = self.map.tiles[best_guard_position[0]][
    #                 best_guard_position[1]
    #             ]
    #             unit.handle_assigned_location(best_guard.position)
    #             unit.holding_defense = int(best_guard_value)
    #             unit.defense_position = best_guard.position
    #             self.guarded_positions.add(best_guard.position)

    #     if len(available_units) == 0:
    #         defensive_units = [u for u in self.units if u.holding_defense]
    #         for unit in defensive_units:
    #             best_expansion_value = float("-inf")
    #             best_guard_value = float("-inf")
    #             if expansion_targets:
    #                 best_expansion_value = expansion_targets[0][0]
    #             if guard_targets:
    #                 best_guard_value = guard_targets[0][0]

    #             if (
    #                 unit.holding_defense > best_expansion_value
    #                 or unit.holding_defense > best_guard_value
    #             ):
    #                 continue

    #             if unit.defense_position:
    #                 self.guarded_positions.remove(unit.defense_position)

    #             if best_expansion_value > best_guard_value:

    #                 best_expansive_position = expansion_targets.pop(0)[1]

    #                 best_expansive = self.map.tiles[best_expansive_position[0]][
    #                     best_expansive_position[1]
    #                 ]
    #                 unit.handle_assigned_location(best_expansive.position)
    #                 unit.holding_defense = 0
    #                 self.assigned_positions.add(best_expansive.position)

    #             else:
    #                 best_guard_position = guard_targets.pop(0)[1]

    #                 best_guard = self.map.tiles[best_guard_position[0]][
    #                     best_guard_position[1]
    #                 ]
    #                 unit.handle_assigned_location(best_guard.position)
    #                 unit.holding_defense = int(best_guard_value)
    #                 unit.defense_position = best_guard.position
    #                 self.guarded_positions.add(best_guard.position)

    def assign_units_to_expand(self):
        expansion_targets = self.find_expansion_targets()
        guard_targets = self.find_guard_targets()

        available_units = [u for u in self.units if u.is_idle()]
        defensive_units = [u for u in self.units if u.holding_defense]

        print(
            self.region_id,
            len(available_units),
            len(self.assigned_positions),
            len(self.guarded_positions),
            f"{(len(self.controlled_tiles)/self.tile_cap)*100:.2f}% capacity",
            [x[0] for x in expansion_targets[:5]],
            [x[0] for x in guard_targets[:5]],
            self.local_paths != [],
        )

        def find_closest_unit(position, units):
            return min(
                units, key=lambda unit: self.manhattan_distance(position, unit.position)
            )

        all_targets = expansion_targets + guard_targets
        all_targets.sort(reverse=True, key=lambda x: x[0])

        # Step 2: Assign to available (idle) units first
        for value, position in all_targets:
            if not available_units:
                break

            closest_unit = find_closest_unit(position, available_units)
            tile = self.map.tiles[position[0]][position[1]]
            closest_unit.handle_assigned_location(tile.position)

            if (value, position) in expansion_targets:
                self.assigned_positions.add(tile.position)
            else:
                closest_unit.holding_defense = int(value)
                closest_unit.defense_position = tile.position
                self.guarded_positions.add(tile.position)

            available_units.remove(closest_unit)

        # Step 3: Reassign defensive units if it's beneficial
        for value, position in all_targets:
            if not defensive_units:
                break

            closest_unit = find_closest_unit(position, defensive_units)

            # Only reassign if the new value is higher
            if closest_unit.holding_defense < value:
                if closest_unit.defense_position:
                    self.guarded_positions.discard(closest_unit.defense_position)

                tile = self.map.tiles[position[0]][position[1]]
                closest_unit.handle_assigned_location(tile.position)

                if (value, position) in expansion_targets:
                    self.assigned_positions.add(tile.position)
                    closest_unit.holding_defense = 0
                else:
                    closest_unit.holding_defense = int(value)
                    closest_unit.defense_position = tile.position
                    self.guarded_positions.add(tile.position)

                defensive_units.remove(closest_unit)

        self.calibrate_tasking()
