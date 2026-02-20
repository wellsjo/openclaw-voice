---
name: voice
description: Generate audio from text using TTS. Use for podcasts, audio summaries, daily briefs, voice memos, or any spoken content.
---

# Voice

Generate audio content using local TTS. Supports podcasts, summaries, briefs, voice memos — anything spoken.

## Setup (run once per user)

### 1. Check if TTS server is running

```bash
curl -s http://localhost:8001/health
```

If not running, guide user to start it:
```bash
cd ~/skills/voice  # or wherever they cloned openclaw-voice
python pocketapi.py
```

For background/persistent running, suggest they add to their shell startup or use a process manager.

### 2. Configure defaults

Ask user to add to their shell profile (`~/.zshrc`, `~/.bashrc`, etc.):

```bash
export TTS_DEFAULT_VOICE=alba       # or their custom voice name
export TTS_DEFAULT_SPEED=1.0        # 0.25-4.0, lower = slower
```

### 3. Add a custom voice (optional)

If user wants a custom voice, they need to:

1. Find a YouTube video with clear speech from the target voice
2. Give you the URL and **specific timestamps** (you cannot watch the video)
3. You run:
```bash
python scripts/add_voice.py "URL" --name <voice_name> --start <seconds> --duration 30
```
4. Restart TTS server to load the new voice

**What to tell the user:**
> "Find a YouTube video with the voice you want (interviews work great). Watch it and give me the exact timestamp of 30-60 seconds where only that person is speaking clearly — no background music or other voices. Example: 'Use 1:30 to 2:15 from this video: [URL]'"

## Generating Audio

### Quick TTS (short text)

```bash
curl -s "http://localhost:8001/v1/audio/speech" -X POST \
  -H "Content-Type: application/json" \
  -d '{"input":"Your text here", "voice":"'$TTS_DEFAULT_VOICE'", "speed":'${TTS_DEFAULT_SPEED:-1.0}'}' \
  -o output.wav
```

### Long-form content (podcasts, briefs)

```bash
python scripts/generate_audio.py script.txt -o output.mp3
```

Uses `$TTS_DEFAULT_VOICE` and `$TTS_DEFAULT_SPEED` automatically. Override:
```bash
python scripts/generate_audio.py script.txt -o output.mp3 -v alba -s 0.92
```

## Available Voices

**Built-in:** alba, marius, javert, jean, fantine, cosette, eponine, azelma

**Custom:** Any `.wav` file in `voices/` directory (auto-loaded on server start)

## Podcast Workflow

### 1. Get Content

- **URL**: Use `web_fetch` to get readable content
- **File**: Read the file directly
- **Text**: Use as-is

### 2. Write Script

Create a conversational script — don't just summarize:

- **Length**: 2000-4000 words for 10-20 minute podcasts
- **Tone**: Conversational, like explaining to a friend
- **Structure**: Hook → Context → Deep dive → Takeaways
- **Style**: Natural speech patterns, rhetorical questions, varied sentence length

### 3. Generate Audio

```bash
python scripts/generate_audio.py script.txt -o podcast.mp3
```

### 4. Deliver

Send the audio file with a brief summary of what's covered.

## Tips

- **Longer is better**: 2-minute podcasts feel thin. Aim for 10+ minutes.
- **Add context**: Don't assume the listener knows the source material.
- **Be specific**: Concrete examples beat abstract explanations.
