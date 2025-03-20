from enum import Enum
from ascii_tile import water_tile, mountain_tile, plains_tile, forest_tile, pines_tile, lava_tile, snow_tile


EXTRA_SMALL_MAP = 9 # n = 3
SMALL_MAP = 17 # n = 4
MEDIUM_MAP = 33 # n = 5
LARGE_MAP = 65 # n = 6
EXTRA_LARGE_MAP = 129 # n = 7

class DisplayMode(Enum):
    ASCII_MODE = 0
    PIXEL_MODE = 1
    
class MapSizes(Enum):
    EXTRA_SMALL_MAP = 9 # n = 3
    SMALL_MAP = 17 # n = 4
    MEDIUM_MAP = 33 # n = 5
    LARGE_MAP = 65 # n = 6
    EXTRA_LARGE_MAP = 129 # n = 7

class Biome(Enum):
    WATER = 0
    DESERT = 1
    PLAINS = 2
    FOREST = 3
    TUNDRA = 4
    MOUNTAINS = 5
    
biome_dict = {
    'water': Biome.WATER,
    'desert': Biome.DESERT,
    'plains': Biome.PLAINS,
    'forest': Biome.FOREST,
    'tundra': Biome.TUNDRA,
    'mountains': Biome.MOUNTAINS,
}

# Maps string to an RBG tuple
color_dict = {"red": (169, 50, 38),
              "blue": (36, 113, 163),
              "gray": (127, 140, 141),
              "white": (255, 255, 255),
              "dark_green": (20, 90, 50),
              "grass_green": (121, 208, 29),
              "light_green": (125, 206, 160),
              "green": (34, 153, 84),
              "light_yellow": (249, 231, 159 ),
              "desert_yellow": (254, 207, 71),
              "pink": (254, 137, 236)
              }

# ascii_color_map = {
#     lava_tile: color_dict["red"],
#     water_tile: color_dict["blue"],
#     snow_tile: color_dict["white"],
#     mountain_tile: color_dict["gray"],
#     plains_tile: color_dict["light_yellow"],
#     pines_tile: color_dict["green"],
#     forest_tile: color_dict["dark_green"],
# }

# Bridge from ASCII char to an RGB tuple. I formatted it this way for readability.
ascii_color_map = {
    "l": color_dict["red"],
    "~": color_dict["blue"],
    "s": color_dict["white"],
    'M': color_dict["gray"],
    '\"': color_dict["grass_green"],
    'T': color_dict["green"],
    '8': color_dict["dark_green"],
    # '▒' : color_dict["desert_yellow"], $ not supported by consolas font
    '.' : color_dict["desert_yellow"],
    '*' : color_dict["pink"],
}
