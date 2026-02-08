"""
CLI Tool - Yapılandırılmış Hukuki Belge Çıkarıcı
Kullanım: python extract_structured.py <input_dir> [output_dir]
"""

import sys
import asyncio
from pathlib import Path
from structured_extractor import StructuredExtractor


async def main():
    # Argüman kontrolü
    if len(sys.argv) < 2:
        print("""
╔════════════════════════════════════════════════════════════════╗
║   Yapılandırılmış Hukuki Belge Çıkarıcı                        ║
║   LlamaParse + OpenRouter LLM                                  ║
╚════════════════════════════════════════════════════════════════╝

KULLANIM:
  python extract_structured.py <input_directory> [output_directory]

ÖRNEK:
  python extract_structured.py data/kanunlar extracted_laws
  python extract_structured.py data/yonetmelikler

ÖZELLİKLER:
  ✅ PDF → Yapılandırılmış JSON
  ✅ Madde, fıkra, bent hiyerarşisi
  ✅ Metadata ve tarih bilgileri
  ✅ Atıf tespiti (cross-references)
  ✅ Ceza hükümleri analizi
  ✅ Tablo çıkarma (markdown)
  ✅ Pydantic validation

NOT:
  MongoDB entegrasyonu için Legislation_RAG kullanın

ÇIKTI FORMATI:
  JSON şema: landingextr.json
  Model: pydantic_models.py → LegalDocument
        """)
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "extracted_laws"
    
    # Klasör kontrolü
    if not Path(input_dir).exists():
        print(f"❌ Hata: {input_dir} klasörü bulunamadı!")
        sys.exit(1)
    
    # İşlemi başlat
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║   İşlem Başlatılıyor                                           ║
╚════════════════════════════════════════════════════════════════╝

📂 Input:     {input_dir}
📁 Output:    {output_dir}
    """)
    
    extractor = StructuredExtractor()
    await extractor.process_directory(input_dir, output_dir)
    
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║   ✅ İşlem Tamamlandı                                          ║
╚════════════════════════════════════════════════════════════════╝

Çıktılar: {output_dir}/
    """)


if __name__ == "__main__":
    asyncio.run(main())
