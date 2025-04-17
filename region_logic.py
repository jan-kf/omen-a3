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

        for pos in list_of_positions:
            self.controlled_tiles.add(pos)
            tile = self.map.get_tile(pos)
            tile.occupation = (self.side, self.region_id)

    def can_expand(self) -> bool:
        return len(self.controlled_tiles) < self.tile_cap

    def assign_unit(self, unit: "Unit"):
        if unit not in self.units:
            unit.assigned_region = self.region_id
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

    def find_expansion_targets(self) -> List[Tuple[int, int]]:
        frontier = self.get_frontier_tiles()
        candidates: List[Tuple[int, Tile]] = []

        for position in frontier:
            tile = self.map.tiles[position[0]][position[1]]
            for neighbor in self.map.get_adjacent(position):
                if neighbor.position in self.controlled_tiles:
                    continue
                if neighbor.occupation and neighbor.occupation[0] == self.side:
                    continue

                priority = (
                    100
                    if neighbor.occupation and neighbor.occupation[0] != self.side
                    else 50
                )
                maneuver = neighbor.maneuver_score
                elevation_penalty = abs(neighbor.elevation - tile.elevation)
                value = priority + maneuver - elevation_penalty

                candidates.append((value, neighbor))

        candidates.sort(reverse=True, key=lambda x: x[0])
        return [tile.position for _, tile in candidates]

    def assign_units_to_expand(self):
        if not self.can_expand():
            return

        targets = self.find_expansion_targets()
        available_units = [u for u in self.units if u.is_idle()]

        for unit in available_units:
            if not targets:
                break
            best_target_position = targets.pop(0)
            best_target = self.map.tiles[best_target_position[0]][
                best_target_position[1]
            ]
            unit.handle_assigned_location(self.map, best_target.position)

            # unit needs to be the one that adds the tile to the controlled set
            # unit needs to let the region know that it's expanded
            # self.controlled_tiles.add(best_target.position)
            # best_target.occupation = (self.side, self.region_id)
