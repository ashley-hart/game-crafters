# ANSI COLOR CODES FOR DISPLAY (may move these to a Colors class later on for modularity)
ANSI_RESET = "\033[0m"
ANSI_YELLOW = "\033[33m"
ANSI_GREEN = "\033[32m"
ANSI_BLUE = "\033[34m"
ANSI_RED = "\033[31m"
ANSI_WHITE = "\033[97m"
ANSI_MAGENTA = "\033[35m"
ANSI_CYAN = "\033[36m"

class Tile:
    def __init__(self, symbol: str, color: str = ANSI_RESET, colored: bool = True):
        if colored:
            self.symbol = f"{color}{symbol}{ANSI_RESET}"
        else:
            self.symbol = symbol
            
plains = Tile(".", ANSI_YELLOW)
forest = Tile("8", ANSI_GREEN)
pines = Tile("Y", ANSI_GREEN)
mountain = Tile("A", ANSI_WHITE)
water = Tile("~", ANSI_CYAN)
        