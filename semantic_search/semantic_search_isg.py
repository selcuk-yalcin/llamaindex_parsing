"""
Semantic Search - OHS Legislation (Turkish)
Multi-AI Provider System with OpenAI GPT-4, Google Gemini, and Response Length Control
"""

import warnings
warnings.filterwarnings('ignore')

import sys
import os
import time
import torch
import re
from dotenv import load_dotenv
import PyPDF2
from openai import OpenAI
import google.generativeai as genai
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from tqdm.auto import tqdm

# Add DLAIUtils to path
sys.path.append('../../../../DLAIUtils')
from DLAIUtils import Utils

# Load environment variables from .env file
load_dotenv()

# ==================== CONFIGURATION ====================

# Load API keys from .env file
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Verify Pinecone API key is loaded
if not PINECONE_API_KEY or PINECONE_API_KEY == 'your_pinecone_api_key_here':
    raise ValueError("Please set PINECONE_API_KEY in .env file")

# Configure Google Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("✓ API keys loaded from .env file (OpenAI + Google Gemini)")
else:
    print("✓ API keys loaded from .env file (OpenAI only)")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ==================== PDF PROCESSING ====================

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text


def split_text_into_chunks(text, chunk_size=800, overlap=200):
    """Split text into overlapping chunks at sentence boundaries"""
    # Split into sentences (Turkish-aware)
    sentence_endings = r'[.!?]\s+'
    sentences = re.split(sentence_endings, text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # If adding this sentence exceeds chunk_size and we have content, save chunk
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Keep overlap: start new chunk with last part of previous chunk
            words = current_chunk.split()
            overlap_words = words[-int(len(words) * 0.2):] if len(words) > 5 else []
            current_chunk = ' '.join(overlap_words) + ' ' + sentence
        else:
            current_chunk += ' ' + sentence
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def clean_text(text):
    """Clean and prepare text"""
    # Replace problematic characters with ASCII equivalents
    text = text.replace('–', '-')  # en dash
    text = text.replace('—', '-')  # em dash
    text = text.replace(''', "'")  # left single quotation mark
    text = text.replace(''', "'")  # right single quotation mark
    text = text.replace('"', '"')  # left double quotation mark
    text = text.replace('"', '"')  # right double quotation mark
    # Keep Turkish characters but remove other problematic Unicode
    return text


# ==================== MODEL SETUP ====================

def setup_model():
    """Setup sentence transformer model"""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    if device != 'cuda':
        print('Sorry no cuda.')
    model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
    return model


# ==================== PINECONE SETUP ====================

def setup_pinecone(model):
    """Setup Pinecone index"""
    utils = Utils()
    pinecone = Pinecone(api_key=PINECONE_API_KEY)
    INDEX_NAME = utils.create_dlai_index_name('isg')
    
    # Check and delete existing index if present
    if INDEX_NAME in [index.name for index in pinecone.list_indexes()]:
        print(f"Deleting existing index: {INDEX_NAME}")
        pinecone.delete_index(INDEX_NAME)
        time.sleep(5)  # Wait for deletion to complete
    
    print(f"Creating new index: {INDEX_NAME}")
    pinecone.create_index(
        name=INDEX_NAME, 
        dimension=model.get_sentence_embedding_dimension(), 
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )
    
    # Wait for index to be ready
    print("Waiting for index to be ready...")
    time.sleep(10)
    
    # Connect to index
    index = pinecone.Index(INDEX_NAME)
    print(f"✓ Index ready: {index}")
    print(f"✓ Index stats: {index.describe_index_stats()}")
    
    return index


# ==================== EMBEDDINGS ====================

def upload_embeddings(index, model, chunks, batch_size=100):
    """Create embeddings and upload to Pinecone"""
    # Create a mapping to store the actual text (for later retrieval)
    text_mapping = {i: text for i, text in enumerate(chunks)}
    
    print(f"Total chunks to process: {len(chunks)}")
    
    for i in tqdm(range(0, len(chunks), batch_size)):
        # find end of batch
        i_end = min(i + batch_size, len(chunks))
        # create IDs batch
        ids = [f"isg_{x}" for x in range(i, i_end)]
        # create embeddings
        xc = model.encode(chunks[i:i_end])
        # create metadata batch - store only chunk_id to avoid encoding issues
        metadatas = [{'chunk_id': idx} for idx in range(i, i_end)]
        # create records list for upsert with proper format
        records = [
            {
                'id': id_,
                'values': values.tolist(),
                'metadata': metadata
            }
            for id_, values, metadata in zip(ids, xc, metadatas)
        ]
        # upsert to Pinecone
        index.upsert(vectors=records)
    
    print(f"\n✓ Successfully uploaded {len(chunks)} ISG mevzuat chunks to Pinecone")
    print(f"Text mapping created with {len(text_mapping)} entries")
    
    return text_mapping


# ==================== QUERY FUNCTION ====================

def run_query(query, index, model, text_mapping, use_ai=True, ai_provider="openai", 
              use_reasoning=False, max_length="normal", top_k=5):
    """
    Query ISG legislation with semantic search and optional AI enhancement
    
    Args:
        query: The question to ask (in Turkish)
        index: Pinecone index
        model: SentenceTransformer model
        text_mapping: Dictionary mapping chunk_id to text
        use_ai: Whether to use AI for response synthesis (default: True)
        ai_provider: "openai", "gemini", or "none" (default: "openai")
        use_reasoning: Use advanced reasoning models (default: False)
        max_length: "short" (3-4 sentences), "medium" (5-7 sentences), or "normal" (detailed)
        top_k: Number of relevant chunks to retrieve (default: 5)
    """
    embedding = model.encode(query).tolist()
    results = index.query(top_k=top_k, vector=embedding, include_metadata=True, include_values=False)
    
    if not use_ai or ai_provider == "none":
        # Simple mode: just print the chunks
        print("🔍 Most Relevant Results:\n")
        for i, result in enumerate(results['matches'], 1):
            chunk_id = result['metadata']['chunk_id']
            text = text_mapping.get(chunk_id, "Text not found")
            print(f"{i}. [Score: {round(result['score'], 2)}]\n{text}\n")
    else:
        # AI mode: use AI to synthesize a better answer
        if ai_provider == "gemini":
            if use_reasoning:
                print("🧠 Deep Analysis with Gemini 2.0 Flash Thinking:\n")
            else:
                print("🤖 Enhanced Response with Gemini 2.0 Flash:\n")
        else:  # openai
            if use_reasoning:
                print("🧠 Deep Analysis with GPT-4 (o1 Reasoning):\n")
            else:
                print("🤖 Enhanced Response with GPT-4 Turbo:\n")
        
        # Gather relevant chunks
        relevant_texts = []
        for result in results['matches']:
            chunk_id = result['metadata']['chunk_id']
            text = text_mapping.get(chunk_id, "")
            if text:
                relevant_texts.append(text)
        
        context = "\n\n".join(relevant_texts)
        
        # Length-aware instructions
        if max_length == "short":
            length_instruction = "VERY IMPORTANT: Limit your response to maximum 3-4 sentences. Only mention the most important points."
            max_tokens = 300
        elif max_length == "medium":
            length_instruction = "Keep your response concise (5-7 sentences)."
            max_tokens = 500
        else:  # normal
            length_instruction = "Provide a detailed but concise response."
            max_tokens = 2048
        
        system_prompt = f"""You are an expert on OHS (Occupational Health and Safety) legislation. 
Answer questions based ONLY on the provided legislation texts. 
Provide answers in proper Turkish, in a bullet-point format, and reference relevant articles.
{length_instruction}"""

        user_prompt = f"""Answer the question based on the following OHS legislation texts.

Question: {query}

Legislation Texts:
{context}

Please:
1. Answer the question fully and clearly
2. Use ONLY the information from the provided legislation texts
3. Provide the answer in proper Turkish, in bullet-point format
4. Reference relevant articles
5. Give practical examples
6. Highlight important points
{length_instruction}"""

        # Call AI provider
        if ai_provider == "gemini":
            if use_reasoning:
                # Use Gemini 1.5 Pro with extended thinking
                gemini_model = genai.GenerativeModel('gemini-1.5-pro-latest')
                response = gemini_model.generate_content(
                    f"{system_prompt}\n\n{user_prompt}",
                    generation_config={
                        'temperature': 0.3,
                        'max_output_tokens': max_tokens
                    }
                )
                print("💭 Used Gemini 1.5 Pro (with reasoning)\n")
                print(response.text)
            else:
                # Use Gemini 1.5 Flash (fastest, FREE)
                gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = gemini_model.generate_content(
                    f"{system_prompt}\n\n{user_prompt}",
                    generation_config={
                        'temperature': 0.3,
                        'max_output_tokens': max_tokens
                    }
                )
                print(response.text)
        else:  # openai
            if use_reasoning:
                # Use o1 model for deep reasoning
                response = openai_client.chat.completions.create(
                    model="o1-preview",
                    messages=[
                        {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                    ]
                )
                print("💭 Used O1 Reasoning Model (with internal reasoning)\n")
                print(response.choices[0].message.content)
            else:
                # Use GPT-4 for standard response
                response = openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=max_tokens
                )
                print(response.choices[0].message.content)
        
        print("\n" + "="*80)
        print(f"📚 Source Texts (showing top {min(3, len(relevant_texts))}):")
        for i, text in enumerate(relevant_texts[:3], 1):
            print(f"\n{i}. {text[:200]}...")
    
    return results


# ==================== MAIN ====================

def main():
    """Main function to setup and run semantic search"""
    
    print("="*80)
    print("ISG MEVZUAT SEMANTIC SEARCH")
    print("Multi-AI Provider System (OpenAI GPT-4 + Google Gemini)")
    print("="*80 + "\n")
    
    # 1. Load and process PDF
    print("📄 Loading ISG Mevzuat PDF...")
    pdf_path = 'data/isg_mevzuat.pdf'
    pdf_text = extract_text_from_pdf(pdf_path)
    print(f"✓ Extracted {len(pdf_text)} characters\n")
    
    # 2. Split into chunks
    print("✂️  Splitting text into chunks...")
    text_chunks = split_text_into_chunks(pdf_text, chunk_size=800, overlap=200)
    print(f"✓ Created {len(text_chunks)} chunks\n")
    
    # 3. Clean chunks
    print("🧹 Cleaning text...")
    cleaned_chunks = [clean_text(chunk) for chunk in text_chunks if len(chunk.strip()) > 50]
    print(f"✓ Cleaned {len(cleaned_chunks)} chunks\n")
    
    # 4. Setup model
    print("🤖 Loading sentence transformer model...")
    model = setup_model()
    print("✓ Model loaded\n")
    
    # 5. Setup Pinecone
    print("📊 Setting up Pinecone index...")
    index = setup_pinecone(model)
    print()
    
    # 6. Upload embeddings
    print("⬆️  Uploading embeddings to Pinecone...")
    text_mapping = upload_embeddings(index, model, cleaned_chunks)
    print()
    
    # 7. Example queries
    print("="*80)
    print("EXAMPLE QUERIES")
    print("="*80 + "\n")
    
    # Example 1: Gemini with reasoning
    print("\n" + "="*80)
    print("EXAMPLE 1: Gemini 1.5 Pro (FREE, with reasoning)")
    print("="*80)
    run_query(
        'iş yerinde güvenlik önlemleri nelerdir?',
        index, model, text_mapping,
        use_ai=True,
        ai_provider="gemini",
        use_reasoning=True,
        max_length="normal"
    )
    
    # Example 2: Gemini short response
    print("\n\n" + "="*80)
    print("EXAMPLE 2: Gemini 1.5 Flash (FREE, short response - FASTEST!)")
    print("="*80)
    run_query(
        'işveren sorumlulukları nelerdir?',
        index, model, text_mapping,
        use_ai=True,
        ai_provider="gemini",
        max_length="short"
    )
    
    # Example 3: No AI (raw chunks)
    print("\n\n" + "="*80)
    print("EXAMPLE 3: No AI (raw semantic search results)")
    print("="*80)
    run_query(
        'çalışan hakları nelerdir?',
        index, model, text_mapping,
        use_ai=False
    )
    
    print("\n" + "="*80)
    print("✓ Setup complete! You can now use run_query() for custom queries.")
    print("="*80)
    
    return index, model, text_mapping


if __name__ == "__main__":
    index, model, text_mapping = main()
    
    # Interactive mode
    print("\n\n" + "="*80)
    print("INTERACTIVE MODE")
    print("="*80)
    print("\nYou can now run custom queries using:")
    print("run_query(query, index, model, text_mapping, use_ai=True, ai_provider='gemini')")
    print("\nExamples:")
    print("- run_query('iş kazası nedir?', index, model, text_mapping, ai_provider='gemini')")
    print("- run_query('işveren yükümlülükleri', index, model, text_mapping, ai_provider='openai', max_length='short')")
    print("- run_query('güvenlik eğitimi', index, model, text_mapping, use_ai=False)")
