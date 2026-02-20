---
name: voice
description: Generate audio from text using TTS. Use for podcasts, audio summaries, daily briefs, voice memos, or any spoken content.
---

# Voice

Generate audio content using local TTS. Supports podcasts, summaries, briefs, voice memos — anything spoken.

## Prerequisites

TTS server must be running at `http://localhost:8001`. Check with:
```bash
curl -s http://localhost:8001/health
```

## Quick TTS

For simple audio generation:
```bash
curl -s "http://localhost:8001/v1/audio/speech" -X POST \
  -H "Content-Type: application/json" \
  -d '{"input":"Your text here", "voice":"alba"}' \
  -o output.wav
```

## Long-Form Content

For podcasts and longer content:
```bash
python scripts/generate_audio.py script.txt -o output.mp3
```

Override voice with `-v`:
```bash
python scripts/generate_audio.py script.txt -o output.mp3 -v morgan
```

## Adding Custom Voices

When user wants a custom voice:

1. Ask them to find a YouTube video with clear speech (30-60 seconds of the voice they want)
2. Run the add_voice script:
```bash
python scripts/add_voice.py "https://youtube.com/watch?v=..." --name <voice_name>
```
3. Restart TTS server to load the new voice
4. Use the voice by name: `-v <voice_name>`

**Tips for good source audio:**
- Interviews and podcasts work best
- Avoid background music
- Skip intros with `--start 30`
- 30-60 seconds is ideal

## Available Voices

**Built-in:** alba, marius, javert, jean, fantine, cosette, eponine, azelma

**Custom:** Any `.wav` file in `voices/` directory (auto-loaded on server start)

## Use Cases

- **Voice memos** — Quick audio messages
- **Podcasts** — Long-form conversational content
- **Daily briefs** — Morning summaries, news roundups
- **Audio summaries** — TL;DR versions of documents

## Podcast Workflow

### 1. Get Content

Based on input type:
- **URL**: Use `web_fetch` to get readable content
- **File**: Read the file directly
- **Text**: Use as-is

### 2. Write Script

Create a conversational script. Don't just summarize — make it engaging:

**Guidelines:**
- Length: 2000-4000 words for 10-20 minute podcasts
- Tone: Conversational, like explaining to a friend
- Structure: Hook → Context → Deep dive → Takeaways

**Style:**
- Natural speech patterns ("So here's the thing...", "What's interesting is...")
- Rhetorical questions to engage listeners
- Vary sentence length
- Add personality and opinions

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
- **Slow down**: Use `ffmpeg -filter:a "atempo=0.9"` if speech is too fast.
