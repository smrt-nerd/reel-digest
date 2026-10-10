# 🎞️ ReelDigest

A production-grade, open-source Python pipeline that automatically downloads short and long-form video content (Instagram Reels, YouTube Videos, YouTube Shorts), transcribes the audio, and uses AI to summarize key takeaways, research angles, and quotes into highly structured Obsidian-ready Markdown notes.

Perfect for researchers, creators, and idea curators who want to capture value from social media completely hands-free.

---

## ✨ Features

- **Multi-Platform Auto-Detection:** Seamlessly processes both Instagram Reels and YouTube content (Videos & Shorts). Hand it any URL and it figures out what to do.
- **Automated Audio Extraction:** Powered by `yt-dlp` and automatically discovers `ffmpeg` seamlessly.
- **Local Private Transcription:** Uses CPU-optimized `faster-whisper` (`int8` precision) for ultra-fast and stable offline transcription (designed specifically for laptops with unstable discrete GPUs).
- **AI Synthesis:** Connects to [Omniroute](https://github.com/omniroute), OpenAI, or local vLLM instances to generate high-signal summaries.
- **Structured Knowledge:** Outputs standard YAML-frontmatter Markdown notes containing timelines, tags, AI insights, and platform-specific metadata (author, video ID, upload date).
- **Smart Filing:** Configurable output organization (e.g., sort downloads into platform-specific subfolders automatically).
- **Clipboard Watcher Mode:** Run `reel watch` in the background; it automatically detects and processes reels and videos the moment you copy a link.

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/smrt-nerd/reel-digest.git
   cd reel-digest
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the package:**
   ```bash
   pip install -e .
   ```

4. **Prepare the configuration:**
   Copy the example config and add your API keys:
   ```bash
   cp .env.example .env
   ```

*(Note: FFmpeg is required. If running on Windows, the pipeline attempts to auto-discover existing WinGet or CapCut FFmpeg installations automatically.)*

---

## ⚙️ Configuration (`.env`)

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `OMNIROUTE_API_KEY` | Your AI Inference API key | *(Empty)* |
| `OMNIROUTE_BASE_URL` | Endpoint (e.g. `http://localhost:8000/v1`) | `https://api.openai.com/v1` |
| `OMNIROUTE_MODEL` | The LLM model used for summarization | `gpt-4o-mini` |
| `WHISPER_MODEL_SIZE` | Size of the Whisper model to download | `small.en` |
| `WHISPER_DEVICE` | `cpu` or `cuda`. (CPU recommended for stability) | `cpu` |
| `WHISPER_COMPUTE_TYPE`| `int8` (fastest CPU), `float16` (GPU) | `int8` |
| `OUTPUT_DIR` | Folder to save the markdown notes | `output` |
| `PLATFORM_OUTPUT_ORG`| Auto-sort files: `same_folder`, `subfolders`, `prefix` | `same_folder` |
| `BROWSER_COOKIES`| Use `chrome`, `firefox`, `brave` for IG auth | *(Empty)* |

---

## 🚀 Usage

ReelDigest ships with a beautiful CLI powered by `Typer` and `Rich`.

### 1. Process a Single URL
```bash
reel digest "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```
*Tip: Quotes around the URL prevent terminal character escaping.*

### 2. Live Clipboard Watcher (Magic Mode ✨)
Leave this running in the background while you scroll on your phone/PC. Whenever you "Copy Link" for an Instagram reel or YouTube video, ReelDigest automatically wakes up, downloads, transcribes, and saves the summarized note!
```bash
reel watch
```

### 3. Batch Processing
Process an entire list of mixed URLs overnight:
```bash
reel batch links.txt
```

---

## 🏗️ Architecture Design

ReelDigest is built completely modular. You can reuse components individually in other scripts:

- **`platform/`**: Abstract class architecture easily extensible to new platforms. Includes URL detection regexes.
- **`detector.py`**: Smart routing to auto-detect platform metadata and capabilities just from the raw URL.
- **`downloader.py`**: Isolates `yt-dlp` logic and environment variables.
- **`transcriber.py`**: Abstract base class. `FasterWhisperTranscriber` implements the CPU-safe int8 optimizations.
- **`summarizer.py`**: Interacts with any OpenAI-compatible API to inject context and return markdown.
- **`storage.py`**: Handles filename sanitization, timestamps, platform-specific filing, and YAML configurations.

---

## 📜 License
Published under the MIT License. Feel free to fork, expand, and embed inside your own apps!
