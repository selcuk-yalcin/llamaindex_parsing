"""
Batch Document Processor - Multi Legal Document Processing System
Structured data extraction with LlamaParse + LLM
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from tqdm import tqdm

from llama_parse import LlamaParse
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.openai import OpenAI
from llama_index.llms.gemini import Gemini
from llama_index.llms.openrouter import OpenRouter

from pydantic_models import LegalDocument


# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LegalDocumentExtractor:
    """
    Main class for parsing legal documents and converting to structured JSON format
    """
    
    def __init__(
        self,
        llama_parse_api_key: str,
        llm_provider: str = "openai",
        llm_api_key: Optional[str] = None,
        llm_model: str = "gpt-4o",
        output_dir: str = "./extracted_documents",
        markdown_dir: str = "./parsed_markdown",
        chunk_size: int = 50000  # Chunk size for token limit
    ):
        """
        Args:
            llama_parse_api_key: LlamaCloud API key
            llm_provider: "openai", "gemini", or "openrouter"
            llm_api_key: OpenAI, Gemini or OpenRouter API key
            llm_model: Model to use
                For OpenRouter: "anthropic/claude-3.5-sonnet", "openai/gpt-4o", "google/gemini-pro-1.5"
                For OpenAI: "gpt-4o", "gpt-4-turbo"
                For Gemini: "gemini-1.5-pro", "gemini-1.5-flash"
            output_dir: Directory to save extracted JSONs
            markdown_dir: Directory to save parsed markdowns
            chunk_size: Chunk size for long documents
        """
        self.llama_parse_api_key = llama_parse_api_key
        self.output_dir = Path(output_dir)
        self.markdown_dir = Path(markdown_dir)
        self.chunk_size = chunk_size
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize LlamaParse
        self.parser = LlamaParse(
            api_key=llama_parse_api_key,
            result_type="markdown",
            verbose=True,
            language="tr",  # For Turkish
            num_workers=4,
            invalidate_cache=False
        )
        
        # Initialize LLM
        if llm_provider == "openrouter":
            self.llm = OpenRouter(
                api_key=llm_api_key,
                model=llm_model,
                temperature=0.1,  # For deterministic output
                max_tokens=16000
            )
        elif llm_provider == "openai":
            self.llm = OpenAI(model=llm_model, api_key=llm_api_key)
        elif llm_provider == "gemini":
            self.llm = Gemini(model=llm_model, api_key=llm_api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}. Available: openai, gemini, openrouter")
        
        # Create extraction program
        self.extraction_program = LLMTextCompletionProgram.from_defaults(
            output_cls=LegalDocument,
            prompt_template_str=self._get_extraction_prompt(),
            llm=self.llm,
            verbose=True
        )
        
        logger.info(f"LegalDocumentExtractor initialized - LLM: {llm_provider}/{llm_model}")
    
    def _get_extraction_prompt(self) -> str:
        """Optimized prompt template for extraction"""
        return """You are an AI assistant specialized in the Turkish legal system. 
Carefully analyze the following legal text and extract it according to the specified JSON structure.

IMPORTANT RULES:
1. **Preserve hierarchy**: PART > CHAPTER > ARTICLE > PARAGRAPH > SUB_CLAUSE
2. **Index article numbers correctly**: "Article 1", "Article 2" format
3. **Place paragraphs and clauses in children**: "(1)", "(2)" paragraphs, "a)", "b)" clauses
4. **Identify references**: Add expressions like "...according to the article" to cross_references
5. **Extract definitions**: Find terms from articles titled "Definitions"
6. **Identify penalty articles**: Add articles containing administrative fines to penalties
7. **Capture Official Gazette info**: Get the Official Gazette date and number from the beginning of the law

LEGAL TEXT:
---------------------
{text}
---------------------

