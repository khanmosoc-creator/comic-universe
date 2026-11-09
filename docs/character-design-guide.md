# Character design guide

House style: chunky cartoon, big heads (about one third of body height), thick ink outline `#1b1035`
(5–8 px at 1×), flat colour with a single darker shade on the right side, halftone-dot and ray-burst
backgrounds. Every character must read clearly at 170 px wide (card size). Kid-friendly: no blood, no real
weapons (foam swords, light arrows, bubbles), conflicts end in bonks, boings and splashes.

Source of truth for shapes: `tools/art/generate_art.py`. Change the function, regenerate, review.

## The Maze Guardians

| Character | Palette | Silhouette keys | Power read | Function |
| --- | --- | --- | --- | --- |
| **Super Zayd** (leader) | Teal `#0fb5a6`, gold `#facc15`, navy cape/mask `#1e3a8a` | Curly dark hair, navy domino mask, cape with gold maze lines, gold Z-maze emblem | Eyes glow gold for Maze-Sight; golden dotted paths | `zayd()` |
| **Dragoncrest** | Armour grey `#94a3b8`/`#64748b`, dragon green `#22c55e`, flame red `#ef4444` | Big boxy armour, visor with green eyes, **three green dragon heads** on the helmet, red flame tufts (from the owner sketch) | Segmented Stretch-Punch arm | `dragoncrest(punch=…)` |
| **Arrowlight** | Blue `#2563eb`, cyan `#67e8f9` | Blue hood, cyan bow, quiver of light arrows, arrow emblem | Glowing yellow arrows, light-bridges | `arrowlight()` |
| **Bubbleguard** | Aqua `#06b6d4`, pink `#f472b6` | Two hair puffs with bubble clips, pink mask, bubble emblem | Translucent cyan dome with highlight | `bubbleguard(dome=…)` |
| **Zigzag** | Purple `#9333ea`, yellow `#fde047`, orange boots `#f97316` | Swept spiky hair, teal goggles, lightning emblem, running pose | Six-colour rainbow trail | `zigzag(trail=…)` |

## Villains

| Character | Palette | Silhouette keys | Function |
| --- | --- | --- | --- |
| **Grumblejaw** — junkyard Robo-Beast | Greys `#9ca3af`/`#6b7280`, red eyes, gold bolt badge | Box head, huge underbite jaw with square teeth, smokestack ears puffing smoke, tank-tread feet (from the owner's "roar/crash" sketch) | `robo_beast()` |
| **Blizzardbyte** — Glitch Yeti | Snow white `#f1f5f9`, ice blue `#bae6fd`/`#7dd3fc` | Huge rounded body, zigzag fur hem, ice crown, coloured glitch pixels in the fur | `yeti(mood=…)` |
| **Splashfang** — Wave Serpent | Blue `#2563eb`, cyan fins `#22d3ee` | S-curve body with dashed belly stripe, fin crest, big eye, one goofy fang | `serpent()` |
| **Glitchlings** — minions | Lime `#84cc16` (variants allowed) | Square pixel body, square eyes, pink foam pool-noodle sword | `glitchling()` |

## Rules

1. Keep every hero's emblem readable — don't mirror Super Zayd (the Z flips); pose his arms instead.
2. Villains are funny before they are scary: big eyes, visible weakness, no sharp teeth aimed at heroes.
3. Text inside art is outlined Poppins (via `words()`), so nothing depends on fonts at runtime. Dialogue
   lives in `issue-001.json`, not in images, so it is readable by screen readers and translatable.
4. Colour contrast for anything text-like in art: ink on light, white/yellow on dark.
5. Do not imitate any existing comic character, costume, logo or distinctive setting. If a new design
   starts to resemble one, change the silhouette, palette and emblem until it doesn't.
