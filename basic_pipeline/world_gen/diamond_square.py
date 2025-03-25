import numpy as np
import random
from biome_mask import create_biome_mask
from world_config import Biome, MapSizes
from utility_methods import print_grid

# ! do i still need this
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

# These "force" certain biomes to have variation around certain height values.
# The amount of variation is captured by the roughness value.
biome_height_offsets = {
    Biome.WATER: -0.05, # What would a good roughness value be for this? 
    Biome.DESERT: 0.3,
    Biome.FOREST: 0.4,
    Biome.PLAINS: 0.2,
    Biome.MOUNTAINS: 0.9
}

# Do diamond square map gen with respect to the biome mask.
def generate_heightmap_w_biome_mask(size, biome_mask, base_roughness=0.5, base_height_offset=0.1, seed=None):
    if seed:
        print(f"Generating heightmap with seed = ", seed)
        rng = np.random.default_rng(seed)
    else:       
        rng = np.random.default_rng()
    grid = np.zeros((size, size))
    print(f"size = {size}")
    
    # Init corners
    grid[0, 0] = grid[0, -1] = grid[-1, 0] = grid[-1, -1] = rng.uniform(0, 1)

    step_size = size - 1 # start big, then get smaller.
    iteration_num = 1
    while step_size > 1:
        half_step = step_size // 2
        
        # Check the biome map and then perform the diamond & square steps with the 
        # parameters for that biome
        # Diamond Step
        for x in range (0, size - 1, step_size):
            for y in range(0, size - 1, step_size):
                biome = biome_mask[x + half_step, y + half_step]
                roughness = biome_roughness.get(Biome(biome), base_roughness)
                biome_height_offset = biome_height_offsets.get(Biome(biome), base_height_offset)
                diamond_step(grid, x, y, step_size, roughness, biome_height_offset, rng)
                
        # Square step
        for x in range(0, size, half_step):
            for y in range((x + half_step) % step_size, size, step_size):
                biome = biome_mask[x % size, y % size] # use mod to stay in bounds
                roughness = biome_roughness.get(Biome(biome), base_roughness)
                biome_height_offset = biome_height_offsets.get(Biome(biome), base_height_offset)
                square_step(grid, x, y, step_size, roughness, size,  biome_height_offset, rng)
        
        # Cut the step size in half
        step_size = half_step
        iteration_num += 1
        
        # Normalize array - 
        # Ashley: I'm still looking into how normalization impacts the final outcome. 
        # min_val = np.min(grid)
        # max_val = np.max(grid)
        # grid = (grid - min_val) / (max_val - min_val)
    return grid


def diamond_step(grid, x, y, step, roughness, biome_height_offset, rng):
    # Take the average value of the 4 corners and assign it to the point in the 
    # middle of the diamond. 
    # if seed:
    #     random.seed(seed)
        
    avg = (grid[x, y] + grid[x + step, y] + grid[x, y + step] + grid[x + step, y + step]) / 4.0
    grid[x + step // 2, y + step // 2] = avg + rng.uniform(-roughness, roughness) + biome_height_offset
    
    
def square_step(grid, x, y, step, roughness, map_size, biome_height_offset, rng):
    # Take the average of the 3-4 points that point out from the point 
    # computed in the diamond step in the 4 cardinal directions. These points 
    # will be the average of all points that surround them in the 4 cardinal directions.
    # if seed:
    #     random.seed(seed)
    
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
    grid[x, y] = avg + rng.uniform(-roughness, roughness) + biome_height_offset


# Generates a heightmap using the Diamond Square algorithim
def generate_heightmap(size, roughness, seed=None):
    if seed:
        random.seed(seed)
        
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


# Smooth out the biomes to make them less blocky
def smooth_biome_transitions(biome_mask, height_map, smoothing_radius=1):
    size = biome_mask.shape[0]
    smoothed_height_map = height_map.copy() # prep the output map
    
    for y in range(size):
        for x in range(size):
            # Collect neighboring heights and biome types
            heights = []
            for dy in range(-smoothing_radius, smoothing_radius + 1):
                for dx in range(-smoothing_radius, smoothing_radius + 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < size and 0 <= nx < size:
                        if biome_mask[ny][nx] == biome_mask[y][x]:
                            heights.append(height_map[ny][nx])
            # Average height for smoothing
            if heights:
                smoothed_height_map[y][x] = sum(heights) / len(heights)
    return smoothed_height_map

def enforce_generation_rules():
    pass


# HELPER METHODS
# ================
# Unused helper
def in_bounds(grid, index):
    if (index < 0) or (index > grid.length()):
        return False
    return True
    
    
if __name__ == "__main__":
    print(f"Creating a biome mask")
    
    user_params = {'north': 'desert',
                   'south': 'mountains',
                   'southwest': 'desert',
                   'center': 'forest'}
    b_mask = create_biome_mask(MapSizes.SMALL_MAP.value, user_params)
    
    print(f"Displaying base biome mask")
    print_grid(b_mask)
    
    print("Generating heightmap")
    hm = generate_heightmap_w_biome_mask(b_mask.shape[0], b_mask)
    
    print("Displaying heightmap")
    print_grid(hm)
    
    print(f"Smoothing biome tranisitons")
    smoothed_hm = smooth_biome_transitions(b_mask, hm)
            
    print(f"Displaying final height map")
    print_grid(smoothed_hm)
    # print_grid(b_mask)