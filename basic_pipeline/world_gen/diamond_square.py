import numpy as np
import random
from biome_mask import Biome

biome_roughness = {
    'water': 0.0, # What would a good roughness value be for this? 
    'desert': 0.1,
    'forest': 0.3,
    'plains': 0.2,
    'mountain': 0.6
}

biome_roughness = {
    Biome.WATER: 0.1, # What would a good roughness value be for this? 
    Biome.DESERT: 0.1,
    Biome.FOREST: 0.2,
    Biome.PLAINS: 0.15,
    Biome.MOUNTAINS: 0.6
}

biome_height_offsets = {
    Biome.WATER: -0.2, # What would a good roughness value be for this? 
    Biome.DESERT: 0.3,
    Biome.FOREST: 0.4,
    Biome.PLAINS: 0.2,
    Biome.MOUNTAINS: 0.9
}

# Generates a heightmap using the Diamond Square algorithim
def generate_heightmap_w_biome_mask(size, biome_mask, base_roughness=0.5, base_height_offset=0.1):
    grid = np.zeros((size, size))
    
    # Init corners
    grid[0, 0] = grid[0, -1] = grid[-1, 0] = grid[-1, -1] = random.uniform(0, 1)

    # Get the displacement value for the midpoint.
    def displace(x1, y1, x2, y2, variance):
        mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2  # Recall // is int division
        if grid[mid_x, mid_y] == 0: # If unitiialized (this is what 0 means)... displace it.
            grid[mid_x, mid_y] = (grid[x1, y1] + grid[x2, y2]) / 2 + random.uniform(-variance, variance)

    step_size = size - 1 # start big, then get smaller.
    iteration_num = 1
    while step_size > 1:
        half_step = step_size // 2
        
        # # Square step
        # for x in range(0, size - 1, step_size):
        #     for y in range(0, size - 1, step_size):
        #         displace(x, y, x + step_size, y + step_size, variance)

        # # Diamond step
        # for x in range(0, size, half):
        #     for y in range((x + half) % step_size, size, step_size):
        #         avg = np.mean([grid[(x - half) % size, y], grid[(x + half) % size, y],
        #                     grid[x, (y - half) % size], grid[x, (y + half) % size]])
        #         grid[x, y] = avg + random.uniform(-variance, variance)
        
        # Diamond Step
        # Check the biome and then perform the diamond step with the 
        # parameters for that biome
        for x in range (0, size - 1, step_size):
            for y in range(0, size - 1, step_size):
                biome = biome_mask[x + half_step, y + half_step]
                roughness = biome_roughness.get(Biome(biome), base_roughness)
                biome_height_offset = biome_height_offsets.get(Biome(biome), base_height_offset)
                diamond_step(grid, x, y, step_size, roughness, biome_height_offset)
                
        # Square step
        for x in range(0, size, half_step):
            for y in range((x + half_step) % step_size, size, step_size):
                biome = biome_mask[x % size, y % size] # use mod to stay in bounds
                roughness = biome_roughness.get(Biome(biome), base_roughness)
                biome_height_offset = biome_height_offsets.get(Biome(biome), base_height_offset)
                square_step(grid, x, y, step_size, roughness, size,  biome_height_offset)
        
        # Cut the step size in half
        step_size = half_step
        iteration_num += 1
        
        # Normalize array
        # min_val = np.min(grid)
        # max_val = np.max(grid)
        # grid = (grid - min_val) / (max_val - min_val)

    return grid


def diamond_step(grid, x, y, step, roughness, biome_height_offset):
    # Take the average value of the 4 corners and assign it to the point in the 
    # middle of the diamond. 
    avg = (grid[x, y] + grid[x + step, y] + grid[x, y + step] + grid[x + step, y + step]) / 4.0
    grid[x + step // 2, y + step // 2] = avg + np.random.uniform(-roughness, roughness) + biome_height_offset
    
    
def square_step(grid, x, y, step, roughness, map_size, biome_height_offset):
    # Take the average of the 3-4 points that point out from the point 
    # computed in the diamond step in the 4 cardinal directions. These points 
    # will be the average of all points that surround them in the 4 cardinal directions.
    
    neighbors = []
    if x - step >= 0: # get left pt
        neighbors.append(grid[x - step, y])
    if x + step < map_size: # get right pt
        neighbors.append(grid[x + step, y])
    if y - step >= 0: # get top pt
        neighbors.append(grid[x, y - step])
    if y + step < map_size: # get bottom pt
        neighbors.append(grid[x, y + step])
    avg = np.mean(neighbors)
    grid[x, y] = avg + np.random.uniform(-roughness, roughness) + biome_height_offset


def in_bounds(grid, index):
    if (index < 0) or (index > grid.length()):
        return False
    return True
    


# Generates a heightmap using the Diamond Square algorithim
def generate_heightmap(size, roughness):
    # size = map_size
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
