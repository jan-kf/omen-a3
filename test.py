import random
from game_map import GameMap
from unit import Unit
from region_logic import RegionControl
import time
import math

s = random.randint(0, 1000000)

map_size = 50
tile_cap = 1000

waveform = lambda x, y: 20 * math.sin(x / 5) + 20 * math.cos(y / 5)
flat_random = lambda x, y: 0 + random.uniform(-5, 5)
radial_bump = lambda x, y: 50 * math.sin(math.hypot(x - 25, y - 25) / 5)
valley = lambda x, y: abs(x - y) * 10  # * 100
hills = lambda x, y: (math.sin(x / 2) + math.cos(y / 2)) * 200
hills_with_water = (
    lambda x, y: 10 * math.sin(0.1 * x) * math.cos(0.05 * y)
    + math.sin(0.5 * x)
    + math.cos(0.5 * y)
    + 5
)
valuable_tiles = [
    (5, 20),
    (45, 30),
    (6, 30),
    (44, 20),
    (25, 25),
    (25, 40),
]

start_time = time.time()
game_map = GameMap(
    size=map_size,
    generation_funct=hills_with_water,
    points_of_interest=valuable_tiles,
)
map_gen_time = time.time() - start_time
print(f"Map generation time: {map_gen_time:.9f} seconds")


#### path testing
# path = game_map.find_path(1, (6, 10), (18, 25))
# game_map.print_colored_map(coordinates=path)
# print(f"Path length: {len(path)}")
# print(f"Path: {path}")


#### region testing
units_per_region = 20


def get_adjacent_positions(position):
    x, y = position
    return [
        (x - 1, y),
        (x + 1, y),
        (x, y - 1),
        (x, y + 1),
        (x - 1, y - 1),
        (x + 1, y + 1),
        (x - 1, y + 1),
        (x + 1, y - 1),
    ]


region = RegionControl(
    region_id="Alpha",
    side="A",
    tile_cap=tile_cap,
    game_map=game_map,
    list_of_positions=get_adjacent_positions((10, 10)),
)


region2 = RegionControl(
    region_id="Bravo",
    side="B",
    tile_cap=tile_cap,
    game_map=game_map,
    list_of_positions=get_adjacent_positions((40, 40)),
)

regions = {"Alpha": region, "Bravo": region2}
# regions = {"Alpha": region}

region_list = list(regions.values())


for _region in region_list:
    for i in range(units_per_region):
        _region.assign_unit(
            Unit(
                game_map=game_map,
                region_map=regions,
                assigned_region_id=_region.region_id,
                agent_id=i,
                side=_region.side,
                position=random.choice(list(_region.controlled_tiles)),
            )
        )


for _ in range(1000):
    game_map.print_maneuver_map(regions=region_list)
    for _region in region_list:
        _region.assign_units_to_expand()
        for _unit in _region.units:
            _unit.act()
    time.sleep(0.3)
