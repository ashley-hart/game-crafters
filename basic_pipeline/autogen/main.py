import os
import sys
import json
import requests
import argparse
from typing import Dict, Any

# Import our custom modules
from json_extraction import extract_json_from_text, fix_common_json_errors, validate_json
from prompt_engineering import generate_prompt
from ollama_chunking import query_ollama_with_chunking
from template_approach import generate_template_based_config, DEFAULT_TEMPLATE

# Import the new agent-based approach
from agent_framework import generate_config_with_agents

def test_ollama_connection(model="mistral"):
    """
    Test if Ollama is running locally and the specified model is available.
    """
    print(f"Testing connection to Ollama with model: {model}")
    
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            print(f"Error: Ollama API returned status code {response.status_code}")
            return False
            
        models = response.json().get("models", [])
        model_names = [m.get("name") for m in models]
        
        print("Success! Ollama is running.")
        return True
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Ollama API at http://localhost:11434")
        print("Make sure Ollama is installed and running. Use 'ollama serve' to start it.")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def process_user_request(user_query: str, model: str = "mistral", approach: str = "agents") -> Dict[str, Any]:
    """
    Process a user request and return a generated configuration.
    Supports multiple approaches: agents, template, direct
    """
    # try:
    if approach == "agents":
        print("Using multi-agent approach...")
        return generate_config_with_agents(user_query, model)
    elif approach == "template":
        print("Using template-based approach...")
        return generate_template_based_config(user_query, model)
    elif approach == "direct":
        print("Using direct JSON generation approach...")
        # Generate the prompt
        prompt = generate_prompt(user_query)
        
        # Query the Ollama LLM with improved chunking
        llm_response = query_ollama_with_chunking(prompt, model)
        
        # Validate and return the JSON
        return validate_json(llm_response)
    else:
        print(f"Unknown approach: {approach}, falling back to agents")
        return generate_config_with_agents(user_query, model)
    # except Exception as e:
    #     print(f"Error in {approach} approach: {str(e)}")
    #     print("Falling back to template-based approach...")
    #     try:
    #         return generate_template_based_config(user_query, model)
    #     except Exception as e2:
    #         print(f"Error in fallback approach: {str(e2)}")
    #         print("Using default template...")
    #         return DEFAULT_TEMPLATE

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
    parser.add_argument("--approach", "-a", default="agents", choices=["agents", "template", "direct"], 
                        help="Generation approach: agents (default), template, or direct")
    
    args = parser.parse_args()
    
    # Test Ollama connection
    if not test_ollama_connection(args.model):
        print("Exiting due to Ollama connection issues.")
        sys.exit(1)
    
    if args.interactive:
        print("PCG Configuration Generator")
        print("===========================")
        print(f"Using model: {args.model}")
        print(f"Approach: {args.approach}")
        print("Enter your world description prompt, or 'quit' to exit.")
        
        while True:
            prompt = input("\nPrompt> ")
            if prompt.lower() in ("quit", "exit", "q"):
                break
                
            try:
                print(f"Generating configuration with {args.model} using {args.approach} approach...")
                config = process_user_request(prompt, args.model, args.approach)
                filename = save_config(config, args.output)
                print(f"Configuration saved to {filename}")
                print("\nGenerated configuration:")
                print(json.dumps(config, indent=2))
            except Exception as e:
                print(f"Error: {str(e)}")
    
    elif args.prompt:
        try:
            print(f"Generating configuration with {args.model} using {args.approach} approach...")
            config = process_user_request(args.prompt, args.model, args.approach)
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


# python main.py "Create a world with a series of islands. Include unique cultures and civilizations on each island." --output output_world_10.json --model mistral --approach agents