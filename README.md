# OpenClaw Voice

Local TTS with custom voice cloning for [OpenClaw](https://github.com/openclaw/openclaw) agents.

## Requirements

- Python 3.10+
- ffmpeg
- yt-dlp (for voice cloning)

## Install

```bash
git clone https://github.com/wellsjo/openclaw-voice.git
cd openclaw-voice
pip install -r requirements.txt
```

## Run

```bash
python pocketapi.py
# Server runs at http://localhost:8001
```

## Agent Setup

Copy the skill to your OpenClaw skills directory:

```bash
cp -r /path/to/openclaw-voice ~/skills/voice
```

Or symlink:

```bash
ln -s /path/to/openclaw-voice ~/skills/voice
```

The agent will handle voice configuration, custom voice setup, and audio generation from there.

## Responsible Use

This tool enables voice cloning from audio samples. Please use responsibly:

- **Get consent** before cloning someone's voice
- **Do not use** for impersonation, fraud, or deception
- **Do not create** non-consensual deepfakes or misleading content
- **Respect copyright** when using audio from YouTube or other sources

## Credits

Based on [pocket-tts-openapi](https://github.com/IceFog72/pocket-tts-openapi) by IceFog72.

## License

MIT
