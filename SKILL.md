---
name: voice
description: Generate audio from local TTS for podcasts, audio summaries, daily briefs, voice memos, or any spoken content. Use when spoken output is requested, and repair the local voice runtime with `python scripts/ensure_tts.py` if localhost:8001 is unhealthy or a Python upgrade broke the virtualenv.
---

# Voice

Generate audio with the local Pocket TTS skill.

## Canonical commands

Install or repair the runtime:
```bash
cd ~/git-repos/openclaw-voice
python3 scripts/ensure_tts.py --install-only
```

Start or self-heal the server:
```bash
cd ~/git-repos/openclaw-voice
python3 scripts/ensure_tts.py
```

Verify:
```bash
curl -s http://localhost:8001/health
```

What `ensure_tts.py` does:
- pick a supported local Python (3.10-3.14)
- rebuild `.venv` if it is missing or broken
- reinstall requirements
- start `pocketapi.py`
- wait for `localhost:8001/health`

Use it whenever the server is down, after Python/Homebrew upgrades, or before blaming TTS.

## Configuration

Set defaults in the shell profile if needed:
```bash
export TTS_DEFAULT_VOICE=alba
export TTS_DEFAULT_SPEED=1.0
```

## Adding custom voices

Require the user to provide:
- YouTube URL
- exact timestamps with 30-60 seconds of isolated speech

Then run:
```bash
cd ~/git-repos/openclaw-voice
python scripts/add_voice.py "URL" --name <voice_name> --start <seconds> --duration 30
python scripts/ensure_tts.py
```

## Generating audio

Quick request:
```bash
curl -s http://localhost:8001/v1/audio/speech -X POST \
  -H "Content-Type: application/json" \
  -d '{"input":"Text here","voice":"'"${TTS_DEFAULT_VOICE:-alba}"'","speed":'"${TTS_DEFAULT_SPEED:-1.0}"'}' \
  -o output.wav
```

Long-form:
```bash
cd ~/git-repos/openclaw-voice
python scripts/generate_audio.py script.txt -o output.mp3
```

`generate_audio.py` now auto-runs `scripts/ensure_tts.py` if the server is unhealthy.

## Voices

Built-in:
- alba
- marius
- javert
- jean
- fantine
- cosette
- eponine
- azelma

Custom:
- any `.wav` file in `voices/`

## Workflow

1. Gather content with `web_fetch`, files, or user text.
2. Write a conversational script.
3. Run `python scripts/generate_audio.py ...`.
4. Deliver the audio file with a short summary.
