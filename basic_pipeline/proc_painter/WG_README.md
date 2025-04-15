# ProcPainter - World Generator

Welcome to ProcPainter(short for Procedural Painter)! This is a command-line tool that extracts world parameters from a user-provided prompt and generates a world representation based on the specified mode. Users can pass prompts directly or from a text file, customize the output format, and configure various settings.

Please note that ProcPainter uses `gpt-3.5-turbo`. While experimenting should you make changes to the system message or the GPT model (which can be found in `main.py`) **be sure to document those changes and to revert the model and or message back to the baseline components** as needed.


## Installation
Ensure you have Python installed on your system. Clone or download the repository and navigate to the project directory.

### Setting Up a Conda Environment
To manage dependencies, create a Conda environment using the provided `requirements.txt` file:
```sh
conda create --name world-gen-env --file world-gen/requirements.txt
conda activate world-gen-env
```

## OpenAI API Key Requirement
This tool requires an OpenAI API key to function. Ensure you have an API key and set it as an environment variable before running the script:
```sh
export OPENAI_API_KEY="your-api-key-here"
```
On Windows (Command Prompt):
```sh
set OPENAI_API_KEY="your-api-key-here"
```

## Usage
Run the script using Python with the following options:

### Providing a Prompt
You must provide a prompt using either `--prompt` (`-p`) or `--file` (`-f`).

- **Direct Prompt:**
  ```sh
  python world_generator.py --prompt "Generate a mountainous terrain with lakes."
  ```
- **Prompt from File:**
  ```sh
  python world_generator.py --file prompt.txt
  ```

### Display Mode
Choose how the world is displayed:

- ASCII mode (default):
  ```sh
  python world_generator.py --mode ascii
  ```
- Pixel-based rendering:
  ```sh
  python world_generator.py --mode pixel
  ```
- Shortcuts:
  ```sh
  python world_generator.py -m a  # ASCII
  python world_generator.py -m p  # Pixel
  ```

### Debug and Quiet Modes (Not Yet Functional)
- Enable debug mode for detailed logs:
  ```sh
  python world_generator.py --debug
  ```
- Suppress all non-critical output:
  ```sh
  python world_generator.py --quiet
  ```

### Setting a Seed
To ensure reproducibility, set a seed for the world generator:
```sh
python world_generator.py --seed 42
```

### Saving Images (Not Yet Functional)
Specify a directory to save images (feature in development):
```sh
python world_generator.py --img output_images/
```

### Verbose Mode (Not Yet Functional)
Enable verbose output for additional information during execution:
```sh
python world_generator.py --verbose
```

## Notes
- Modes listed as 'Not Yet Functional' will be implemented in future updates. 

## License
TBD


