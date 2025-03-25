#!/usr/bin/env python3
import json
import os
import subprocess
import time
import sys
import shlex

def load_queries(file_path):
    """Load queries from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data.get('queries', [])
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: '{file_path}' is not a valid JSON file.")
        return []
    except Exception as e:
        print(f"Error loading queries: {str(e)}")
        return []

def run_query(query, query_id, model="mistral", approach="agents"):
    """Run a query through main.py and save the output."""
    output_file = f"output_world_{query_id}.json"
    
    try:
        # This approach uses Python's module importing rather than command line
        # which avoids shell quoting issues entirely
        print(f"\nProcessing query {query_id}: {query}")
        
        # Prepare args as they would be passed to main() function
        import importlib.util
        
        # Check if main.py exists in the current directory
        main_path = os.path.join(os.getcwd(), "main.py")
        if not os.path.exists(main_path):
            print(f"Error: main.py not found at {main_path}")
            return False, None
            
        # Import the main module
        spec = importlib.util.spec_from_file_location("main_module", main_path)
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        
        # Save the original sys.argv
        original_argv = sys.argv.copy()
        
        # Set up the arguments as if they were passed from command line
        sys.argv = ["main.py", query, "--output", output_file, "--model", model, "--approach", approach]
        
        print(f"Running with args: {' '.join([shlex.quote(arg) for arg in sys.argv])}")
        
        # Call the main function
        try:
            main_module.main()
            success = True
        except Exception as e:
            print(f"Error executing main.py: {str(e)}")
            success = False
        
        # Restore the original sys.argv
        sys.argv = original_argv
        
        if success:
            print(f"Successfully processed query {query_id}")
            print(f"Output saved to {output_file}")
            
            # Print a snippet of the output file if it exists
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    content = json.load(f)
                    print(f"Generated configuration with {len(content)} top-level keys")
                return True, output_file
            else:
                print(f"Warning: Output file {output_file} not found after processing")
                return False, None
        else:
            return False, None
            
    except Exception as e:
        print(f"Error running query {query_id}: {str(e)}")
        return False, None

def main():
    """Main function to process all queries."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Process queries from a JSON file")
    parser.add_argument("--file", "-f", default="queries.json", help="Path to the queries JSON file")
    parser.add_argument("--model", "-m", default="mistral", help="Model to use for generation")
    parser.add_argument("--approach", "-a", default="agents", choices=["agents", "template", "direct"], 
                        help="Approach to use for generation")
    parser.add_argument("--delay", "-d", type=int, default=2, help="Delay in seconds between queries")
    parser.add_argument("--start", "-s", type=int, default=1, help="ID to start processing from")
    parser.add_argument("--end", "-e", type=int, default=None, help="ID to end processing at")
    parser.add_argument("--update-json", "-u", action="store_true", help="Update the original JSON with output filenames")
    
    args = parser.parse_args()
    
    print(f"Loading queries from {args.file}")
    queries = load_queries(args.file)
    
    if not queries:
        print("No queries found. Exiting.")
        return
    
    print(f"Found {len(queries)} queries")
    
    # Sort queries by ID to ensure they're processed in order
    queries.sort(key=lambda q: q.get('id', 0))
    
    # Filter queries based on start and end IDs
    if args.end:
        filtered_queries = [q for q in queries if args.start <= q.get('id', 0) <= args.end]
    else:
        filtered_queries = [q for q in queries if args.start <= q.get('id', 0)]
    
    print(f"Processing {len(filtered_queries)} queries from ID {args.start}{f' to {args.end}' if args.end else ''}")
    
    successful = 0
    failed = 0
    
    # Create a dictionary to map query IDs to their indices in the original list
    id_to_index = {q.get('id'): i for i, q in enumerate(queries)}
    
    # Track updates for the original JSON
    json_updates = False
    
    for i, query_data in enumerate(filtered_queries):
        query_id = query_data.get('id', i+1)
        query_text = query_data.get('query', '')
        
        if not query_text:
            print(f"Warning: Empty query for ID {query_id}, skipping")
            continue
        
        success, output_file = run_query(query_text, query_id, args.model, args.approach)
        
        if success:
            successful += 1
            
            # Update the query data with the output filename
            if args.update_json and output_file and query_id in id_to_index:
                original_index = id_to_index[query_id]
                queries[original_index]['output_file'] = output_file
                json_updates = True
        else:
            failed += 1
        
        # Add a delay between queries to avoid overwhelming the LLM service
        if i < len(filtered_queries) - 1:
            print(f"Waiting {args.delay} seconds before next query...")
            time.sleep(args.delay)
    
    # Update the original JSON file if requested
    if args.update_json and json_updates:
        try:
            with open(args.file, 'r') as f:
                full_data = json.load(f)
            
            full_data['queries'] = queries
            
            with open(args.file, 'w') as f:
                json.dump(full_data, f, indent=2)
                
            print(f"\nUpdated {args.file} with output filenames")
        except Exception as e:
            print(f"\nError updating {args.file}: {str(e)}")
    
    print(f"\nSummary: Processed {len(filtered_queries)} queries")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

if __name__ == "__main__":
    main()



# python process_queries_alternative.py --update-json