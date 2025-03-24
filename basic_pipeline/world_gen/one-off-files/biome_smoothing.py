import numpy as np

def smooth_biome_transitions(biome_mask, height_map, smoothing_radius=1):
    size = biome_mask.shape[0]
    smoothed_height_map = height_map.copy()
    
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

# Example usage:
biome_mask = np.array([
    ['desert', 'desert', 'grass'],
    ['desert', 'grass', 'grass'],
    ['forest', 'forest', 'grass']
])

height_map = np.array([
    [0.2, 0.3, 0.5],
    [0.3, 0.6, 0.7],
    [0.1, 0.2, 0.8]
])

smoothed_map = smooth_biome_transitions(biome_mask, height_map)
print(smoothed_map)
