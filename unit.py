from typing import TYPE_CHECKING, Optional, Dict

if TYPE_CHECKING:
    from game_map import GameMap
    from region_logic import RegionControl

unit_behavior_options = ["SAFE", "DEFENSIVE", "AGGRESSIVE", "STEALTHY"]
unit_rules_of_engagement = ["HOLD_FIRE", "RETURN_FIRE", "OPEN_FIRE"]


class Unit:
    def __init__(
        self,
        game_map: "GameMap",
        region_map: Dict[str, "RegionControl"],
        assigned_region_id: str,
        agent_id,
        side,
        position,
        infantry=1,
        has_transport=False,
        armor_rating=0,
        direction=0,
        vision_cone=120,
        vision_range=5,
    ):
        self.game_map = game_map
        self.region_map = region_map
        self.assigned_region = region_map[assigned_region_id]
        self.agent_id = agent_id
        self.position = position
        self.count = infantry
        self.has_transport = has_transport
        self.armor_rating = armor_rating
        self.current_tasking = "HOLD"

        self.direction = direction  # implied ARD
        self.vision_cone = vision_cone  # degrees
        self.vision_range = vision_range

        self.assigned_path = []
        self.behavior = "SAFE"
        self.rules_of_engagement = "RETURN_FIRE"
        self.side: Optional[str] = side  # "A" or "B"

    def assign_region(self, region_id: str):
        self.assigned_region = self.region_map[region_id]

    def handle_assigned_location(self, position):
        if position == self.position:
            return []

        if not self.assigned_path:
            self.assigned_path = self.game_map.find_path(
                unit_weight=self.armor_rating,
                start=self.position,
                goal=position,
            )

        if not self.assigned_path:
            return []

        if self.assigned_path[0] == self.position:
            self.assigned_path.pop(0)

        return self.assigned_path

    def get_visible_tiles(self):
        return self.game_map.get_visible_tiles(
            self.position, self.direction, self.vision_cone, self.vision_range
        )

    def act(self):
        if self.assigned_path:
            self.move()
        else:
            self.hold()

    def get_visible_units(self, visible_tiles=None):
        if visible_tiles is None:
            visible_tiles = self.get_visible_tiles()
        visible_units = {}
        for tile_pos in visible_tiles:
            tile = self.game_map.get_tile(tile_pos)
            if units := tile.units:
                for unit in units:
                    visible_units[unit.side] = unit
        return visible_units

    def handle_contact(self):
        # Placeholder for contact handling logic
        # handle contact that's next to us first
        nearby_units = []
        nearby_tiles = self.game_map.get_adjacent(self.position)
        for tile in nearby_tiles:
            if units := tile.units:
                for unit in units:
                    if unit.side != self.side:
                        nearby_units.append(unit)

        ...  # handle contact that's next to us

        # handle contact that's not nearby
        visible_units = self.get_visible_units()
        for friendly_unit in visible_units.get(self.side, []):
            if friendly_unit != self:
                # check if enemies are near friendly unit
                ...
        pass

    def move(self):
        if not self.assigned_path:
            return self.hold()

        new_position = self.assigned_path.pop(0)

        self.current_tasking = "MOVE"
        vector = [
            new_position[0] - self.position[0],
            new_position[1] - self.position[1],
        ]
        if vector[0] > 1:
            vector[0] = 1
        if vector[0] < -1:
            vector[0] = -1
        if vector[1] > 1:
            vector[1] = 1
        if vector[1] < -1:
            vector[1] = -1

        match vector:
            case [0, 1]:
                self.direction = 90
            case [1, 1]:
                self.direction = 45
            case [1, 0]:
                self.direction = 0
            case [1, -1]:
                self.direction = 315
            case [0, -1]:
                self.direction = 180
            case [-1, -1]:
                self.direction = 225
            case [-1, 0]:
                self.direction = 270
            case [-1, 1]:
                self.direction = 135

        tile_moving_off_of = self.game_map.get_tile(self.position)
        tile_moving_off_of.units.remove(self)
        self.position = new_position

        new_tile = self.game_map.get_tile(self.position)
        new_tile.units.append(self)
        if new_tile.occupation[0] != self.side:
            # if tile is occupied by enemy, we need to let enemy know that it's taken
            if prev_occupier := self.region_map.get(new_tile.occupation[1]):
                prev_occupier.remove_tile(new_tile)
            self.assigned_region.add_tile(new_tile)

    def hold(self):
        self.current_tasking = "HOLD"
        self.direction = -1

    def is_idle(self):
        return self.current_tasking == "HOLD"
