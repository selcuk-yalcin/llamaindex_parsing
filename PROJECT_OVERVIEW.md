# PROJECT OVERVIEW - Legal Document Extraction System

## Proje Amacı

Türk hukuk dökümanlarını (PDF) otomatik olarak parse edip yapılandırılmış JSON formatına çeviren, batch processing destekli, production-ready bir sistem.

##  Mimari

```
┌─────────────────┐
│   PDF Dosyası   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LlamaParse     │ ← Markdown'a çevirme
│  (OCR + Layout) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   LLM (GPT-4o)  │ ← Yapılandırılmış extraction
│   + Pydantic    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  JSON Output    │
│  + MongoDB      │
└─────────────────┘
```

##  Bileşenler

### 1. **pydantic_models.py** (Veri Modelleri)
- `LegalDocument`: Ana model
- `LawMetadata`: Kanun bilgileri
- `ContentStructure`: Hiyerarşik madde yapısı
- `Penalty`: Ceza bilgileri
- Enum'lar: `HierarchyLevel`, `ElementType`

### 2. **batch_extractor.py** (Ana Motor)
- `LegalDocumentExtractor`: Ana sınıf
- Parse işlemi (LlamaParse)
- Extraction işlemi (LLM + Pydantic)
- Batch processing
- Error handling & logging

### 3. **cli_extractor.py** (Komut Satırı)
- Argparse ile CLI
- Tek dosya / batch / klasör işleme
- API key yönetimi
- İlerleme gösterimi

### 4. **mongodb_integration.py** (Veritabanı)
- `LegalDocumentDatabase`: MongoDB sınıfı
- CRUD operasyonları
- Full-text search
- Cross-reference analizi
- Bulk insert

### 5. **examples.py** (Kullanım Örnekleri)
- 8 farklı senaryo
- İnteraktif menü
- Best practices

### 6. **test_models.py** (Test)
- Pydantic model testi
- JSON validasyon
- Örnek veri oluşturma

##  Teknolojiler

| Kategori | Teknoloji | Amaç |
|----------|-----------|------|
| **PDF Parsing** | LlamaParse | Markdown'a çevirme |
| **LLM** | GPT-4o / Gemini | Extraction |
| **Validasyon** | Pydantic v2 | Şema uyumluluğu |
| **Veritabanı** | MongoDB | Saklama & arama |
| **CLI** | argparse | Komut satırı |
| **Logging** | Python logging | İzlenebilirlik |

##  Veri Akışı

1. **Input**: PDF dosyası
2. **Parse**: LlamaParse → Markdown (tablo korumalı)
3. **Extract**: LLM + Pydantic → Yapılandırılmış JSON
4. **Validate**: Pydantic şema kontrolü
5. **Save**: JSON dosyası + MongoDB
6. **Query**: Full-text search + cross-reference

##  JSON Şeması

```json
{
  "law_metadata": {
    "law_title": "İş Sağlığı ve Güvenliği Kanunu",
    "law_number": "6331",
    "acceptance_date": "20.06.2012"
  },
  "sections": [...],
  "definitions": [...],
  "content_structure": [
    {
      "level": "ARTICLE",
      "index": "Madde 1",
      "text_content": "...",
      "children": [...]
    }
  ],
  "penalties": [...],
  "amendment_summary": [...]
}
```

##  Kullanım

### Hızlı Başlangıç
```bash
# Kurulum
pip install -r requirements.txt

# Tek dosya işle
python cli_extractor.py --file kanun.pdf

# Klasör işle
python cli_extractor.py --directory ./data/laws
```

### Python API
```python
from batch_extractor import LegalDocumentExtractor

extractor = LegalDocumentExtractor(
    llama_parse_api_key="llx-...",
    llm_provider="openai",
    llm_api_key="sk-...",
    llm_model="gpt-4o"
)

result = extractor.process_single_document("kanun.pdf")
```

##  Performans

- **Parse**: ~30-60 saniye/döküman
- **Extraction**: ~20-40 saniye/döküman
- **Toplam**: ~1-2 dakika/döküman
- **Maliyet**: ~$0.30-0.50/döküman (GPT-4o)

##  Güvenlik

- API key'ler `.env` dosyasında
- `.gitignore` ile korumalı
- MongoDB authentication destekli

##  Klasör Yapısı

```
llamaindex-parsing/
├── pydantic_models.py          # Veri modelleri
├── batch_extractor.py          # Ana motor
├── cli_extractor.py            # CLI
├── mongodb_integration.py      # DB
├── examples.py                 # Örnekler
├── test_models.py              # Test
├── requirements.txt            # Bağımlılıklar
├── .env.example               # Örnek config
├── README.md                  # Detaylı dok
├── QUICKSTART.md              # Hızlı başlangıç
├── PROJECT_OVERVIEW.md        # Bu dosya
├── data/                      # Input
├── extracted_laws/            # Output JSON
├── parsed_markdown/           # Output MD
└── extraction.log             # Logs
```

##  Özellikler

Batch processing  
 Hiyerarşik yapı koruması  
 Pydantic validasyon  
 Multi-LLM desteği (OpenAI, Gemini)  
 MongoDB entegrasyonu  
 Full-text search  
 Cross-reference analizi  
 Error handling & retry  
 Detaylı logging  
 CLI & Python API  
 Progress bar  
 Chunk processing (uzun dökümanlar)  

##  Gelecek Planları

- [ ] Vector search entegrasyonu
- [ ] RAG pipeline entegrasyonu
- [ ] Web arayüzü (Streamlit)
- [ ] Docker containerization
- [ ] API endpoint (FastAPI)
- [ ] Async processing
- [ ] Caching mekanizması
- [ ] Test coverage %100

##  Dokümantasyon

- **README.md**: Detaylı kullanım kılavuzu
- **QUICKSTART.md**: 5 dakikada başla
- **PROJECT_OVERVIEW.md**: Bu dosya
- **examples.py**: 8 kullanım senaryosu


