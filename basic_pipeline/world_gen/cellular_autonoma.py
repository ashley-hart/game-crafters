# Midpoint Displacement + Cellular Automata
import numpy as np
import random

'''
LEARNING RESOURCES:
    - Midpoint Displacement Article: https://stevelosh.com/blog/2016/02/midpoint-displacement/
    - Cellular Autonoma 
    
    * Using MD for heightmap and biome assingment and CA for biome smoothing. 
'''

# ASCII terrain mapping
TERRAIN_CHARS = {
    "water": "~",
    "grass": ".",
    "hills": "n",
    "mountains": "^"
}

class ASCIIMapGenerator():

    def generate_heightmap(self, size, roughness):
        """Generates a heightmap using Midpoint Displacement."""
        grid = np.zeros((size, size))
        grid[0, 0] = grid[0, -1] = grid[-1, 0] = grid[-1, -1] = random.uniform(0, 1)

        def displace(x1, y1, x2, y2, variance):
            mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2  # Recall // is int division
            if grid[mid_x, mid_y] == 0:
                grid[mid_x, mid_y] = (grid[x1, y1] + grid[x2, y2]) / 2 + random.uniform(-variance, variance)

        step = size - 1
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

        return grid

    def height_to_ascii(self, grid):
        """Converts heightmap values into ASCII terrain."""
        ascii_map = []
        for row in grid:
            line = ""
            for val in row:
                if val < 0.3:
                    line += TERRAIN_CHARS["water"]
                elif val < 0.5:
                    line += TERRAIN_CHARS["grass"]
                elif val < 0.7:
                    line += TERRAIN_CHARS["hills"]
                else:
                    line += TERRAIN_CHARS["mountains"]
            ascii_map.append(line)
        return ascii_map

    def get_ascii_output(self):
        # Generate ASCII World
        size = 33  # Must be (2^n) + 1 for Midpoint Displacement
        roughness = 0.5
        heightmap = self.generate_heightmap(size, roughness)
        ascii_world = self.height_to_ascii(heightmap)

        # Print ASCII world
        for line in ascii_world:
            print(line)
        
        print("Displaying map in PyGame Window")
        return ascii_world
