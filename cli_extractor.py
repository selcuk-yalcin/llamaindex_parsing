"""
CLI Interface for Legal Document Extractor
For batch processing from command line
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from batch_extractor import LegalDocumentExtractor

# Load .env file
load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Parse legal documents and convert to JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single file
  python cli_extractor.py --file law.pdf
  
  # Batch processing
  python cli_extractor.py --batch file1.pdf file2.pdf file3.pdf
  
  # Process directory
  python cli_extractor.py --directory ./data/laws
  
  # Use Gemini
  python cli_extractor.py --file law.pdf --llm gemini --model gemini-1.5-pro
        """
    )
    
    # File options
    file_group = parser.add_mutually_exclusive_group(required=True)
    file_group.add_argument(
        '--file', '-f',
        type=str,
        help='Process a single PDF file'
    )
    file_group.add_argument(
        '--batch', '-b',
        nargs='+',
        help='Process multiple PDF files'
    )
    file_group.add_argument(
        '--directory', '-d',
        type=str,
        help='Process all PDF files in directory'
    )
    
    # LLM options
    parser.add_argument(
        '--llm',
        choices=['openai', 'gemini'],
        default='openai',
        help='LLM provider (default: openai)'
    )
    parser.add_argument(
        '--model', '-m',
        type=str,
        default='gpt-4o',
        help='LLM model (default: gpt-4o)'
    )
    
    # Output options
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='./extracted_laws',
        help='Directory to save JSON outputs (default: ./extracted_laws)'
    )
    parser.add_argument(
        '--markdown-dir',
        type=str,
        default='./parsed_markdown',
        help='Directory to save markdown outputs (default: ./parsed_markdown)'
    )
    
    # API keys
    parser.add_argument(
        '--llama-key',
        type=str,
        default=os.getenv('LLAMA_CLOUD_API_KEY'),
        help='LlamaCloud API key (default: LLAMA_CLOUD_API_KEY environment variable)'
    )
    parser.add_argument(
        '--llm-key',
        type=str,
        help='LLM API key (default: OPENAI_API_KEY or GEMINI_API_KEY environment variable)'
    )
    
    # Other options
    parser.add_argument(
        '--pattern',
        type=str,
        default='*.pdf',
        help='File pattern when processing directory (default: *.pdf)'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=50000,
        help='Chunk size for long documents (default: 50000)'
    )
    
    args = parser.parse_args()
    
    # API key check
    if not args.llama_key:
        print("ERROR: LlamaCloud API key not found!")
        print("Solution: Use --llama-key parameter or set LLAMA_CLOUD_API_KEY environment variable")
        sys.exit(1)
    
    # LLM API key
    llm_key = args.llm_key
    if not llm_key:
        if args.llm == 'openai':
            llm_key = os.getenv('OPENAI_API_KEY')
        elif args.llm == 'gemini':
            llm_key = os.getenv('GEMINI_API_KEY')
        
        if not llm_key:
            print(f"ERROR: {args.llm.upper()} API key not found!")
            print(f"Solution: Use --llm-key parameter or set {args.llm.upper()}_API_KEY environment variable")
            sys.exit(1)
    
    # Create extractor
    print("=" * 60)
    print("Starting Legal Document Extractor...")
    print(f"   LLM: {args.llm} / {args.model}")
    print(f"   Output: {args.output}")
    print("=" * 60)
    
    extractor = LegalDocumentExtractor(
        llama_parse_api_key=args.llama_key,
        llm_provider=args.llm,
        llm_api_key=llm_key,
        llm_model=args.model,
        output_dir=args.output,
        markdown_dir=args.markdown_dir,
        chunk_size=args.chunk_size
    )
    
    # Start processing
    try:
        if args.file:
            # Single file
            print(f"\n Processing single file: {args.file}")
            result = extractor.process_single_document(args.file)
            
            if result['status'] == 'success':
                print(f"\n Success!")
                print(f"   JSON: {result['json_path']}")
                print(f"   Markdown: {result['markdown_path']}")
                print(f"   Time: {result['processing_time']:.2f} seconds")
            else:
                print(f"\n Error: {result['error']}")
                sys.exit(1)
        
        elif args.batch:
            # Batch processing
            print(f"\n Starting batch processing: {len(args.batch)} files")
            results = extractor.process_batch(args.batch)
            
            success_count = sum(1 for r in results if r['status'] == 'success')
            print(f"\n Successful: {success_count}/{len(results)}")
            
            if success_count < len(results):
                print("\n Failed files:")
                for r in results:
                    if r['status'] == 'failed':
                        print(f"   - {r['file']}: {r['error']}")
        
        elif args.directory:
            # Process directory
            print(f"\n Processing directory: {args.directory}")
            print(f"   Pattern: {args.pattern}")
            results = extractor.process_directory(args.directory, args.pattern)
            
            if not results:
                print(f"\n  No files found!")
                sys.exit(1)
            
            success_count = sum(1 for r in results if r['status'] == 'success')
            print(f"\n Successful: {success_count}/{len(results)}")
    
    except KeyboardInterrupt:
        print("\n\n Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print(" Processing completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
