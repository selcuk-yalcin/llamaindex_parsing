"""
Quick test - Tek dosya ile test
Sadece JSON çıktısı
"""
import asyncio
from structured_extractor import StructuredExtractor

async def test():
    extractor = StructuredExtractor()
    
    # Test dosyası: İş Sağlığı ve Güvenliği Kanunu (en küçük dosya)
    test_file = "data/laws/6331-sayili-is-sagligi-ve-guvenligi-kanunu.pdf"
    
    print("🧪 TEST BAŞLADI")
    print("=" * 80)
    
    result = await extractor.process_file(
        test_file,
        "test_output"
    )
    
    print("=" * 80)
    print("✅ Test tamamlandı!")
    print(f"📄 Çıktı: {result}")

if __name__ == "__main__":
    asyncio.run(test())
