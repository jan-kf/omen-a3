from tile import Tile

class GameMap:
    def __init__(self, size):
        self.size = size
        self.tiles = [[Tile((x,y)) for y in range(size)] for x in range(size)]

    