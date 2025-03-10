import pygame
import sys
import io
import contextlib
from ascii_tile import ASCIITile, water_tile, mountain_tile, plains_tile, forest_tile, pines_tile, lava_tile, snow_tile

from world_generator import WorldGenerator

# Maps string to an RBG tuple
color_dict = {"red": (169, 50, 38),
              "blue": (36, 113, 163),
              "gray": (127, 140, 141),
              "white": (255, 255, 255),
              "dark_green": (20, 90, 50),
              "light_green": (125, 206, 160),
              "green": (34, 153, 84),
              "light_yellow": (249, 231, 159 ),
              }

ascii_color_map = {
    lava_tile: color_dict["red"],
    water_tile: color_dict["blue"],
    snow_tile: color_dict["white"],
    mountain_tile: color_dict["gray"],
    plains_tile: color_dict["light_yellow"],
    pines_tile: color_dict["green"],
    forest_tile: color_dict["dark_green"],
}

SMALL_MAP = 17 # n = 4
MEDIUM_MAP = 33 # n = 5
LARGE_MAP = 65 # n = 6

def draw_tilemap(ascii_map):
    # TODO: Add frame.
    
    for y, row in enumerate(ascii_map):
        for x, tile in enumerate(row):
            
            # Set color (colors stored in color_dict)
            # print(tile.symbol, end="")
            color = ascii_color_map.get(tile, (255, 255, 255)) # If we fail to get something, default to white
            
            # Render symbol
            text_surface = font.render(tile.raw_symbol, True, color)
            window.blit(text_surface, (x * tile_size, y * tile_size))

# Init all imported modules
pygame.init()

# Display Settings 
tile_size = 24
cols, rows = None, None # need to get these from the ASCII map.
# TODO: Add size settings to the world generator (S, M, L)

# Font Settings
font_size = 16
font = pygame.font.SysFont('Consolas', 30) # use a monospaced font
# char_width, char_height = font.size('@') # using @ since @ is usually one of the widest ASCII chats


window_width = tile_size * MEDIUM_MAP + 1
window_height = tile_size * MEDIUM_MAP + 1
window = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
pygame.display.set_caption('ASCII World Generator')

# Remember: Not using fill will cause the game to write 
# frames on top of old ones. Not a desirable effect. 
# Is there a better way to manage colors in PyGame?
background_color = (0, 0, 0)
window.fill(background_color)
# Updates the entire display.
# pygame.display.flip()

# Init & Create map
# TODO: Pass in any settings for the map from the cmd line or future UI here.
map_generator = WorldGenerator()
ascii_map = map_generator.create_world(size=MEDIUM_MAP, roughness=1)

# Game Loop, running kicks off the loop and sustains it until QUIT event.
running = True
while running:
    window.fill((0,0,0))
    draw_tilemap(ascii_map)
    pygame.display.flip()
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit() 
    
