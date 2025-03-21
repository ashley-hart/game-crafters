def query_ollama_with_chunking(prompt: str, model: str = "mistral") -> str:
    """
    Send the prompt to a locally running Ollama instance with the Mistral model,
    using a chunking approach to handle large structured outputs.
    """
    import requests
    
    try:
        # Ollama API endpoint
        url = "http://localhost:11434/api/generate"
        
        # Add explicit instruction to start JSON output
        final_prompt = f"""{prompt}

Start by outputting the opening brace of the JSON:

{{"""
        
        # Prepare the request payload - with very low temperature for structured output
        payload = {
            "model": model,
            "prompt": final_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Lower temperature for more deterministic output
                "num_predict": 4000, # Increased token limit
                "stop": ["```"]      # Stop at code block markers
            }
        }
        
        # Send the request
        response = requests.post(url, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json().get("response", "").strip()
            
            # If the response doesn't start with a brace, something went wrong
            if not result.startswith("{"):
                result = "{" + result
                
            # If the response doesn't end properly, try to complete it
            if not (result.rstrip().endswith("}") or result.rstrip().endswith(",") or result.rstrip().endswith(":")):
                # Request a completion with another chunk
                completion_payload = {
                    "model": model,
                    "prompt": f"Continue generating the JSON. Here's what you have so far:\n\n{result}",
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 2000
                    }
                }
                
                completion_response = requests.post(url, json=completion_payload)
                if completion_response.status_code == 200:
                    continuation = completion_response.json().get("response", "").strip()
                    result += continuation
            
            return result
        else:
            return f"Error: Received status code {response.status_code} from Ollama API"
    except Exception as e:
        return f"Error querying Ollama: {str(e)}"