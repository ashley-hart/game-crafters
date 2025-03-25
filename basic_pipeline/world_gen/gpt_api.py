import openai
import argparse
import json
from dotenv import load_dotenv
import os

# Load API key from environment variables
load_dotenv(dotenv_path="../api/.env")
api_key = os.getenv("OPENAI_API_KEY")

def extract_world_data(prompt):
    # Define the system instruction explicitly asking for JSON output
    system_message = (
        "You are an AI assistant that extracts world generation parameters from natural language prompts and returns them as a JSON object.\n"
        "Ensure the response is a valid JSON object with the following fields:\n"
        "- 'biomes': a dictionary mapping 'north', 'south', 'east', 'west', 'northeast', 'southeast', 'northwest', 'southwest' and 'center' to biomes ('water', 'desert', 'plains', 'forest', 'mountains').\n"
        "- 'temperature': a dictionary mapping regions to temperature descriptions.\n"
        "- 'precipitation': a dictionary mapping regions to precipitation descriptions.\n"
        "- 'seed': an optional alphanumeric string if the user specifies one.\n"
        "- 'map_size': one of ['extra small', 'small', 'medium', 'large', 'extra large'] if specified.\n"
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
            #  response_format={"type": "json"}  # **Fixed: Now correctly formatted**
        )

        extracted_data = response.choices[0].message.content.strip()  # Get response text

        return json.loads(extracted_data)  # Convert to JSON
    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Extract world parameters from a prompt.")
    parser.add_argument("input_text", type=str, help="User description of the world")
    args = parser.parse_args()
    print(args)

    world_data = extract_world_data(args.input_text)
    print("\nExtracted JSON:\n", json.dumps(world_data, indent=4))

if __name__ == "__main__":
    main()
