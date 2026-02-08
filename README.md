# LlamaIndex Legal Document Parser

Türk hukuk dökümanlarını (PDF) parse edip yapılandırılmış JSON formatına çeviren sistem.

## Özellikler

✅ **Batch Processing**: Birden fazla dökümanı otomatik işleme  
✅ **Hiyerarşik Yapı**: PART > CHAPTER > ARTICLE > PARAGRAPH > SUB_CLAUSE  
✅ **Pydantic Validasyon**: %100 şema uyumluluğu garantisi  
✅ **LlamaParse Entegrasyonu**: Tablo ve numaralandırma koruması  
✅ **Multi-LLM Desteği**: OpenAI (GPT-4o) ve Gemini 1.5 Pro  
✅ **Detaylı Loglama**: Her adımda izlenebilirlik  
✅ **Error Handling**: Hata yönetimi ve raporlama  

## Kurulum

### 1. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### 2. API Key'lerini Ayarla

`.env` dosyası oluşturun:

```bash
LLAMA_CLOUD_API_KEY=llx-your-key-here
OPENAI_API_KEY=sk-your-key-here
# veya
GEMINI_API_KEY=your-gemini-key
```

## Kullanım

### Hızlı Başlangıç

```python
from batch_extractor import LegalDocumentExtractor
import os

# Extractor'ı başlat
extractor = LegalDocumentExtractor(
    llama_parse_api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
    llm_provider="openai",
    llm_api_key=os.getenv("OPENAI_API_KEY"),
    llm_model="gpt-4o"
)

# Tek döküman işle
result = extractor.process_single_document("./kanun_6331.pdf")
print(f"Sonuç: {result['json_path']}")
```

### Batch İşlem

```python
# Birden fazla dosyayı işle
files = [
    "./data/6331_sayili_kanun.pdf",
    "./data/4857_sayili_kanun.pdf",
    "./data/5510_sayili_kanun.pdf"
]

results = extractor.process_batch(files)

# Başarılı olanları filtrele
successful = [r for r in results if r["status"] == "success"]
print(f"Başarılı: {len(successful)}/{len(files)}")
```

### Klasör İşleme

```python
# Tüm klasörü işle
results = extractor.process_directory(
    directory="./data/laws",
    pattern="*.pdf"
)
```

## CLI Kullanımı

```bash
# Tek dosya
python cli_extractor.py --file kanun.pdf

# Batch işlem
python cli_extractor.py --batch file1.pdf file2.pdf file3.pdf

# Klasör işle
python cli_extractor.py --directory ./data/laws

# Gemini kullan
python cli_extractor.py --file kanun.pdf --llm gemini --model gemini-1.5-pro
```

## Çıktı Formatı

### JSON Yapısı

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
  "definitions": [
    {
      "term": "İşveren",
      "definition": "..."
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
          "text_content": "...",
          "cross_references": ["Madde 5", "Madde 10"]
        }
      ],
      "cross_references": []
    }
  ],
  "penalties": [
    {
      "violated_article": "Madde 26",
      "penalty_amount": "10.000 TL",
      "penalty_logic": "Her bir çalışan için ayrı ayrı uygulanır"
    }
  ]
}
```

### Klasör Yapısı

```
llamaindex-parsing/
├── extracted_laws/           # Çıkarılan JSON'lar
│   ├── 6331_sayili_kanun.json
│   ├── 4857_sayili_kanun.json
│   └── batch_summary_20260206_143022.json
├── parsed_markdown/          # Parse edilmiş markdown'lar
│   ├── 6331_sayili_kanun.md
│   └── 4857_sayili_kanun.md
└── extraction.log            # Detaylı loglar
```

## Performans ve Maliyet

### LlamaParse Kotası
- **Ücretsiz**: 1000 sayfa/gün
- **Pro**: 7000 sayfa/gün ($48/ay)

### LLM Maliyeti (GPT-4o)
- **Input**: ~$2.5 / 1M token
- **Output**: ~$10 / 1M token
- Ortalama 50 sayfalık kanun: ~$0.30-0.50

### İşlem Süresi
- Parse (LlamaParse): ~30-60 saniye/döküman
- Extraction (GPT-4o): ~20-40 saniye/döküman
- Toplam: ~1-2 dakika/döküman

## Gelişmiş Özellikler

### Chunk İşleme (Uzun Dökümanlar)

Eğer dökümanınız 100+ sayfa ise:

```python
extractor = LegalDocumentExtractor(
    chunk_size=30000,  # Karakter limiti
    # ... diğer parametreler
)
```

### Özel Prompt Kullanımı

`batch_extractor.py` içindeki `_get_extraction_prompt()` metodunu düzenleyebilirsiniz.

### Retry Mekanizması

```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
def process_with_retry(file_path):
    return extractor.process_single_document(file_path)
```

## Sorun Giderme

### LlamaParse Hatası
```
Error: API rate limit exceeded
```
**Çözüm**: Ücretsiz kotanız dolmuş olabilir. Pro plana geçin veya yarın tekrar deneyin.

### LLM Timeout
```
Error: Request timeout
```
**Çözüm**: Dökümanı chunk'lara ayırın veya `chunk_size` parametresini küçültün.

### Eksik Alanlar
```
ValidationError: field required
```
**Çözüm**: LLM doğru veriyi çıkaramadı. Prompt'u iyileştirin veya daha güçlü model kullanın.

## Lisans

MIT

## Katkıda Bulunma

Pull request'ler kabul edilir. Büyük değişiklikler için önce bir issue açın.
