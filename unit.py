class Unit:
    def __init__(
        self, agent_id, position, infantry=1, has_transport=False, armor_rating=0
    ):
        self.agent_id = agent_id
        self.position = position
        self.count = infantry
        self.has_transport = has_transport
        self.armor_rating = armor_rating
        self.current_tasking = "HOLD"
        self.direction = -1  # implied ARD
        self.assigned_path = []

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
                self.direction = 0
            case [1, 1]:
                self.direction = 45
            case [1, 0]:
                self.direction = 90
            case [1, -1]:
                self.direction = 135
            case [0, -1]:
                self.direction = 180
            case [-1, -1]:
                self.direction = 225
            case [-1, 0]:
                self.direction = 270
            case [-1, 1]:
                self.direction = 315

        self.position = new_position

    def hold(self):
        self.current_tasking = "HOLD"
        self.direction = -1
