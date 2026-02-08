"""
Test Script - Sistem testi için
"""

from pydantic_models import (
    LegalDocument, LawMetadata, OfficialGazette,
    Section, Definition, ContentStructure, ContentChild,
    Penalty, AmendmentSummary, LayoutAnalysis
)

def test_pydantic_models():
    """Pydantic modellerinin doğru çalıştığını test et"""
    print("🧪 Pydantic Modelleri Test Ediliyor...\n")
    
    # Örnek veri oluştur
    legal_doc = LegalDocument(
        law_metadata=LawMetadata(
            law_title="İş Sağlığı ve Güvenliği Kanunu",
            law_number="6331",
            acceptance_date="20.06.2012",
            publication_date="30.06.2012",
            official_gazette=OfficialGazette(
                date="30.06.2012",
                number="28339"
            )
        ),
        sections=[
            Section(
                section_title="BİRİNCİ BÖLÜM",
                section_heading="Amaç, Kapsam ve Tanımlar"
            )
        ],
        definitions=[
            Definition(
                term="İşveren",
                definition="Çalışanları istihdam eden gerçek veya tüzel kişi yahut tüzel kişiliği olmayan kurum ve kuruluşları"
            )
        ],
        content_structure=[
            ContentStructure(
                level="ARTICLE",
                index="Madde 1",
                title="Amaç",
                text_content="Bu Kanunun amacı; işyerlerinde iş sağlığı ve güvenliğinin sağlanması...",
                children=[
                    ContentChild(
                        level="PARAGRAPH",
                        index="(1)",
                        text_content="İşveren, çalışanların sağlık ve güvenliğini sağlamakla yükümlüdür.",
                        cross_references=["Madde 4", "Madde 5"]
                    )
                ],
                cross_references=[]
            )
        ],
        penalties=[
            Penalty(
                violated_article="Madde 26",
                penalty_amount="10.000 TL",
                penalty_logic="Her bir çalışan için ayrı ayrı uygulanır"
            )
        ],
        amendment_summary=[
            AmendmentSummary(
                effective_date="01.01.2023",
                affected_articles="Madde 4, 10, 15",
                amending_law_number="7417"
            )
        ],
        layout_analysis=[
            LayoutAnalysis(
                element_type="BODY_TEXT",
                content="Madde 1 - Amaç"
            )
        ]
    )
    
    # JSON'a çevir
    json_output = legal_doc.model_dump_json(indent=2, exclude_none=False)
    
    print("✅ Model başarıyla oluşturuldu!")
    print(f"\n📊 İstatistikler:")
    print(f"   - Bölüm sayısı: {len(legal_doc.sections)}")
    print(f"   - Tanım sayısı: {len(legal_doc.definitions)}")
    print(f"   - Madde sayısı: {len(legal_doc.content_structure)}")
    print(f"   - Ceza sayısı: {len(legal_doc.penalties)}")
    
    print(f"\n📄 JSON Çıktısı (ilk 500 karakter):")
    print(json_output[:500] + "...")
    
    # JSON'u dosyaya kaydet
    with open("test_output.json", "w", encoding="utf-8") as f:
        f.write(json_output)
    
    print(f"\n💾 Test çıktısı kaydedildi: test_output.json")
    
    return True


if __name__ == "__main__":
    try:
        test_pydantic_models()
        print("\n✨ Tüm testler başarılı!")
    except Exception as e:
        print(f"\n❌ Test başarısız: {str(e)}")
        import traceback
        traceback.print_exc()
