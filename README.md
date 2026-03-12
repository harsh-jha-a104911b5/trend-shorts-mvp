# 🎬 Trend Shorts — Autonomous Content Pipeline

> Automatically fetch trending topics → generate YouTube Shorts → upload to YouTube → post to Telegram.
> Zero cost. Fully local. GPU-accelerated. One command.

---

## What It Does

1. **Fetches** real-time trending keywords from Google Trends (India).
2. **Filters** trends to keep only tech-relevant topics.
3. **Generates** punchy 4-scene video scripts with title, description, and tags.
4. **Renders** premium vertical **1080×1920** videos with gradient backgrounds, glowing text, and background music.
5. **Uploads** each video to YouTube automatically.
6. **Posts** video links to a Telegram channel.
7. **Schedules** runs every 3 hours (optional).

---

## System Architecture

```
main.py                      ← orchestrator + trend filter + scheduler
├── trends.py                ← Google Trends RSS → pytrends → fallback
├── script_generator.py      ← scenes + title + description + tags
├── video_generator.py       ← PIL rendering → moviepy → ffmpeg (GPU/CPU)
├── youtube_uploader.py      ← YouTube Data API v3 + OAuth + token caching
├── telegram_poster.py       ← Telegram Bot HTTP API
└── config.py                ← all settings + GPU detection
```

| Module               | Responsibility                                         |
| -------------------- | ------------------------------------------------------ |
| `config.py`          | Video specs, filters, API keys, GPU/CUDA detection     |
| `trends.py`          | 3-tier trend fetching (RSS → pytrends → fallback)      |
| `script_generator.py`| Scene text + YouTube metadata (mock or AI-powered)     |
| `video_generator.py` | Premium rendering + background music + GPU encoding    |
| `youtube_uploader.py`| OAuth upload with progress + token caching             |
| `telegram_poster.py` | MarkdownV2 formatted posts via Bot API                 |
| `main.py`            | Pipeline: fetch → filter → generate → upload → notify  |

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
git clone https://github.com/harsh-jha-a104911b5/trend-shorts-mvp.git
cd trend-shorts-mvp

# Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
python -m pip install -r requirements.txt
```

> **GPU Note:** For NVIDIA GPU support, install CUDA-enabled PyTorch:
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cu121
> ```

---

## YouTube OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project (or use existing).
3. Enable **YouTube Data API v3**.
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**.
5. Select **Desktop App** as application type.
6. Download the JSON file and save it as `youtube_credentials.json` in the project root.

On first run, a browser window will open for authentication. After that, the token is cached in `youtube_token.json` — no login required again.

> ⚠️ **Never commit** `youtube_credentials.json` or `youtube_token.json` to Git (they're in `.gitignore`).

---

## Telegram Bot Setup

1. Open Telegram and message [@BotFather](https://t.me/BotFather).
2. Send `/newbot` and follow the prompts to create a bot.
3. Copy the **bot token**.
4. Create a channel/group and add the bot as an admin.
5. Get the **chat ID** (forward a message from the channel to [@userinfobot](https://t.me/userinfobot)).

Set in `config.py` or environment variables:

```python
TELEGRAM_BOT_TOKEN = "your-bot-token"
TELEGRAM_CHAT_ID = "your-chat-id"
```

Or via environment:

```bash
set TELEGRAM_BOT_TOKEN=your-bot-token
set TELEGRAM_CHAT_ID=your-chat-id
```

---

## How to Run

### Single run (generate + upload + post)

```bash
python main.py
```

### Scheduled mode (every 3 hours)

Set in `config.py`:

```python
SCHEDULE_ENABLED = True
SCHEDULE_INTERVAL_HOURS = 3
```

Then run:

```bash
python main.py
```

The system will run immediately, then repeat every 3 hours. Press `Ctrl+C` to stop.

---

## Expected Console Output

```
============================================================
  🎬  TREND SHORTS — Autonomous Content Pipeline
  🕐  2026-03-12 16:51:42
============================================================
  Device : CUDA
  CUDA   : ✅ Available
  Mode   : mock
  Upload : ✅ YouTube
  Notify : ✅ Telegram
============================================================

📡 Fetching trends...
✅ Fetched 10 trends via RSS feed

🔍 Filtering 10 trends...
   ✅ Allowed: ChatGPT update
   🚫 Blocked: cricket world cup
   ✅ Allowed: Samsung S25
   ⏭️  Skipped (no match): Budget 2026

🎯 3 trend(s) selected for video generation

────────────────────────────────────────────────────────────
  📌 [1/3] ChatGPT update
────────────────────────────────────────────────────────────
  ✍️  Generating script...
  📝 Title: Chatgpt Update — Trending Now! 🔥 #Shorts
  🎞️  Generating video...
  💾 Saved: output/short_20260312_165200.mp4
  📤 Uploading to YouTube...
   📤 Upload progress: 50%
   📤 Upload progress: 100%
   ✅ Upload complete: https://youtube.com/shorts/XXXX
  📨 Posting to Telegram...
   ✅ Telegram post sent

============================================================
  ✅  PIPELINE COMPLETE — 3 video(s) in 45.2s
============================================================
  • ChatGPT update: https://youtube.com/shorts/XXXX
  • Samsung S25: https://youtube.com/shorts/YYYY
  • AI tools: https://youtube.com/shorts/ZZZZ
============================================================
```

---

## Configuration

All settings in `config.py`:

| Setting                    | Default   | Description                                      |
| -------------------------- | --------- | ------------------------------------------------ |
| `SCRIPT_MODE`              | `"mock"`  | `"mock"`, `"gemini"`, `"openai"`, `"claude"`     |
| `MAX_VIDEOS_PER_RUN`       | `5`       | Max videos generated per pipeline run            |
| `YOUTUBE_UPLOAD_ENABLED`   | `True`    | Enable/disable YouTube uploads                   |
| `YOUTUBE_PRIVACY`          | `"public"`| `"public"`, `"unlisted"`, `"private"`            |
| `TELEGRAM_ENABLED`         | `True`    | Enable/disable Telegram posting                  |
| `SCHEDULE_ENABLED`         | `False`   | Enable auto-scheduling                           |
| `SCHEDULE_INTERVAL_HOURS`  | `3`       | Hours between scheduled runs                     |
| `SCENE_COUNT`              | `4`       | Scenes per video                                 |
| `SCENE_DURATION`           | `2`       | Seconds per scene                                |
| `FPS`                      | `24`      | Video frame rate                                 |

---

## GPU Acceleration

The system automatically detects CUDA:

| CUDA Available | Codec Used     | Performance        |
|----------------|----------------|--------------------|
| ✅ Yes         | `h264_nvenc`   | GPU-accelerated    |
| ❌ No          | `libx264`      | CPU (still works)  |

No configuration needed — detection is automatic via PyTorch.

---

## Failsafe Design

| Failure                  | Behaviour                                     |
|--------------------------|-----------------------------------------------|
| Google Trends down       | Falls back to pytrends → hardcoded list       |
| YouTube upload fails     | Video saved locally, pipeline continues       |
| Telegram post fails      | Pipeline continues                             |
| No trends pass filter    | Uses first unblocked trends as fallback       |
| AI API fails             | Falls back to mock script generator           |
| No GPU                   | Falls back to CPU encoding                    |

The system **never crashes** due to external API errors.

---

## License

MIT — use it, fork it, ship it.
