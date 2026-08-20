# elevareadv.github.io

Elevare Advertising — work site. Plain static HTML/CSS/JS, no build step.

## Structure

```
index.html          Homepage — cinematic scroll hero, work rows, two case sections, services, reels, studio, footer
assets/             Elevare logo (white for dark bg, ink for the orange footer)
frames/             Scroll-scrubbed mascot sequence (desktop) + manifest.json
frames/mobile/      Same sequence, smaller/lighter (mobile) + manifest.json
scripts/extract_frames.py              Turns the source mascot mp4 into frames/ + frames/mobile/
scripts/generate_placeholder_frames.py Generates placeholder frames when no real footage exists yet
work/index.html     Full work archive — case cards + motion reels
work/boujie.html    Boujie case study
work/elegant-candles.html   Elegant Candles case study
work/media/         All images and reels
```

## The cinematic scroll hero (`#top`)

The old static hero was replaced with a scroll-scrubbed image-sequence section: a pinned
canvas plays the mascot's walk down the staircase, one frame per unit of scroll progress,
with three headline states crossfading over it (`WE MAKE BRANDS MOVE.` → `IDEAS BUILT TO
MOVE.` → `MAKE YOUR BRAND IMPOSSIBLE TO IGNORE.` + the "Explore our work" CTA). It's a
500vh section (420vh on phones) with `position:sticky` pinning the viewport while scroll
position drives everything else — no autoplay, no video element.

**Updating the footage.** Drop the new source clip anywhere and run:

```
python3 scripts/extract_frames.py path/to/clip.mp4
```

This calls ffmpeg, writes `frames/frame_0001.webp … frame_NNNN.webp` + `frames/manifest.json`
(desktop) and the same into `frames/mobile/` at a smaller size, and never hard-codes 120 —
the page reads the frame count from `manifest.json` at load, so any length clip works.
Useful flags: `--fps`, `--width`, `--quality`, `--mobile-width`, `--mobile-quality`,
`--skip-mobile`. Requires ffmpeg on PATH.

No footage yet? `python3 scripts/generate_placeholder_frames.py` draws a simple stand-in
sequence (charcoal bg, orange-stroked staircase, a walking silhouette) so the scroll
mechanics can be built/tested before the real animation exists.

**How the frame lands on screen.** Canvas draws with `devicePixelRatio` (capped at 2) for
sharpness. On wide/landscape screens it shows the full 16:9 frame, letterboxed to the
container's own aspect if that isn't exactly 16:9. On narrow/tall screens (phones) it crops
the staircase's outer edges to fill the height, but never crops past 60% of the source
width — the mascot (head, hair, body, shoes, headphones) always stays fully in frame; if a
phone is tall enough that the 60% floor can't fill the screen, it letterboxes instead of
cropping further. Both crop and letterbox blend into the page because the canvas is cleared
against the site's own `--ink` background.

**Loading.** Frame 1 (plus the last frame) loads first and eagerly; the loading screen
(`ELEVARE` + a thin orange bar) disappears the instant frame 1 is decoded, and the rest of
the sequence trickles in afterward via `requestIdleCallback` in small batches — the page
never blocks on the full sequence.

**Reduced motion.** `prefers-reduced-motion: reduce` skips the whole rig: the section
collapses to a normal `100vh` block, the canvas is hidden, the final frame renders as a
plain `<img>`, and the three headlines stack in normal document flow (opening + final + CTA;
the brief mid-scroll line is dropped since there's no scroll to hang it on) — everything
stays readable and keyboard/screen-reader accessible, nothing lives only inside the canvas.

## Adding a project

**Homepage** — copy the `<a class="workrow" ...>` block, bump the number, swap the name /
category / `data-peek` image. Then copy a `<section class="case-sec">` block, alternate
between the cream version (no inline background) and the ink version
(`style="background:#121110;color:#F2EFE8"`) so the sections keep the light/dark rhythm.

**Work archive** — copy an `<a class="case">` block in `work/index.html`.

**Case study page** — copy `work/boujie.html`, swap images, facts and palette hexes.

Images: ~1400px wide, JPEG q85. Every concept project keeps its `Concept` tag.

## Interactions

All vanilla JS, no dependencies. Everything respects `prefers-reduced-motion`.

- Scroll-scrubbed cinematic hero (`#top`) — canvas frame + headline timeline tied to scroll progress, see above
- Scroll reveal on `[data-rv]` (staggered by sibling index)
- Scroll progress bar + nav background on scroll
- Parallax on the ghosted ELEVARE background fields
- Magnetic buttons on `[data-ev="magnet"]`
- Cursor-following image preview on the work rows (`data-peek` sets the image)
- Drag-to-compare before/after on the Elegant Candles photography
- Reels autoplay when scrolled into view, click to pause
- Boujie page: palette swatches lift and brighten their hex, mark parallax (desktop only)

## Hosting

GitHub Pages from `main` / root. Netlify and Cloudflare Pages are unreachable from Egypt —
`*.github.io` is the only host that works. The repo name must match the username exactly.
