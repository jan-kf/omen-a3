from heapq import heappop, heappush
import math


class DStarLite:
    def __init__(
        self,
        game_map,
        start,
        goal,
        unit_weight,
        heuristic_weight=1.0,
        stealth_preference=0.0,
    ):
        self.map = game_map
        self.start = start
        self.goal = goal
        self.unit_weight = unit_weight
        self.heuristic_weight = heuristic_weight
        self.stealth_preference = stealth_preference

        self.km = 0
        self.rhs = {}
        self.g = {}
        self.open_list = []

        self.rhs[goal] = 0
        self.g[goal] = float("inf")
        heappush(self.open_list, (self.calculate_key(goal), goal))

    def calculate_key(self, node):
        g = self.g.get(node, float("inf"))
        rhs = self.rhs.get(node, float("inf"))
        h = self.heuristic(node, self.start)
        return (min(g, rhs) + h + self.km, min(g, rhs))

    def heuristic(self, a, b):
        return self.heuristic_weight * (abs(a[0] - b[0]) + abs(a[1] - b[1]))

    def update_vertex(self, node):
        if node != self.goal:
            self.rhs[node] = min(
                [
                    self.g.get(s, float("inf")) + self.cost(node, s)
                    for s in self.get_neighbors(node)
                ]
            )
        self.open_list = [item for item in self.open_list if item[1] != node]
        if self.g.get(node, float("inf")) != self.rhs.get(node, float("inf")):
            heappush(self.open_list, (self.calculate_key(node), node))

    def cost(self, a, b):
        tile_b = self.map.tiles[b[0]][b[1]]
        maneuver = tile_b.maneuver_score
        concealment = tile_b.concealment_score
        altitude_diff = abs(self.map.tiles[a[0]][a[1]].altitude - tile_b.altitude)

        if self.unit_weight > 15:
            if maneuver < -50 or altitude_diff > 15:
                return float("inf")
            base_cost = -maneuver
        else:
            base_cost = -maneuver

        base_cost += max(0, altitude_diff - 5) / 5
        base_cost -= (concealment / 100) * self.stealth_preference
        return max(0.1, base_cost)

    def get_neighbors(self, node):
        x, y = node
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.map.size and 0 <= ny < self.map.size:
                neighbors.append((nx, ny))
        return neighbors

    def compute_shortest_path(self):
        while self.open_list and (
            self.open_list[0][0] < self.calculate_key(self.start)
            or self.rhs.get(self.start, float("inf"))
            != self.g.get(self.start, float("inf"))
        ):
            k_old, u = heappop(self.open_list)
            k_new = self.calculate_key(u)
            if k_old < k_new:
                heappush(self.open_list, (k_new, u))
            elif self.g.get(u, float("inf")) > self.rhs.get(u, float("inf")):
                self.g[u] = self.rhs[u]
                for s in self.get_neighbors(u):
                    self.update_vertex(s)
            else:
                self.g[u] = float("inf")
                self.update_vertex(u)
                for s in self.get_neighbors(u) + [u]:
                    self.update_vertex(s)

    def get_path(self):
        path = []
        current = self.start
        path.append(current)

        while current != self.goal:
            neighbors = self.get_neighbors(current)
            min_cost = float("inf")
            next_node = None

            for neighbor in neighbors:
                move_cost = self.cost(current, neighbor)
                if move_cost == float("inf"):
                    continue
                total_cost = move_cost + self.rhs.get(neighbor, float("inf"))
                if total_cost < min_cost:
                    min_cost = total_cost
                    next_node = neighbor

            if next_node is None:
                break
            current = next_node
            path.append(current)

        return path
