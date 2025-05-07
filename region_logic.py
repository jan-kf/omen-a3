from typing import List, Set, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game_map import GameMap
    from unit import Unit
    from tile import Tile


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
        self.map = game_map
        self.units: List["Unit"] = []
        self.commander: Optional[str] = None  # Could be a unit_id or name

        self.controlled_tiles: Set[Tuple[int, int]] = set()

        self.assigned_positions: Set[Tuple[int, int]] = set()
        self.guarded_positions: Set[Tuple[int, int]] = set()

        for pos in list_of_positions:
            self.controlled_tiles.add(pos)
            tile = self.map.get_tile(pos)
            tile.occupation = (self.side, self.region_id)

    def can_expand(self) -> bool:
        return len(self.controlled_tiles) < self.tile_cap

    def add_tile(self, tile: "Tile"):
        if tile.position not in self.controlled_tiles:
            self.controlled_tiles.add(tile.position)
            tile.occupation = (self.side, self.region_id)
            if tile.position in self.assigned_positions:
                self.assigned_positions.remove(tile.position)

    def remove_tile(self, tile: "Tile"):
        self.controlled_tiles.remove(tile.position)

    def assign_unit(self, unit: "Unit"):
        if unit not in self.units:
            unit.assign_region(self.region_id)
            self.units.append(unit)

    def get_frontier_tiles(self) -> List[Tuple[int, int]]:
        frontier = []
        for pos in self.controlled_tiles:
            tile = self.map.get_tile(pos)
            for adj in self.map.get_adjacent(tile.position):
                if adj.position not in self.controlled_tiles:
                    frontier.append(tile.position)
                    break
        return frontier

    def find_expansion_targets(self) -> List[Tuple[float, Tuple[int, int]]]:
        frontier = self.get_frontier_tiles()
        candidates: List[Tuple[float, Tuple[int, int]]] = []
        for position in frontier:
            tile = self.map.tiles[position[0]][position[1]]
            for neighbor in self.map.get_adjacent(position):
                if neighbor.position in self.controlled_tiles:
                    continue
                if neighbor.position in self.assigned_positions:
                    continue
                if neighbor.occupation and neighbor.occupation[0] == self.side:
                    continue

                score = neighbor.fuel + neighbor.resources + neighbor.manpower

                priority = (
                    5
                    if neighbor.occupation and neighbor.occupation[0] != self.side
                    else 0
                )

                tile_cap_modifier = (self.tile_cap // len(self.controlled_tiles)) * 10

                maneuver = neighbor.maneuver_score
                elevation_difference = neighbor.elevation - tile.elevation

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

                candidates.append((value, neighbor.position))

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

    def assign_units_to_expand(self):
        if not self.can_expand():
            print("Region is at capacity, cannot expand.", self.region_id)
            return

        expansion_targets = self.find_expansion_targets()
        guard_targets = self.find_guard_targets()
        available_units = [u for u in self.units if u.is_idle()]
        print(
            self.region_id,
            len(available_units),
            len(self.assigned_positions),
            len(self.guarded_positions),
            f"{(len(self.controlled_tiles)/self.tile_cap)*100:.2f}% capacity",
            [x[0] for x in expansion_targets[:5]],
            [x[0] for x in guard_targets[:5]],
        )
        for unit in available_units:
            if len(expansion_targets) == 0 and len(guard_targets) == 0:
                print("No targets available for expansion or guarding", self.region_id)
                break

            best_expansion_value = float("-inf")
            best_guard_value = float("-inf")
            if expansion_targets:
                best_expansion_value = expansion_targets[0][0]
            if guard_targets:
                best_guard_value = guard_targets[0][0]

            if best_expansion_value > best_guard_value:

                best_expansive_position = expansion_targets.pop(0)[1]

                best_expansive = self.map.tiles[best_expansive_position[0]][
                    best_expansive_position[1]
                ]
                unit.handle_assigned_location(best_expansive.position)
                self.assigned_positions.add(best_expansive.position)

            else:
                best_guard_position = guard_targets.pop(0)[1]

                best_guard = self.map.tiles[best_guard_position[0]][
                    best_guard_position[1]
                ]
                unit.handle_assigned_location(best_guard.position)
                unit.holding_defense = int(best_guard_value)
                unit.defense_position = best_guard.position
                self.guarded_positions.add(best_guard.position)

        if len(available_units) == 0:
            defensive_units = [u for u in self.units if u.holding_defense]
            for unit in defensive_units:
                best_expansion_value = float("-inf")
                best_guard_value = float("-inf")
                if expansion_targets:
                    best_expansion_value = expansion_targets[0][0]
                if guard_targets:
                    best_guard_value = guard_targets[0][0]

                if (
                    unit.holding_defense > best_expansion_value
                    or unit.holding_defense > best_guard_value
                ):
                    continue

                if unit.defense_position:
                    self.guarded_positions.remove(unit.defense_position)

                if best_expansion_value > best_guard_value:

                    best_expansive_position = expansion_targets.pop(0)[1]

                    best_expansive = self.map.tiles[best_expansive_position[0]][
                        best_expansive_position[1]
                    ]
                    unit.handle_assigned_location(best_expansive.position)
                    unit.holding_defense = 0
                    self.assigned_positions.add(best_expansive.position)

                else:
                    best_guard_position = guard_targets.pop(0)[1]

                    best_guard = self.map.tiles[best_guard_position[0]][
                        best_guard_position[1]
                    ]
                    unit.handle_assigned_location(best_guard.position)
                    unit.holding_defense = int(best_guard_value)
                    unit.defense_position = best_guard.position
                    self.guarded_positions.add(best_guard.position)
