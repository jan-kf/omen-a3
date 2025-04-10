import random
from game_map import GameMap
from unit import Unit
import time

s = random.randint(0, 1000000)

game_map = GameMap(size=50, random_map=(s, 0.2))
unit = Unit(agent_id=1, position=(0, 0), infantry=1, has_transport=False, armor_rating=0, direction=0, vision_cone=270, vision_range=5)
# game_map.save_map("map_encoding")

# game_map = GameMap(size=50, map_encoding="map_encoding")


unit_weight = 4
start = (0, 0)
goal = (35, 35)

path = game_map.find_path(unit_weight, start, goal)
unit.assigned_path = path

for i in range(len(path)):
    time.sleep(0.2)
    unit.act()
    visible_tiles = game_map.get_visible_tiles(
        unit.position, unit.direction, unit.vision_cone, unit.vision_range
    )
    game_map.print_maneuver_map(unit, path=path, vision=visible_tiles)

# print(path)
