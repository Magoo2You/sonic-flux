# SONIC FLUX - AI-Powered Music Discovery System

## 🎵 PROJECT OVERVIEW

**Sonic Flux** is a **desktop music discovery application** that uses AI to analyze sonic characteristics of your Amazon Music library and generates personalized playlists based on mood, energy, instrumentation, and other audio features. The app then controls your WiiM AMP Ultra stereo via HTTP API to play the generated playlists directly.

### Core Capabilities
- ✅ Audio feature analysis (tempo, energy, valence, instrumentalness, etc.)
- ✅ Playlist generation from Amazon Music library
- ✅ Local AI processing (no cloud API calls)
- ✅ WiiM AMP Ultra integration via HTTP API (play on stereo)
- ✅ SQLite-based metadata storage
- ✅ Privacy-first design (everything runs locally)
- ✅ **Desktop GUI Interface** (visual controls, progress indicators, playlist viewer)

### End Goal Architecture
```
┌─────────────────────────────────────────────────────────┐
│  Sonic Flux Desktop App                                  │
│                                                          │
│  [🎵 Select Analysis Plan]                               │
│     └─ Morning Energy / Late Night Chill / Focus         │
│                                                          │
│  [📊 Generate Playlist]                                   │
│     ├─ Visual progress: "Analyzing 50 songs..."           │
│     ├─ Preview: Shows selected tracks with metadata      │
│     └─ Output: Detailed playlist list with Amazon links  │
│                                                          │
│  [▶️ Play via WiiM AMP Ultra]                             │
│     └─ One-click: Switch source → Play on stereo         │
│                                                          │
│  [📁 Export Playlist]                                     │
│     └─ Save as M3U/Spotify SmartPlaylist/Apple Music     │
└─────────────────────────────────────────────────────────┘
```

### Tech Stack
- Python 3.10+ with **CustomTkinter** (modern cross-platform GUI)
- librosa / essentia-python for audio features
- Amazon Music Web Playback API
- pywiim for WiiM control
- SQLite for local database

---

## 🚀 QUICK START

### Installation (First Time Only)

```bash
# Install core dependencies
pip install librosa essentia-python music21 scikit-learn joblib amazon-music pywiim aiofiles mutagen chromaprint-py customtkinter tkinter

# Install development dependencies (optional, for testing)
pip install pytest pytest-cov black isort flake8 mypy
```

### Desktop App Launch (Once Installed)

```bash
cd C:\HermesWiiM
python src/sonic_flux_app.py

# First run will launch GUI and request Amazon Music OAuth authentication
```

### Authentication Setup

1. Run Sonic Flux app once
2. Click "Authenticate with Amazon Music"
3. Browser opens for login (one-time only)
4. Tokens saved to `data/token_store.json`

---

## 📁 PROJECT STRUCTURE

```
C:\HermesWiiM\
├── src/
│   ├── __init__.py              # Package initialization
│   ├── sonic_flux_app.py        # Main desktop GUI application (CustomTkinter)
│   └── modules/
│       ├── amazon_api.py        # Amazon Music API wrapper
│       ├── wiim_client.py       # WiiM HTTP API client
│       ├── audio_features.py    # librosa feature extraction
│       ├── ml_model.py          # Local ML model loading/persistence
│       ├── playlist_gen.py      # Playlist generation logic
│       └── database.py          # SQLite operations
├── models/                      # Pre-trained models (if any)
│   └── music2vec_model.pt       # [INCOMPLETE] - Audio embeddings model
├── data/                        # Data files & tokens
│   ├── token_store.json         # Amazon Music OAuth tokens
│   ├── user_prefs.json          # User preferences & ratings
│   └── database.db              # SQLite metadata storage
├── logs/                        # Application logs
│   └── sonic-flux.log           # Main log file (date-rotated)
├── tests/                       # Unit/integration tests
│   ├── test_amazon_api.py
│   ├── test_audio_features.py
│   └── test_playlist_gen.py
├── docs/                        # Documentation
│   ├── api_reference.md         # API documentation
│   └── usage_guide.md           # User guide
├── config/                      # Configuration files
│   └── config.json              # Application settings
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
└── requirements.txt             # Python dependencies
```

