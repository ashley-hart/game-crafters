#!/usr/bin/env python3
import json
import subprocess
import os
import argparse
import tempfile
import shutil
import sys

def create_config_for_query(query, template_config_path="trail.json"):
    """
    Create a customized configuration file based on the query.
    
    Args:
        query (dict): The query containing world generation parameters
        template_config_path (str): Path to the template configuration file
        
    Returns:
        str: Path to the created configuration file
    """
    # Load the template configuration
    with open(template_config_path, 'r') as f:
        config = json.load(f)
    
    # Extract keywords from the query to customize the configuration
    query_text = query["query"].lower()
    
    # Customize world parameters based on query keywords
    # This is a simplified approach - in a real implementation, you would use
    # more sophisticated NLP to extract parameters from the query
    
    # Adjust world size based on keywords
    if "archipelago" in query_text or "islands" in query_text:
        config["world"]["width"] = 120
        config["world"]["height"] = 80
    elif "continent" in query_text:
        config["world"]["width"] = 150
        config["world"]["height"] = 100
    
    # Adjust terrain generation based on keywords
    if "mountains" in query_text:
        # Add more mountains
        config["world_gen"]["main_hills"].append({"x": 75, "y": 40, "size": 20, "height": 0.8})
    
    if "volcano" in query_text:
        # Add volcanic features
        config["world_gen"]["main_hills"].append({"x": 60, "y": 30, "size": 8, "height": 1.0})
    
    if "rivers" in query_text:
        # Increase river generation
        config["world"]["min_river_length"] = 5
    
    # Climate adjustments
    if "desert" in query_text:
        # Make some regions drier
        if "precipitation" in config:
            config["precipitation"]["offset"] = -0.2
    
    if "tropical" in query_text or "jungle" in query_text:
        # Make some regions more humid
        if "precipitation" in config:
            config["precipitation"]["offset"] = 0.3
    
    if "polar" in query_text or "tundra" in query_text:
        # Adjust temperature for colder regions
        if "world_gen" in config and "pole_generation" in config["world_gen"]:
            config["world_gen"]["pole_generation"]["north"]["fixed_value"] = 0.95
            config["world_gen"]["pole_generation"]["south"]["fixed_value"] = 0.95
    
    # Create a temporary config file
    fd, temp_path = tempfile.mkstemp(suffix='.json', prefix='world_config_')
    with os.fdopen(fd, 'w') as temp_file:
        json.dump(config, temp_file, indent=2)
    
    return temp_path

def process_queries(queries_file):
    """
    Process each query in the JSON file and generate worlds.
    
    Args:
        queries_file (str): Path to the JSON file containing queries
    """
    # Load queries from file
    with open(queries_file, 'r') as f:
        data = json.load(f)
    
    queries = data.get("queries", [])
    
    # Process each query
    for query in queries:
        query_id = query.get("id", "unknown")
        query_text = query.get("query", "")
        output_file = query.get("output_file", f"output_world_{query_id}.txt")
        
        print(f"\n--- Processing Query {query_id} ---")
        print(f"Query: {query_text}")
        
        # Create a custom configuration based on the query
        config_path = create_config_for_query(query)
        
        try:
            # Run jsonWorld.py with the custom configuration
            cmd = [
                "python", "newJsonWorld.py",
                "--config", config_path,
                "--output", output_file
            ]
            
            print(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            
            print(f"✓ World generated successfully: {output_file}")
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Error generating world: {e}")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
        finally:
            # Clean up the temporary config file
            if os.path.exists(config_path):
                os.remove(config_path)

def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(description='Process world generation queries from a JSON file')
    parser.add_argument('queries_file', help='Path to the JSON file containing queries')
    parser.add_argument('--template', default='trail.json', help='Path to the template configuration file')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.queries_file):
        print(f"Error: Queries file '{args.queries_file}' not found")
        sys.exit(1)
    
    if not os.path.exists(args.template):
        print(f"Error: Template configuration file '{args.template}' not found")
        sys.exit(1)
    
    process_queries(args.queries_file)
    
    print("\nAll queries processed.")

if __name__ == "__main__":
    main()