#!/usr/bin/env python3
"""
Generates a PLACEHOLDER frame sequence for the cinematic scroll section, so the
scroll-scrubbing mechanics can be built and tested before the real mascot
animation is supplied.

Produces /frames/frame_0001.webp ... frame_00NN.webp (16:9, charcoal bg, a
simple orange-stroked staircase and a walking silhouette that grows and moves
toward camera) plus /frames/manifest.json describing the sequence.

Deliberately uses a frame count that is NOT 120, to prove the front-end reads
the count from manifest.json rather than assuming a fixed number.

Run:
    python3 scripts/generate_placeholder_frames.py

Replace these with the real extracted frames via extract_frames.py once the
mascot animation is supplied — same manifest-driven pipeline, no JS changes
needed.
"""
import json
import math
import os

from PIL import Image, ImageDraw

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "frames")
WIDTH, HEIGHT = 960, 540
FRAME_COUNT = 56  # intentionally not 120
INK = (18, 17, 16)
INK_2 = (27, 25, 24)
ORANGE = (233, 91, 62)
CREAM = (242, 239, 232)
MUTED = (60, 56, 53)


def lerp(a, b, t):
    return a + (b - a) * t


def ease_in_out(t):
    return t * t * (3 - 2 * t)


def draw_background(draw):
    for y in range(HEIGHT):
        t = y / HEIGHT
        c = tuple(int(lerp(INK_2[i], INK[i], t)) for i in range(3))
        draw.line([(0, y), (WIDTH, y)], fill=c)


def draw_staircase(draw, progress):
    """A simple receding staircase made of orange-stroked steps, drifting
    upward/back as progress increases (camera 'descending')."""
    steps = 9
    vanish_x = WIDTH * 0.62
    vanish_y = HEIGHT * 0.18
    base_y = HEIGHT * 1.05
    drift = progress * HEIGHT * 0.5
    for i in range(steps):
        t0 = i / steps
        t1 = (i + 1) / steps
        y0 = lerp(base_y, vanish_y, t0) - drift
        y1 = lerp(base_y, vanish_y, t1) - drift
        w0 = lerp(WIDTH * 1.15, 40, t0)
        w1 = lerp(WIDTH * 1.15, 40, t1)
        x0a, x0b = vanish_x - w0 / 2, vanish_x + w0 / 2
        x1a, x1b = vanish_x - w1 / 2, vanish_x + w1 / 2
        if y1 < -60 or y0 > HEIGHT + 60:
            continue
        shade = int(lerp(34, 22, t0))
        draw.polygon(
            [(x0a, y0), (x0b, y0), (x1b, y1), (x1a, y1)],
            fill=(shade, shade - 2, shade - 3),
        )
        draw.line([(x0a, y0), (x1a, y1)], fill=ORANGE, width=2)
        draw.line([(x0b, y0), (x1b, y1)], fill=ORANGE, width=2)
        draw.line([(x0a, y0), (x0b, y0)], fill=ORANGE, width=1)


def draw_mascot(draw, progress):
    """Simple walking silhouette: grows and centers as progress -> 1."""
    cx = lerp(WIDTH * 0.5, WIDTH * 0.5, progress)
    cy = lerp(HEIGHT * 0.42, HEIGHT * 0.62, ease_in_out(progress))
    scale = lerp(0.34, 1.15, ease_in_out(progress))

    walk = math.sin(progress * math.pi * 10) * scale
    bob = abs(math.sin(progress * math.pi * 10)) * 6 * scale

    body_h = 92 * scale
    body_w = 40 * scale
    head_r = 20 * scale
    leg_len = 58 * scale

    hip_y = cy + body_h / 2 - bob
    head_y = cy - body_h / 2 - head_r - bob

    # legs
    for side, off in ((-1, walk), (1, -walk)):
        hip_x = cx + side * body_w * 0.18
        foot_x = hip_x + off * 0.9
        foot_y = hip_y + leg_len
        draw.line([(hip_x, hip_y), (foot_x, foot_y)], fill=CREAM, width=int(max(3, 7 * scale)))
        # shoe (orange accent)
        draw.ellipse(
            [foot_x - 7 * scale, foot_y - 4 * scale, foot_x + 9 * scale, foot_y + 6 * scale],
            fill=ORANGE,
        )

    # body (torso)
    draw.rounded_rectangle(
        [cx - body_w / 2, cy - body_h / 2 - bob, cx + body_w / 2, hip_y],
        radius=body_w * 0.4,
        fill=CREAM,
    )

    # arms
    for side, off in ((-1, -walk), (1, walk)):
        sh_x = cx + side * body_w * 0.45
        sh_y = cy - body_h * 0.28 - bob
        hand_x = sh_x + off * 0.6
        hand_y = sh_y + 44 * scale
        draw.line([(sh_x, sh_y), (hand_x, hand_y)], fill=CREAM, width=int(max(2, 5 * scale)))

    # head
    draw.ellipse(
        [cx - head_r, head_y - head_r, cx + head_r, head_y + head_r],
        fill=CREAM,
    )
    # hair (small orange wedge, keeps "orange accent" thread through frames)
    draw.pieslice(
        [cx - head_r, head_y - head_r, cx + head_r, head_y + head_r],
        200, 340, fill=ORANGE,
    )
    # headphones
    draw.arc(
        [cx - head_r * 1.15, head_y - head_r * 1.1, cx + head_r * 1.15, head_y + head_r * 0.5],
        180, 360, fill=INK, width=int(max(2, 4 * scale)),
    )
    draw.ellipse(
        [cx - head_r * 1.2, head_y - head_r * 0.15, cx - head_r * 0.85, head_y + head_r * 0.5],
        fill=INK,
    )
    draw.ellipse(
        [cx + head_r * 0.85, head_y - head_r * 0.15, cx + head_r * 1.2, head_y + head_r * 0.5],
        fill=INK,
    )


def build_frame(i, n):
    progress = i / (n - 1) if n > 1 else 0
    img = Image.new("RGB", (WIDTH, HEIGHT), INK)
    draw = ImageDraw.Draw(img)
    draw_background(draw)
    draw_staircase(draw, progress)
    draw_mascot(draw, progress)
    return img


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for i in range(FRAME_COUNT):
        img = build_frame(i, FRAME_COUNT)
        path = os.path.join(OUT_DIR, f"frame_{i + 1:04d}.webp")
        img.save(path, "WEBP", quality=80, method=4)

    manifest = {
        "count": FRAME_COUNT,
        "prefix": "frame_",
        "digits": 4,
        "ext": "webp",
        "width": WIDTH,
        "height": HEIGHT,
        "aspect": round(WIDTH / HEIGHT, 6),
        "source": "placeholder",
        "note": "Generated by scripts/generate_placeholder_frames.py. Replace via scripts/extract_frames.py once the real mascot animation is supplied.",
    }
    with open(os.path.join(OUT_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Wrote {FRAME_COUNT} placeholder frames + manifest.json to {os.path.abspath(OUT_DIR)}")


if __name__ == "__main__":
    main()
