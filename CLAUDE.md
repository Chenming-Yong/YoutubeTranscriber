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

## Key behaviours

- **SSL bypass** — `ssl._create_default_https_context = ssl._create_unverified_context` is set at import time to handle corporate proxies with self-signed certificates. This only affects the Whisper model download via Python's `urllib`.
- **venv is local** — `run.sh` creates `venv/` inside the project directory on first run. Delete it to force a clean reinstall.
- **Model cache is global** — Whisper models live in `~/.cache/whisper/` and are shared across projects. `medium` is ~1.42 GB.
- **Default language is Mandarin** (`zh`) — pass `--language en` or another ISO 639-1 code to change it. Use `--language auto` to let Whisper detect the language automatically (slightly slower).
- **Audio is not auto-deleted** — MP3s in `input/` persist after transcription and must be deleted manually.
