import pygame
import sys
from world_config import MapSizes, ascii_color_map
from world_generator import WorldGenerator
from world_config import DisplayMode

# TODO: rename ascii_map to world map
def draw_tilemap(window, ascii_map, tile_size, font, display_mode, generate_image=False, filename=None):
    # TODO: Add frame.
    for y, row in enumerate(ascii_map):
        for x, tile in enumerate(row):
            
            color = ascii_color_map.get(tile.raw_symbol, (255, 255, 255)) # set color
            
            image_surface = pygame.Surface((len(ascii_map) * tile_size, len(ascii_map) * tile_size))
            
            if display_mode == DisplayMode.ASCII_MODE:
                text_surface = font.render(tile.raw_symbol, True, color)
                window.blit(text_surface, (x * tile_size, y * tile_size))
            elif display_mode == DisplayMode.PIXEL_MODE:
                # Render tile as a solid colored pixel
                pygame.draw.rect(window, color, (x * tile_size, y * tile_size, tile_size, tile_size))
            else:
                print(f"Error: Invalid map render mode provided. Receieved display_mode = {display_mode}")
                return
            
            if generate_image:
                pygame.image.save(image_surface, filename)
                generate_image = False

def save_tilemap_to_png(tilemap, tile_size, color_mapping, display_mode, filename="tilemap.png"):
    
    rows, cols = len(tilemap), len(tilemap[0])
    image_surface = pygame.Surface((cols * tile_size, rows * tile_size))

    for y, row in enumerate(tilemap):
        for x, tile in enumerate(row):
            
            if display_mode == DisplayMode.ASCII_MODE:
                pass
            elif display_mode == DisplayMode.PIXEL_MODE:
                # Render tile as a solid colored pixel
                color = color_mapping.get(tile.raw_symbol, (255, 255, 255))  # Default to black if no mapping exists
                pygame.draw.rect(image_surface, color, (x * tile_size, y * tile_size, tile_size, tile_size))
            else:
                pass

    pygame.image.save(image_surface, filename)
    print(f"Tilemap saved as {filename}")

def generate_many_worlds(num_worlds, map_size, display_mode, generate_image=True):
    '''
    Use this to generate about n = num_worlds silently without the world 
    generator displaying anything in Python.
    
    Desired I/O
    Input: - This function will ouput the number of maps provided with 
            the size and format specified.
    Output: A directory will be made (if one is not specifed) that 
            contains images of all of the worlds created and a text file that 
            labels the JSON input used for that world. 
    
    Note: Images and JSON entries will be labeled numerically.
    
    ! I might move this to an evaluation method file...
    '''
    pass

# -------


def main():

    # TODO: Handle User input
    # TODO: Pass in any settings for the map from the cmd line or future UI here.
    user_params = {'north': 'plains',
                    'northeast': 'mountains',
                    'east': 'plains',
                    'west': 'desert',
                    "northwest": 'plains',
                    "southwest": 'water',
                    'center': 'plains'}

    # Set up Pygame Display
    pygame.init()

    # Display Settings 
    tile_size = 24
    cols, rows = None, None # need to get these from the ASCII map.
    # TODO: Add size settings to the world generator (S, M, L)

    # Init World Generator & Create map
    # map_display_mode = DisplayMode.ASCII_MODE
    map_display_mode = DisplayMode.PIXEL_MODE
    generate_image = True
    # generate_image = False
    filename = "temp_filename.png"
    seed = "apples"
    map_generator = WorldGenerator(MapSizes.SMALL_MAP, user_params, display_mode=map_display_mode, seed=seed)
    ascii_map = map_generator.create_world(roughness=1)
    print(f"Type of ASCII Map: {type(ascii_map)}")

    if generate_image:
        save_tilemap_to_png(ascii_map, tile_size, ascii_color_map, display_mode=map_display_mode, filename=filename)
        
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
        draw_tilemap(window, ascii_map, tile_size, font, map_display_mode)
        pygame.display.flip()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                
    pygame.quit()
    sys.exit() 
    
# TODO: Add input parsing here.
if __name__ == "__main__":
    main()