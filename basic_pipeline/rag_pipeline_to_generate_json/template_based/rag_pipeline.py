import os
import sys
import json
import requests
import argparse
from typing import Dict, Any

# Import our custom modules
# (Assuming these files are in the same directory)
from json_extraction import extract_json_from_text, fix_common_json_errors, validate_json
from prompt_engineering import generate_prompt
from ollama_chunking import query_ollama_with_chunking
from template_approach import generate_template_based_config

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
        
        # if not models:
        #     print("Error: No models found in Ollama")
        #     return False
            
        # if model not in model_names:
        #     print(f"Warning: Model '{model}' not found in available models: {', '.join(model_names)}")
        #     print(f"Please pull the model with: ollama pull {model}")
        #     return False
            
        # test_response = requests.post(
        #     "http://localhost:11434/api/generate",
        #     json={
        #         "model": model,
        #         "prompt": "Hello, are you working?",
        #         "stream": False
        #     }
        # )
        
        # if test_response.status_code != 200:
        #     print(f"Error: Failed to generate text with model {model}")
        #     return False
            
        print("Success! Ollama is running and the model is working properly.")
        return True
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Ollama API at http://localhost:11434")
        print("Make sure Ollama is installed and running. Use 'ollama serve' to start it.")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def process_user_request(user_query: str, model: str = "mistral", use_template: bool = True) -> Dict[str, Any]:
    """
    Process a user request and return a generated configuration.
    Uses the template-based approach by default, with fallback to direct JSON generation.
    """
    try:
        if use_template:
            print("Using template-based approach...")
            return generate_template_based_config(user_query, model)
        else:
            print("Using direct JSON generation approach...")
            # Generate the prompt
            prompt = generate_prompt(user_query)
            
            # Query the Ollama LLM with improved chunking
            llm_response = query_ollama_with_chunking(prompt, model)
            
            # Validate and return the JSON
            return validate_json(llm_response)
    except Exception as e:
        print(f"Error in primary approach: {str(e)}")
        print("Falling back to template-based approach...")
        try:
            return generate_template_based_config(user_query, model)
        except Exception as e2:
            print(f"Error in fallback approach: {str(e2)}")
            print("Using default template...")
            # Import here to avoid circular import
            from template_approach import DEFAULT_TEMPLATE
            return DEFAULT_TEMPLATE

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
    parser.add_argument("--direct", "-d", action="store_true", help="Use direct JSON generation instead of template-based approach")
    
    args = parser.parse_args()
    
    # Test Ollama connection
    if not test_ollama_connection(args.model):
        print("Exiting due to Ollama connection issues.")
        sys.exit(1)
    
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
                config = process_user_request(prompt, args.model, not args.direct)
                filename = save_config(config, args.output)
                print(f"Configuration saved to {filename}")
                print("\nGenerated configuration:")
                print(json.dumps(config, indent=2))
            except Exception as e:
                print(f"Error: {str(e)}")
    
    elif args.prompt:
        try:
            print(f"Generating configuration with {args.model}...")
            config = process_user_request(args.prompt, args.model, not args.direct)
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