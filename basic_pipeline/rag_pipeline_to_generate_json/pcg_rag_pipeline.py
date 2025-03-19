import os
import json
import requests
import textwrap
import argparse
from typing import Dict, Any, List

# PCG Pipeline Context
PCG_CONTEXT = """
The PCG (Procedural Content Generation) pipeline in this code generates fantasy worlds with detailed terrain, biomes, 
civilizations, and simulates their growth over time. Here's how the components work:

WORLD GENERATION:
- Creates heightmaps using hill placement and noise algorithms
- Generates poles at world edges
- Applies tectonic features to create mountain ranges
- Uses erosion to make terrain more realistic
- Calculates temperature based on latitude and height
- Determines precipitation and drainage patterns
- Creates rivers that flow downhill

BIOME DETERMINATION:
- Biomes are assigned based on height, temperature, precipitation, and drainage
- Examples include forests, deserts, plains, tundra, mountains, and oceans
- Each biome has a unique ID, visual representation, and properties

CIVILIZATION CREATION:
- Reads race definitions from file with traits like preferred biomes
- Civilizations are divided into "civilized" and "tribal" types
- Each civilization has:
  * A race with inherent traits
  * A government type affecting aggression and development
  * A unique color and flag
  * Population centers that grow over time
  * Strategic expansion to new suitable territories

SIMULATION:
- Population grows based on reproduction rates and prosperity
- New settlements are founded when populations reach capacity
- Wars break out between civilizations that get too close
- Armies move and engage based on a simplified military model

VISUALIZATION:
- Multiple map views (terrain, height, temperature, precipitation, etc.)
- Characters and colors represent different biomes and features
- Civilizations and their territories are displayed on the map

The configuration JSON controls all these aspects, from world size to civilization behaviors.
"""

# Simplified JSON schema reference
JSON_SCHEMA = """
{
  "world": {
    "width": int,            // World width in tiles
    "height": int,           // World height in tiles
    "min_river_length": int  // Minimum length for rivers to be generated
  },
  "screen": {
    "width": int,            // Display window width
    "height": int            // Display window height
  },
  "civilizations": {
    "civilized": int,        // Number of advanced civilizations
    "tribal": int,           // Number of tribal civilizations
    "max_sites": int,        // Maximum settlements per civilization
    "expansion_distance": int, // Distance threshold for expansion
    "war_distance": int      // Distance threshold for triggering wars
  },
  "world_gen": {
    "main_hills": [          // Major terrain features
      { "x": int, "y": int, "size": int, "height": float }
    ],
    "small_hills": [         // Minor terrain features
      { "x": int, "y": int, "size": int, "height": float }
    ],
    "simplex_noise": {       // Noise parameters for terrain generation
      "parameters": {
        "octaves": int,      // Detail levels in the noise
        "frequency": int,    // Base frequency of the noise
        "lacunarity": int,   // How frequency increases per octave
        "gain": float        // How amplitude changes per octave
      }
    },
    "pole_generation": {     // Controls ice caps at world edges
      "south": {
        "rng_values": [int], // Pattern for pole edge variation
        "fixed_value": float // Height value for pole areas
      },
      "north": {
        "rng_values": [int],
        "fixed_value": float
      }
    },
    "tectonic": {            // Controls mountain range creation
      "horizontal": {
        "position": int,     // Y position of horizontal mountain range
        "variation": [int]   // Variation pattern for the range
      },
      "vertical": {
        "position": int,     // X position of vertical mountain range
        "variation": [int]
      },
      "hill_size": int,      // Size of hills along tectonic borders
      "hill_height": float   // Height of hills along tectonic borders
    },
    "erosion": {
      "coefficient": float   // Strength of the erosion effect
    },
    "river": {
      "start_x": int,        // X coordinate for river start
      "start_y": int         // Y coordinate for river start
    }
  },
  "precipitation": {
    "offset": float,         // Base precipitation value
    "noise_parameters": {    // Noise parameters for precipitation map
      "scale": [float, float],
      "octaves": int,
      "gain": float
    }
  },
  "drainage": {
    "noise_parameters": {    // Noise parameters for drainage map
      "scale": [float, float],
      "octaves": int,
      "gain": float
    }
  },
  "flag_templates": {        // Controls civilization flag generation
    "background": string,    // Filename for background patterns
    "overlay": string,       // Filename for overlay patterns
    "background_choice": int,
    "overlay_choice": int,
    "back_color2_index": int,
    "over_color1_index": int,
    "over_color2_index": int
  },
  "civilizations_config": {
    "civilized": {
      "name_suffix": string, // Added to civilization names
      "color": string,       // Hex color code
      "race_index": int,     // Index into Races array
      "government_index": int,
      "initial_site_index": int,
      "new_site_index": int
    },
    "tribal": {
      "name_suffix": string,
      "government": {
        "name": string,
        "description": string,
        "aggressiveness": int,
        "militarization": int,
        "tech_bonus": int
      },
      "color": string,
      "race_index": int,
      "initial_site_index": int,
      "new_site_index": int
    }
  },
  "names": {
    "civilized": [string],   // Civilization name pool
    "tribal": [string]       // Tribal name pool
  }
}
"""

