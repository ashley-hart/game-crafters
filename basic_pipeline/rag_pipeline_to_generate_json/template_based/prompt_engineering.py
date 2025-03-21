def generate_prompt(user_query: str) -> str:
    """
    Create an improved prompt for the local LLM that includes context, explicit
    instructions on JSON formatting, and strong guardrails.
    """
    return f"""You are an expert on procedural world generation. Your task is to create a valid JSON configuration based on a user request.

IMPORTANT: Your entire response must be ONLY a valid JSON object with no additional explanation or text.

USER REQUEST:
{user_query}

INSTRUCTIONS:
1. Analyze the user request and determine what world generation settings would fulfill it
2. Produce a complete, valid JSON configuration following the schema below
3. Include ALL required fields from the sample
4. Format numbers appropriately (integers for counts, floats for decimal values)
5. Make sure all arrays have correct syntax with commas between items
6. Do not include any explanation text, only output the JSON

JSON SCHEMA:
{{
  "world": {{
    "width": int,            // World width in tiles
    "height": int,           // World height in tiles
    "min_river_length": int  // Minimum length for rivers to be generated
  }},
  "screen": {{
    "width": int,            // Display window width
    "height": int            // Display window height
  }},
  "civilizations": {{
    "civilized": int,        // Number of advanced civilizations
    "tribal": int,           // Number of tribal civilizations
    "max_sites": int,        // Maximum settlements per civilization
    "expansion_distance": int, // Distance threshold for expansion
    "war_distance": int      // Distance threshold for triggering wars
  }},
  "world_gen": {{
    "main_hills": [          // Major terrain features
      {{ "x": int, "y": int, "size": int, "height": float }}
    ],
    "small_hills": [         // Minor terrain features
      {{ "x": int, "y": int, "size": int, "height": float }}
    ],
    "simplex_noise": {{       // Noise parameters for terrain generation
      "parameters": {{
        "octaves": int,      // Detail levels in the noise
        "frequency": int,    // Base frequency of the noise
        "lacunarity": int,   // How frequency increases per octave
        "gain": float        // How amplitude changes per octave
      }}
    }},
    "pole_generation": {{     // Controls ice caps at world edges
      "south": {{
        "rng_values": [int], // Pattern for pole edge variation
        "fixed_value": float // Height value for pole areas
      }},
      "north": {{
        "rng_values": [int],
        "fixed_value": float
      }}
    }},
    "tectonic": {{            // Controls mountain range creation
      "horizontal": {{
        "position": int,     // Y position of horizontal mountain range
        "variation": [int]   // Variation pattern for the range
      }},
      "vertical": {{
        "position": int,     // X position of vertical mountain range
        "variation": [int]
      }},
      "hill_size": int,      // Size of hills along tectonic borders
      "hill_height": float   // Height of hills along tectonic borders
    }},
    "erosion": {{
      "coefficient": float   // Strength of the erosion effect
    }},
    "river": {{
      "start_x": int,        // X coordinate for river start
      "start_y": int         // Y coordinate for river start
    }}
  }},
  "precipitation": {{
    "offset": float,         // Base precipitation value
    "noise_parameters": {{    // Noise parameters for precipitation map
      "scale": [float, float],
      "octaves": int,
      "gain": float
    }}
  }},
  "drainage": {{
    "noise_parameters": {{    // Noise parameters for drainage map
      "scale": [float, float],
      "octaves": int,
      "gain": float
    }}
  }},
  "flag_templates": {{        // Controls civilization flag generation
    "background": string,    // Filename for background patterns
    "overlay": string,       // Filename for overlay patterns
    "background_choice": int,
    "overlay_choice": int,
    "back_color2_index": int,
    "over_color1_index": int,
    "over_color2_index": int
  }},
  "civilizations_config": {{
    "civilized": {{
      "name_suffix": string, // Added to civilization names
      "color": string,       // Hex color code
      "race_index": int,     // Index into Races array
      "government_index": int,
      "initial_site_index": int,
      "new_site_index": int
    }},
    "tribal": {{
      "name_suffix": string,
      "government": {{
        "name": string,
        "description": string,
        "aggressiveness": int,
        "militarization": int,
        "tech_bonus": int
      }},
      "color": string,
      "race_index": int,
      "initial_site_index": int,
      "new_site_index": int
    }}
  }},
  "names": {{
    "civilized": [string],   // Civilization name pool
    "tribal": [string]       // Tribal name pool
  }}
}}

SAMPLE CONFIG (modify this based on user request):
```json
{{
  "world": {{
    "width": 200,
    "height": 80,
    "min_river_length": 3
  }},
  "screen": {{
    "width": 200,
    "height": 80
  }},
  "civilizations": {{
    "civilized": 2,
    "tribal": 2,
    "max_sites": 20,
    "expansion_distance": 10,
    "war_distance": 8
  }},
  "world_gen": {{
    "main_hills": [
      {{ "x": 25, "y": 20, "size": 14, "height": 8 }},
      {{ "x": 50, "y": 30, "size": 15, "height": 9 }}
    ],
    "small_hills": [
      {{ "x": 10, "y": 10, "size": 3, "height": 7 }},
      {{ "x": 15, "y": 15, "size": 4, "height": 6 }}
    ],
    "simplex_noise": {{
      "parameters": {{
        "octaves": 6,
        "frequency": 6,
        "lacunarity": 32,
        "gain": 1
      }}
    }},
    "pole_generation": {{
      "south": {{
        "rng_values": [2, 3, 4, 3, 2, 3, 4, 3],
        "fixed_value": 0.31
      }},
      "north": {{
        "rng_values": [2, 3, 4, 3, 2, 3, 4, 3],
        "fixed_value": 0.31
      }}
    }},
    "tectonic": {{
      "horizontal": {{
        "position": 40,
        "variation": [0]
      }},
      "vertical": {{
        "position": 100,
        "variation": [0]
      }},
      "hill_size": 3,
      "hill_height": 0.15
    }},
    "erosion": {{
      "coefficient": 0.07
    }},
    "river": {{
      "start_x": 100,
      "start_y": 10
    }}
  }},
  "precipitation": {{
    "offset": 2,
    "noise_parameters": {{
      "scale": [2, 2],
      "octaves": 32,
      "gain": 1
    }}
  }},
  "drainage": {{
    "noise_parameters": {{
      "scale": [2, 2],
      "octaves": 32,
      "gain": 1
    }}
  }},
  "flag_templates": {{
    "background": "Background.txt",
    "overlay": "Overlay.txt",
    "background_choice": 1,
    "overlay_choice": 1,
    "back_color2_index": 1,
    "over_color1_index": 2,
    "over_color2_index": 3
  }},
  "civilizations_config": {{
    "civilized": {{
      "name_suffix": "Civilization",
      "color": "#FF2D21",
      "race_index": 0,
      "government_index": 0,
      "initial_site_index": 0,
      "new_site_index": 0
    }},
    "tribal": {{
      "name_suffix": "Tribe",
      "government": {{
        "name": "Tribal",
        "description": "*PLACE HOLDER*",
        "aggressiveness": 2,
        "militarization": 50,
        "tech_bonus": 0
      }},
      "color": "#00FF00",
      "race_index": 0,
      "initial_site_index": 0,
      "new_site_index": 0
    }}
  }},
  "names": {{
    "civilized": ["Alpha", "Beta"],
    "tribal": ["Gamma", "Delta"]
  }}
}}
```

Remember to output ONLY the JSON with no additional text or explanations. Modify the sample based on the user's request.
"""