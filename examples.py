"""
Usage Examples - Çeşitli kullanım senaryoları
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# SENARYO 1: TEK DÖKÜMAN İŞLEME
# ============================================================================

def example_single_document():
    """Tek bir PDF dökümanını işle"""
    from batch_extractor import LegalDocumentExtractor
    
    print("=" * 60)
    print("SENARYO 1: Tek Döküman İşleme")
    print("=" * 60)
    
    extractor = LegalDocumentExtractor(
        llama_parse_api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
        llm_provider="openai",
        llm_api_key=os.getenv("OPENAI_API_KEY"),
        llm_model="gpt-4o"
    )
    
    # Örnek dosya (gerçek dosya yolunuzu buraya yazın)
    result = extractor.process_single_document("./data/6331_sayili_kanun.pdf")
    
    if result['status'] == 'success':
        print(f"✅ Başarılı!")
        print(f"   JSON: {result['json_path']}")
        print(f"   Süre: {result['processing_time']:.2f} saniye")
    else:
        print(f"❌ Hata: {result['error']}")


# ============================================================================
# SENARYO 2: BATCH İŞLEM
# ============================================================================

def example_batch_processing():
    """Birden fazla dökümanı toplu işle"""
    from batch_extractor import LegalDocumentExtractor
    
    print("\n" + "=" * 60)
    print("SENARYO 2: Batch İşlem")
    print("=" * 60)
    
    extractor = LegalDocumentExtractor(
        llama_parse_api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
        llm_provider="openai",
        llm_api_key=os.getenv("OPENAI_API_KEY"),
        llm_model="gpt-4o"
    )
    
    # İşlenecek dosyalar
    files = [
        "./data/6331_sayili_kanun.pdf",
        "./data/4857_sayili_kanun.pdf",
        "./data/5510_sayili_kanun.pdf"
    ]
    
    results = extractor.process_batch(files)
    
    # Sonuçları analiz et
    success = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']
    
    print(f"\n✅ Başarılı: {len(success)}/{len(files)}")
    
    if failed:
        print("\n❌ Başarısız dosyalar:")
        for r in failed:
            print(f"   - {r['file']}: {r['error']}")


# ============================================================================
# SENARYO 3: KLASÖR İŞLEME
# ============================================================================

def example_directory_processing():
    """Bir klasördeki tüm PDF'leri işle"""
    from batch_extractor import LegalDocumentExtractor
    
    print("\n" + "=" * 60)
    print("SENARYO 3: Klasör İşleme")
    print("=" * 60)
    
    extractor = LegalDocumentExtractor(
        llama_parse_api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
        llm_provider="openai",
        llm_api_key=os.getenv("OPENAI_API_KEY"),
        llm_model="gpt-4o"
    )
    
    # Klasördeki tüm PDF'leri işle
    results = extractor.process_directory(
        directory="./data/laws",
        pattern="*.pdf"
    )
    
    print(f"\n✅ Toplam {len(results)} dosya işlendi")


# ============================================================================
# SENARYO 4: GEMİNİ KULLANIMI
# ============================================================================

def example_gemini_usage():
    """Gemini LLM kullanarak işle (daha ekonomik)"""
    from batch_extractor import LegalDocumentExtractor
    
    print("\n" + "=" * 60)
    print("SENARYO 4: Gemini Kullanımı")
    print("=" * 60)
    
    extractor = LegalDocumentExtractor(
        llama_parse_api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
        llm_provider="gemini",
        llm_api_key=os.getenv("GEMINI_API_KEY"),
        llm_model="gemini-1.5-pro"
    )
    
    result = extractor.process_single_document("./data/6331_sayili_kanun.pdf")
    print(f"Sonuç: {result['status']}")


# ============================================================================
# SENARYO 5: MONGODB ENTEGRASYONU
# ============================================================================

def example_mongodb_integration():
    """Extract edilen verileri MongoDB'ye kaydet"""
    from mongodb_integration import LegalDocumentDatabase
    
    print("\n" + "=" * 60)
    print("SENARYO 5: MongoDB Entegrasyonu")
    print("=" * 60)
    
    # Database bağlantısı
    db = LegalDocumentDatabase(
        mongodb_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
        database_name="legal_documents"
    )
    
    # Extract edilmiş JSON'ları toplu yükle
    db.bulk_insert_from_json_files("./extracted_laws")
    
    # Arama yap
    results = db.search_articles("iş güvenliği", limit=5)
    print(f"\n🔍 '{len(results)}' arama sonucu bulundu")
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['law_number']} - {result['index']}: {result.get('title', 'Başlık yok')}")
        print(f"   {result['text_content'][:100]}...")
    
    # İstatistikler
    stats = db.get_statistics()
    print(f"\n📊 Veritabanı İstatistikleri:")
    print(f"   Toplam kanun: {stats['total_laws']}")
    print(f"   Toplam madde: {stats['total_articles']}")
    
    db.close()


