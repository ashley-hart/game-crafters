# Midpoint Displacement + Cellular Automata
import numpy as np
from ascii_tile import water_tile, mountain_tile, plains_tile, desert_tile, forest_tile, pines_tile, lava_tile, snow_tile

from biome_mask import create_biome_mask, print_mask
from diamond_square import generate_heightmap_w_biome_mask, smooth_biome_transitions
from utility_methods import print_grid
from world_config import DisplayMode, MapSizes

# ASCII terrain mapping
TERRAIN_CHARS = {
    "water": "~",
    "grass": ".",
    "hills": "n",
    "mountains": "^"
}

class WorldGenerator():
    
    def __init__(self, map_size, user_params, roughness=0.5, display_mode=DisplayMode.ASCII_MODE, seed=None):
        self.map_size = map_size.value
        self.base_roughness = roughness
        self.user_params = user_params
        self.display_mode = display_mode
        self.seed = seed
        
        print(f"Creating a new world")
        print(f"Map dimensions: {self.map_size}x{self.map_size}")
        print(f"Inspired by the following user_params: {self.user_params}")
        print(f"Generator Seed: {self.seed}")
 
    # TODO: Move this to a map renderer class.
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
    def create_world(self, roughness=0.5):
        # Generate ASCII World
        
        # PRE-PROCESSING (Pre-Heightmap)
        # ===============================
        
        # TODO: Set global world parameters & and biome frequencies, then set explitly defined biomes 
        
        print("Creating biome mask")
        print("Using sample params... delete these later")
        biome_mask = create_biome_mask(self.map_size, self.user_params)
        
        print("Printing biome mask")
        print_grid(biome_mask)
        
        # HEIGHTMAP GENERATION
        # ======================
        
        # 1 - Generate the height map wrt the biome mask
        # heightmap = self.generate_heightmap(roughness)
        
        print("Generating heightmap w/ biome mask")
        height_map = generate_heightmap_w_biome_mask(self.map_size, biome_mask, roughness, seed=self.seed)
        print_grid(height_map)
        
        for row in height_map:
            print("".join("{:.1f}, ".format(val) for val in row))
        
        # PRE-PROCESSING (Post-Heightmap)
        # ===============================
        print("Smoothing heightmap for nicer biome transitions")
        smoothed_hm = smooth_biome_transitions(biome_mask, height_map)
        print_grid(smoothed_hm)

        
        # POST-PROCESSING
        # ======================
        # TODO: Add post processing rules, I'll do this after the pipeline has been prototyped
        # Enforce generation rules via cellular autonoma 
        # & perlin noise
        
        
        # ASCII RENDERING
        # ======================
        # Map heightmap values to ASCII chars
        ascii_world = self.heightmap_to_ascii(smoothed_hm)
        # ascii_world = self.heightmap_to_ascii(height_map)
        
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
    print("\033[38;2;64;244;208m World Generator\033[0m") # RGC Color Test
    print("\033[38;2;64;244;208m=================\033[0m") # RGC Color Test
    
    # user_params = {'north': 'desert',
    #             'south': 'mountains',
    #             'center': 'forest'}
    user_params = {'north': 'water',
                'south': 'mountains',
                'center': 'water'}
    world_map = WorldGenerator(MapSizes.SMALL_MAP, user_params) 
    world_map.create_world()
    
    