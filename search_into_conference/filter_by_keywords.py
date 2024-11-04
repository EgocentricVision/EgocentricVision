import json
import re
import argparse

def filter_entries_by_keywords(json_data, l_keywords):
    filtered_entries = []
    
    # Convert all keywords to lowercase
    l_keywords = [keyword.lower() for keyword in l_keywords]
    # Create a regex pattern for the keywords in lowercase
    keyword_pattern = re.compile(r'\b(' + '|'.join(re.escape(keyword) for keyword in l_keywords) + r')\b')
    
    for entry in json_data:
        # Convert title and abstract to lowercase for case-insensitive matching
        title = entry.get("title", "").lower()
        abstract = entry.get("abstract", "").lower()
        
        # Check for keywords in title or abstract
        if keyword_pattern.search(title) or keyword_pattern.search(abstract):
            # Create a new entry with additional fields
            new_entry = {
                **entry,  # Copy existing entry data
                "ego-relevance": "NOT relevant",  # New field with default value
                "processed": "NOT done"            # New field with default value
            }
            filtered_entries.append(new_entry)
    
    return filtered_entries

def load_keywords(keywords_file):
    # Read the keywords file and strip any whitespace
    with open(keywords_file, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]
    return keywords

def main():
    parser = argparse.ArgumentParser(description="Filtra un JSON in base alla presenza di parole chiave nel titolo o abstract.")
    parser.add_argument("--input_file", help="Path del file JSON di input")
    parser.add_argument("--output_file", help="Path del file JSON di output")
    parser.add_argument("--keywords_file", help="Path del file di testo contenente le parole chiave")

    args = parser.parse_args()
    
    # Load keywords from the file
    keywords = load_keywords(args.keywords_file)

    # Load the input JSON file
    with open(args.input_file, "r", encoding="utf-8") as infile:
        json_data = json.load(infile)
    
    # Filter entries based on keywords
    filtered_json = filter_entries_by_keywords(json_data, keywords)
    
    # Save the filtered JSON to the output file
    with open(args.output_file, "w", encoding="utf-8") as outfile:
        json.dump(filtered_json, outfile, indent=4)
    
    # Print totals
    print(f"Total entries in initial JSON: {len(json_data)}")
    print(f"Total entries in filtered JSON: {len(filtered_json)}")
    print(f"Filtered JSON saved to {args.output_file}")

if __name__ == "__main__":
    main()
