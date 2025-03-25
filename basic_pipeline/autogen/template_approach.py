import json
import copy
import random
from typing import Dict, Any, List, Tuple

# Define a minimal but complete template
DEFAULT_TEMPLATE = {
    "world": {
        "width": 200,
        "height": 80,
        "min_river_length": 3
    },
    "screen": {
        "width": 200,
        "height": 80
    },
    "civilizations": {
        "civilized": 2,
        "tribal": 2,
        "max_sites": 20,
        "expansion_distance": 10,
        "war_distance": 8
    },
    "world_gen": {
        "main_hills": [
            {"x": 25, "y": 20, "size": 14, "height": 8},
            {"x": 50, "y": 30, "size": 15, "height": 9}
        ],
        "small_hills": [
            {"x": 10, "y": 10, "size": 3, "height": 7},
            {"x": 15, "y": 15, "size": 4, "height": 6}
        ],
        "simplex_noise": {
            "parameters": {
                "octaves": 6,
                "frequency": 6,
                "lacunarity": 32,
                "gain": 1
            }
        },
        "pole_generation": {
            "south": {
                "rng_values": [2, 3, 4, 3, 2, 3, 4, 3],
                "fixed_value": 0.31
            },
            "north": {
                "rng_values": [2, 3, 4, 3, 2, 3, 4, 3],
                "fixed_value": 0.31
            }
        },
        "tectonic": {
            "horizontal": {
                "position": 40,
                "variation": [0]
            },
            "vertical": {
                "position": 100,
                "variation": [0]
            },
            "hill_size": 3,
            "hill_height": 0.15
        },
        "erosion": {
            "coefficient": 0.07
        },
        "river": {
            "start_x": 100,
            "start_y": 10
        }
    },
    "precipitation": {
        "offset": 2,
        "noise_parameters": {
            "scale": [2, 2],
            "octaves": 32,
            "gain": 1
        }
    },
    "drainage": {
        "noise_parameters": {
            "scale": [2, 2],
            "octaves": 32,
            "gain": 1
        }
    },
    "flag_templates": {
        "background": "Background.txt",
        "overlay": "Overlay.txt",
        "background_choice": 1,
        "overlay_choice": 1,
        "back_color2_index": 1,
        "over_color1_index": 2,
        "over_color2_index": 3
    },
    "civilizations_config": {
        "civilized": {
            "name_suffix": "Civilization",
            "color": "#FF2D21",
            "race_index": 0,
            "government_index": 0,
            "initial_site_index": 0,
            "new_site_index": 0
        },
        "tribal": {
            "name_suffix": "Tribe",
            "government": {
                "name": "Tribal",
                "description": "*PLACE HOLDER*",
                "aggressiveness": 2,
                "militarization": 50,
                "tech_bonus": 0
            },
            "color": "#00FF00",
            "race_index": 0,
            "initial_site_index": 0,
            "new_site_index": 0
        }
    },
    "names": {
        "civilized": ["Alpha", "Beta"],
        "tribal": ["Gamma", "Delta"]
    }
}

def generate_template_filling_prompt(user_query: str) -> str:
    """
    Create a prompt for the LLM that focuses on extracting key parameters
    from the user query to fill in a template.
    """
    return f"""Analyze this user request about procedural world generation and extract key parameters.

USER REQUEST: "{user_query}"

Based on the request, provide values for these parameters (one per line):
- World size (width, height): 
- Number of civilized civilizations:
- Number of tribal civilizations:
- Main hills (describe locations, sizes, heights):
- River starting position:
- Precipitation level (low/medium/high):
- Erosion coefficient (0.0-1.0):
- Civilization names (comma separated):
- Tribal names (comma separated):
- Civilized aggression level (1-10):
- Tribal aggression level (1-10):
- War distance threshold:

Only provide the values, not the parameter names. Be concise and focused.
"""

