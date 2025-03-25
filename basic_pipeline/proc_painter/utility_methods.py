import numpy as np
from world_config import Biome
   
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
                