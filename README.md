# Toplantı Asistanı (Meeting Assistant)

Toplantılarda konuşmacıları tanıyarak ses kaydı yapan, transkript oluşturan, AI ile özet çıkaran, görev atayan ve ilerleme raporları üreten web uygulaması.

## Özellikler

- **Konuşmacı Tanıma** - pyannote.audio ile ses kaydından konuşmacıları otomatik ayırt etme
- **Transkripsiyon** - WhisperX ile Türkçe/İngilizce konuşmayı metne dönüştürme
- **Toplantı Özeti** - LLM ile önemli noktalar, kararlar ve genel özet çıkarma
- **Görev Çıkarımı** - Toplantıdan aksiyon maddelerini otomatik tespit edip atama
- **Kanban Board** - Görevleri Bekleyen / Devam Eden / Tamamlanan olarak takip etme
- **İlerleme Raporları** - Toplantı bazlı ve haftalık raporlar oluşturma

## Teknoloji

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python, FastAPI, SQLAlchemy, Celery |
| Frontend | React, TypeScript, Tailwind CSS |
| Ses İşleme | WhisperX (Whisper + pyannote.audio) |
| LLM | Claude / OpenAI / Ollama (değiştirilebilir) |
| Veritabanı | PostgreSQL |
| Kuyruk | Redis + Celery |

## Kurulum

### Gereksinimler

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- HuggingFace token (pyannote modeli için)
- LLM API key (Claude, OpenAI veya Ollama)

### 1. Veritabanı ve Redis

```bash
docker compose up -d
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# .env dosyasını düzenleyin: API key'leri ve HF token'ı ekleyin

uvicorn app.main:app --reload
```

### 3. Celery Worker

```bash
cd backend
celery -A celery_app worker --loglevel=info
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Uygulama http://localhost:5173 adresinde çalışacaktır.

## Ortam Değişkenleri

| Değişken | Açıklama | Varsayılan |
|----------|----------|------------|
| `MA_DATABASE_URL` | PostgreSQL bağlantı adresi | `postgresql+asyncpg://meeting_user:meeting_pass@localhost:5432/meeting_assistant` |
| `MA_REDIS_URL` | Redis bağlantı adresi | `redis://localhost:6379/0` |
| `MA_LLM_PROVIDER` | LLM sağlayıcı (`claude` / `openai` / `ollama`) | `claude` |
| `MA_ANTHROPIC_API_KEY` | Claude API anahtarı | - |
| `MA_OPENAI_API_KEY` | OpenAI API anahtarı | - |
| `MA_OLLAMA_BASE_URL` | Ollama sunucu adresi | `http://localhost:11434` |
| `MA_OLLAMA_MODEL` | Ollama model adı | `llama3.1` |
| `MA_WHISPER_MODEL` | Whisper model boyutu | `large-v3` |
| `MA_WHISPER_LANGUAGE` | Transkripsiyon dili | `tr` |
| `MA_HF_TOKEN` | HuggingFace erişim token'ı | - |

## Kullanım

1. **Toplantı Oluştur** - Ana sayfadan "Yeni Toplantı" butonuna tıklayın
2. **Ses Yükle** - Toplantı ses dosyasını (WAV, MP3, M4A) yükleyin
3. **Otomatik İşleme** - Sistem arka planda ses dosyasını işler:
   - Konuşmacı ayrıştırma (diarization)
   - Konuşmayı metne dönüştürme (transcription)
   - Özet ve görev çıkarma (LLM analysis)
4. **Sonuçları İncele** - Transkript, özet ve görevleri toplantı detay sayfasında görüntüleyin
5. **Görev Takibi** - Görevler sayfasından tüm görevleri kanban board üzerinde yönetin
6. **Raporlama** - İlerleme raporları oluşturun

## Proje Yapısı

```
meeting-assistant/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy ORM modelleri
│   │   ├── schemas/         # Pydantic request/response şemaları
│   │   ├── routers/         # FastAPI endpoint'leri
│   │   ├── services/        # İş mantığı (audio, LLM, özetleme)
│   │   │   └── llm/         # Değiştirilebilir LLM provider'ları
│   │   └── workers/         # Celery arka plan görevleri
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React bileşenleri
│   │   ├── pages/           # Sayfa bileşenleri
│   │   ├── api/             # API istemcisi
│   │   └── types/           # TypeScript tipleri
│   └── package.json
└── docker-compose.yml
```

## Lisans

MIT
