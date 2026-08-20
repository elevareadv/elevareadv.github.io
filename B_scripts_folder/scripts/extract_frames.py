#!/usr/bin/env python3
"""
Extracts the real mascot animation into the scroll-scrubbed frame sequence
used by the cinematic hero section.

Reads any input video (tested against the 5s 1920x1080 mascot-on-stairs clip)
and writes:

    frames/frame_0001.webp ... frame_NNNN.webp   (desktop set)
    frames/manifest.json                          (frame count + dims, read by the page's JS)

    frames/mobile/frame_0001.webp ... frame_NNNN.webp   (optional, smaller/lighter set)
    frames/mobile/manifest.json

The front-end never hard-codes a frame count — it always reads manifest.json,
so whatever count ffmpeg produces here (governed by --fps) is what plays.

Usage:
    python3 scripts/extract_frames.py path/to/mascot.mp4

    # tune output:
    python3 scripts/extract_frames.py mascot.mp4 --fps 24 --width 1600 --quality 82
    python3 scripts/extract_frames.py mascot.mp4 --skip-mobile
    python3 scripts/extract_frames.py mascot.mp4 --mobile-width 900 --mobile-quality 72

Requires ffmpeg on PATH (already the case in most dev environments; on
Windows install via https://ffmpeg.org/download.html or `winget install ffmpeg`).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(__file__), "..")
FRAMES_DIR = os.path.join(ROOT, "frames")


def run_ffmpeg(input_path, out_dir, fps, width, quality, digits=4):
    os.makedirs(out_dir, exist_ok=True)
    pattern = os.path.join(out_dir, f"frame_%0{digits}d.webp")
    vf = f"fps={fps},scale={width}:-2:flags=lanczos"
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", vf,
        "-vsync", "0",
        "-c:v", "libwebp",
        "-lossless", "0",
        "-q:v", str(quality),
        "-compression_level", "6",
        pattern,
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def probe_dims(sample_frame_path):
    from PIL import Image
    with Image.open(sample_frame_path) as im:
        return im.size


def write_manifest(out_dir, count, width, height, digits, source_note):
    manifest = {
        "count": count,
        "prefix": "frame_",
        "digits": digits,
        "ext": "webp",
        "width": width,
        "height": height,
        "aspect": round(width / height, 6),
        "source": source_note,
    }
    with open(os.path.join(out_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    return manifest


def clear_old_frames(out_dir):
    if not os.path.isdir(out_dir):
        return
    for name in os.listdir(out_dir):
        if name.startswith("frame_") and name.endswith(".webp"):
            os.remove(os.path.join(out_dir, name))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", help="Path to the source mascot animation (mp4/mov/webm...)")
    p.add_argument("--fps", type=float, default=24, help="Extraction frame rate (default 24 -> ~120 frames for a 5s clip)")
    p.add_argument("--width", type=int, default=1600, help="Desktop frame width in px, height auto (default 1600)")
    p.add_argument("--quality", type=int, default=82, help="WebP quality 0-100 for desktop frames (default 82)")
    p.add_argument("--skip-mobile", action="store_true", help="Skip generating the lighter mobile frame set")
    p.add_argument("--mobile-fps", type=float, default=None, help="Mobile extraction fps (default: same as --fps)")
    p.add_argument("--mobile-width", type=int, default=900, help="Mobile frame width in px (default 900)")
    p.add_argument("--mobile-quality", type=int, default=72, help="WebP quality for mobile frames (default 72)")
    args = p.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found on PATH. Install it first: https://ffmpeg.org/download.html")

    if not os.path.isfile(args.input):
        sys.exit(f"Input file not found: {args.input}")

    # Desktop set
    clear_old_frames(FRAMES_DIR)
    run_ffmpeg(args.input, FRAMES_DIR, args.fps, args.width, args.quality)
    desktop_frames = sorted(f for f in os.listdir(FRAMES_DIR) if f.startswith("frame_") and f.endswith(".webp"))
    if not desktop_frames:
        sys.exit("ffmpeg produced no frames — check the input file and ffmpeg output above.")
    w, h = probe_dims(os.path.join(FRAMES_DIR, desktop_frames[0]))
    write_manifest(FRAMES_DIR, len(desktop_frames), w, h, 4, "extracted")
    print(f"Desktop: {len(desktop_frames)} frames at {w}x{h} -> {FRAMES_DIR}")

    # Mobile set (optional, lighter)
    if not args.skip_mobile:
        mobile_dir = os.path.join(FRAMES_DIR, "mobile")
        clear_old_frames(mobile_dir)
        run_ffmpeg(args.input, mobile_dir, args.mobile_fps or args.fps, args.mobile_width, args.mobile_quality)
        mobile_frames = sorted(f for f in os.listdir(mobile_dir) if f.startswith("frame_") and f.endswith(".webp"))
        if mobile_frames:
            mw, mh = probe_dims(os.path.join(mobile_dir, mobile_frames[0]))
            write_manifest(mobile_dir, len(mobile_frames), mw, mh, 4, "extracted")
            print(f"Mobile:  {len(mobile_frames)} frames at {mw}x{mh} -> {mobile_dir}")

    print("\nDone. Delete frames/*.webp placeholders manually if any remain unrelated to this run.")
    print("The page reads frames/manifest.json (and frames/mobile/manifest.json if present) at load time — no code changes needed.")


if __name__ == "__main__":
    main()
