#!/usr/bin/env python3
"""
add_voice.py - Clone a voice from a YouTube video.

Usage:
    python add_voice.py "https://youtube.com/watch?v=..." --name matt
    python add_voice.py "https://youtube.com/watch?v=..." --name matt --start 30 --duration 45

Requirements:
    - yt-dlp (pip install yt-dlp)
    - ffmpeg (brew install ffmpeg / apt install ffmpeg)
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

VOICES_DIR = Path(__file__).parent.parent / "voices"
DEFAULT_DURATION = 30  # seconds
DEFAULT_SAMPLE_RATE = 24000


def check_dependencies():
    """Check that required tools are installed."""
    for tool in ["yt-dlp", "ffmpeg"]:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"ERROR: {tool} not found. Install it first.", file=sys.stderr)
            print(f"  brew install {tool}" if sys.platform == "darwin" else f"  apt install {tool}", file=sys.stderr)
            sys.exit(1)


def download_audio(url: str, output_path: str) -> bool:
    """Download audio from YouTube video."""
    print(f"Downloading audio from: {url}")
    result = subprocess.run([
        "yt-dlp",
        "-x",  # Extract audio
        "--audio-format", "wav",
        "--audio-quality", "0",  # Best quality
        "-o", output_path,
        url
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: Failed to download audio: {result.stderr}", file=sys.stderr)
        return False
    return True


def extract_segment(input_path: str, output_path: str, start: int, duration: int) -> bool:
    """Extract a segment from audio file."""
    print(f"Extracting {duration}s segment starting at {start}s...")
    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-ss", str(start),
        "-t", str(duration),
        "-ar", str(DEFAULT_SAMPLE_RATE),  # Resample to TTS expected rate
        "-ac", "1",  # Mono
        "-acodec", "pcm_s16le",  # 16-bit PCM
        output_path
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: Failed to extract segment: {result.stderr}", file=sys.stderr)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Clone a voice from a YouTube video",
        epilog="Example: python add_voice.py 'https://youtube.com/watch?v=xyz' --name morgan"
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--name", "-n", required=True, help="Name for the voice (e.g., 'morgan')")
    parser.add_argument("--start", "-s", type=int, default=0, help="Start time in seconds (default: 0)")
    parser.add_argument("--duration", "-d", type=int, default=DEFAULT_DURATION, 
                        help=f"Duration in seconds (default: {DEFAULT_DURATION})")
    parser.add_argument("--output-dir", "-o", type=Path, default=VOICES_DIR,
                        help="Output directory for voice files")
    args = parser.parse_args()
    
    check_dependencies()
    
    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = args.output_dir / f"{args.name}.wav"
    
    if output_path.exists():
        response = input(f"Voice '{args.name}' already exists. Overwrite? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Download full audio
        temp_audio = os.path.join(temp_dir, "audio.wav")
        if not download_audio(args.url, temp_audio):
            sys.exit(1)
        
        # Find the actual downloaded file (yt-dlp may add extension)
        actual_file = None
        for f in os.listdir(temp_dir):
            if f.endswith('.wav'):
                actual_file = os.path.join(temp_dir, f)
                break
        
        if not actual_file:
            print("ERROR: Downloaded audio file not found", file=sys.stderr)
            sys.exit(1)
        
        # Extract segment
        if not extract_segment(actual_file, str(output_path), args.start, args.duration):
            sys.exit(1)
    
    print(f"\n✓ Voice '{args.name}' saved to: {output_path}")
    print(f"\nTo use this voice:")
    print(f"  curl http://localhost:8001/v1/audio/speech -X POST \\")
    print(f"    -H 'Content-Type: application/json' \\")
    print(f"    -d '{{\"input\": \"Hello world\", \"voice\": \"{args.name}\"}}' \\")
    print(f"    -o test.wav")
    print(f"\nNote: Restart the TTS server to load the new voice.")


if __name__ == "__main__":
    main()
