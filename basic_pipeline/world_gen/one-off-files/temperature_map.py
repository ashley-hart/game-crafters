import noise
import numpy as np

def generate_temperature_map(size, scale=10.0, seed=None):
    if seed:
        np.random.seed(seed)
    
    temp_map = np.zeros((size, size))
    for y in range(size):
        for x in range(size):
            temp = noise.pnoise2(x / scale, y / scale, octaves=4, persistence=0.5, lacunarity=2.0, base=seed or 0)
            temp_map[y, x] = (temp + 1) / 2  # Normalize to [0,1]
    
    return temp_map

def print_grid(grid):
    # Print grid of floats rounded to 2 places
    if isinstance(grid, np.ndarray) and (isinstance(grid[0][0], np.float64) or isinstance(grid[0][0], np.float32)):
        for row in grid:
            print(" ".join(f"{val:.2f}" for val in row))
    # Print Biome Enum grid
    elif isinstance(grid, np.ndarray) and isinstance(grid[0][0], Biome): 
        for row in grid:
                print(" ".join(str(cell.value) for cell in row))
    # Print ints and any other data type
    else: 
        for row in grid:
                print(" ".join(cell for cell in row))
                
    print()
                

if __name__ == "__main__":
    temp_map = generate_temperature_map(10)
    print_grid(temp_map)