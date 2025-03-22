import pygame

def save_tilemap_to_png(tilemap, tile_size, color_mapping, filename="tilemap.png"):
    """
    Saves the given tilemap as a PNG image.

    Parameters:
    - tilemap: 2D list representing the map
    - tile_size: Pixel size of each tile
    - color_mapping: Dictionary mapping tile characters to RGB colors
    - filename: Name of the output image file
    """

    rows, cols = len(tilemap), len(tilemap[0])
    image_surface = pygame.Surface((cols * tile_size, rows * tile_size))

    for y, row in enumerate(tilemap):
        for x, tile in enumerate(row):
            color = color_mapping.get(tile, (0, 0, 0))  # Default to black if no mapping exists
            pygame.draw.rect(image_surface, color, (x * tile_size, y * tile_size, tile_size, tile_size))

    pygame.image.save(image_surface, "..\saved_world.png")
    print(f"Tilemap saved as {filename}")

# Example Usage
pygame.init()

# Sample tilemap using ASCII characters
tilemap = [
    ['~', '~', '~', '#', '#'],
    ['~', '~', '.', '.', '#'],
    ['.', '.', '.', '.', '#'],
    ['#', '#', '.', '.', '.'],
    ['#', '#', '~', '~', '~']
]

# Define ASCII to color mapping
color_mapping = {
    '~': (0, 0, 255),  # Water (blue)
    '.': (34, 139, 34),  # Grass (green)
    '#': (139, 69, 19)  # Mountain (brown)
}

# Save the tilemap
save_tilemap_to_png(tilemap, tile_size=32, color_mapping=color_mapping)

pygame.quit()
