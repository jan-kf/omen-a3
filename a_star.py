import heapq


class AStar:
    def __init__(self, game_map, start, goal, unit_weight=1.0, stealth_priority=0.0):
        self.map = game_map
        self.start = start
        self.goal = goal
        self.unit_weight = unit_weight
        self.stealth_priority = stealth_priority

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cost(self, from_tile, to_tile):
        maneuver_penalty = max(0, to_tile.maneuver_score * -1)
        elevation_difference: int = to_tile.elevation - from_tile.elevation

        # if elevation_difference > 200:
        #     return float("inf")

        elevation_penalty = (
            abs(elevation_difference) * 1.5
            if elevation_difference > 0
            else abs(elevation_difference)
        )

        concealment_penalty: int = (
            100 - to_tile.concealment_score
        ) * self.stealth_priority
        cover_maneuver_penalty: int = 1 + to_tile.cover_score // 100
        return float(
            maneuver_penalty
            + (elevation_penalty * self.unit_weight)
            + concealment_penalty
            + cover_maneuver_penalty
        )

    def find_path(self):
        open_set = []
        heapq.heappush(open_set, (0, self.start))
        came_from = {}
        g_score = {self.start: 0.0}
        f_score = {self.start: self.heuristic(self.start, self.goal)}

        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == self.goal:
                return self.reconstruct_path(came_from, current)

            for dx, dy in [
                (0, 1),
                (1, 0),
                (0, -1),
                (-1, 0),
                (1, 1),
                (-1, -1),
                (1, -1),
                (-1, 1),
            ]:
                neighbor = (current[0] + dx, current[1] + dy)
                if not (
                    0 <= neighbor[0] < self.map.size
                    and 0 <= neighbor[1] < self.map.size
                ):
                    continue

                from_tile = self.map.get_tile(current)
                to_tile = self.map.get_tile(neighbor)
                if to_tile.isWater:
                    continue
                tentative_g = g_score[current] + self.cost(from_tile, to_tile)

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(
                        neighbor, self.goal
                    )
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]
