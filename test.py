import random
from game_map import GameMap
from unit import Unit
from region_logic import RegionControl
import time

s = random.randint(0, 1000000)

start_time = time.time()
game_map = GameMap(size=25, random_map=(s, 0.1))
map_gen_time = time.time() - start_time
print(f"Map generation time: {map_gen_time:.9f} seconds")


unit = Unit(
    agent_id=1,
    side="A",
    position=(0, 0),
    infantry=1,
    has_transport=False,
    armor_rating=0,
    direction=0,
    vision_cone=270,
    vision_range=5,
)
# game_map.save_map("map_encoding")

# game_map = GameMap(size=50, map_encoding="map_encoding")


# unit_weight = 4
# start = (0, 0)
# goal = (49, 49)


# start_time = time.time()
# path = unit.handle_assigned_location(game_map, goal)
# path_calc_time = time.time() - start_time
# print(f"Path calculation time: {path_calc_time:.9f} seconds")

# path_length = len(path)

act_time = 0
visible_time = 0


region = RegionControl(
    region_id="A",
    side="A",
    tile_cap=10,
    game_map=game_map,
    list_of_positions=[
        (0, 0),
        (1, 0),
        (2, 0),
        (0, 1),
        (0, 2),
        (1, 1),
        (1, 2),
        (2, 2),
        (2, 1),
    ],
)

region.assign_unit(unit)

for _ in range(10):
    game_map.print_maneuver_map(unit, region=region)
    region.assign_units_to_expand()
    unit.act()
    time.sleep(0.1)


# for i in range(len(path)):
#     # time.sleep(0.2)
#     start_time = time.time()
#     unit.act()
#     act_time += time.time() - start_time
#     start_time = time.time()
#     visible_tiles = game_map.get_visible_tiles(
#         unit.position, unit.direction, unit.vision_cone, unit.vision_range
#     )
#     visible_time += time.time() - start_time
#     # game_map.print_maneuver_map(unit, path=path, vision=visible_tiles)

# act_time /= path_length
# visible_time /= path_length

# print(f"Path length: {path_length}")
# print(f"Act time: {act_time:.9f} seconds")
# print(f"Visible time: {visible_time:.9f} seconds")
