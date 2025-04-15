import argparse
import json
import logging
import openai
import os
import pygame
import sys

from dotenv import load_dotenv
from map_renderer import draw_tilemap
from world_config import MapSizes, ascii_color_map
from world_generator import WorldGenerator
from world_config import DisplayMode

# Saves the generated world as an img file.
def save_tilemap_to_png(tilemap, tile_size, color_mapping, display_mode, filename="tilemap.png"):
    print("Writing map out to: ", filename)
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
    print(f"Map write to {filename} completed successfully.")

# Saves the generated world as a text file.
def save_tilemap_to_txt(world_map, filename="generated_map.txt"):
    print("Writing map out to: ", filename)
    
    # ! Note each tile in the map is an ASCIITile object.
    with open(filename, 'w') as file:
        for row in world_map:
            s = " ".join(tile.raw_symbol for tile in row)
            file.write(s+'\n')
    print(f"Map write to {filename} completed successfully.")

def load_json_config(json_file):
    '''_summary_

    Args:
        json_file (_type_): _description_

    Returns:
        _type_: _description_
    '''
    try:
        with open(json_file, 'r') as f:
            config = json.load(f)
        print(f"Loaded JSON config from {json_file}")
        return config
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None

def extract_world_data(prompt):
    '''_summary_

    Args:
        prompt (_type_): _description_

    Returns:
        _type_: _description_
    '''
    
    load_dotenv(dotenv_path="../api/.env")
    api_key = os.getenv("OPENAI_API_KEY")
    print(api_key)
    
    # Define the system instruction explicitly asking for JSON output
    system_message = (
        "You are an AI assistant that extracts world generation parameters from natural language prompts and returns them as a JSON object.\n"
        "Ensure the response is a valid JSON object with the following fields:\n"
        "- 'biomes': a dictionary mapping 'north', 'south', 'east', 'west', 'northeast', 'southeast', 'northwest', 'southwest' and 'center' to biomes ('water', 'desert', 'plains', 'forest', 'mountains').\n"
        "- 'temperature': a dictionary mapping regions to temperature descriptions.\n"
        "- 'precipitation': a dictionary mapping regions to precipitation descriptions.\n"
        "- 'seed': an optional alphanumeric string if the user specifies one.\n"
        "- 'map_size': one of ['extra small', 'small', 'medium', 'large', 'extra large'] if specified.\n"
        "The default value for biomes, temperature and preceptiation are 'plains', 'temperate' and 'medium' respectively."
        "If a feature in the north or south are specified without mention of features in corner regions, then the corner regions should also take on the feature for the north or south."
        "Do not include any text outside of the JSON object."
    )

    try:
        client = openai.OpenAI(api_key=api_key)  # Instantiate OpenAI client

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            #  response_format={"type": "json"}
        )

        extracted_data = response.choices[0].message.content.strip()  # Get response text
        return json.loads(extracted_data)  # Convert to JSON
    except Exception as e:
        return {"error": str(e)}


def main():
    
    # Surpress pygame welcome messages
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    
    # Handle command line args.
    parser = argparse.ArgumentParser(description="Extract world parameters from a prompt recieved as a string or from a text file.")
    parser.add_argument("--prompt", "-p", type=str, help="Directly provide the prompt as a string.")
    parser.add_argument("--file", "-f", type=str, help="Path of the text file containing the prompt.")
    parser.add_argument("--debug", '-d', action='store_true', help="Toggles debug mode.")
    parser.add_argument("--quiet", '-q', action='store_true', help="Mutes all non-critical outputs.")
    parser.add_argument("--seed", '-s', type=int, help="Specifies the world generator seed.")
    parser.add_argument("-m", "--mode", choices=["ascii", "pixel", "a", "p"], default="ascii", 
                    help="Choose display mode: 'ascii' or 'pixel' (default: 'ascii').") 
    parser.add_argument("--text", '-t', type=str, help="Outputs the text block containing the ASCII map")
    # Not yet functional below this line.
    parser.add_argument("--image", "--img", "-i", type=str, metavar="DIR", 
                    help="Specify a directory where the image should be saved. If omitted, no image is saved.")
    parser.add_argument("--verbose", '-v', action='store_true', help="Toggles verbose output mode.")
    args = parser.parse_args()

    # TODO: Add input handling for when the promp comes from a file.
    user_prompt = None
    if args.file:
        with open(args.file, "r") as f:
            user_prompt = f.read().strip()
    elif args.prompt:
        user_prompt = args.prompt
        
    if args.prompt is None:
        print("Error: No prompt provided. Terminating program.")
        return
    
    print("\033[38;2;64;244;208m ProcPainter - A World Generator\033[0m")
    print("\033[38;2;64;244;208m=================================\033[0m")
    
    if args.quiet == True:
        silent = True
    else:
        silent = False
        
    print("Processing user prompt: ", user_prompt)
    world_data = extract_world_data(user_prompt)
    print("User prompt proccessed successfully!")
    print(world_data)
    
    # world_data = load_json_config("config.json")    
    if args.mode == "pixel" or args.mode == "p":
        print("Map will be displayed in PIXEL mode")
        map_display_mode = DisplayMode.PIXEL_MODE
    else:
        print("Map will be displayed in ASCII mode")
        map_display_mode = DisplayMode.ASCII_MODE
    
    
    # TODO: Update this so the args object is used directly to determine if the export methods get called.
    generate_text_file = False
    print("text args: ", args.text)
    if args.text:
        generate_text_file = True    
        
    generate_image = False
    if args.image:
        generate_image = True
    
    # If there is one, grab and pass on an INTEGER seed from the JSON
    # to the world generator
    wg_seed = None # world generator seed
    try: 
        if world_data["seed"] and int(world_data["seed"]):
            wg_seed = int(world_data["seed"])
    except(KeyError): 
        print("ERROR: Seed not specified or invalid in the provided JSON input.")
        print("World will be generated WITHOUT a seed.")
        wg_seed = None
    except(ValueError):
        print("ERROR: Seed is not a valid data type. Please provide an integer.")
        print("World will be generated WITHOUT a seed.")
        
    # Init World Generator & Create map
    tile_size = 24
    map_generator = WorldGenerator(MapSizes.SMALL_MAP, world_data["biomes"], display_mode=map_display_mode, seed=wg_seed)
    # map_generator = WorldGenerator(MapSizes.MEDIUM_MAP, user_params, display_mode=map_display_mode, seed=seed)
    world_map = map_generator.create_world(roughness=1)
    
    # Export map as image or text based on what the user specified
    if generate_image:
        save_tilemap_to_png(world_map, tile_size, ascii_color_map, display_mode=map_display_mode, filename=args.image)
        
    if generate_text_file:
        save_tilemap_to_txt(world_map, filename=args.text)
        
    if silent == False:
        # Set up Pygame Display
        pygame.init()

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
            draw_tilemap(window, world_map, tile_size, font, map_display_mode)
            pygame.display.flip()
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                    
        pygame.quit()
        sys.exit() 
    
    
# TODO: Add input parsing here.
if __name__ == "__main__":
    main()
    
    