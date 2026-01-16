"""
arcade-jam Producer

Batch generates AI backing tracks using MusicGen + Demucs.
Run this on RunPod (A40/A6000 recommended) before your stream.

Output: "READY_FOR_BASS.wav" files — full backing tracks with bass removed.

Usage:
    python producer.py
    python producer.py --prompts custom_prompts.yaml
    python producer.py --duration 45 --takes 2
"""

import os
import gc
import argparse
from pathlib import Path
from datetime import datetime

import torch
import torchaudio
import yaml
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import subprocess


# --- CONFIGURATION ---
DEFAULT_DURATION = 60      # Seconds per track
DEFAULT_TAKES = 4          # Variations per prompt
OUTPUT_DIR = "/workspace/sessions"


def cleanup_gpu():
    """Free up GPU memory between generations."""
    gc.collect()
    torch.cuda.empty_cache()


def load_prompts(prompts_file: Path) -> list[dict]:
    """
    Load prompts from YAML file.
    
    Expected format:
        prompts:
          - name: "Neo Soul"
            prompt: "Neo-soul loop, 85 bpm, fender rhodes..."
    """
    with open(prompts_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    return data.get("prompts", [])


def separate_stems(input_path: str, output_dir: str) -> bool:
    """
    Separate audio into stems using Demucs.
    
    Uses 'htdemucs' (Hybrid Transformer) for high quality GPU-accelerated separation.
    Creates: drums.wav, bass.wav, other.wav, vocals.wav
    """
    print(f"   >>> Separating stems for {os.path.basename(input_path)}...")
    
    cmd = [
        "demucs",
        "-n", "htdemucs",
        "-d", "cuda",
        "-o", output_dir,
        "--filename", "{track}/{stem}.{ext}",
        input_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"   [!] Demucs error: {result.stderr}")
        return False
    
    return True


def create_backing_track(stem_dir: str, output_path: str) -> bool:
    """
    Combine Drums + Other (keys/synth) into a bassless backing track.
    
    This creates the "READY_FOR_BASS.wav" that the streamer jams over.
    """
    try:
        drums_path = os.path.join(stem_dir, "drums.wav")
        other_path = os.path.join(stem_dir, "other.wav")
        
        if not os.path.exists(drums_path):
            print(f"   [!] Missing drums.wav in {stem_dir}")
            return False
        
        if not os.path.exists(other_path):
            print(f"   [!] Missing other.wav in {stem_dir}")
            return False
        
        # Load stems
        drums_wav, sr = torchaudio.load(drums_path)
        other_wav, _ = torchaudio.load(other_path)
        
        # Mix together (simple sum, assuming same length/sr)
        min_len = min(drums_wav.shape[1], other_wav.shape[1])
        backing = drums_wav[:, :min_len] + other_wav[:, :min_len]
        
        # Normalize to prevent clipping
        max_val = backing.abs().max()
        if max_val > 0.95:
            backing = backing * (0.95 / max_val)
        
        # Save the backing track
        torchaudio.save(output_path, backing, sr)
        print(f"   >>> Created: {os.path.basename(output_path)}")
        return True
        
    except Exception as e:
        print(f"   [!] Error creating backing track: {e}")
        return False


def create_metadata(output_dir: str, prompt_data: dict, take_num: int):
    """
    Save metadata about the generated track for display during stream.
    """
    metadata = {
        "name": prompt_data.get("name", "Unknown"),
        "prompt": prompt_data.get("prompt", ""),
        "take": take_num,
        "generated": datetime.now().isoformat(),
    }
    
    metadata_path = os.path.join(output_dir, "metadata.yaml")
    with open(metadata_path, "w", encoding="utf-8") as f:
        yaml.dump(metadata, f, default_flow_style=False)


def run_session(
    prompts_file: Path,
    duration: int = DEFAULT_DURATION,
    takes: int = DEFAULT_TAKES,
    output_dir: str = OUTPUT_DIR
):
    """
    Main generation session.
    
    For each prompt, generates multiple takes, separates stems,
    and creates bassless backing tracks.
    """
    # Load prompts
    prompts = load_prompts(prompts_file)
    if not prompts:
        print("[!] No prompts found in file. Exiting.")
        return
    
    print(f">>> Loaded {len(prompts)} prompts")
    print(f">>> Duration: {duration}s per track")
    print(f">>> Takes: {takes} per prompt")
    print(f">>> Total tracks to generate: {len(prompts) * takes}")
    print()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize MusicGen
    print(">>> Loading MusicGen Large model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = MusicGen.get_pretrained('facebook/musicgen-large', device=device)
    model.set_generation_params(duration=duration)
    print(f">>> Model loaded on {device}")
    print()
    
    # Process each prompt
    for i, prompt_data in enumerate(prompts):
        prompt_name = prompt_data.get("name", f"Prompt_{i+1}")
        prompt_text = prompt_data.get("prompt", "")
        
        print(f"\n{'='*60}")
        print(f"SESSION {i+1}/{len(prompts)}: {prompt_name}")
        print(f"{'='*60}")
        print(f"Prompt: {prompt_text[:80]}...")
        print()
        
        # Generate multiple takes at once (batch)
        print(f">>> Generating {takes} takes...")
        wavs = model.generate([prompt_text] * takes)
        
        # Process each take
        for take_idx, one_wav in enumerate(wavs):
            take_num = take_idx + 1
            take_name = f"{prompt_name.replace(' ', '_')}_Take_{take_num}"
            take_dir = os.path.join(output_dir, take_name)
            os.makedirs(take_dir, exist_ok=True)
            
            print(f"\n   --- Take {take_num}/{takes} ---")
            
            # 1. Save full mix (for reference)
            full_mix_path = os.path.join(take_dir, "full_mix")
            audio_write(full_mix_path, one_wav.cpu(), model.sample_rate, strategy="loudness")
            print(f"   >>> Saved full mix")
            
            # 2. Separate stems
            full_mix_wav = full_mix_path + ".wav"
            if not separate_stems(full_mix_wav, take_dir):
                print(f"   [!] Stem separation failed for {take_name}")
                continue
            
            # 3. Create bassless backing track
            # Demucs output structure: take_dir/htdemucs/full_mix/stems
            stem_location = os.path.join(take_dir, "htdemucs", "full_mix")
            backing_path = os.path.join(take_dir, "READY_FOR_BASS.wav")
            create_backing_track(stem_location, backing_path)
            
            # 4. Save metadata
            create_metadata(take_dir, prompt_data, take_num)
        
        # Clean up GPU memory between prompts
        cleanup_gpu()
    
    print()
    print("="*60)
    print(">>> ALL SESSIONS COMPLETE")
    print(f">>> Output: {output_dir}")
    print(">>> Ready for download!")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI backing tracks for arcade-jam"
    )
    parser.add_argument(
        "--prompts", "-p",
        type=Path,
        default=Path("prompts.yaml"),
        help="Path to prompts YAML file (default: prompts.yaml)"
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=DEFAULT_DURATION,
        help=f"Duration in seconds per track (default: {DEFAULT_DURATION})"
    )
    parser.add_argument(
        "--takes", "-t",
        type=int,
        default=DEFAULT_TAKES,
        help=f"Number of takes per prompt (default: {DEFAULT_TAKES})"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=OUTPUT_DIR,
        help=f"Output directory (default: {OUTPUT_DIR})"
    )
    
    args = parser.parse_args()
    
    if not args.prompts.exists():
        print(f"[!] Prompts file not found: {args.prompts}")
        print("    Create a prompts.yaml file or specify with --prompts")
        return
    
    run_session(
        prompts_file=args.prompts,
        duration=args.duration,
        takes=args.takes,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()