---

## ⚙️ CONFIGURATION

### `config/config.json`

```json
{
  "amazon_music": {
    "enabled": true,
    "use_tokens_file": true,
    "token_file_path": "data/token_store.json"
  },
  "wiim_amp_ultra": {
    "enabled": true,
    "ip_address": "192.168.1.100",  // [INCOMPLETE] - Update with your WiiM IP
    "port": 5000,
    "source_name": "Amazon Music"
  },
  "audio_extraction": {
    "sample_rate": 22050,
    "use_streaming": true,
    "cache_features": true
  },
  "playlist_templates": [
    {
      "name": "morning-energy",
      "target_mood": "energetic",
      "min_energy": 0.7,
      "max_energy": 1.0,
      "min_valence": 0.6,
      "max_valence": 1.0,
      "preferred_instrumentation": "full-band"
    },
    {
      "name": "late-night-chill",
      "target_mood": "chill",
      "min_energy": 0.2,
      "max_energy": 0.5,
      "min_valence": 0.3,
      "max_valence": 0.7,
      "preferred_instrumentation": "ambient"
    },
    {
      "name": "focus-flow",
      "target_mood": "focus",
      "min_energy": 0.4,
      "max_energy": 0.8,
      "min_valence": 0.3,
      "max_valence": 0.6,
      "preferred_instrumentation": "instrumental-heavy"
    }
  ]
}
```

---

## 📋 GROUND RULES (Agreed Upon)

1. ✅ **No Mock or Fake Data** - Placeholders marked `[INCOMPLETE]`, use `None` for missing values
2. ⭐ **Error Handling & Failure Modes** - Log and handle all errors, provide graceful fallbacks
3. ⭐ **Data Persistence & Backups** - SQLite for data, backup tokens separately
4. ⭐ **Logging Requirements** - Consistent logging with timestamps, never log secrets
5. ⭐ **API Rate Limit Awareness** - Cache and throttle API calls, implement queuing
6. 📁 **File Organization** - Strict folder structure as defined above
7. 🧪 **Testing Strategy** - Minimal viable tests for core functions
8. 🎛️ **Environment Variables** - Use config files, support `.env` for local dev
9. 🔒 **Data Privacy & Security** - Secure token handling, no credentials in logs

---

## 🎯 NEXT STEPS (Desktop GUI Focus)

We'll build this incrementally toward a full desktop GUI app:

1. ✅ **Project Setup Complete** - Folder structure created on GitHub
2. ⏭️ **Amazon Music API Integration** - Core authentication and search
3. ⏭️ **WiiM HTTP Client** - Control layer implementation
4. ⏭️ **Audio Feature Extraction** - librosa integration
5. ⏭️ **Database Schema** - SQLite table creation
6. ⏭️ **Playlist Generation Logic** - Core algorithm
7. ⏭️ **Desktop GUI Framework** - CustomTkinter interface (Primary goal!)
8. ⏭️ **Testing & Documentation** - Quality assurance

---

## 📞 HOW TO USE THIS PROJECT

### For Development:

```bash
# Navigate to project folder
cd "C:\HermesWiiM"

# Run specific module tests
python -m pytest tests/test_amazon_api.py -v

# View logs
tail -f logs/sonic-flux.log

# Check current configuration
cat config/config.json
```

### For Running (Desktop App):

```bash
cd "C:\HermesWiiM"
python src/sonic_flux_app.py

# App launches GUI with:
# - Amazon Music authentication button
# - Playlist generation controls
# - WiiM play/pause buttons
# - Playlist export options
```

### For CLI Testing (Optional):

```bash
cd "C:\HermesWiiM"

# Authenticate with Amazon Music API
python src/modules/amazon_api.py --auth

# Generate a playlist (CLI test)
python src/modules/playlist_gen.py --generate "morning-energy"
```


---

## 📚 RESOURCES & DOCUMENTATION

- **Amazon Music API Docs**: https://developer.amazon.com/docs/music
- **pywiim GitHub**: https://github.com/mjcumming/wiim
- **librosa Documentation**: http://librosa.org/doc/latest/index.html

---

**Project Status**: 🟢 Ready for Development

All ground rules established. Ready to build! 🎵
