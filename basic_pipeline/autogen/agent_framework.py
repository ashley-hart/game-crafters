import os
import json
import requests
import copy
from typing import Dict, Any, List, Optional, Tuple

# Import the default template from your existing code
from template_approach import DEFAULT_TEMPLATE

class Agent:
    """Base class for all agents in the system"""
    
    def __init__(self, model: str = "mistral"):
        self.model = model
        self.name = "BaseAgent"
        
    def query_llm(self, prompt: str) -> str:
        """Query the Ollama LLM with a prompt"""
        try:
            # Ollama API endpoint
            url = "http://localhost:11434/api/generate"
            
            # Prepare the request payload
            payload = {
                "model": self.model,
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
    
    def process(self, input_data: Any) -> Any:
        """Process method to be implemented by all agent subclasses"""
        raise NotImplementedError("Subclasses must implement the process method")


class AnalyzerAgent(Agent):
    """Agent that analyzes user queries and extracts requirements"""
    
    def __init__(self, model: str = "mistral"):
        super().__init__(model)
        self.name = "AnalyzerAgent"
    
    def generate_analysis_prompt(self, user_query: str) -> str:
        """Create a prompt that focuses on thoroughly analyzing the user query"""
        return f"""As an Analysis Expert, examine this procedural world generation request and extract ALL key details.

USER REQUEST: "{user_query}"

Break down this request into:

1. WORLD GEOGRAPHY:
   - World size and shape
   - Terrain features (mountains, hills, plains, etc.)
   - Water features (oceans, rivers, lakes)
   - Climate conditions (precipitation, temperature)
   - Special geographical features mentioned

2. CIVILIZATIONS:
   - Number and types of civilizations/societies
   - Their level of development (primitive, advanced, etc.)
   - Names or naming themes
   - Relationships between civilizations (peaceful, hostile)
   - Special civilization characteristics

3. GAME MECHANICS:
   - Any specific gameplay rules or mechanics mentioned
   - Simulation parameters that need adjustment
   - Special algorithms or processes to implement

4. IMPLICIT REQUIREMENTS:
   - Requirements not explicitly stated but implied
   - Player preferences or goals that might be assumed

Provide a comprehensive analysis in these categories, highlighting any ambiguities or contradictions.
"""

    def process(self, user_query: str) -> Dict[str, Any]:
        """Analyze the user query and extract structured requirements"""
        analysis_prompt = self.generate_analysis_prompt(user_query)
        analysis_response = self.query_llm(analysis_prompt)
        
        # Now create a structured parameter extraction prompt based on the analysis
        parameter_prompt = f"""Based on this analysis of a world generation request:

{analysis_response}

Extract specific parameter values in this exact JSON format:
{{
  "world_params": {{
    "width": [number],
    "height": [number],
    "geography_type": "[flat/hilly/mountainous/archipelago/etc]",
    "major_features": ["list", "of", "features"],
    "climate": "[arid/temperate/tropical/etc]"
  }},
  "civilization_params": {{
    "civilized_count": [number],
    "tribal_count": [number], 
    "civilized_names": ["list", "of", "names"],
    "tribal_names": ["list", "of", "names"],
    "civilized_aggression": [1-10 scale],
    "tribal_aggression": [1-10 scale],
    "war_distance": [number]
  }},
  "terrain_params": {{
    "hill_description": "[detailed hill/mountain configuration]",
    "river_start_x": [number],
    "river_start_y": [number],
    "precipitation": [1.0-3.0 scale],
    "erosion": [0.01-0.1 scale]
  }}
}}

Use reasonable defaults if specific values aren't mentioned. Only include the JSON in your response.
"""
        
        parameters_response = self.query_llm(parameter_prompt)
        
        # Try to extract just the JSON part from the response
        try:
            # Find the start and end of the JSON block
            json_start = parameters_response.find('{')
            json_end = parameters_response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = parameters_response[json_start:json_end]
                return json.loads(json_str)
            else:
                # If can't find JSON markers, try to parse the whole thing
                return json.loads(parameters_response)
                
        except json.JSONDecodeError as e:
            # Return a basic structure if JSON parsing fails
            print(f"Warning: Could not parse analyzer response as JSON: {e}")
            print(f"Raw response: {parameters_response}")
            
            # Return a default structure
            return {
                "world_params": {
                    "width": 200,
                    "height": 80,
                    "geography_type": "default",
                    "major_features": ["hills", "river"],
                    "climate": "temperate"
                },
                "civilization_params": {
                    "civilized_count": 2,
                    "tribal_count": 2,
                    "civilized_names": ["Alpha", "Beta"],
                    "tribal_names": ["Gamma", "Delta"],
                    "civilized_aggression": 3,
                    "tribal_aggression": 5,
                    "war_distance": 8
                },
                "terrain_params": {
                    "hill_description": "default hills and mountains",
                    "river_start_x": 100,
                    "river_start_y": 10,
                    "precipitation": 2.0,
                    "erosion": 0.07
                }
            }


class GeneratorAgent(Agent):
    """Agent that generates the configuration based on analyzed requirements"""
    
    def __init__(self, model: str = "mistral"):
        super().__init__(model)
        self.name = "GeneratorAgent"
    
    def generate_hills(self, description: str, world_width: int, world_height: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Generate hill configurations based on a text description"""
        # Create a prompt to generate hill configurations
        prompt = f"""Create realistic hill configurations for a procedural world with:
- World width: {world_width}
- World height: {world_height}
- Description: {description}

Generate two lists of hills:
1. Main hills (larger, primary terrain features)
2. Small hills (smaller, secondary terrain features)

Each hill needs these properties:
- x position (between 0 and {world_width})
- y position (between 0 and {world_height})
- size (1-25, with main hills being 10-25 and small hills being 1-9)
- height (1-10, with main hills generally taller)

Return JSON in this exact format:
{{
  "main_hills": [
    {{"x": X, "y": Y, "size": S, "height": H}},
    ...more hills...
  ],
  "small_hills": [
    {{"x": X, "y": Y, "size": S, "height": H}},
    ...more hills...
  ]
}}

Place hills appropriately to create a {description} landscape.
"""
        
        hill_response = self.query_llm(prompt)
        
        # Try to extract the JSON from the response
        try:
            # Find the start and end of the JSON block
            json_start = hill_response.find('{')
            json_end = hill_response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = hill_response[json_start:json_end]
                hills_data = json.loads(json_str)
                return hills_data.get("main_hills", []), hills_data.get("small_hills", [])
                
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Warning: Could not parse hill generation response as JSON: {e}")
            print(f"Raw response: {hill_response}")
        
        # Return default hills if parsing fails
        return ([
            {"x": world_width // 4, "y": world_height // 3, "size": 14, "height": 8},
            {"x": 2 * world_width // 3, "y": world_height // 2, "size": 15, "height": 9}
        ], [
            {"x": world_width // 6, "y": world_height // 6, "size": 3, "height": 7},
            {"x": 5 * world_width // 6, "y": 5 * world_height // 6, "size": 4, "height": 6}
        ])
    
    def process(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete configuration based on the analyzed data"""
        # Start with a copy of the default template
        config = copy.deepcopy(DEFAULT_TEMPLATE)
        
        # Extract values from the analysis
        world_params = analysis_data.get("world_params", {})
        civ_params = analysis_data.get("civilization_params", {})
        terrain_params = analysis_data.get("terrain_params", {})
        
        # Apply world size
        if "width" in world_params:
            config["world"]["width"] = world_params["width"]
            config["screen"]["width"] = world_params["width"]
        
        if "height" in world_params:
            config["world"]["height"] = world_params["height"]
            config["screen"]["height"] = world_params["height"]
        
        # Apply civilization counts
        if "civilized_count" in civ_params:
            config["civilizations"]["civilized"] = civ_params["civilized_count"]
        
        if "tribal_count" in civ_params:
            config["civilizations"]["tribal"] = civ_params["tribal_count"]
        
        # Generate hills based on description
        if "hill_description" in terrain_params:
            main_hills, small_hills = self.generate_hills(
                terrain_params["hill_description"],
                config["world"]["width"],
                config["world"]["height"]
            )
            config["world_gen"]["main_hills"] = main_hills
            config["world_gen"]["small_hills"] = small_hills
        
        # Apply river starting position
        if "river_start_x" in terrain_params:
            config["world_gen"]["river"]["start_x"] = terrain_params["river_start_x"]
        
        if "river_start_y" in terrain_params:
            config["world_gen"]["river"]["start_y"] = terrain_params["river_start_y"]
        
        # Apply precipitation
        if "precipitation" in terrain_params:
            config["precipitation"]["offset"] = terrain_params["precipitation"]
        
        # Apply erosion
        if "erosion" in terrain_params:
            config["world_gen"]["erosion"]["coefficient"] = terrain_params["erosion"]
        
        # Apply civilization names
        if "civilized_names" in civ_params and len(civ_params["civilized_names"]) > 0:
            # Ensure we have enough names for the civilization count
            civ_names = civ_params["civilized_names"]
            while len(civ_names) < config["civilizations"]["civilized"]:
                civ_names.append(f"Civ{len(civ_names)+1}")
            config["names"]["civilized"] = civ_names[:config["civilizations"]["civilized"]]
        
        # Apply tribal names
        if "tribal_names" in civ_params and len(civ_params["tribal_names"]) > 0:
            # Ensure we have enough names for the tribal count
            tribal_names = civ_params["tribal_names"]
            while len(tribal_names) < config["civilizations"]["tribal"]:
                tribal_names.append(f"Tribe{len(tribal_names)+1}")
            config["names"]["tribal"] = tribal_names[:config["civilizations"]["tribal"]]
        
        # Apply aggression levels
        if "civilized_aggression" in civ_params:
            aggression = civ_params["civilized_aggression"]
            config["civilizations_config"]["civilized"]["government_index"] = min(aggression // 3, 3)
        
        if "tribal_aggression" in civ_params:
            aggression = civ_params["tribal_aggression"]
            config["civilizations_config"]["tribal"]["government"]["aggressiveness"] = min(aggression // 2, 5)
            config["civilizations_config"]["tribal"]["government"]["militarization"] = min(40 + aggression * 5, 90)
        
        # Apply war distance
        if "war_distance" in civ_params:
            config["civilizations"]["war_distance"] = civ_params["war_distance"]
        
        # Apply color schemes based on parameters
        if "civilized_aggression" in civ_params:
            aggression = civ_params["civilized_aggression"]
            if aggression > 7:
                config["civilizations_config"]["civilized"]["color"] = "#FF0000"  # Bright red for aggressive
            elif aggression > 4:
                config["civilizations_config"]["civilized"]["color"] = "#8B0000"  # Dark red for moderate
            else:
                config["civilizations_config"]["civilized"]["color"] = "#0000FF"  # Blue for peaceful
        
        if "tribal_aggression" in civ_params:
            aggression = civ_params["tribal_aggression"]
            if aggression > 7:
                config["civilizations_config"]["tribal"]["color"] = "#8B4513"  # Brown for aggressive
            elif aggression > 4:
                config["civilizations_config"]["tribal"]["color"] = "#006400"  # Dark green for moderate
            else:
                config["civilizations_config"]["tribal"]["color"] = "#00FF00"  # Bright green for peaceful
        
        # Apply special customizations based on geography type
        geo_type = world_params.get("geography_type", "").lower()
        
        # Climate adjustments
        climate = world_params.get("climate", "").lower()
        if "arid" in climate or "desert" in climate:
            config["precipitation"]["offset"] = 1.0
            config["world_gen"]["erosion"]["coefficient"] = 0.09
        elif "tropical" in climate or "rainforest" in climate:
            config["precipitation"]["offset"] = 3.0
            config["world_gen"]["erosion"]["coefficient"] = 0.05
        
        # Geography type adjustments
        if "ocean" in geo_type or "sea" in geo_type:
            # Reduce the height of hills to create more ocean
            for hill in config["world_gen"]["main_hills"]:
                hill["height"] *= 0.8
            for hill in config["world_gen"]["small_hills"]:
                hill["height"] *= 0.8
        
        if "mountain" in geo_type and "range" in geo_type:
            # Create a more dramatic tectonic border
            config["world_gen"]["tectonic"]["hill_size"] = 5
            config["world_gen"]["tectonic"]["hill_height"] = 0.25
        
        return config


class ValidatorAgent(Agent):
    """Agent that validates the generated configuration for correctness and consistency"""
    
    def __init__(self, model: str = "mistral"):
        super().__init__(model)
        self.name = "ValidatorAgent"
        # Initialize the specialized JSON validator
        from json_validator import JsonValidator
        self.json_validator = JsonValidator()
    
    def generate_semantic_validation_prompt(self, config: Dict[str, Any], original_query: str) -> str:
        """Create a prompt for validating the configuration against user requirements"""
        # Convert config to a formatted string
        config_str = json.dumps(config, indent=2)
        
        return f"""As a Configuration Validator, check if this procedural world generation config properly implements the user's request.

USER REQUEST: "{original_query}"

GENERATED CONFIG:
```json
{config_str}
```

Focus on SEMANTIC validation:
1. Verify that the configuration SATISFIES the user's requirements
2. Check if anything important from the user's request is MISSING
3. Identify any IMPROVEMENTS that would better fulfill the user's request

For each issue found, provide:
- The location of the issue (path in the JSON)
- What the problem is
- How to fix it

Your response should be in this JSON format:
{{
  "is_valid": true/false,
  "issues": [
    {{
      "path": "path.to.issue",
      "problem": "Description of the problem",
      "fix": "Recommended fix"
    }},
    ...more issues...
  ],
  "improvements": [
    {{
      "path": "path.to.improvement",
      "suggestion": "Suggested improvement",
      "reason": "Why this would better meet the requirements"
    }},
    ...more improvements...
  ]
}}
"""
    
    def process(self, data: Tuple[Dict[str, Any], str]) -> Dict[str, Any]:
        """Validate the configuration against the original query"""
        config, original_query = data
        
        print(f"[{self.name}] Performing technical validation...")
        # First, perform technical validation using the specialized validator
        technical_validation = self.json_validator.validate(config)
        
        # If there are technical issues, fix them
        if not technical_validation.get("is_valid", True) and technical_validation.get("issues"):
            print(f"[{self.name}] Found {len(technical_validation['issues'])} technical issues, fixing...")
            config = self.json_validator.fix_issues(config, technical_validation)
            print(f"[{self.name}] Technical issues fixed")
        
        print(f"[{self.name}] Performing semantic validation...")
        # Then, perform semantic validation with the LLM
        semantic_validation_prompt = self.generate_semantic_validation_prompt(config, original_query)
        semantic_validation_response = self.query_llm(semantic_validation_prompt)
        
        # Try to extract the JSON validation results from semantic validation
        try:
            # Find the start and end of the JSON block
            json_start = semantic_validation_response.find('{')
            json_end = semantic_validation_response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = semantic_validation_response[json_start:json_end]
                semantic_validation_results = json.loads(json_str)
                
                # If there are semantic issues, fix them
                if not semantic_validation_results.get("is_valid", True) and semantic_validation_results.get("issues"):
                    print(f"[{self.name}] Found {len(semantic_validation_results['issues'])} semantic issues, fixing...")
                    config = self.json_validator.fix_issues(config, semantic_validation_results)
                    print(f"[{self.name}] Semantic issues fixed")
                
                # Apply improvements if requested (could be made optional)
                if semantic_validation_results.get("improvements"):
                    improvement_data = {
                        "issues": semantic_validation_results.get("improvements", [])
                    }
                    print(f"[{self.name}] Applying {len(improvement_data['issues'])} improvements...")
                    config = self.json_validator.fix_issues(config, improvement_data)
                    print(f"[{self.name}] Improvements applied")
            
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Warning: Could not parse semantic validation response as JSON: {e}")
            print(f"Raw response: {semantic_validation_response}")
        
        return config


class AgentManager:
    """Manages the multi-agent system for PCG configuration generation"""
    
    def __init__(self, model: str = "mistral"):
        self.analyzer = AnalyzerAgent(model)
        self.generator = GeneratorAgent(model)
        self.validator = ValidatorAgent(model)
        self.model = model
    
    def process_user_request(self, user_query: str) -> Dict[str, Any]:
        """Process a user request through the multi-agent pipeline"""
        print(f"[AgentManager] Processing user request with {self.model} model")
        
        # Step 1: Analyze the request
        print(f"[{self.analyzer.name}] Analyzing user request...")
        analysis = self.analyzer.process(user_query)
        print(f"[{self.analyzer.name}] Analysis complete")
        
        # Step 2: Generate the configuration
        print(f"[{self.generator.name}] Generating configuration...")
        config = self.generator.process(analysis)
        print(f"[{self.generator.name}] Generation complete")
        
        # Step 3: Validate the configuration
        print(f"[{self.validator.name}] Validating configuration...")
        validated_config = self.validator.process((config, user_query))
        print(f"[{self.validator.name}] Validation complete")
        
        return validated_config


def generate_config_with_agents(user_query: str, model: str = "mistral") -> Dict[str, Any]:
    """
    Generate a PCG configuration using the multi-agent approach.
    This function serves as the main entry point for the agent-based generation.
    """
    manager = AgentManager(model)
    return manager.process_user_request(user_query)