import argparse
import sys
from processor import DocumentProcessor

def main():
    parser = argparse.ArgumentParser(description="Document Intelligence Processor")
    parser.add_argument("file_path", help="Path to the document (PDF, JPG, PNG)")
    args = parser.parse_args()

    processor = DocumentProcessor()
    
    # Process the document
    result = processor.process(args.file_path)
    
    # Print the strictly structured JSON response
    print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    # Ensure API key is present
    import os
    if "GOOGLE_API_KEY" not in os.environ:
        print('{"processing_errors": ["GOOGLE_API_KEY environment variable not set"]}')
        sys.exit(1)
        
    main()