import pygame
import sys
from world_config import MapSizes, color_dict, ascii_color_map

from world_generator import WorldGenerator
from world_config import DisplayMode

def draw_tilemap(window, ascii_map, display_mode=DisplayMode.ASCII_MODE):
    # TODO: Add frame.
    for y, row in enumerate(ascii_map):
        for x, tile in enumerate(row):
            
            # Set color (colors stored in color_dict)
            # print(tile.symbol, end="")
            # color = ascii_color_map.get(tile, (255, 255, 255)) # If we fail to get something, default to white
            symbol = tile.raw_symbol
            color = ascii_color_map.get(symbol, (255, 255, 255)) # If we fail to get something, default to white
            
            # Render symbol
            text_surface = font.render(tile.raw_symbol, True, color)
            window.blit(text_surface, (x * tile_size, y * tile_size))
            # color = color_map.get(tile.raw_symbol)
            # pygame.draw.rect(window, color, (x * tile_size, y * tile_size, tile_size, tile_size))

# TODO: Handle User input
# TODO: Pass in any settings for the map from the cmd line or future UI here.
user_params = {'north': 'desert',
                'south': 'mountains',
                'center': 'forest'}
# user_params = {'north': 'water',
#                 'south': 'mountains',
#                 'center': 'water'}

# Init World Generator & Create map
map_generator = WorldGenerator(MapSizes.EXTRA_SMALL_MAP, user_params)
ascii_map = map_generator.create_world(roughness=1)

# Set up Pygame Display
pygame.init()

# Display Settings 
tile_size = 24
cols, rows = None, None # need to get these from the ASCII map.
# TODO: Add size settings to the world generator (S, M, L)

# Font Settings (Use a monospaced font)
font_size = 16
font = pygame.font.SysFont('Consolas', 30)

window_width = tile_size * map_generator.map_size + 1
window_height = tile_size * map_generator.map_size + 1
window = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
pygame.display.set_caption('ASCII World Generator')

# Remember: Not using fill will cause the game to write 
# frames on top of old ones. Not a desirable effect. 
# Is there a better way to manage colors in PyGame?
background_color = (0, 0, 0)
window.fill(background_color)

# Game Loop, running kicks off the loop and sustains it until QUIT event.
running = True
while running:
    window.fill((0,0,0))
    draw_tilemap(window, ascii_map)
    pygame.display.flip() # update display
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit() 
    
