# RunPod Quick Start

Step-by-step guide to generating your first batch of backing tracks.

## 1. Create a RunPod Account

1. Go to https://runpod.io
2. Sign up / Log in
3. Add credits ($10 is plenty to start)

## 2. Deploy a GPU Pod

1. Click **Deploy** → **GPU Pods**
2. Select a GPU:
   - **Recommended:** NVIDIA A40 (48GB) — ~$0.50/hr
   - **Alternative:** RTX A6000 (48GB) — ~$0.70/hr
   - **Budget:** RTX 3090 (24GB) — ~$0.30/hr (may need smaller batch size)
3. Select template: **RunPod PyTorch 2.1** (or newer)
4. Set disk:
   - Container Disk: 50GB
   - Volume Disk: 20GB (optional, for persistence)
5. Click **Deploy**

Wait ~2 minutes for the pod to start.

## 3. Connect to the Pod

### Option A: Web Terminal
1. Click **Connect** on your pod
2. Select **Terminal**

### Option B: SSH (Recommended)
1. Add your SSH key in RunPod settings
2. Click **Connect** → copy the SSH command
3. Run in your terminal:
   ```bash
   ssh root@[IP] -p [PORT] -i ~/.ssh/your_key
   ```

## 4. Set Up the Environment

Run these commands in the pod:

```bash
# Install system dependencies
apt-get update && apt-get install -y ffmpeg libsndfile1

# Install Python packages
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install git+https://github.com/facebookresearch/audiocraft.git
pip install demucs scipy pyyaml

# Create workspace
mkdir -p /workspace/arcade-jam
cd /workspace/arcade-jam
```

## 5. Upload Your Files

### Option A: Copy/Paste
Create the files directly in the pod using `nano` or `vim`:

```bash
nano producer.py
# Paste the contents of generator/producer.py
# Ctrl+X, Y, Enter to save

nano prompts.yaml
# Paste the contents of generator/prompts.yaml
# Ctrl+X, Y, Enter to save
```

### Option B: SCP Upload
From your local machine:

```bash
scp -P [PORT] generator/producer.py generator/prompts.yaml root@[IP]:/workspace/arcade-jam/
```

### Option C: JupyterLab
1. Click **Connect** → **Jupyter Lab**
2. Navigate to `/workspace/arcade-jam`
3. Upload files via the UI

## 6. Generate Tracks

```bash
cd /workspace/arcade-jam

# Generate with defaults (60s tracks, 4 takes per prompt)
python producer.py

# Or customize:
python producer.py --duration 45 --takes 2
```

**Expected time:**
- 16 prompts × 4 takes = 64 tracks
- ~30-45 minutes on A40
- Cost: ~$0.50

## 7. Download Your Tracks

### Option A: SCP (Recommended)
From your local machine:

```bash
# Download all sessions
scp -P [PORT] -r root@[IP]:/workspace/sessions ./arcade-jam-sessions

# Or just the READY_FOR_BASS files
scp -P [PORT] root@[IP]:/workspace/sessions/*/READY_FOR_BASS.wav ./jams/ready/
```

### Option B: Zip and Download
In the pod:

```bash
cd /workspace
zip -r sessions.zip sessions/
```

Then use JupyterLab to download `sessions.zip`.

## 8. Organize for Stream

Move the downloaded tracks to your stream folder:

```
C:\stream\jams\ready\
├── Neo_Soul_Groove_Take_1\
│   ├── READY_FOR_BASS.wav
│   └── metadata.yaml
├── Neo_Soul_Groove_Take_2\
│   └── ...
└── ...
```

## 9. Stop the Pod

**Important:** Stop your pod when done to avoid charges!

1. Go to RunPod dashboard
2. Click **Stop** on your pod
3. Or terminate completely if you don't need it

## Cost Summary

| Action | Time | Cost |
|--------|------|------|
| Setup | 10 min | ~$0.08 |
| Generation (64 tracks) | 30 min | ~$0.25 |
| **Total** | 40 min | **~$0.33** |

## Tips

- **Save a Template:** After setup, save your pod as a template for faster future deployments
- **Use Volume Disk:** If you want tracks to persist across pod restarts
- **Batch Smartly:** Generate enough for 2-3 streams at once
- **Test First:** Run with `--takes 1` to verify setup before full batch
