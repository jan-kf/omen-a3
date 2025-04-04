from grid import Grid
from commander import Commander
from settings import GRID_SIZE, TURN_LIMIT
from visibility import VisibilityManager
from influence_map import InfluenceMap

def main():
    grid = Grid(GRID_SIZE)
    visibility = VisibilityManager(grid)
    commanders = [Commander("A", grid, visibility), Commander("B", grid, visibility)]

    for turn in range(TURN_LIMIT):
        # Update visibility based on all units
        all_units = [unit for cmd in commanders for unit in cmd.units]
        visibility.update_visibility(all_units)

        # Generate updated influence map
        influence_map = InfluenceMap(grid, all_units, visibility)
        influence_map.generate()

        # Each commander performs actions
        for commander in commanders:
            commander.take_turn(influence_map)

        # Update grid after all moves
        grid.update()
        grid.display()

if __name__ == "__main__":
    main()
