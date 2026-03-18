# Peptigotchi Sprite Assets

## Spec

- Format: PNG, 48×48 pixels, transparent background
- Style: Pixel art (Aseprite recommended)
- Each emotion needs 4 animation frames (for idle bob animation)

## Directory Structure

```
{species}/{stage}/{emotion}_{frame}.png
```

Example: `axolotl/juvenile/worried_01.png`

## Species

| Species | Protocol | Visual Theme |
|---------|----------|-------------|
| axolotl | Healing (BPC/TB-500) | Aquatic, gills, regeneration glow |
| phoenix | Weight loss (GLP-1s) | Fire, wings, transformation |
| bear | GH/Recovery (CJC/IPA) | Forest, strength, calm |
| octopus | Nootropic (Semax/Selank) | Deep sea, neural, bioluminescent |

## Emotions (7 per stage)

| Emotion | Visual Cue |
|---------|-----------|
| happy | Bright colors, open eyes |
| neutral | Default colors, calm expression |
| curious | Head tilted, one eye larger |
| worried | Muted colors, looking sideways |
| alarmed | Red tinge, squinting |
| proud | Glowing, puffed up |
| sleepy | Eyes half-closed, slow breathing |

## Evolution Stages (5)

| Stage | Day | Visual |
|-------|-----|--------|
| egg | 0 | Small, mostly round, eyes peeking |
| hatchling | 3 | Small, species features emerging |
| juvenile | 14 | Medium, recognizable species |
| adult | 45 | Full size, ~3 variants per species |
| elder | 90 | Full size + aura/special effects |

## Adult/Elder Variants

At adult and elder stages, ~3 visual variants per species based on user journey:
- **Clean run** — pristine, bright, unblemished
- **Weathered** — dealt with side effects, adapted — scarred but glowing
- **Complex** — ran multi-compound stacks — chimera elements from other species

## Frame Count

- 4 species × 5 stages × 7 emotions × 4 frames = 560 base frames
- ~3 adult/elder variants × 2 stages × 7 emotions × 4 frames = +168 frames
- Total: ~728 frames

## Chat Images

For WhatsApp/Telegram, also export a single representative frame per
species/stage/emotion at 256×256 (nearest-neighbor upscale) for sending
in chat messages. These go in a `chat/` subdirectory:

```
{species}/{stage}/chat/{emotion}.png
```

## Notchi Sprite Sheets

For the macOS notch app, combine frames into sprite sheets per
species/stage/emotion:

```
{species}/{stage}/sheet_{emotion}.png
```

4 frames in a horizontal strip (192×48 for 48px sprites).
