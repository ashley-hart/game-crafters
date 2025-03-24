from opensimplex import OpenSimplex
import numpy as np
import random

def generate_perlin_map(rows, cols, scale=10):
    """Generates an ASCII world using Perlin noise for biome placement."""
    grid = np.full((rows, cols), ".", dtype=str)
    noise = OpenSimplex(seed=random.randint(0, 10000))  # Randomized seed

    # Generate Perlin noise-based terrain
    for r in range(rows):
        for c in range(cols):
            value = noise.noise2(r / scale, c / scale)  # Get noise value
            if value < -0.2:
                grid[r, c] = "~"  # Water
            elif value < 0.2:
                grid[r, c] = "."  # Grass
            elif value < 0.5:
                grid[r, c] = "*"  # Forest
            else:
                grid[r, c] = "^"  # Mountain

    return grid

# Generate a 30x30 ASCII world using Perlin noise
grid = generate_perlin_map(30, 30, scale=15)

print("\nPerlin Noise-Based ASCII Map:")
print("\n".join("".join(row) for row in grid))
