# 🎬 Trend Shorts MVP

> Automatically convert trending topics into ready-to-upload **YouTube Shorts** videos — zero cost, fully local, GPU-accelerated.

---

## What It Does

1. **Fetches** real-time trending keywords from Google Trends (India).
2. **Generates** a punchy 4-scene video script (mock or AI-powered).
3. **Renders** a vertical **1080×1920** video with bold text overlays.
4. **Saves** the finished `.mp4` to the `output/` folder.

One command. Fully automated. Zero manual editing.

---

## System Architecture

```
main.py                  ← orchestrator (runs the full pipeline)
├── trends.py            ← fetches trending keywords via pytrends
├── script_generator.py  ← creates scene texts (mock / Gemini / OpenAI / Claude)
├── video_generator.py   ← renders scenes → composes video → exports mp4
└── config.py            ← all settings, GPU detection, API keys
```

| Component         | Responsibility                                   |
| ----------------- | ------------------------------------------------ |
| `config.py`       | Video specs, colours, fonts, GPU/CUDA detection  |
| `trends.py`       | Google Trends India + offline fallback            |
| `script_generator.py` | Mock script or AI API with auto-fallback     |
| `video_generator.py`  | PIL rendering, moviepy composition, ffmpeg export |
| `main.py`         | Glue — fetch → script → video → save             |

---

## Installation

### Prerequisites

- **Python 3.10+**
- **pip**
- **ffmpeg** installed and on PATH ([download](https://ffmpeg.org/download.html))
- *(Optional)* NVIDIA GPU with CUDA for hardware-accelerated encoding

### Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/trend-shorts-mvp.git
cd trend-shorts-mvp

# Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

> **GPU Note:** If you have an NVIDIA GPU, install the CUDA-enabled PyTorch build:
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cu121
> ```

---

## How to Run

```bash
python main.py
```

### Expected Console Output

```
==================================================
  🎬  TREND SHORTS MVP
==================================================
  Device : CPU
  CUDA   : ❌ Not available
  Mode   : mock
==================================================

📡 Fetching trends...
🔥 Trend detected: Nothing Phone 3

✍️  Generating script...
📝 Script (4 scenes):
   Scene 1: 🔥 STOP SCROLLING!
   Scene 2: 🚀 NOTHING PHONE 3 IS TRENDING
   Scene 3: 💥 YOU NEED TO KNOW THIS
   Scene 4: 👇 FOLLOW FOR MORE!

🎞️  Generating video...
🖥  No CUDA GPU — using CPU encoding (libx264)
✅ Video saved: output/short_20260312_163200.mp4
```

The video will be in `output/short_YYYYMMDD_HHMMSS.mp4`.

---

## Configuration

All settings live in `config.py`:

| Setting          | Default   | Description                          |
| ---------------- | --------- | ------------------------------------ |
| `SCRIPT_MODE`    | `"mock"`  | `"mock"`, `"gemini"`, `"openai"`, `"claude"` |
| `TRENDS_REGION`  | `"india"` | Country for Google Trends            |
| `SCENE_COUNT`    | `4`       | Number of scenes per video           |
| `SCENE_DURATION` | `2`       | Seconds per scene                    |
| `FONT_SIZE`      | `80`      | Text size (px)                       |
| `FPS`            | `24`      | Output video frame rate              |

To use an AI provider, set `SCRIPT_MODE` and the matching API key:

```python
SCRIPT_MODE = "gemini"
GEMINI_API_KEY = "your-key-here"
```

Or via environment variables:

```bash
set GEMINI_API_KEY=your-key-here    # Windows
export GEMINI_API_KEY=your-key-here # Linux/macOS
```

---

## Example Output

| Scene | Preview |
|-------|---------|
| 1     | 🔥 STOP SCROLLING! — midnight blue background |
| 2     | 🚀 TOPIC IS TRENDING — dark red background |
| 3     | 💥 YOU NEED TO KNOW THIS — dark green background |
| 4     | 👇 FOLLOW FOR MORE! — indigo background |

**Video specs:** 1080×1920, ~8 seconds, 24 fps, `.mp4`

---

## Future Extensions (planned)

- [ ] Batch multi-video generation
- [ ] Automatic YouTube upload via API
- [ ] Telegram channel posting
- [ ] Trend filtering / keyword blocklist
- [ ] Background images & animated transitions
- [ ] Text-to-speech voiceover
- [ ] Scheduling / cron automation

---

## License

MIT — use it, fork it, ship it.