Analyze the text above and return in JSON format.
"""
    
    def parse_document(self, file_path: str) -> str:
        """
        Parses PDF document and converts to Markdown
        
        Args:
            file_path: PDF file path
            
        Returns:
            Markdown text
        """
        logger.info(f"Parsing document: {file_path}")
        
        try:
            documents = self.parser.load_data(file_path)
            full_text = "\n\n".join([doc.text for doc in documents])
            
            # Save markdown
            file_name = Path(file_path).stem
            markdown_path = self.markdown_dir / f"{file_name}.md"
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            logger.info(f"Markdown saved: {markdown_path}")
            logger.info(f"Total characters: {len(full_text)}")
            
            return full_text
        
        except Exception as e:
            logger.error(f"Parse error ({file_path}): {str(e)}")
            raise
    
    def extract_structured_data(self, markdown_text: str, source_file: str) -> LegalDocument:
        """
        Extracts structured data from markdown text
        
        Args:
            markdown_text: Parsed markdown text
            source_file: Source file name (for logging)
            
        Returns:
            LegalDocument object
        """
        logger.info(f"Starting structured data extraction: {source_file}")
        
        try:
            # Split long documents into chunks (for future use)
            if len(markdown_text) > self.chunk_size:
                logger.warning(f"Document too long ({len(markdown_text)} characters), chunking may be needed")
            
            # Extract with LLM
            result = self.extraction_program(text=markdown_text)
            
            logger.info(f"Extraction completed: {source_file}")
            logger.info(f"  - Number of articles: {len(result.content_structure)}")
            logger.info(f"  - Number of definitions: {len(result.definitions)}")
            logger.info(f"  - Number of penalties: {len(result.penalties)}")
            
            return result
        
        except Exception as e:
            logger.error(f"Extraction error ({source_file}): {str(e)}")
            raise
    
    def save_json(self, legal_doc: LegalDocument, output_filename: str) -> Path:
        """
        Saves LegalDocument object as JSON
        
        Args:
            legal_doc: LegalDocument object
            output_filename: Output file name
            
        Returns:
            Saved file path
        """
        output_path = self.output_dir / f"{output_filename}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(
                legal_doc.model_dump(),
                f,
                ensure_ascii=False,
                indent=2
            )
        
        logger.info(f"JSON saved: {output_path}")
        return output_path
    
    def process_single_document(self, file_path: str) -> Dict:
        """
        Processes a single document (parse + extract + save)
        
        Args:
            file_path: PDF file path
            
        Returns:
            Processing result information
        """
        start_time = datetime.now()
        file_name = Path(file_path).stem
        
        result = {
            "file": file_path,
            "status": "pending",
            "markdown_path": None,
            "json_path": None,
            "error": None,
            "processing_time": None
        }
        
        try:
            # 1. Parse
            markdown_text = self.parse_document(file_path)
            result["markdown_path"] = str(self.markdown_dir / f"{file_name}.md")
            
            # 2. Extract
            legal_doc = self.extract_structured_data(markdown_text, file_name)
            
            # 3. Save
            json_path = self.save_json(legal_doc, file_name)
            result["json_path"] = str(json_path)
            
            result["status"] = "success"
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.error(f"Document processing failed: {file_path} - {str(e)}")
        
        finally:
            end_time = datetime.now()
            result["processing_time"] = (end_time - start_time).total_seconds()
        
        return result
    
    def process_batch(self, file_paths: List[str]) -> List[Dict]:
        """
        Processes multiple documents in batch
        
        Args:
            file_paths: List of PDF file paths
            
        Returns:
            Processing results for each file
        """
        logger.info(f"Starting batch processing - Total files: {len(file_paths)}")
        
        results = []
        
        for file_path in tqdm(file_paths, desc="Processing documents"):
            result = self.process_single_document(file_path)
            results.append(result)
        
        # Summary report
        success_count = sum(1 for r in results if r["status"] == "success")
        failed_count = len(results) - success_count
        total_time = sum(r["processing_time"] for r in results)
        
        logger.info("=" * 50)
        logger.info("BATCH PROCESSING COMPLETED")
        logger.info(f"Total files: {len(file_paths)}")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Failed: {failed_count}")
        logger.info(f"Total time: {total_time:.2f} seconds")
        logger.info("=" * 50)
        
        # Save results as JSON
        summary_path = self.output_dir / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Batch summary saved: {summary_path}")
        
        return results
    
    def process_directory(self, directory: str, pattern: str = "*.pdf") -> List[Dict]:
        """
        Processes all PDFs in a directory
        
        Args:
            directory: Directory path
            pattern: File pattern (default: *.pdf)
            
        Returns:
            Processing results
        """
        dir_path = Path(directory)
        file_paths = list(dir_path.glob(pattern))
        
        logger.info(f"Scanning directory: {directory}")
        logger.info(f"Files found: {len(file_paths)}")
        
        return self.process_batch([str(f) for f in file_paths])


# Usage example
if __name__ == "__main__":
    # Get API Keys from environment variables
    LLAMA_PARSE_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY", "llx-...")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-...")
    
    # Create extractor
    extractor = LegalDocumentExtractor(
        llama_parse_api_key=LLAMA_PARSE_API_KEY,
        llm_provider="openai",
        llm_api_key=OPENAI_API_KEY,
        llm_model="gpt-4o",
        output_dir="./extracted_laws",
        markdown_dir="./parsed_markdown"
    )
    
    # Example 1: Process single file
    # result = extractor.process_single_document("./data/law_6331.pdf")
    # print(f"Result: {result}")
    
    # Example 2: Batch processing
    # files = [
    #     "./data/law_6331.pdf",
    #     "./data/law_4857.pdf",
    #     "./data/law_5510.pdf"
    # ]
    # results = extractor.process_batch(files)
    
    # Example 3: Process directory
    results = extractor.process_directory("./data/laws", pattern="*.pdf")
