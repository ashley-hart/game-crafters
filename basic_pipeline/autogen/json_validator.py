import json
import copy
from typing import Dict, Any, List, Tuple, Optional

class JsonValidator:
    """
    A specialized validator specifically for PCG configuration JSON validation.
    This enhances the ValidatorAgent by providing more rigorous checks.
    """
    
    def __init__(self):
        # Define the expected structure for validation
        self.required_sections = [
            "world", "screen", "civilizations", "world_gen", 
            "precipitation", "drainage", "flag_templates", 
            "civilizations_config", "names"
        ]
        
        self.required_fields = {
            "world": ["width", "height", "min_river_length"],
            "screen": ["width", "height"],
            "civilizations": ["civilized", "tribal", "max_sites", "expansion_distance", "war_distance"],
            "world_gen": ["main_hills", "small_hills", "simplex_noise", "pole_generation", "tectonic", "erosion", "river"],
            "precipitation": ["offset", "noise_parameters"],
            "drainage": ["noise_parameters"],
            "flag_templates": ["background", "overlay", "background_choice", "overlay_choice"],
            "civilizations_config": ["civilized", "tribal"],
            "names": ["civilized", "tribal"]
        }
    
    def validate_structure(self, config: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Validate the overall structure of the configuration.
        """
        issues = []
        
        # Check for required sections
        for section in self.required_sections:
            if section not in config:
                issues.append({
                    "path": section,
                    "problem": f"Missing required section: {section}",
                    "fix": f"Add the '{section}' section with appropriate values"
                })
        
        # Check required fields in each section
        for section, fields in self.required_fields.items():
            if section in config:
                for field in fields:
                    # Handle nested fields with dots
                    if "." in field:
                        parts = field.split(".")
                        current = config[section]
                        missing = False
                        for i, part in enumerate(parts):
                            if part not in current:
                                issues.append({
                                    "path": f"{section}.{'.'.join(parts[:i+1])}",
                                    "problem": f"Missing required field: {part} in {section}.{'.'.join(parts[:i])}",
                                    "fix": "{}" if i < len(parts) - 1 else "Appropriate value needed"
                                })
                                missing = True
                                break
                            if i < len(parts) - 1:
                                current = current[part]
                    elif field not in config[section]:
                        issues.append({
                            "path": f"{section}.{field}",
                            "problem": f"Missing required field: {field} in {section}",
                            "fix": "Appropriate value needed"
                        })
        
        return issues

    def validate_value_types(self, config: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Validate that values have the correct types.
        """
        issues = []
        
        # Validate world and screen dimensions
        for section in ["world", "screen"]:
            if section in config:
                for field in ["width", "height"]:
                    if field in config[section]:
                        value = config[section][field]
                        if not isinstance(value, (int, float)) or value <= 0:
                            issues.append({
                                "path": f"{section}.{field}",
                                "problem": f"Invalid {field} value: {value}. Should be a positive number.",
                                "fix": str(max(100, int(value) if isinstance(value, (int, float)) else 100))
                            })
        
        # Validate civilization counts
        if "civilizations" in config:
            for field in ["civilized", "tribal"]:
                if field in config["civilizations"]:
                    value = config["civilizations"][field]
                    if not isinstance(value, int) or value < 0:
                        issues.append({
                            "path": f"civilizations.{field}",
                            "problem": f"Invalid {field} count: {value}. Should be a non-negative integer.",
                            "fix": str(max(0, int(value) if isinstance(value, (int, float)) else 2))
                        })
        
        # Validate main_hills and small_hills
        if "world_gen" in config:
            for hill_type in ["main_hills", "small_hills"]:
                if hill_type in config["world_gen"]:
                    hills = config["world_gen"][hill_type]
                    if not isinstance(hills, list):
                        issues.append({
                            "path": f"world_gen.{hill_type}",
                            "problem": f"{hill_type} should be a list of hill objects",
                            "fix": "[]"
                        })
                    else:
                        for i, hill in enumerate(hills):
                            if not isinstance(hill, dict):
                                issues.append({
                                    "path": f"world_gen.{hill_type}[{i}]",
                                    "problem": "Hill should be an object with x, y, size, and height properties",
                                    "fix": '{"x": 10, "y": 10, "size": 10, "height": 5}'
                                })
                            else:
                                for prop in ["x", "y", "size", "height"]:
                                    if prop not in hill:
                                        issues.append({
                                            "path": f"world_gen.{hill_type}[{i}].{prop}",
                                            "problem": f"Missing required property: {prop}",
                                            "fix": "10" if prop in ["x", "y", "size"] else "5"
                                        })
                                    elif not isinstance(hill[prop], (int, float)):
                                        issues.append({
                                            "path": f"world_gen.{hill_type}[{i}].{prop}",
                                            "problem": f"{prop} should be a number",
                                            "fix": "10" if prop in ["x", "y", "size"] else "5"
                                        })
        
        # Validate names
        if "names" in config:
            for group in ["civilized", "tribal"]:
                if group in config["names"]:
                    names = config["names"][group]
                    if not isinstance(names, list):
                        issues.append({
                            "path": f"names.{group}",
                            "problem": f"{group} names should be a list of strings",
                            "fix": '["Default1", "Default2"]'
                        })
                    else:
                        for i, name in enumerate(names):
                            if not isinstance(name, str):
                                issues.append({
                                    "path": f"names.{group}[{i}]",
                                    "problem": "Name should be a string",
                                    "fix": f'"Default{i+1}"'
                                })
        
        return issues

    def validate_consistency(self, config: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Validate the consistency between different parts of the configuration.
        """
        issues = []
        
        # Check world and screen dimensions match
        if "world" in config and "screen" in config:
            if "width" in config["world"] and "width" in config["screen"]:
                if config["world"]["width"] != config["screen"]["width"]:
                    issues.append({
                        "path": "screen.width",
                        "problem": f"Screen width ({config['screen']['width']}) does not match world width ({config['world']['width']})",
                        "fix": str(config["world"]["width"])
                    })
            
            if "height" in config["world"] and "height" in config["screen"]:
                if config["world"]["height"] != config["screen"]["height"]:
                    issues.append({
                        "path": "screen.height",
                        "problem": f"Screen height ({config['screen']['height']}) does not match world height ({config['world']['height']})",
                        "fix": str(config["world"]["height"])
                    })
        
        # Check that civilization names match civilization counts
        if "civilizations" in config and "names" in config:
            if "civilized" in config["civilizations"] and "civilized" in config["names"]:
                civ_count = config["civilizations"]["civilized"]
                civ_names = config["names"]["civilized"]
                if isinstance(civ_names, list) and len(civ_names) < civ_count:
                    issues.append({
                        "path": "names.civilized",
                        "problem": f"Not enough civilization names ({len(civ_names)}) for the specified count ({civ_count})",
                        "fix": f"Add {civ_count - len(civ_names)} more civilization names"
                    })
            
            if "tribal" in config["civilizations"] and "tribal" in config["names"]:
                tribal_count = config["civilizations"]["tribal"]
                tribal_names = config["names"]["tribal"]
                if isinstance(tribal_names, list) and len(tribal_names) < tribal_count:
                    issues.append({
                        "path": "names.tribal",
                        "problem": f"Not enough tribal names ({len(tribal_names)}) for the specified count ({tribal_count})",
                        "fix": f"Add {tribal_count - len(tribal_names)} more tribal names"
                    })
        
        # Check hill placements are within world bounds
        if "world" in config and "world_gen" in config:
            world_width = config["world"].get("width", 200)
            world_height = config["world"].get("height", 80)
            
            for hill_type in ["main_hills", "small_hills"]:
                if hill_type in config["world_gen"]:
                    hills = config["world_gen"][hill_type]
                    if isinstance(hills, list):
                        for i, hill in enumerate(hills):
                            if isinstance(hill, dict):
                                # Check x-coordinate
                                if "x" in hill and isinstance(hill["x"], (int, float)):
                                    if hill["x"] < 0 or hill["x"] >= world_width:
                                        issues.append({
                                            "path": f"world_gen.{hill_type}[{i}].x",
                                            "problem": f"Hill x-coordinate ({hill['x']}) is outside world bounds (0 to {world_width-1})",
                                            "fix": str(min(max(0, int(hill["x"])), world_width-1))
                                        })
                                
                                # Check y-coordinate
                                if "y" in hill and isinstance(hill["y"], (int, float)):
                                    if hill["y"] < 0 or hill["y"] >= world_height:
                                        issues.append({
                                            "path": f"world_gen.{hill_type}[{i}].y",
                                            "problem": f"Hill y-coordinate ({hill['y']}) is outside world bounds (0 to {world_height-1})",
                                            "fix": str(min(max(0, int(hill["y"])), world_height-1))
                                        })
        
        # Check river start position is within world bounds
        if "world" in config and "world_gen" in config and "river" in config["world_gen"]:
            world_width = config["world"].get("width", 200)
            world_height = config["world"].get("height", 80)
            river = config["world_gen"]["river"]
            
            if "start_x" in river and isinstance(river["start_x"], (int, float)):
                if river["start_x"] < 0 or river["start_x"] >= world_width:
                    issues.append({
                        "path": "world_gen.river.start_x",
                        "problem": f"River start x-coordinate ({river['start_x']}) is outside world bounds (0 to {world_width-1})",
                        "fix": str(min(max(0, int(river["start_x"])), world_width-1))
                    })
            
            if "start_y" in river and isinstance(river["start_y"], (int, float)):
                if river["start_y"] < 0 or river["start_y"] >= world_height:
                    issues.append({
                        "path": "world_gen.river.start_y",
                        "problem": f"River start y-coordinate ({river['start_y']}) is outside world bounds (0 to {world_height-1})",
                        "fix": str(min(max(0, int(river["start_y"])), world_height-1))
                    })
        
        return issues

    def validate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the configuration and return validation results.
        """
        # Collect issues from all validation methods
        structure_issues = self.validate_structure(config)
        type_issues = self.validate_value_types(config)
        consistency_issues = self.validate_consistency(config)
        
        all_issues = structure_issues + type_issues + consistency_issues
        
        return {
            "is_valid": len(all_issues) == 0,
            "issues": all_issues,
            "improvements": []  # Improvements would be more context-dependent
        }

    def fix_issues(self, config: Dict[str, Any], validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply fixes to the configuration based on validation results.
        """
        fixed_config = copy.deepcopy(config)
        
        # Apply fixes for reported issues
        for issue in validation_results.get("issues", []):
            path = issue.get("path", "")
            fix = issue.get("fix", "")
            
            # Skip if path or fix is empty
            if not path or not fix:
                continue
            
            # Parse the path
            parts = path.split(".")
            
            # Navigate to the parent object
            current = fixed_config
            for i in range(len(parts) - 1):
                part = parts[i]
                
                # Handle array indices
                if "[" in part and "]" in part:
                    key, idx_str = part.split("[", 1)
                    idx = int(idx_str.rstrip("]"))
                    
                    if key not in current:
                        current[key] = []
                    
                    # Ensure the list is long enough
                    while len(current[key]) <= idx:
                        current[key].append({})
                    
                    current = current[key][idx]
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
            
            # Set the final value
            last_part = parts[-1]
            
            # Handle array indices in the last part
            if "[" in last_part and "]" in last_part:
                key, idx_str = last_part.split("[", 1)
                idx = int(idx_str.rstrip("]"))
                
                if key not in current:
                    current[key] = []
                
                # Ensure the list is long enough
                while len(current[key]) <= idx:
                    current[key].append(None)
                
                # Try to parse the fix as JSON, fallback to string
                try:
                    current[key][idx] = json.loads(fix)
                except json.JSONDecodeError:
                    # Handle various value types
                    if fix.isdigit():
                        current[key][idx] = int(fix)
                    elif fix.replace(".", "", 1).isdigit():
                        current[key][idx] = float(fix)
                    else:
                        current[key][idx] = fix
            else:
                # Try to parse the fix as JSON, fallback to string
                try:
                    current[last_part] = json.loads(fix)
                except json.JSONDecodeError:
                    # Handle various value types
                    if fix.isdigit():
                        current[last_part] = int(fix)
                    elif fix.replace(".", "", 1).isdigit():
                        current[last_part] = float(fix)
                    else:
                        current[last_part] = fix
        
        return fixed_config