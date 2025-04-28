import random
from game_map import GameMap
from unit import Unit
from region_logic import RegionControl
import time

s = random.randint(0, 1000000)

map_size = 50
tile_cap = 1000

start_time = time.time()
game_map = GameMap(size=map_size, random_map=(s, 0.1))
map_gen_time = time.time() - start_time
print(f"Map generation time: {map_gen_time:.9f} seconds")


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
    list_of_positions=get_adjacent_positions((5, 5)),
)


region2 = RegionControl(
    region_id="Bravo",
    side="B",
    tile_cap=tile_cap,
    game_map=game_map,
    list_of_positions=get_adjacent_positions((45, 45)),
)

regions = {"Alpha": region, "Bravo": region2}

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
