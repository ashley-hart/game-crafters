# Midpoint Displacement + Cellular Automata
import numpy as np
import random
from ascii_tile import ASCIITile, water_tile, mountain_tile, plains_tile, desert_tile, forest_tile, pines_tile, lava_tile, snow_tile

from biome_mask import create_biome_mask, print_mask
from diamond_square import generate_heightmap_w_biome_mask



'''
LEARNING RESOURCES:
    - Midpoint Displacement Article: https://stevelosh.com/blog/2016/02/midpoint-displacement/
    - Cellular Autonoma 
    - Perlin Noise
    
    * Using MD for heightmap and biome assignment and CA for biome smoothing. 
'''

# ASCII terrain mapping
TERRAIN_CHARS = {
    "water": "~",
    "grass": ".",
    "hills": "n",
    "mountains": "^"
}

EXTRA_SMALL_MAP = 9 # n = 3
SMALL_MAP = 17 # n = 4
MEDIUM_MAP = 33 # n = 5
LARGE_MAP = 65 # n = 6
EXTRA_LARGE_MAP = 129 # n = 7

class WorldGenerator():
    
    def __init__(self, map_size, roughness=0.5):
        self.map_size = map_size
        self.base_roughness = roughness
 
    def heightmap_to_ascii(self, grid):
        """Converts heightmap values into ASCII terrain tiles."""
        ascii_map = []
        for row in grid:
            line = []
            for val in row:
                if val < 0.2:
                    line.append(water_tile)
                elif val < 0.5:
                    line.append(desert_tile)
                elif val < 0.7:
                    line.append(plains_tile)
                elif val < 1.2:
                    line.append(pines_tile)
                elif val < 1.9:
                    line.append(mountain_tile)
                else:
                    line.append(snow_tile)
            ascii_map.append(line)
        return ascii_map

    # TODO: Adjust these default vals & get a better understanding of what they do
    def create_world(self, size=9, roughness=0.5):
        # Generate ASCII World
        
        # PRE-PROCESSING (Pre-Heightmap)
        # ===============================
        
        # Set global world parameters & and biome frequencies, then set explitly defined biomes 
        
        print("Creating biome mask")
        print("Using sample params... delete these later")
        user_params = {'north': 'desert',
                'south': 'mountains',
                'center': 'forest'}
        biome_mask = create_biome_mask(size, user_params)
        
        print("Printing biome mask")
        print_mask(biome_mask)
        
        # HEIGHTMAP GENERATION
        # ======================
        
        # 1 - Generate the height map wrt the biome mask
        # heightmap = self.generate_heightmap(roughness)
        heightmap = generate_heightmap_w_biome_mask(self.map_size, biome_mask, roughness)
        
        for row in heightmap:
            print("".join("{:.1f}, ".format(val) for val in row))
        
        # PRE-PROCESSING (Post-Heightmap)
        # ===============================
        
        
        # POST-PROCESSING
        # ======================
        # TODO: Add post processing rules
        # Enforce generation rules via cellular autonoma 
        # & perlin noise
        
        
        # ASCII RENDERING
        # ======================
        
        # Map heightmap values to ASCII chars
        ascii_world = self.heightmap_to_ascii(heightmap)
        
        # TODO: Add map frame

        # Print ASCII world
        for row in ascii_world:
            for tile in row:
                print(tile.symbol, end="")
            print()
        
        return ascii_world


# Call this file from the cmd line only when testing. Otherwise, 
# call pygame_main.py for the full UI display.
if __name__ == "__main__":
    world_map = WorldGenerator(EXTRA_SMALL_MAP) 
    world_map.create_world()
    print("\033[38;5;196mBright red text\033[0m") # ANSI Color Test
    print("\033[38;2;255;100;0mOrange text\033[0m") # RGC Color Test

    