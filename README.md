# elevareadv.github.io

Elevare Advertising — work site. Plain static HTML/CSS/JS, no build step.

## Structure

```
index.html          Homepage — hero, work rows, two case sections, services, reels, studio, footer
assets/             Elevare logo (white for dark bg, ink for the orange footer)
work/index.html     Full work archive — case cards + motion reels
work/boujie.html    Boujie case study
work/elegant-candles.html   Elegant Candles case study
work/media/         All images and reels
```

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
