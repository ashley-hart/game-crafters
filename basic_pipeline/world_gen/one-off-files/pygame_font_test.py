import pygame
import sys

# Initialize Pygame
pygame.init()

# Settings
tile_size = 32
cols, rows = 10, 10
window_width, window_height = cols * tile_size, rows * tile_size
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Colored ASCII Tilemap")

# Colors (R, G, B)
color_map = {
    "#": (0, 0, 255),    # Blue for walls
    ".": (0, 255, 0),    # Green for ground
    "~": (0, 100, 255),  # Light blue for water
}

# Sample ASCII Tilemap
tilemap = [
    ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
    ["#", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
    ["#", ".", "~", "~", ".", ".", "~", "~", ".", "#"],
    ["#", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
    ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
]

# Set up font
font = pygame.font.SysFont("Courier", tile_size)

def draw_tilemap():
    for y, row in enumerate(tilemap):
        for x, char in enumerate(row):
            color = color_map.get(char, (255, 255, 255))  # Default to white
            text_surface = font.render(char, True, color)
            window.blit(text_surface, (x * tile_size, y * tile_size))

# Main loop
running = True
while running:
    window.fill((0, 0, 0))  # Clear screen with black
    draw_tilemap()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit()
