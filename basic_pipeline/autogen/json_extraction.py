import re
import json
from typing import Dict, Any, Optional

def extract_json_from_text(text: str) -> Optional[str]:
    """
    Extract JSON from a text that might contain additional content.
    Handles various ways the model might format its response.
    """
    # Case 1: Response is already valid JSON
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass
    
    # Case 2: JSON is in a code block with language specified
    json_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    matches = re.findall(json_block_pattern, text)
    
    for match in matches:
        try:
            json.loads(match)
            return match
        except json.JSONDecodeError:
            continue
    
    # Case 3: Response has JSON-like content but with errors
    # Try to find content that looks like JSON (starts with { and ends with })
    json_like_pattern = r"\{[\s\S]*\}"
    matches = re.findall(json_like_pattern, text)
    
    for match in matches:
        try:
            json.loads(match)
            return match
        except json.JSONDecodeError:
            continue
    
    return None

def fix_common_json_errors(json_str: str) -> str:
    """
    Attempt to fix common JSON formatting errors that LLMs make.
    """
    # Replace single quotes with double quotes (but not in keys/values)
    fixed = re.sub(r"(?<!\\)'([^']*?)(?<!\\)'", r'"\1"', json_str)
    
    # Fix trailing commas in arrays and objects
    fixed = re.sub(r",\s*}", "}", fixed)
    fixed = re.sub(r",\s*\]", "]", fixed)
    
    # Fix missing quotes around keys
    fixed = re.sub(r"([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)", r'\1"\2"\3', fixed)
    
    # Fix unquoted true/false/null
    fixed = re.sub(r':\s*true([,}])', r':true\1', fixed)
    fixed = re.sub(r':\s*false([,}])', r':false\1', fixed)
    fixed = re.sub(r':\s*null([,}])', r':null\1', fixed)
    
    return fixed

def validate_json(json_str: str) -> Dict[str, Any]:
    """
    Validate and parse JSON with improved error handling and fixing.
    """
    if not json_str:
        raise ValueError("Empty JSON string provided")
    
    # First try direct parsing
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Extract JSON if embedded in other text
    extracted_json = extract_json_from_text(json_str)
    if extracted_json:
        try:
            return json.loads(extracted_json)
        except json.JSONDecodeError:
            # Try to fix common errors
            fixed_json = fix_common_json_errors(extracted_json)
            try:
                return json.loads(fixed_json)
            except json.JSONDecodeError:
                pass
    
    # If all else fails, raise an error with diagnostic info
    raise ValueError(f"Could not parse valid JSON from the response. Check the model output format.")