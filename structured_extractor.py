"""
Structured Legal Document Extractor
LlamaParse + OpenRouter LLM ile hukuki belgeleri yapılandırılmış JSON'a çevirme
"""

import os
import json
import asyncio
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

from llama_parse import LlamaParse
from pydantic_models import LegalDocument
from config import Config

import httpx

load_dotenv()


class StructuredExtractor:
    """LlamaParse + OpenRouter ile yapılandırılmış çıktı üretici"""
    
    def __init__(self):
        self.parser = LlamaParse(
            api_key=Config.LLAMAPARSE_API_KEY,
            result_type=Config.LLAMAPARSE_RESULT_TYPE,
            language=Config.LLAMAPARSE_LANGUAGE,
            premium_mode=Config.LLAMAPARSE_PREMIUM_MODE,
            verbose=True
        )
        
        self.openrouter_key = Config.OPENROUTER_API_KEY
        self.model = Config.DEFAULT_MODEL
        
    async def parse_pdf(self, pdf_path: str) -> str:
        """PDF'i markdown'a çevir"""
        print(f"📄 Parsing: {pdf_path}")
        documents = await self.parser.aload_data(pdf_path)
        
        # Tüm sayfa içeriklerini birleştir
        full_text = "\n\n".join([doc.text for doc in documents])
        print(f"✅ Parsed {len(documents)} pages")
        return full_text
    
    async def extract_structured_json(self, markdown_text: str, filename: str) -> dict:
        """Markdown metni yapılandırılmış JSON'a çevir"""
        print("🤖 LLM ile yapılandırma başlatılıyor...")
        
        # Metin uzunluğunu kontrol et
        text_length = len(markdown_text)
        print(f"📝 Metin uzunluğu: {text_length:,} karakter")
        
        # Çok uzunsa kısalt (context window limiti için)
        max_text_length = 200000  # ~200k karakter
        if text_length > max_text_length:
            print(f"⚠️ Metin çok uzun, ilk {max_text_length:,} karakter kullanılıyor")
            markdown_text = markdown_text[:max_text_length]
        
        # JSON şemasını al
        schema = LegalDocument.model_json_schema()
        
        # LLM prompt'u
        system_prompt = """Sen bir hukuki belge analiz uzmanısın. 
Verilen Türkçe kanun/yönetmelik metnini JSON şemasına göre yapılandır.

KURALLAR:
1. Tüm maddeleri hiyerarşik olarak çıkar
2. Kanun metadata'sını ekle (başlık, numara, tarih)
3. Tanımları ayrı array'e al
4. Ceza hükümlerini penalties'e ekle
5. Madde atıflarını tespit et
6. SADECE VALID JSON döndür"""

        user_prompt = f"""Belge: {filename}

METIN:
{markdown_text}

ŞEMA:
{json.dumps(schema, indent=2, ensure_ascii=False)[:5000]}

Yukarıdaki metni JSON olarak yapılandır."""

        # OpenRouter API çağrısı
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{Config.OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "HTTP-Referer": "https://github.com/your-repo",
                    "X-Title": "Legal Document Extractor"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 100000,  # Increased for long documents
                    "response_format": {"type": "json_object"}
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Debug: JSON uzunluğunu yazdır
            print(f"📊 JSON yanıt uzunluğu: {len(content)} karakter")
            
            # JSON parse et - hata yönetimi ile
            try:
                structured_data = json.loads(content)
                print("✅ Yapılandırma tamamlandı")
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parse hatası: {e}")
                print(f"🔍 Yanıtın ilk 500 karakteri:\n{content[:500]}")
                print(f"🔍 Yanıtın son 500 karakteri:\n{content[-500:]}")
                
                # Fallback: Eksik JSON'u tamamlamaya çalış
                print("🔧 JSON düzeltme deneniyor...")
                # En basit çözüm: JSON'u temizle ve tekrar parse et
                import re
                # Trailing comma'ları temizle
                content = re.sub(r',(\s*[}\]])', r'\1', content)
                try:
                    structured_data = json.loads(content)
                    print("✅ Düzeltme başarılı!")
                except:
                    print("❌ JSON düzeltilemedi, ham veri kaydediliyor")
                    raise
            
            return structured_data
    
    async def process_file(self, pdf_path: str, output_dir: str = "extracted_laws") -> str:
        """Tek bir PDF dosyasını işle"""
        pdf_file = Path(pdf_path)
        
        # 1. PDF'i parse et
        markdown_text = await self.parse_pdf(str(pdf_file))
        
        # 2. LLM ile yapılandır
        try:
            structured_data = await self.extract_structured_json(
                markdown_text, 
                pdf_file.stem
            )
        except Exception as e:
            print(f"❌ LLM yapılandırma hatası: {e}")
            print("💡 Raw markdown kaydediliyor...")
            
            # Raw markdown'ı kaydet
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            markdown_file = output_path / f"{pdf_file.stem}_raw.md"
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(markdown_text)
            print(f"💾 Raw markdown: {markdown_file}")
            raise
        
        # 3. Pydantic ile validate et
        try:
            validated = LegalDocument(**structured_data)
            final_json = validated.model_dump()
            print("✅ Validation başarılı")
        except Exception as e:
            print(f"⚠️ Validation hatası: {e}")
            print("🔧 Raw JSON kullanılıyor...")
            final_json = structured_data
        
        # 4. JSON dosyasını kaydet
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        output_file = output_path / f"{pdf_file.stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_json, f, ensure_ascii=False, indent=2)
        
        print(f"💾 JSON kaydedildi: {output_file}")
        
        return str(output_file)
    
    async def process_directory(self, input_dir: str, output_dir: str = "extracted_laws"):
        """Bir klasördeki tüm PDF'leri işle"""
        input_path = Path(input_dir)
        pdf_files = list(input_path.glob("*.pdf"))
        
        if not pdf_files:
            print(f"❌ {input_dir} içinde PDF bulunamadı")
            return
        
        print(f"📁 {len(pdf_files)} PDF bulundu")
        
        for pdf_file in pdf_files:
            try:
                await self.process_file(str(pdf_file), output_dir)
                print("-" * 80)
            except Exception as e:
                print(f"❌ Hata ({pdf_file.name}): {e}")
                continue


async def main():
    """Ana fonksiyon - test için"""
    extractor = StructuredExtractor()
    
    # Örnek: data klasöründeki tüm PDF'leri işle
    data_dir = Path(__file__).parent / "data"
    
    if data_dir.exists():
        await extractor.process_directory(str(data_dir))
    else:
        print(f"❌ {data_dir} klasörü bulunamadı")
        print("💡 Kullanım: data/ klasörüne PDF dosyalarınızı ekleyin")


if __name__ == "__main__":
    asyncio.run(main())
