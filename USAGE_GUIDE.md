# Yapılandırılmış Hukuki Belge Çıkarıcı

LlamaParse + OpenRouter LLM kullanarak PDF formatındaki hukuki belgeleri yapılandırılmış JSON formatına çevirir.

## 🎯 Özellikler

- ✅ **PDF → JSON Dönüşümü**: PDF belgelerini yapılandırılmış JSON'a çevirir
- ✅ **Hiyerarşik Yapı**: Madde, fıkra, bent hiyerarşisini korur
- ✅ **Metadata Çıkarımı**: Kanun adı, numarası, tarihleri otomatik çıkarır
- ✅ **Atıf Tespiti**: Maddeler arası atıfları (cross-references) tespit eder
- ✅ **Ceza Analizi**: İdari para cezalarını ayrı bir bölüme alır
- ✅ **Tablo Desteği**: Tablolar markdown formatında çıkarılır
- ✅ **Validation**: Pydantic ile şema doğrulaması

## 📋 Gereksinimler

```bash
pip install -r requirements.txt
```

## ⚙️ Kurulum

1. `.env` dosyası oluşturun:
```bash
cp .env.example .env
```

2. API anahtarlarını düzenleyin:
```bash
# LlamaParse API Key
LLAMAPARSE_API_KEY=your-key-here

# OpenRouter API Key
OPENROUTER_API_KEY=your-key-here

# Model seçimi (önerilen)
OPENROUTER_MODEL=google/gemini-pro-1.5
```

## 🚀 Kullanım

### Tek Klasör İşleme

```bash
python extract_structured.py data/kanunlar
```

### Özel Çıktı Klasörü

```bash
python extract_structured.py data/yonetmelikler extracted_output
```

### Programatik Kullanım

```python
from structured_extractor import StructuredExtractor
import asyncio

async def main():
    extractor = StructuredExtractor()
    
    # Tek dosya işleme
    result = await extractor.process_file(
        "data/tcmb_kanunu.pdf",
        "output"
    )
    
    # Klasör işleme
    await extractor.process_directory(
        "data/kanunlar",
        "extracted_laws"
    )

asyncio.run(main())
```

### MongoDB Entegrasyonu

JSON dosyalarını MongoDB'ye yüklemek için **Legislation_RAG** modülünü kullanın:

```bash
cd ../Legislation_RAG
python upload_json_to_mongodb.py ../llamaindex-parsing/extracted_laws/
```

## 📊 Çıktı Formatı

Çıktı JSON yapısı `landingextr.json` şemasına uygundur:

```json
{
  "law_metadata": {
    "law_title": "İş Sağlığı ve Güvenliği Kanunu",
    "law_number": "6331",
    "acceptance_date": "20.06.2012",
    "publication_date": "30.06.2012",
    "official_gazette": {
      "date": "30.06.2012",
      "number": "28339"
    }
  },
  "sections": [
    {
      "section_title": "BİRİNCİ BÖLÜM",
      "section_heading": "Amaç, Kapsam ve Tanımlar"
    }
  ],
  "content_structure": [
    {
      "level": "ARTICLE",
      "index": "Madde 1",
      "title": "Amaç",
      "text_content": "Bu Kanunun amacı...",
      "children": [
        {
          "level": "PARAGRAPH",
          "index": "(1)",
          "text_content": "İşyerlerinde...",
          "cross_references": ["Madde 5", "Madde 12"]
        }
      ],
      "cross_references": []
    }
  ],
  "definitions": [
    {
      "term": "İşveren",
      "definition": "İşçi çalıştıran gerçek veya tüzel kişiyi..."
    }
  ],
  "penalties": [
    {
      "violated_article": "Madde 26",
      "penalty_amount": "10.000 TL",
      "penalty_logic": "İşveren her bir ihlal için..."
    }
  ]
}
```

## 🔧 Model Önerileri

### Uzun Belgeler (100+ sayfa)
```bash
OPENROUTER_MODEL=google/gemini-pro-1.5  # 1M token context
```

### Karmaşık Hiyerarşi
```bash
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet  # En güçlü analiz
```

### Düşük Maliyet
```bash
OPENROUTER_MODEL=qwen/qwen-2.5-72b-instruct  # Uygun fiyat
```

## 📁 Klasör Yapısı

```
llamaindex-parsing/
├── data/                      # Input PDF'ler buraya
│   ├── kanunlar/
│   ├── yonetmelikler/
│   └── tebligler/
├── extracted_laws/            # Çıktı JSON'lar
├── pydantic_models.py         # Veri modelleri
├── structured_extractor.py    # Ana çıkarıcı
├── extract_structured.py      # CLI aracı
├── config.py                  # Ayarlar
├── landingextr.json          # JSON şeması
└── .env                       # API anahtarları
```

## 🧪 Test

```bash
# Config test
python config.py

# Tek dosya test
python extract_structured.py data/test.pdf test_output

# Toplu işleme
python extract_structured.py data/kanunlar extracted_laws
```

## 🐛 Hata Ayıklama

### API Hatası
```bash
# .env dosyasını kontrol edin
cat .env | grep API_KEY

# API anahtarlarını test edin
python config.py
```

### Validation Hatası
```bash
# Pydantic modelleri kontrol edin
python pydantic_models.py

# JSON şemasını görüntüleyin
python -c "from pydantic_models import LegalDocument; import json; print(json.dumps(LegalDocument.model_json_schema(), indent=2))"
```

## 📝 Notlar

- PDF'ler UTF-8 Türkçe karakter desteği ile işlenir
- Premium mode tablolar için önerilir
- Uzun belgeler (50k+ karakter) otomatik chunk'lanır
- Validation hatası durumunda raw JSON kaydedilir

## 🔗 Bağlantılar

- [LlamaParse Docs](https://docs.llamaindex.ai/en/stable/module_guides/loading/connector/llama_parse/)
- [OpenRouter Models](https://openrouter.ai/models)
- [Pydantic v2](https://docs.pydantic.dev/latest/)

## 📄 Lisans

MIT License
