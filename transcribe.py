import argparse
import os
import ssl
import sys
from pathlib import Path

# Bypass SSL verification for model download (self-signed cert in network chain)
ssl._create_default_https_context = ssl._create_unverified_context

try:
    import yt_dlp
except ImportError:
    sys.exit("Missing dependency: pip install yt-dlp")

try:
    import whisper
except ImportError:
    sys.exit("Missing dependency: pip install openai-whisper")

INPUT_DIR = Path(__file__).parent / "input"
OUTPUT_DIR = Path(__file__).parent / "output"


def download_audio(url: str, output_path: str) -> str:
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "no_warnings": True,
        "cookiesfrombrowser": ("chrome",),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "video")
    return title


def transcribe(audio_path: str, language: str, model_name: str) -> dict:
    print(f"Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)
    print("Transcribing... (this may take a while)")
    result = model.transcribe(audio_path, language=language, verbose=False)
    return result


def save_transcript(result: dict, output_file: str, fmt: str):
    if fmt == "txt":
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["text"].strip())

    elif fmt == "srt":
        with open(output_file, "w", encoding="utf-8") as f:
            for i, seg in enumerate(result["segments"], start=1):
                start = _format_timestamp(seg["start"])
                end = _format_timestamp(seg["end"])
                f.write(f"{i}\n{start} --> {end}\n{seg['text'].strip()}\n\n")

    elif fmt == "vtt":
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")
            for seg in result["segments"]:
                start = _format_timestamp(seg["start"], vtt=True)
                end = _format_timestamp(seg["end"], vtt=True)
                f.write(f"{start} --> {end}\n{seg['text'].strip()}\n\n")


def _format_timestamp(seconds: float, vtt: bool = False) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    sep = "." if vtt else ","
    return f"{h:02}:{m:02}:{s:02}{sep}{ms:03}"


def main():
    parser = argparse.ArgumentParser(
        description="Download a YouTube video and generate a transcript using Whisper."
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "--language", "-l", default="zh",
        help="Language code (default: zh for Mandarin). Use 'en' for English, etc."
    )
    parser.add_argument(
        "--model", "-m", default="medium",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: medium)"
    )
    parser.add_argument(
        "--format", "-f", default="txt",
        choices=["txt", "srt", "vtt"],
        help="Output format (default: txt)"
    )
    args = parser.parse_args()

    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    safe_name = _safe_filename(args.url.split("v=")[-1].split("&")[0])
    audio_path = str(INPUT_DIR / safe_name)

    print(f"Downloading audio from: {args.url}")
    title = download_audio(args.url, audio_path)
    audio_file = audio_path + ".mp3"

    if not os.path.exists(audio_file):
        sys.exit("Audio download failed — check the URL and that ffmpeg is installed.")

    print(f"Audio saved to: {audio_file}")

    result = transcribe(audio_file, args.language, args.model)

    output_file = OUTPUT_DIR / f"{_safe_filename(title)}.{args.format}"
    save_transcript(result, str(output_file), args.format)

    print(f"\nDone! Transcript saved to: {output_file}")
    print(f"Total segments: {len(result['segments'])}")


def _safe_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in " -_" else "_" for c in name).strip()


if __name__ == "__main__":
    main()
