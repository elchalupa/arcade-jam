# arcade-jam

AI-powered jam roulette for music streams — viewers trigger backing tracks, streamer plays along.

## Concept

Viewers redeem channel points to spin the "jam roulette." A random AI-generated backing track plays, and the streamer has to improvise over it live. Like karaoke, but for instrumentalists.

**The twist:** The backing track has no bass — that's your job.

## How It Works

### Pre-Stream (Batch Generation)

1. You define a list of vibes/prompts (genre, BPM, instruments)
2. Run the generator on RunPod (~$0.20 for a pool of tracks)
3. Download the backing tracks to your PC
4. Tracks are ready for stream

### During Stream

1. Viewer redeems "Jam Roulette" channel points
2. Streamer.bot picks a random track from the pool
3. The vibe/prompt displays on screen
4. Backing track plays through OBS
5. You jam along live
6. Track moves to "played" folder (no repeats)

## Architecture

```
PRE-STREAM (RunPod)                      DURING STREAM (Local)
┌─────────────────────┐                  ┌─────────────────────┐
│   producer.py       │                  │   Streamer.bot      │
│                     │   Download       │                     │
│   MusicGen Large    │ ───────────────► │   Channel Point     │
│   + Demucs          │   .wav files     │   Redemption        │
│                     │                  │                     │
│   Output:           │                  │   → Random track    │
│   READY_FOR_BASS.wav│                  │   → Display vibe    │
└─────────────────────┘                  │   → Play audio      │
                                         └─────────────────────┘
                                                   │
                                                   ▼
                                         ┌─────────────────────┐
                                         │   Streamer jams 🎸  │
                                         └─────────────────────┘
```

## Project Structure

```
arcade-jam/
├── generator/
│   ├── producer.py         # RunPod batch generator
│   ├── prompts.yaml        # Your curated vibes
│   └── requirements.txt    # Python dependencies
│
├── streamerbot/
│   └── setup.md            # Streamer.bot configuration guide
│
├── pool/                   # Local only (gitignored)
│   ├── ready/              # Tracks waiting to be played
│   └── played/             # Used tracks (no repeats)
│
├── README.md
├── ROADMAP.md
└── LICENSE
```

## Quick Start

### 1. Generate Your Pool (RunPod)

Spin up an A40 or A6000 pod (~$0.50/hr):

```bash
# On RunPod
apt-get update && apt-get install -y ffmpeg libsndfile1
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install git+https://github.com/facebookresearch/audiocraft.git
pip install demucs scipy

cd /workspace
# Upload producer.py and prompts.yaml
python producer.py
```

### 2. Download to PC

```bash
# On your local machine
scp -P [PORT] -r root@[IP]:/workspace/sessions ./pool/ready
```

Or use the RunPod JupyterLab interface to download.

### 3. Configure Streamer.bot

See [streamerbot/setup.md](streamerbot/setup.md) for detailed instructions.

### 4. Stream!

- Start your music stream
- Have a few tracks in `pool/ready/`
- Viewers redeem → you jam

## Cost Estimate

| Pool Size | Generation Time | Cost |
|-----------|-----------------|------|
| 12 tracks (3 prompts × 4 takes) | ~8 min | ~$0.20 |
| 24 tracks (6 prompts × 4 takes) | ~15 min | ~$0.40 |
| 48 tracks (12 prompts × 4 takes) | ~30 min | ~$0.80 |

One batch generation can fuel multiple streams.

## Customizing Prompts

Edit `generator/prompts.yaml` to define your vibes:

```yaml
prompts:
  - name: "Neo Soul"
    prompt: "Neo-soul loop, 85 bpm, fender rhodes, dilla swing drums, vinyl crackle, warm sub bass"
    
  - name: "Dirty South"
    prompt: "Dirty south hip hop, 145 bpm, trap drums, orchestral hits, dark brass, 808"
```

Tips for good prompts:
- Include BPM (helps you lock in)
- Specify instruments you want
- Mention the vibe/era
- Keep bass references minimal (Demucs removes it anyway)

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features:
- v1: Pre-generated pool (current)
- v2: Live generation via redemption
- v3: Viewer-submitted prompts with moderation

## Related Projects

- [arcade-tts](https://github.com/elchalupa/arcade-tts) — Channel point TTS with voice cloning
- [arcade-heartbeat](https://github.com/elchalupa/arcade-heartbeat) — Stream engagement copilot
- [arcade-newsletter](https://github.com/elchalupa/arcade-newsletter) — Automated monthly newsletter

## License

MIT License — See [LICENSE](LICENSE) for details.
