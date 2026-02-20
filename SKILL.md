---
name: voice
description: Generate audio from text using TTS. Use for podcasts, audio summaries, daily briefs, voice memos, or any spoken content.
---

# Voice

Generate audio content using local TTS.

## Installation

If TTS server isn't running (`curl -s http://localhost:8001/health` fails):

```bash
# Clone if not already present
if [ ! -d ~/skills/voice ]; then
  git clone https://github.com/wellsjo/openclaw-voice.git ~/skills/voice
fi

cd ~/skills/voice

# Install dependencies
pip install -r requirements.txt

# Install system deps if missing
which ffmpeg || brew install ffmpeg      # macOS
which yt-dlp || pip install yt-dlp
```

Start the server:
```bash
cd ~/skills/voice && nohup python pocketapi.py > /tmp/tts.log 2>&1 &
```

Verify:
```bash
curl -s http://localhost:8001/health
```

## Configuration

Set defaults in user's shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export TTS_DEFAULT_VOICE=alba       # or custom voice name
export TTS_DEFAULT_SPEED=1.0        # 0.25-4.0, lower = slower
```

## Adding Custom Voices

User must provide:
- YouTube URL with the voice they want
- **Specific timestamps** (you cannot watch the video)

Tell them:
> "Find a YouTube video with the voice you want. Watch it and give me the exact timestamp of 30-60 seconds where only that person is speaking clearly — no background music. Example: 'Use 1:30 to 2:15 from this video: [URL]'"

Once they provide URL + timestamps:
```bash
cd ~/skills/voice
python scripts/add_voice.py "URL" --name <voice_name> --start <seconds> --duration 30
```

Restart server to load new voice:
```bash
pkill -f pocketapi.py
cd ~/skills/voice && nohup python pocketapi.py > /tmp/tts.log 2>&1 &
```

Update their shell profile:
```bash
echo 'export TTS_DEFAULT_VOICE=<voice_name>' >> ~/.zshrc
```

## Generating Audio

### Quick TTS
```bash
curl -s "http://localhost:8001/v1/audio/speech" -X POST \
  -H "Content-Type: application/json" \
  -d '{"input":"Text here", "voice":"'$TTS_DEFAULT_VOICE'", "speed":'${TTS_DEFAULT_SPEED:-1.0}'}' \
  -o output.wav
```

### Long-form (podcasts, briefs)
```bash
python ~/skills/voice/scripts/generate_audio.py script.txt -o output.mp3
```

Override defaults:
```bash
python ~/skills/voice/scripts/generate_audio.py script.txt -o output.mp3 -v alba -s 0.92
```

## Available Voices

**Built-in:** alba, marius, javert, jean, fantine, cosette, eponine, azelma

**Custom:** Any `.wav` in `voices/` directory (loaded on server start)

## Podcast Workflow

1. **Get content** — `web_fetch` for URLs, read files, or use provided text
2. **Write script** — Conversational, 2000-4000 words, not a dry summary
3. **Generate** — `python ~/skills/voice/scripts/generate_audio.py script.txt -o podcast.mp3`
4. **Deliver** — Send audio with brief summary
