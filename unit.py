from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from game_map import GameMap

unit_behavior_options = ["SAFE", "DEFENSIVE", "AGGRESSIVE", "STEALTHY"]
unit_rules_of_engagement = ["HOLD_FIRE", "RETURN_FIRE", "OPEN_FIRE"]


class Unit:
    def __init__(
        self,
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

        self.assigned_region: Optional[str] = None
        self.side: Optional[str] = side  # "A" or "B"

    def handle_assigned_location(self, game_map: "GameMap", position):
        if position == self.position:
            return []

        if not self.assigned_path:
            self.assigned_path = game_map.find_path(
                unit_weight=self.armor_rating,
                start=self.position,
                goal=position,
            )

        if not self.assigned_path:
            return []

        if self.assigned_path[-1] == position:
            self.assigned_path.pop(-1)

        return self.assigned_path

    def get_visible_tiles(self, game_map: "GameMap"):
        return game_map.get_visible_tiles(
            self.position, self.direction, self.vision_cone, self.vision_range
        )

    def act(self):
        if self.assigned_path:
            self.move()
        else:
            self.hold()

    def handle_contact(self):
        # Placeholder for contact handling logic
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

        self.position = new_position

    def hold(self):
        self.current_tasking = "HOLD"
        self.direction = -1

    def is_idle(self):
        return self.current_tasking == "HOLD"
