# arcade-jam Roadmap

## v1.0 — Pre-Generated Pool (Current)

The foundation: batch generate tracks before stream, play randomly during stream.

### Phase 1: Generator Setup
- [x] RunPod deployment instructions
- [x] producer.py script (MusicGen + Demucs)
- [x] prompts.yaml configuration
- [ ] Test generation on RunPod
- [ ] Verify stem quality

### Phase 2: Streamer.bot Integration
- [ ] Channel point redemption trigger
- [ ] Random file selection from pool
- [ ] Audio playback via OBS
- [ ] On-screen vibe display
- [ ] Move played tracks to archive

### Phase 3: Polish
- [ ] Pool management (track remaining count)
- [ ] Low pool warning notification
- [ ] Cooldown between redemptions
- [ ] Documentation and examples

---

## v2.0 — Live Generation (Future)

Real-time track generation from viewer prompts.

### Requirements
- Dedicated RunPod pod during music streams
- WebSocket or HTTP API for trigger
- Queue management system
- 2-3 minute generation time per track

### Features
- [ ] RunPod serverless endpoint
- [ ] Streamer.bot → API trigger
- [ ] Generation queue with status display
- [ ] "Now generating..." overlay
- [ ] Auto-download and queue for playback

### Challenges
- Generation latency (2-3 min)
- Pod cost during stream (~$0.50/hr)
- Queue management complexity

---

## v3.0 — Viewer Prompts (Future)

Viewers submit their own text prompts.

### Features
- [ ] Text input with redemption
- [ ] Prompt moderation/filtering
- [ ] Banned words list
- [ ] Prompt length limits
- [ ] Display submitted prompt on screen

### Challenges
- Inappropriate prompt submissions
- Prompt quality varies wildly
- May need manual approval queue

---

## v4.0 — Advanced Features (Ideas)

### Stem Control
- Let viewers vote on which stems to include
- "Drums only" vs "Full band" modes
- Real-time stem mixing

### BPM Detection
- Auto-detect BPM from generated track
- Display BPM prominently for streamer
- Metronome overlay option

### Recording Integration
- Auto-record streamer's performance
- Save jam session as clip
- Upload highlights automatically

### Leaderboard
- Track which viewers triggered best jams
- Community voting on performances
- Monthly "best jam" compilation

---

## Technical Debt / Improvements

- [ ] Create RunPod template for faster deployment
- [ ] Optimize Demucs settings for speed vs quality
- [ ] Add progress indicators during generation
- [ ] Support multiple audio formats (not just WAV)
- [ ] Add track metadata (BPM, key, duration)