# ============================================================================
# SENARYO 6: ÇAPRAZ REFERANS ANALİZİ
# ============================================================================

def example_cross_reference_analysis():
    """Madde atıflarını analiz et"""
    from mongodb_integration import LegalDocumentDatabase
    
    print("\n" + "=" * 60)
    print("SENARYO 6: Çapraz Referans Analizi")
    print("=" * 60)
    
    db = LegalDocumentDatabase()
    
    # Belirli bir maddenin atıflarını bul
    law_number = "6331"
    article_index = "Madde 4"
    
    cross_refs = db.get_cross_referenced_articles(law_number, article_index)
    
    print(f"\n📎 {law_number} {article_index} Atıf Analizi:")
    
    print(f"\n   Bu maddenin atıf yaptığı maddeler ({len(cross_refs['referenced_by_this'])}):")
    for ref in cross_refs['referenced_by_this'][:5]:
        print(f"   - {ref['index']}: {ref.get('title', 'Başlık yok')}")
    
    print(f"\n   Bu maddeye atıf yapan maddeler ({len(cross_refs['referring_to_this'])}):")
    for ref in cross_refs['referring_to_this'][:5]:
        print(f"   - {ref['index']}: {ref.get('title', 'Başlık yok')}")
    
    db.close()


# ============================================================================
# SENARYO 7: CEZA MADDELERİ ANALİZİ
# ============================================================================

def example_penalty_analysis():
    """Ceza içeren maddeleri analiz et"""
    from mongodb_integration import LegalDocumentDatabase
    
    print("\n" + "=" * 60)
    print("SENARYO 7: Ceza Maddeleri Analizi")
    print("=" * 60)
    
    db = LegalDocumentDatabase()
    
    # Ceza içeren kanunları getir
    laws_with_penalties = db.get_articles_with_penalties()
    
    print(f"\n⚖️  Ceza içeren kanun sayısı: {len(laws_with_penalties)}")
    
    for law in laws_with_penalties[:3]:
        print(f"\n📜 {law['law_metadata']['law_number']} - {law['law_metadata']['law_title']}")
        print(f"   Ceza sayısı: {len(law['penalties'])}")
        
        for penalty in law['penalties'][:2]:
            print(f"   - {penalty['violated_article']}: {penalty['penalty_amount']}")
    
    db.close()


# ============================================================================
# SENARYO 8: JSON VALIDATION
# ============================================================================

def example_json_validation():
    """Extract edilmiş JSON'un şemaya uygunluğunu kontrol et"""
    import json
    from pydantic_models import LegalDocument
    
    print("\n" + "=" * 60)
    print("SENARYO 8: JSON Validasyon")
    print("=" * 60)
    
    # JSON dosyasını oku
    with open("./extracted_laws/6331_sayili_kanun.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    try:
        # Pydantic ile validate et
        legal_doc = LegalDocument(**data)
        
        print("✅ JSON şemaya uygun!")
        print(f"\n📊 Döküman İstatistikleri:")
        print(f"   Kanun: {legal_doc.law_metadata.law_number} - {legal_doc.law_metadata.law_title}")
        print(f"   Bölüm sayısı: {len(legal_doc.sections)}")
        print(f"   Madde sayısı: {len(legal_doc.content_structure)}")
        print(f"   Tanım sayısı: {len(legal_doc.definitions)}")
        print(f"   Ceza sayısı: {len(legal_doc.penalties)}")
        
    except Exception as e:
        print(f"❌ Validasyon hatası: {str(e)}")


# ============================================================================
# ANA PROGRAM
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("Legal Document Extractor - Kullanım Örnekleri")
    print("=" * 60)
    
    scenarios = {
        "1": ("Tek Döküman İşleme", example_single_document),
        "2": ("Batch İşlem", example_batch_processing),
        "3": ("Klasör İşleme", example_directory_processing),
        "4": ("Gemini Kullanımı", example_gemini_usage),
        "5": ("MongoDB Entegrasyonu", example_mongodb_integration),
        "6": ("Çapraz Referans Analizi", example_cross_reference_analysis),
        "7": ("Ceza Maddeleri Analizi", example_penalty_analysis),
        "8": ("JSON Validasyon", example_json_validation),
    }
    
    print("\nHangi senaryoyu çalıştırmak istersiniz?")
    for key, (name, _) in scenarios.items():
        print(f"  {key}. {name}")
    print(f"  0. Tümünü çalıştır")
    print(f"  q. Çık")
    
    choice = input("\nSeçiminiz: ").strip()
    
    if choice == "q":
        sys.exit(0)
    elif choice == "0":
        for _, (name, func) in scenarios.items():
            try:
                func()
            except Exception as e:
                print(f"\n❌ Hata ({name}): {str(e)}")
    elif choice in scenarios:
        _, func = scenarios[choice]
        try:
            func()
        except Exception as e:
            print(f"\n❌ Hata: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Geçersiz seçim!")
    
    print("\n✨ İşlem tamamlandı!")
