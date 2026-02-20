#!/usr/bin/env python3
"""
generate_audio.py - Generate podcast audio from a script using Pocket TTS.

Handles long scripts by chunking into segments and concatenating.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import urllib.request
import urllib.error

TTS_URL = os.environ.get("TTS_URL", "http://localhost:8001/v1/audio/speech")
DEFAULT_VOICE = os.environ.get("TTS_DEFAULT_VOICE", "alba")
DEFAULT_SPEED = float(os.environ.get("TTS_DEFAULT_SPEED", "1.0"))
MAX_CHARS_PER_CHUNK = 4000  # Safe limit per TTS request


def check_tts_server():
    """Check if TTS server is running."""
    try:
        req = urllib.request.Request("http://localhost:8001/health")
        urllib.request.urlopen(req, timeout=5)
        return True
    except:
        return False


def chunk_text(text: str, max_chars: int = MAX_CHARS_PER_CHUNK) -> list[str]:
    """Split text into chunks at sentence boundaries."""
    chunks = []
    current = ""
    
    # Split by sentences (rough heuristic)
    sentences = []
    temp = ""
    for char in text:
        temp += char
        if char in '.!?' and len(temp) > 1:
            sentences.append(temp.strip())
            temp = ""
    if temp.strip():
        sentences.append(temp.strip())
    
    for sentence in sentences:
        if len(current) + len(sentence) + 1 > max_chars:
            if current:
                chunks.append(current.strip())
            current = sentence
        else:
            current = current + " " + sentence if current else sentence
    
    if current:
        chunks.append(current.strip())
    
    return chunks if chunks else [text]


def generate_chunk(text: str, voice: str, speed: float, output_path: str) -> bool:
    """Generate audio for a single chunk."""
    payload = json.dumps({
        "model": "tts-1",
        "input": text,
        "voice": voice,
        "speed": speed
    }).encode('utf-8')
    
    req = urllib.request.Request(
        TTS_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())
        return True
    except urllib.error.URLError as e:
        print(f"Error generating audio: {e}", file=sys.stderr)
        return False


def concatenate_audio(input_files: list[str], output_path: str) -> bool:
    """Concatenate audio files using ffmpeg."""
    if len(input_files) == 1:
        # Convert single file to MP3
        result = subprocess.run([
            'ffmpeg', '-y', '-i', input_files[0],
            '-codec:a', 'libmp3lame', '-b:a', '192k', output_path
        ], capture_output=True, text=True)
        return result.returncode == 0
    
    # Create concat list file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for path in input_files:
            f.write(f"file '{path}'\n")
        list_path = f.name
    
    try:
        # Concat and encode to MP3 in one step
        result = subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', list_path, '-codec:a', 'libmp3lame', '-b:a', '192k', output_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"ffmpeg error: {result.stderr}", file=sys.stderr)
            return False
        return True
    finally:
        os.unlink(list_path)


def main():
    parser = argparse.ArgumentParser(description='Generate podcast audio from script')
    parser.add_argument('script_file', help='Path to the podcast script (text file)')
    parser.add_argument('-o', '--output', default='podcast.mp3', help='Output file path')
    parser.add_argument('-v', '--voice', default=DEFAULT_VOICE, 
                        help=f'TTS voice (default: $TTS_DEFAULT_VOICE or "{DEFAULT_VOICE}")')
    parser.add_argument('-s', '--speed', type=float, default=DEFAULT_SPEED,
                        help=f'Speech speed 0.25-4.0 (default: $TTS_DEFAULT_SPEED or {DEFAULT_SPEED})')
    parser.add_argument('--text', help='Direct text input instead of file')
    args = parser.parse_args()
    
    # Check TTS server
    if not check_tts_server():
        print("ERROR: TTS server not running at localhost:8001", file=sys.stderr)
        print("Start it with: cd ~/projects/pocket-tts-openapi && source venv/bin/activate && python pocketapi.py", file=sys.stderr)
        sys.exit(1)
    
    # Get script text
    if args.text:
        script_text = args.text
    else:
        script_path = Path(args.script_file)
        if not script_path.exists():
            print(f"ERROR: Script file not found: {script_path}", file=sys.stderr)
            sys.exit(1)
        script_text = script_path.read_text()
    
    # Chunk the script
    chunks = chunk_text(script_text)
    print(f"Script split into {len(chunks)} chunk(s)")
    
    # Generate audio for each chunk
    temp_files = []
    temp_dir = tempfile.mkdtemp()
    
    try:
        for i, chunk in enumerate(chunks):
            chunk_path = os.path.join(temp_dir, f"chunk_{i:03d}.wav")
            print(f"Generating chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
            
            if not generate_chunk(chunk, args.voice, args.speed, chunk_path):
                print(f"Failed to generate chunk {i+1}", file=sys.stderr)
                sys.exit(1)
            
            temp_files.append(chunk_path)
        
        # Concatenate
        print(f"Concatenating {len(temp_files)} chunk(s)...")
        if not concatenate_audio(temp_files, args.output):
            print("Failed to concatenate audio", file=sys.stderr)
            sys.exit(1)
        
        print(f"Podcast saved to: {args.output}")
        
    finally:
        # Cleanup temp files
        for f in temp_files:
            try:
                os.unlink(f)
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass


if __name__ == '__main__':
    main()
