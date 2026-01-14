# ISG Mevzuat Semantic Search - Kullanım Kılavuzu

## Kurulum

### 1. Gerekli kütüphaneleri yükleyin:
```bash
pip install python-dotenv datasets PyPDF2 openai google-generativeai sentence-transformers pinecone-client torch tqdm
```

### 2. .env dosyasını kontrol edin
`.env` dosyasında şunlar olmalı:
```
PINECONE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

## Çalıştırma

### Tek komutla çalıştırma:
```bash
python semantic_search_isg.py
```

Bu komut:
1. PDF'i yükler ve işler
2. Pinecone index oluşturur
3. Embeddings yükler
4. 3 örnek sorgu çalıştırır
5. Interactive mode'a geçer

### Python'dan kullanma:
```python
from semantic_search_isg import run_query, main

# Setup yap
index, model, text_mapping = main()

# Sorgular çalıştır
run_query('iş kazası nedir?', index, model, text_mapping, 
          use_ai=True, ai_provider='gemini')

run_query('işveren yükümlülükleri', index, model, text_mapping,
          ai_provider='openai', max_length='short')

run_query('güvenlik eğitimi', index, model, text_mapping, 
          use_ai=False)
```

## Parametreler

### run_query() parametreleri:
- `query`: Soru (Türkçe)
- `use_ai`: AI kullan (True/False)
- `ai_provider`: "openai", "gemini", veya "none"
- `use_reasoning`: Reasoning modeli kullan (True/False)
- `max_length`: "short" (3-4 cümle), "medium" (5-7 cümle), "normal" (detaylı)
- `top_k`: Kaç chunk getir (default: 5)

## AI Provider Seçenekleri

### 1. Google Gemini (ÜCRETSİZ! 🎉)
```python
# Normal - Gemini 1.5 Flash (en hızlı!)
run_query(query, index, model, text_mapping, ai_provider='gemini')

# Reasoning ile - Gemini 1.5 Pro (deep thinking)
run_query(query, index, model, text_mapping, 
          ai_provider='gemini', use_reasoning=True)
```

### 2. OpenAI GPT-4 (Ücretli)
```python
# Normal
run_query(query, index, model, text_mapping, ai_provider='openai')

# O1 Reasoning ile
run_query(query, index, model, text_mapping,
          ai_provider='openai', use_reasoning=True)
```

### 3. AI Yok (Sadece semantic search)
```python
run_query(query, index, model, text_mapping, use_ai=False)
```

## Maliyet Karşılaştırması

- **Gemini 1.5 Flash**: ÜCRETSİZ (1,500 istek/gün) - EN HIZLI (5-10 saniye)
- **Gemini 1.5 Pro**: ÜCRETSİZ (reasoning için) - HIZLI (8-15 saniye)
- **GPT-4 Turbo**: $10/1M input token - YAVAŞ (15-25 saniye)
- **O1-Preview**: $15/1M input token - ÇOK YAVAŞ (20-30 saniye)

**Önerilen:** Hız ve maliyet için Gemini 1.5 Flash kullanın!

## Örnekler

### Kısa cevap (Gemini):
```python
run_query('işveren sorumlulukları nelerdir?', 
          index, model, text_mapping,
          ai_provider='gemini', max_length='short')
```

### Detaylı analiz (Gemini Reasoning):
```python
run_query('işveren ve çalışanların iş kazalarını önlemedeki sorumlulukları nelerdir?',
          index, model, text_mapping,
          ai_provider='gemini', use_reasoning=True)
```

### Sadece ilgili metinler (AI yok):
```python
run_query('iş kazası durumunda ne yapılmalıdır?',
          index, model, text_mapping,
          use_ai=False)
```