# Sample configuration to show structure
SAMPLE_CONFIG = {
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
      { "x": 25, "y": 20, "size": 14, "height": 8 },
      { "x": 50, "y": 30, "size": 15, "height": 9 }
    ],
    "small_hills": [
      { "x": 10, "y": 10, "size": 3, "height": 7 },
      { "x": 15, "y": 15, "size": 4, "height": 6 }
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

def generate_prompt(user_query: str) -> str:
    """
    Create a prompt for the LLM that includes context about the PCG pipeline
    and the user's query.
    """
    return f"""You are an expert on procedural world generation for fantasy games.
    
CONTEXT ABOUT THE PCG PIPELINE:
{PCG_CONTEXT}

JSON SCHEMA REFERENCE:
{JSON_SCHEMA}

SAMPLE CONFIG:
```json
{json.dumps(SAMPLE_CONFIG, indent=2)}
```

USER REQUEST:
{user_query}

Your task is to create a valid JSON configuration based on the user's request.
The configuration should follow the schema shown above and be compatible with the PCG system.
Be creative but make realistic choices based on the described PCG pipeline.
Return ONLY the JSON configuration with no additional text. The output should be valid JSON.
"""

def query_ollama(prompt: str, model: str = "mistral") -> str:
    """
    Send the prompt to a locally running Ollama instance with the Mistral model.
    """
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
                "num_predict": 2000
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

def validate_json(json_str: str) -> Dict[str, Any]:
    """
    Validate that the returned string is valid JSON.
    """
    try:
        # Try to parse the JSON
        result = json.loads(json_str)
        return result
    except json.JSONDecodeError as e:
        print(f"Invalid JSON returned from LLM: {e}")
        # Try to extract JSON if it's wrapped in markdown code blocks
        if "```json" in json_str and "```" in json_str:
            try:
                json_content = json_str.split("```json")[1].split("```")[0].strip()
                return json.loads(json_content)
            except (IndexError, json.JSONDecodeError):
                pass
        raise ValueError("Could not parse JSON from LLM response")

def process_user_request(user_query: str, model: str = "mistral") -> Dict[str, Any]:
    """
    Process a user request and return a generated configuration.
    """
    # Generate the prompt
    prompt = generate_prompt(user_query)
    
    # Query the Ollama LLM
    llm_response = query_ollama(prompt, model)
    
    # Validate and return the JSON
    return validate_json(llm_response)

def save_config(config: Dict[str, Any], filename: str = "generated_config.json") -> str:
    """
    Save the generated configuration to a file.
    """
    with open(filename, 'w') as f:
        json.dump(config, f, indent=2)
    return filename

def main():
    """
    Main function to process command-line arguments and run the pipeline.
    """
    parser = argparse.ArgumentParser(description="Generate PCG configurations from natural language prompts")
    parser.add_argument("prompt", nargs="?", default="", help="The natural language prompt describing the desired world")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--output", "-o", default="generated_config.json", help="Output filename")
    parser.add_argument("--model", "-m", default="mistral", help="Ollama model to use (default: mistral)")
    
    args = parser.parse_args()
    
    if args.interactive:
        print("PCG Configuration Generator (Using Ollama)")
        print("=========================================")
        print(f"Using model: {args.model}")
        print("Enter your world description prompt, or 'quit' to exit.")
        
        while True:
            prompt = input("\nPrompt> ")
            if prompt.lower() in ("quit", "exit", "q"):
                break
                
            try:
                print(f"Generating configuration with {args.model}...")
                config = process_user_request(prompt, args.model)
                filename = save_config(config, args.output)
                print(f"Configuration saved to {filename}")
                print("\nGenerated configuration:")
                print(json.dumps(config, indent=2))
            except Exception as e:
                print(f"Error: {str(e)}")
    
    elif args.prompt:
        try:
            print(f"Generating configuration with {args.model}...")
            config = process_user_request(args.prompt, args.model)
            filename = save_config(config, args.output)
            print(f"Configuration saved to {filename}")
            print("\nGenerated configuration:")
            print(json.dumps(config, indent=2))
        except Exception as e:
            print(f"Error: {str(e)}")
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()