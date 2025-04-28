import math
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_map import GameMap
    from unit import Unit


def directional_decay(angle_deg: float) -> float:
    angle_deg = min(max(angle_deg, 0), 180)
    return max(0.0, math.exp(-angle_deg / 45) - math.exp(-180 / 45))


class CombatResolver:
    def __init__(self, game_map: "GameMap"):
        self.map = game_map

    def evaluate_engagement(self, attacker: "Unit", defender: "Unit"):
        ax, ay = attacker.position
        dx, dy = defender.position
        attacker_tile = self.map.get_tile((ax, ay))
        defender_tile = self.map.get_tile((dx, dy))

        elevation_diff = attacker_tile.altitude - defender_tile.altitude
        elevation_bonus = 0.1 * elevation_diff  

        concealment_penalty = defender_tile.concealment_score / 100

        flanking_bonus = directional_decay(abs(defender.direction - attacker.direction))

        attack_power = attacker.count
        defense_power = defender.count * (1 + elevation_bonus - concealment_penalty)

        attack_power *= 1 + flanking_bonus

        total = attack_power + defense_power
        attack_chance = attack_power / total
        return attack_chance

    def resolve_combat(self, attacker: "Unit", defender: "Unit"):
        chance = self.evaluate_engagement(attacker, defender)
        outcome = random.random()

        if outcome < chance:
            defender.count -= 1
            result = f"{attacker.agent_id} hit {defender.agent_id}"
        else:
            attacker.count -= 1
            result = f"{defender.agent_id} resisted attack from {attacker.agent_id}"

        return result
