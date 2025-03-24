# Start Here: https://www.youtube.com/watch?v=Lezk01D4ToE&ab_channel=OrkSlayerGamedev

from random import randint
from tile import Tile, plains, forest, pines, mountain, water

DEFAULT_TILE = plains

class Map:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        
        # The map will be a list of a list of strings.
        self.map_data: list[list[Tile]]
        
        
        # Note: eventually we'd want these to be controllable parameters that we can get from the LLM.
        self.generate_map()
        self.generate_patch(water, 6, 4, 7)
        self.generate_patch(forest, 3, 3, 3)
        self.generate_patch(pines, 2, 1, 1)
        self.generate_patch(mountain, 2, 1, 2)
        self.generate_patch(mountain, 2, 3, 5)
        
    def generate_map(self) -> None:
        # Map init (short version)
        self.map_data = [[DEFAULT_TILE for _ in range(self.width)] for _ in range(self.height)]
        
        # Map init (longer version)
        # map_data = []
        # for row in range(self.height):
        #     row_data = []
        #     for col in range (self.width):
        #         row_data.append(".")
        #     map_data.append(row_data)
        
        
    # Set the x and y indexes to make sure that there will be no indexing errors during generation. 
    # This says that we cannot start on index 0 OR the last index of any row or column,
    # The frame that the map is displayed in is not included in these calculations.
    def generate_patch(self, tile: Tile, num_patches: int, min_size: int, max_size: int, irregular: bool = True) -> None:
        for _ in range(num_patches):
            width = randint(min_size, max_size)
            height = randint(min_size, max_size)
            start_x = randint(1, self.width - width - 1)
            start_y = randint(1, self.height - height - 1)
            
            if irregular:
                init_start_x = randint(3, self.width - max_size)
            
            for i in range(height):
                if irregular:
                    width = randint(int(0.5 * max_size), max_size) # ? is 0.7 the dropout rate?
                    start_x = init_start_x - randint(1,2)
                for j in range(width):
                    self.map_data[start_y + i][start_x + j] = tile
        
    def display_map(self) -> None:
        frame = 'x' + self.width * "=" + "x" # header
        print(frame) # print top header
        for row in self.map_data:
            row_tiles = [tile.symbol for tile in row]
            print("|" + "".join(row_tiles) + "|")
            # print("|" + "".join(row) + "|") # this worked before we added tile objects.
        print(frame) # print bottom header