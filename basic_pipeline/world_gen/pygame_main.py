import pygame
import sys
from world_config import MapSizes, color_dict, ascii_color_map

from world_generator import WorldGenerator
from world_config import DisplayMode

def draw_tilemap(window, ascii_map, display_mode):
    # TODO: Add frame.
    for y, row in enumerate(ascii_map):
        for x, tile in enumerate(row):
            
            # Set color (colors stored in color_dict)
            # print(tile.symbol, end="")
            # color = ascii_color_map.get(tile, (255, 255, 255)) # If we fail to get something, default to white
            color = ascii_color_map.get(tile.raw_symbol, (255, 255, 255))
            if display_mode == DisplayMode.ASCII_MODE:
                # print("Rendeing world as an ASCII tile map.")
                text_surface = font.render(tile.raw_symbol, True, color)
                window.blit(text_surface, (x * tile_size, y * tile_size))
            elif display_mode == DisplayMode.PIXEL_MODE:
                # Render tile as a solid colored pixel
                pygame.draw.rect(window, color, (x * tile_size, y * tile_size, tile_size, tile_size))
            else:
                print(f"Error: Invalid map render mode provided. Receieved display_mode = {display_mode}")

# TODO: Handle User input
# TODO: Pass in any settings for the map from the cmd line or future UI here.
# user_params = {'north': 'desert',
#                 'south': 'mountains',
#                 'center': 'forest'}
# user_params = {'north': 'water',
#                 'south': 'mountains',
#                 'center': 'water'}

# island
user_params = {'north': 'plains',
                'northeast': 'mountains',
                'east': 'plains',
                'west': 'desert',
                "northwest": 'plains',
                "southwest": 'water',
                'center': 'plains'}
# user_params = {'north': 'water',
#                 'south': 'water',
#                 'east': 'water',
#                 'west': 'water',
#                 'center': 'mountains'}

# Init World Generator & Create map
map_display_mode = DisplayMode.PIXEL_MODE
seed = "apples"
map_generator = WorldGenerator(MapSizes.SMALL_MAP, user_params, display_mode=map_display_mode, seed=seed)
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
    draw_tilemap(window, ascii_map, map_display_mode)
    pygame.display.flip() # update display
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit() 
    
