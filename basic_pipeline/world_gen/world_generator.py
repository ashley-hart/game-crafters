# Midpoint Displacement + Cellular Automata
import numpy as np
import random
from ascii_tile import ASCIITile, water_tile, mountain_tile, plains_tile, forest_tile, pines_tile, lava_tile, snow_tile



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

class WorldGenerator():
    
    # Generates a heightmap using the Diamond Square algorithim
    def generate_heightmap(self, size, roughness):
        grid = np.zeros((size, size))
        grid[0, 0] = grid[0, -1] = grid[-1, 0] = grid[-1, -1] = random.uniform(0, 1)

        # Get the displacement value for the midpoint.
        def displace(x1, y1, x2, y2, variance):
            mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2  # Recall // is int division
            if grid[mid_x, mid_y] == 0: # If unitiialized (this is what 0 means)... displace it.
                grid[mid_x, mid_y] = (grid[x1, y1] + grid[x2, y2]) / 2 + random.uniform(-variance, variance)

        step = size - 1 # start big, then get smaller.
        iteration_num = 1
        while step > 1:
            half = step // 2
            variance = roughness * step / size
            
            # Square step
            for x in range(0, size - 1, step):
                for y in range(0, size - 1, step):
                    displace(x, y, x + step, y + step, variance)

            # Diamond step
            for x in range(0, size, half):
                for y in range((x + half) % step, size, step):
                    avg = np.mean([grid[(x - half) % size, y], grid[(x + half) % size, y],
                                grid[x, (y - half) % size], grid[x, (y + half) % size]])
                    grid[x, y] = avg + random.uniform(-variance, variance)

            step //= 2
            iteration_num += 1

        return grid

    def heightmap_to_ascii(self, grid):
        """Converts heightmap values into ASCII terrain tiles."""
        ascii_map = []
        for row in grid:
            line = []
            for val in row:
                if val < 0.2:
                    line.append(water_tile)
                elif val < 0.5:
                    line.append(plains_tile)
                elif val < 0.7:
                    line.append(pines_tile)
                elif val < 0.8:
                    line.append(mountain_tile)
                else:
                    line.append(snow_tile)
            ascii_map.append(line)
        return ascii_map

    # TODO: Adjust these default vals & get a better understanding of what they do
    def create_world(self, size=33, roughness=0.5):
        # Generate ASCII World
        
        # PRE-PROCESSING (Pre-Heightmap)
        # ===============================
        
        # Set global world parameters & and biome frequencies, then set explitly defined biomes 
        
        
        # HEIGHTMAP GENERATION
        # ======================
        
        # 1 - Generate the height map
        heightmap = self.generate_heightmap(size, roughness)
        
        # TODO: move this to the end

        # PRE-PROCESSING (Post-Heightmap)
        # ===============================
        
        
        # POST-PROCESSING
        # ======================
        # TODO
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
    world_map = WorldGenerator() 
    world_map.create_world()
    print("\033[38;5;196mBright red text\033[0m") # ANSI Color Test
    print("\033[38;2;255;100;0mOrange text\033[0m") # RGC Color Test

    