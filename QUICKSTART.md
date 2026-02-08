# Hızlı Başlangıç Kılavuzu

## 🚀 5 Dakikada Başla

### 1. Kurulum

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# .env dosyasını oluştur
cp .env.example .env

# API key'lerini düzenle
nano .env
```

### 2. API Key'leri Ayarla

`.env` dosyasını düzenleyin:

```bash
LLAMA_CLOUD_API_KEY=llx-your-key-here
OPENAI_API_KEY=sk-your-key-here
```

**API Key Nasıl Alınır:**
- **LlamaCloud**: https://cloud.llamaindex.ai → Sign up → API Keys
- **OpenAI**: https://platform.openai.com → API Keys → Create new key

### 3. İlk Testinizi Yapın

```bash
# Pydantic modellerini test et
python test_models.py
```

✅ Çıktı: `test_output.json` dosyası oluşturulmalı

### 4. PDF İşleme

#### Yöntem 1: Python Script

```python
from batch_extractor import LegalDocumentExtractor
import os

extractor = LegalDocumentExtractor(
    llama_parse_api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
    llm_provider="openai",
    llm_api_key=os.getenv("OPENAI_API_KEY"),
    llm_model="gpt-4o"
)

# Tek dosya işle
result = extractor.process_single_document("./kanun.pdf")
print(f"Sonuç: {result['json_path']}")
```

#### Yöntem 2: CLI

```bash
# Tek dosya
python cli_extractor.py --file kanun.pdf

# Klasör
python cli_extractor.py --directory ./data/laws
```

## 📁 Proje Yapısı

```
llamaindex-parsing/
│
├── pydantic_models.py          # Veri modelleri (JSON şema)
├── batch_extractor.py          # Ana işlem motoru
├── cli_extractor.py            # Komut satırı arayüzü
├── mongodb_integration.py      # MongoDB entegrasyonu
├── examples.py                 # Kullanım örnekleri
├── test_models.py              # Test scripti
│
├── requirements.txt            # Bağımlılıklar
├── .env.example               # Örnek çevre değişkenleri
├── README.md                  # Detaylı dokümantasyon
├── QUICKSTART.md              # Bu dosya
│
├── data/                      # PDF dosyaları (sizin eklemeniz gerekli)
│   └── laws/
│       ├── 6331_sayili_kanun.pdf
│       └── ...
│
├── extracted_laws/            # Çıktı: JSON dosyaları
│   ├── 6331_sayili_kanun.json
│   └── batch_summary_*.json
│
├── parsed_markdown/           # Çıktı: Markdown dosyaları
│   └── 6331_sayili_kanun.md
│
└── extraction.log             # Log dosyası
```

## 🎯 Kullanım Senaryoları

### Senaryo 1: Tek Kanun İşle

```bash
python cli_extractor.py --file ./data/6331_sayili_kanun.pdf
```

**Çıktı:**
- `extracted_laws/6331_sayili_kanun.json` ✅
- `parsed_markdown/6331_sayili_kanun.md` ✅

### Senaryo 2: Toplu İşlem (Batch)

```bash
python cli_extractor.py --batch \
  ./data/6331_sayili_kanun.pdf \
  ./data/4857_sayili_kanun.pdf \
  ./data/5510_sayili_kanun.pdf
```

### Senaryo 3: Klasör İşle

```bash
python cli_extractor.py --directory ./data/laws
```

### Senaryo 4: MongoDB'ye Kaydet

```python
from mongodb_integration import LegalDocumentDatabase

db = LegalDocumentDatabase()
db.bulk_insert_from_json_files("./extracted_laws")

# Arama yap
results = db.search_articles("iş güvenliği", limit=10)
```

## 💡 İpuçları

### Maliyet Optimizasyonu

1. **Gemini Kullan** (daha ucuz):
```bash
python cli_extractor.py --file kanun.pdf --llm gemini --model gemini-1.5-pro
```

2. **Chunk Size Ayarla** (uzun dökümanlar için):
```bash
python cli_extractor.py --file kanun.pdf --chunk-size 30000
```

### Hata Çözümleri

**Hata: `API rate limit exceeded`**
```
Çözüm: LlamaParse ücretsiz kotanız dolmuş. Pro plana geçin veya yarın tekrar deneyin.
```

**Hata: `ValidationError: field required`**
```
Çözüm: LLM bazı alanları çıkaramadı. Daha güçlü model kullanın (gpt-4o).
```

**Hata: `Import "llama_parse" could not be resolved`**
```
Çözüm: pip install llama-parse
```

## 📊 Performans Beklentileri

| Döküman Boyutu | Parse Süresi | Extraction Süresi | Maliyet (GPT-4o) |
|----------------|--------------|-------------------|------------------|
| 10 sayfa       | ~20 saniye   | ~15 saniye        | ~$0.10          |
| 50 sayfa       | ~40 saniye   | ~30 saniye        | ~$0.40          |
| 100 sayfa      | ~60 saniye   | ~50 saniye        | ~$0.80          |

## 🔧 Gelişmiş Kullanım

### Özel Prompt Kullanımı

`batch_extractor.py` içindeki `_get_extraction_prompt()` metodunu düzenleyin:

```python
def _get_extraction_prompt(self) -> str:
    return """
    [Özel prompt'unuzu buraya yazın]
    
    {text}
    """
```

### Retry Mekanizması

```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
def process_with_retry(file_path):
    return extractor.process_single_document(file_path)
```

## 📞 Destek

**Sorun mu yaşıyorsunuz?**

1. `extraction.log` dosyasını kontrol edin
2. `python test_models.py` çalıştırın
3. API key'lerinizi doğrulayın
4. Bağımlılıkları yeniden yükleyin: `pip install -r requirements.txt --upgrade`

## 🎓 Sonraki Adımlar

1. ✅ İlk dökümanınızı işleyin
2. ✅ MongoDB entegrasyonunu kurun
3. ✅ Toplu işlem yapın
4. ✅ RAG sisteminize entegre edin

**Başarılar!** 🚀
