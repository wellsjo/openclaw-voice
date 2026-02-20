# OpenClaw Voice

Local TTS with custom voice cloning for [OpenClaw](https://github.com/openclaw/openclaw) agents.

Generate voice memos, podcasts, and audio content using your own cloned voices — all running locally, no API keys required.

## Features

- **Voice Cloning** — Clone any voice from a YouTube video in seconds
- **OpenAI-Compatible API** — Drop-in replacement for OpenAI's TTS endpoint
- **Local & Private** — Everything runs on your machine
- **OpenClaw Integration** — SKILL.md for agent automation

## Quick Start

### 1. Install

```bash
git clone https://github.com/wellsjo/openclaw-voice.git
cd openclaw-voice
./install.sh
```

### 2. Start the Server

```bash
./start.sh
# Server runs at http://localhost:8001
```

### 3. Set Default Voice (optional)

```bash
# Add to your shell profile (~/.zshrc, ~/.bashrc, etc.)
export TTS_DEFAULT_VOICE=alba
```

Scripts will use this voice automatically.

### 4. Generate Speech

```bash
curl http://localhost:8001/v1/audio/speech -X POST \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello world", "voice": "'$TTS_DEFAULT_VOICE'"}' \
  -o hello.wav
```

## Adding Custom Voices

Clone a voice from any YouTube video:

```bash
# Provide the URL and specific timestamps for clean speech
python scripts/add_voice.py "https://youtube.com/watch?v=..." --name morgan --start 45 --duration 30

# Use your new voice
curl http://localhost:8001/v1/audio/speech -X POST \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello world", "voice": "morgan"}' \
  -o test.wav
```

**Important:** You must provide specific timestamps (`--start` and `--duration`) pointing to a clean segment of speech. The tool cannot analyze the video — you need to watch it and identify 30-60 seconds where:
- Only the target voice is speaking
- No background music or other speakers
- Clear audio quality

**Example workflow:**
1. Find a YouTube interview or podcast with the voice you want
2. Watch it and note a timestamp with clean solo speech (e.g., 1:30 to 2:15)
3. Run: `python scripts/add_voice.py "URL" --name morgan --start 90 --duration 45`

## Available Voices

**Built-in voices:**
- alba, marius, javert, jean, fantine, cosette, eponine, azelma

**OpenAI aliases** (mapped to built-in voices):
- alloy → alba
- echo → jean
- fable → fantine
- onyx → cosette
- nova → eponine
- shimmer → azelma

**Custom voices:**
- Any `.wav` file in `voices/` directory is auto-loaded on startup

## Long-Form Content

For podcasts and longer content, use the generation script:

```bash
# From a text file
python scripts/generate_audio.py script.txt -o podcast.mp3

# With custom voice
python scripts/generate_audio.py script.txt -o podcast.mp3 -v morgan
```

The script handles:
- Chunking long text into TTS-sized segments
- Concatenating audio seamlessly
- Converting to MP3

## OpenClaw Integration

Copy `SKILL.md` to your OpenClaw skills directory:

```bash
mkdir -p ~/skills/voice
cp SKILL.md ~/skills/voice/
cp -r scripts ~/skills/voice/
```

Or reference directly in your agent config.

## API Reference

### POST /v1/audio/speech

Generate speech from text.

```json
{
  "model": "tts-1",
  "input": "Text to speak",
  "voice": "alba",
  "response_format": "wav",
  "speed": 1.0
}
```

**Parameters:**
- `model`: `tts-1` or `tts-1-hd` (both use same backend)
- `input`: Text to convert (max 4096 chars)
- `voice`: Voice name (built-in, alias, or custom)
- `response_format`: `wav`, `mp3`, `opus`, `aac`, `flac`, `pcm`
- `speed`: 0.25 to 4.0

### GET /health

Check server status.

## Requirements

- Python 3.10+
- ffmpeg
- yt-dlp (for voice cloning)

## Credits

Based on [pocket-tts-openapi](https://github.com/IceFog72/pocket-tts-openapi) by IceFog72.

## Responsible Use

This tool enables voice cloning from audio samples. Please use responsibly:

- **Get consent** before cloning someone's voice
- **Do not use** for impersonation, fraud, or deception
- **Do not create** non-consensual deepfakes or misleading content
- **Respect copyright** when using audio from YouTube or other sources

Voice cloning technology can be misused. The authors are not responsible for how this tool is used.

## License

MIT