def query_ollama_for_parameters(prompt: str, model: str = "mistral") -> str:
    """
    Query Ollama with a parameters-focused prompt that is easier for the LLM to handle.
    """
    import requests
    
    try:
        # Ollama API endpoint
        url = "http://localhost:11434/api/generate"
        
        # Prepare the request payload
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 1000
            }
        }
        
        # Send the request
        response = requests.post(url, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return f"Error: Received status code {response.status_code} from Ollama API"
    except Exception as e:
        return f"Error querying Ollama: {str(e)}"

def parse_parameters(param_text: str) -> Dict[str, Any]:
    """
    Parse the LLM's parameter response into a structured dictionary.
    """
    lines = param_text.strip().split('\n')
    params = {}
    
    if len(lines) >= 12:  # We expect at least 12 parameters
        # Parse world size
        try:
            world_size = lines[0].strip()
            if "x" in world_size:
                width, height = map(int, world_size.split('x'))
            else:
                parts = world_size.split(',')
                width = int(parts[0].strip())
                height = int(parts[1].strip()) if len(parts) > 1 else width
            params["world_width"] = width
            params["world_height"] = height
        except:
            params["world_width"] = 200
            params["world_height"] = 80
            
        # Parse civilizations
        try:
            params["civilized_count"] = int(lines[1].strip())
        except:
            params["civilized_count"] = 2
            
        try:
            params["tribal_count"] = int(lines[2].strip())
        except:
            params["tribal_count"] = 2
            
        # Parse hills (complex, just extract description)
        params["hills_description"] = lines[3].strip()
        
        # Parse river start
        try:
            river_pos = lines[4].strip()
            if "," in river_pos:
                x, y = map(int, river_pos.split(','))
            else:
                parts = river_pos.split()
                x = int(parts[0].strip())
                y = int(parts[1].strip()) if len(parts) > 1 else 10
            params["river_start_x"] = x
            params["river_start_y"] = y
        except:
            params["river_start_x"] = 100
            params["river_start_y"] = 10
            
        # Parse precipitation
        precip = lines[5].lower().strip()
        if "high" in precip:
            params["precipitation"] = 3.0
        elif "low" in precip:
            params["precipitation"] = 1.0
        else:
            params["precipitation"] = 2.0
            
        # Parse erosion
        try:
            params["erosion"] = float(lines[6].strip())
        except:
            params["erosion"] = 0.07
            
        # Parse civilization names
        try:
            civ_names = [name.strip() for name in lines[7].split(',')]
            params["civ_names"] = civ_names if civ_names and civ_names[0] else ["Alpha", "Beta"]
        except:
            params["civ_names"] = ["Alpha", "Beta"]
            
        # Parse tribal names
        try:
            tribal_names = [name.strip() for name in lines[8].split(',')]
            params["tribal_names"] = tribal_names if tribal_names and tribal_names[0] else ["Gamma", "Delta"]
        except:
            params["tribal_names"] = ["Gamma", "Delta"]
            
        # Parse aggression levels
        try:
            params["civ_aggression"] = int(lines[9].strip())
        except:
            params["civ_aggression"] = 3
            
        try:
            params["tribal_aggression"] = int(lines[10].strip())
        except:
            params["tribal_aggression"] = 5
            
        # Parse war distance
        try:
            params["war_distance"] = int(lines[11].strip())
        except:
            params["war_distance"] = 8
    
    return params

def generate_hills_from_description(description: str, world_width: int, world_height: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generate hill configurations based on a text description.
    """
    main_hills = []
    small_hills = []
    
    # Default configurations
    if "mountain" in description.lower():
        # More and larger mountains
        main_hills = [
            {"x": world_width // 4, "y": world_height // 3, "size": 18, "height": 9.5},
            {"x": world_width // 2, "y": world_height // 4, "size": 20, "height": 10},
            {"x": 3 * world_width // 4, "y": world_height // 2, "size": 16, "height": 9}
        ]
        small_hills = [
            {"x": world_width // 6, "y": world_height // 2, "size": 5, "height": 8},
            {"x": world_width // 3, "y": 2 * world_height // 3, "size": 6, "height": 7},
            {"x": 2 * world_width // 3, "y": world_height // 6, "size": 4, "height": 7.5},
            {"x": 5 * world_width // 6, "y": 3 * world_height // 4, "size": 5, "height": 7.2}
        ]
    elif "flat" in description.lower():
        # Fewer and smaller hills
        main_hills = [
            {"x": world_width // 3, "y": world_height // 4, "size": 10, "height": 6},
            {"x": 2 * world_width // 3, "y": 3 * world_height // 4, "size": 8, "height": 5}
        ]
        small_hills = [
            {"x": world_width // 5, "y": world_height // 2, "size": 2, "height": 4},
            {"x": 4 * world_width // 5, "y": world_height // 3, "size": 3, "height": 3.5}
        ]
    elif "island" in description.lower():
        # Scattered smaller hills for islands
        main_hills = [
            {"x": world_width // 4, "y": world_height // 4, "size": 12, "height": 7},
            {"x": 3 * world_width // 4, "y": world_height // 4, "size": 10, "height": 6.5},
            {"x": world_width // 4, "y": 3 * world_height // 4, "size": 11, "height": 6.8},
            {"x": 3 * world_width // 4, "y": 3 * world_height // 4, "size": 13, "height": 7.2}
        ]
        small_hills = [
            {"x": world_width // 2, "y": world_height // 2, "size": 8, "height": 5.5},
            {"x": world_width // 6, "y": world_height // 2, "size": 4, "height": 4.8},
            {"x": 5 * world_width // 6, "y": world_height // 2, "size": 5, "height": 5},
            {"x": world_width // 2, "y": world_height // 6, "size": 3, "height": 4.5},
            {"x": world_width // 2, "y": 5 * world_height // 6, "size": 4, "height": 4.7}
        ]
    elif "continent" in description.lower():
        # One large central continent
        main_hills = [
            {"x": world_width // 2, "y": world_height // 2, "size": 25, "height": 9},
            {"x": world_width // 2 - 15, "y": world_height // 2 - 10, "size": 18, "height": 8.5},
            {"x": world_width // 2 + 15, "y": world_height // 2 + 10, "size": 19, "height": 8.7}
        ]
        small_hills = [
            {"x": world_width // 2 - 25, "y": world_height // 2, "size": 5, "height": 7},
            {"x": world_width // 2 + 25, "y": world_height // 2, "size": 6, "height": 7.2},
            {"x": world_width // 2, "y": world_height // 2 - 20, "size": 7, "height": 7.5},
            {"x": world_width // 2, "y": world_height // 2 + 20, "size": 8, "height": 7.8}
        ]
    elif "archipelago" in description.lower():
        # Many small islands
        main_hills = []
        small_hills = []
        
        # Create 8-12 small islands
        num_islands = random.randint(8, 12)
        for i in range(num_islands):
            x = random.randint(world_width // 10, 9 * world_width // 10)
            y = random.randint(world_height // 10, 9 * world_height // 10)
            size = random.randint(5, 10)
            height = 5.0 + random.random() * 3.0
            
            if size > 7:  # Larger islands go to main hills
                main_hills.append({"x": x, "y": y, "size": size, "height": height})
            else:  # Smaller islands go to small hills
                small_hills.append({"x": x, "y": y, "size": size, "height": height})
        
        # Ensure we have at least one main hill and one small hill
        if not main_hills:
            main_hills.append({"x": world_width // 2, "y": world_height // 2, "size": 10, "height": 8})
        if not small_hills:
            small_hills.append({"x": world_width // 3, "y": world_height // 3, "size": 5, "height": 6})
    else:
        # Default, balanced hill generation
        main_hills = [
            {"x": world_width // 4, "y": world_height // 3, "size": 14, "height": 8},
            {"x": 2 * world_width // 3, "y": world_height // 2, "size": 15, "height": 9}
        ]
        small_hills = [
            {"x": world_width // 6, "y": world_height // 6, "size": 3, "height": 7},
            {"x": 5 * world_width // 6, "y": 5 * world_height // 6, "size": 4, "height": 6},
            {"x": 4 * world_width // 6, "y": 2 * world_height // 6, "size": 5, "height": 6.5}
        ]
    
    return main_hills, small_hills

def customize_template(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Customize the template based on the extracted parameters.
    """
    config = copy.deepcopy(DEFAULT_TEMPLATE)
    
    # Apply world size
    if "world_width" in params:
        config["world"]["width"] = params["world_width"]
        config["screen"]["width"] = params["world_width"]
    
    if "world_height" in params:
        config["world"]["height"] = params["world_height"]
        config["screen"]["height"] = params["world_height"]
    
    # Apply civilization counts
    if "civilized_count" in params:
        config["civilizations"]["civilized"] = params["civilized_count"]
    
    if "tribal_count" in params:
        config["civilizations"]["tribal"] = params["tribal_count"]
    
    # Generate hills based on description
    if "hills_description" in params:
        main_hills, small_hills = generate_hills_from_description(
            params["hills_description"], 
            config["world"]["width"], 
            config["world"]["height"]
        )
        config["world_gen"]["main_hills"] = main_hills
        config["world_gen"]["small_hills"] = small_hills
    
    # Apply river starting position
    if "river_start_x" in params:
        config["world_gen"]["river"]["start_x"] = params["river_start_x"]
    
    if "river_start_y" in params:
        config["world_gen"]["river"]["start_y"] = params["river_start_y"]
    
    # Apply precipitation
    if "precipitation" in params:
        config["precipitation"]["offset"] = params["precipitation"]
    
    # Apply erosion
    if "erosion" in params:
        config["world_gen"]["erosion"]["coefficient"] = params["erosion"]
    
    # Apply civilization names
    if "civ_names" in params and len(params["civ_names"]) > 0:
        # Ensure we have enough names for the civilization count
        civ_names = params["civ_names"]
        while len(civ_names) < config["civilizations"]["civilized"]:
            civ_names.append(f"Civ{len(civ_names)+1}")
        config["names"]["civilized"] = civ_names[:config["civilizations"]["civilized"]]
    
    # Apply tribal names
    if "tribal_names" in params and len(params["tribal_names"]) > 0:
        # Ensure we have enough names for the tribal count
        tribal_names = params["tribal_names"]
        while len(tribal_names) < config["civilizations"]["tribal"]:
            tribal_names.append(f"Tribe{len(tribal_names)+1}")
        config["names"]["tribal"] = tribal_names[:config["civilizations"]["tribal"]]
    
    # Apply aggression levels
    if "civ_aggression" in params:
        # Convert 1-10 scale to appropriate values for the government
        aggression = params["civ_aggression"]
        config["civilizations_config"]["civilized"]["government_index"] = min(aggression // 3, 3)
    
    if "tribal_aggression" in params:
        # Convert 1-10 scale to appropriate values
        aggression = params["tribal_aggression"]
        config["civilizations_config"]["tribal"]["government"]["aggressiveness"] = min(aggression // 2, 5)
        config["civilizations_config"]["tribal"]["government"]["militarization"] = min(40 + aggression * 5, 90)
    
    # Apply war distance
    if "war_distance" in params:
        config["civilizations"]["war_distance"] = params["war_distance"]
        
    # Add some variation to colors based on parameters
    # Different civilization colors based on aggression level
    if "civ_aggression" in params:
        aggression = params["civ_aggression"]
        if aggression > 7:
            config["civilizations_config"]["civilized"]["color"] = "#FF0000"  # Bright red for aggressive
        elif aggression > 4:
            config["civilizations_config"]["civilized"]["color"] = "#8B0000"  # Dark red for moderate
        else:
            config["civilizations_config"]["civilized"]["color"] = "#0000FF"  # Blue for peaceful
    
    if "tribal_aggression" in params:
        aggression = params["tribal_aggression"]
        if aggression > 7:
            config["civilizations_config"]["tribal"]["color"] = "#8B4513"  # Brown for aggressive
        elif aggression > 4:
            config["civilizations_config"]["tribal"]["color"] = "#006400"  # Dark green for moderate
        else:
            config["civilizations_config"]["tribal"]["color"] = "#00FF00"  # Bright green for peaceful
    
    # Apply special customizations based on keywords in the hill description
    hills_desc = params.get("hills_description", "").lower()
    
    # Desert world
    if "desert" in hills_desc:
        config["precipitation"]["offset"] = 1.0
        config["world_gen"]["erosion"]["coefficient"] = 0.09
        
    # Ocean world
    if "ocean" in hills_desc or "sea" in hills_desc:
        # Reduce the height of hills to create more ocean
        for hill in config["world_gen"]["main_hills"]:
            hill["height"] *= 0.8
        for hill in config["world_gen"]["small_hills"]:
            hill["height"] *= 0.8
            
    # Mountain world
    if "mountain" in hills_desc and "range" in hills_desc:
        # Create a more dramatic tectonic border
        config["world_gen"]["tectonic"]["hill_size"] = 5
        config["world_gen"]["tectonic"]["hill_height"] = 0.25
    
    return config

def generate_template_based_config(user_query: str, model: str = "mistral") -> Dict[str, Any]:
    """
    Generate a configuration using the template-based approach.
    """
    # Generate the parameters prompt
    prompt = generate_template_filling_prompt(user_query)
    
    # Query Ollama for parameters
    param_text = query_ollama_for_parameters(prompt, model)
    
    # Parse the parameters
    params = parse_parameters(param_text)
    
    # Customize the template
    return customize_template(params)

if __name__ == "__main__":
    # Test the template approach with a sample query
    test_query = "Create a world with a large mountain range and 3 peaceful civilizations"
    config = generate_template_based_config(test_query)
    print(json.dumps(config, indent=2))