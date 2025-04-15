# ANSI COLOR CODES FOR DISPLAY (may move these to a Colors class later on for modularity)
ANSI_RESET = "\033[0m"
ANSI_YELLOW = "\033[33m"
ANSI_GREEN = "\033[32m"
ANSI_BLUE = "\033[34m"
ANSI_RED = "\033[31m"
ANSI_WHITE = "\033[97m"
ANSI_MAGENTA = "\033[35m"
ANSI_CYAN = "\033[36m"
ANSI_GRAY = "\033[90m"

class ASCIITile:
    def __init__(self, symbol: str, color: str = ANSI_RESET, colored: bool = True):
        self.raw_symbol = symbol
        self.symbol = None
        if colored:
            self.symbol = f"{color}{symbol}{ANSI_RESET}"

# TODO: Store the tiles below in a dict that can be imported.      
default_tiles = {}

plains_tile = ASCIITile("\"", ANSI_YELLOW)
# desert_tile = ASCIITile("▒", ANSI_YELLOW)
desert_tile = ASCIITile(".", ANSI_YELLOW)
forest_tile = ASCIITile("8", ANSI_GREEN)
pines_tile = ASCIITile("T", ANSI_GREEN)
mountain_tile = ASCIITile("M", ANSI_GRAY)
snow_tile = ASCIITile("s", ANSI_WHITE)
lava_tile = ASCIITile("l", ANSI_RED)
water_tile = ASCIITile("~", ANSI_CYAN)

# note, it would be nice to have flowers be a set of random colors. 
flower_tile = ASCIITile("*", ANSI_MAGENTA) 
        