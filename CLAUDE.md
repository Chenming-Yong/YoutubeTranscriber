# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the tool

Always use `run.sh` — it handles venv creation, activation, and dependency installation automatically:

```bash
# Always quote the URL to prevent shell glob expansion on ? and &
./run.sh "https://www.youtube.com/watch?v=VIDEO_ID"

# Common options
./run.sh "URL" --language zh --model medium --format txt
./run.sh "URL" --model large --format srt
```

To run `transcribe.py` directly (e.g. during development), activate the venv first:

```bash
source venv/bin/activate
python transcribe.py "URL" [options]
```

## Folder structure

| Folder | Purpose |
|--------|---------|
| `input/` | Downloaded MP3 audio files — kept until manually deleted |
| `output/` | Generated transcript files (txt, srt, vtt) |

Both folders are created automatically on first run. Their contents are gitignored.

## Architecture

The tool is a single-file CLI (`transcribe.py`) with three stages that run sequentially:

1. **Download** (`download_audio`) — yt-dlp pulls the best audio stream and ffmpeg converts it to MP3, saved to `input/` named by video ID.
2. **Transcribe** (`transcribe`) — `whisper.load_model()` loads from `~/.cache/whisper/` (downloaded on first use). The model runs entirely locally on CPU (FP32).
3. **Save** (`save_transcript`) — writes `txt`, `srt`, or `vtt` to `output/`, named after the sanitised video title.

## Dependencies

### System requirements (install manually)

| Tool | Purpose | Install |
|------|---------|---------|
| Python 3.8+ | Runtime | [python.org](https://www.python.org) or `brew install python` |
| ffmpeg | Converts downloaded audio to MP3 | `brew install ffmpeg` |

### Python libraries (auto-installed by `run.sh`)

| Library | Purpose |
|---------|---------|
| `yt-dlp` | Downloads audio from YouTube |
| `openai-whisper` | Local speech-to-text transcription (no API key needed) |

### Whisper model files (auto-downloaded on first use)

Whisper models are downloaded from OpenAI's servers and cached at `~/.cache/whisper/`. They are **not** stored in this repo.

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | ~75 MB | Fastest | Lowest |
| base | ~145 MB | Fast | Low |
| small | ~465 MB | Moderate | Moderate |
| medium | ~1.42 GB | Slow | Good (default) |
| large | ~2.87 GB | Slowest | Best |

The model cache is global and shared across projects. Delete `~/.cache/whisper/` to free disk space.

## Key behaviours

- **SSL bypass** — `ssl._create_default_https_context = ssl._create_unverified_context` is set at import time to handle corporate proxies with self-signed certificates. This only affects the Whisper model download via Python's `urllib`.
- **venv is local** — `run.sh` creates `venv/` inside the project directory on first run. Delete it to force a clean reinstall.
- **Language prompt** — `run.sh` asks you to choose Mandarin or English before running. You can still pass `--language` directly to `transcribe.py` for other languages.
- **Audio is not auto-deleted** — MP3s in `input/` persist after transcription and must be deleted manually.
