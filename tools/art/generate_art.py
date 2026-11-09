#!/usr/bin/env python3
"""Offline art generator for Super Zayd's Maze Guardians.

Every new illustration on the site (hero + villain portraits, the Issue #1
cover, story panels, the universe map, the logo badge and the social card)
is produced by this script from hand-written vector shapes. Nothing is traced
from or derived from any third-party character, logo or artwork.

Lettering is converted to outlines with the bundled Poppins font (SIL OFL 1.1),
so the SVGs look the same on every device and need no web-font request.

Usage (from repo root):
  python3 tools/art/generate_art.py apps/web/public/art
Requires: Python 3.10+, fontTools. Optional: rsvg-convert (for the PNG social card).
"""
from __future__ import annotations

import math
import random
import subprocess
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
FONT_DIR = ROOT / "tools" / "art" / "fonts"

INK = "#1b1035"
WHITE = "#ffffff"
SKIN = {"a": "#c98c62", "b": "#e2a77d", "c": "#8d5a3b", "d": "#f1c49b", "e": "#a8704b"}

# ----------------------------------------------------------------- lettering


class Lettering:
    def __init__(self, path: Path):
        self.font = TTFont(str(path))
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font["head"].unitsPerEm
        self.hmtx = self.font["hmtx"]

    def width(self, text: str, size: float, tracking: float = 0) -> float:
        s = size / self.upm
        total = 0.0
        for ch in text:
            g = self.cmap.get(ord(ch), self.cmap.get(ord("?")))
            total += self.hmtx[g][0] * s + tracking
        return total - tracking if text else 0

    def path_d(self, text: str, size: float, x: float, y: float, anchor: str = "start", tracking: float = 0) -> str:
        s = size / self.upm
        w = self.width(text, size, tracking)
        cx = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
        parts = []
        for ch in text:
            g = self.cmap.get(ord(ch), self.cmap.get(ord("?")))
            pen = SVGPathPen(self.glyphs)
            self.glyphs[g].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
            parts.append(pen.getCommands())
            cx += self.hmtx[g][0] * s + tracking
        return " ".join(p for p in parts if p)


BOLD = Lettering(FONT_DIR / "Poppins-Bold.ttf")
BOLD_I = Lettering(FONT_DIR / "Poppins-BoldItalic.ttf")


def words(text, size, x, y, fill=WHITE, stroke=INK, sw=10, anchor="middle", font=BOLD_I, tracking=0, extra=""):
    """Comic lettering: thick ink outline behind a solid fill."""
    d = font.path_d(text, size, x, y, anchor, tracking)
    out = ""
    if stroke:
        out += f'<path d="{d}" fill="{stroke}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'
    out += f'<path d="{d}" fill="{fill}" {extra}/>'
    return out


def caption(text, x, y, size=30, fill="#fff7d6", w=None):
    """Narration box: yellow rectangle with ink outline."""
    tw = BOLD.width(text, size)
    w = w or tw + 44
    h = size + 30
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{INK}" stroke-width="6"/>'
        + words(text, size, x + w / 2, y + h / 2 + size * 0.36, fill=INK, stroke=None, font=BOLD)
    )


# ----------------------------------------------------------------- primitives


def svg(w, h, body, title, defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
        f"<title>{title}</title><defs>{halftone_defs()}{defs}</defs>{body}</svg>\n"
    )


def halftone_defs():
    return (
        '<pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse" patternTransform="rotate(20)">'
        '<circle cx="9" cy="9" r="3.4" fill="#ffffff" opacity="0.22"/></pattern>'
        '<pattern id="dotsDark" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(20)">'
        f'<circle cx="8" cy="8" r="2.6" fill="{INK}" opacity="0.18"/></pattern>'
    )


def limb(pts, color, w, ink_extra=10):
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    if len(pts) == 3:
        (x0, y0), (x1, y1), (x2, y2) = pts
        d = f"M {x0:.1f},{y0:.1f} Q {x1:.1f},{y1:.1f} {x2:.1f},{y2:.1f}"
    return (
        f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w + ink_extra}" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def star_points(cx, cy, n, r1, r2, rot=0.0, jitter=0.0, seed=1):
    rnd = random.Random(seed)
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        r *= 1 + rnd.uniform(-jitter, jitter)
        a = rot + math.pi * i / n
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return " ".join(pts)


def burst(cx, cy, r1, r2, fill, n=14, sw=7, seed=3, jitter=0.18):
    return f'<polygon points="{star_points(cx, cy, n, r1, r2, 0.2, jitter, seed)}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>'


def rays(w, h, cx, cy, c1, c2, n=28):
    out = f'<rect width="{w}" height="{h}" fill="{c1}"/>'
    R = math.hypot(w, h)
    for i in range(0, n * 2, 2):
        a0 = 2 * math.pi * i / (n * 2)
        a1 = 2 * math.pi * (i + 1) / (n * 2)
        out += (
            f'<polygon points="{cx},{cy} {cx + R * math.cos(a0):.1f},{cy + R * math.sin(a0):.1f} '
            f'{cx + R * math.cos(a1):.1f},{cy + R * math.sin(a1):.1f}" fill="{c2}"/>'
        )
    return out


def speed_lines(cx, cy, r_in, r_out, n=40, color=INK, seed=5, width=4):
    rnd = random.Random(seed)
    out = ""
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.05, 0.05)
        ri = r_in * rnd.uniform(0.9, 1.3)
        out += (
            f'<line x1="{cx + ri * math.cos(a):.1f}" y1="{cy + ri * math.sin(a):.1f}" '
            f'x2="{cx + r_out * math.cos(a):.1f}" y2="{cy + r_out * math.sin(a):.1f}" '
            f'stroke="{color}" stroke-width="{width * rnd.uniform(0.5, 1.4):.1f}" stroke-linecap="round" opacity="0.55"/>'
        )
    return out


def balloon(x, y, w, h, text_lines, tail, size=30, fill=WHITE, shout=False):
    """Speech balloon with tail pointing to (tx, ty)."""
    tx, ty = tail
    cx, cy = x + w / 2, y + h / 2
    out = ""
    bx = max(x + 30, min(x + w - 30, tx))
    if shout:
        out += f'<polygon points="{star_points(cx, cy, 16, w * 0.62, w * 0.5, 0, 0.08, 9)}" transform="translate({cx},{cy}) scale(1,{h / w:.3f}) translate({-cx},{-cy})" fill="{fill}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
    else:
        out += f'<ellipse cx="{cx}" cy="{cy}" rx="{w / 2}" ry="{h / 2}" fill="{fill}" stroke="{INK}" stroke-width="6"/>'
    by = y + h - 6 if ty > cy else y + 6
    out += f'<path d="M {bx - 18},{by} L {tx},{ty} L {bx + 18},{by}" fill="{fill}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
    out += f'<path d="M {bx - 14},{by - (4 if ty > cy else -4)} L {bx + 14},{by - (4 if ty > cy else -4)}" stroke="{fill}" stroke-width="10"/>'
    lh = size * 1.18
    start = cy - (len(text_lines) - 1) * lh / 2 + size * 0.36
    for i, line in enumerate(text_lines):
        out += words(line, size, cx, start + i * lh, fill=INK, stroke=None, font=BOLD)
    return out


def place(inner, x, y, s=1.0, flip=False):
    sx = -s if flip else s
    return f'<g transform="translate({x:.1f},{y:.1f}) scale({sx},{s})">{inner}</g>'


def shadow(x, y, rx, ry=14, op=0.25):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{INK}" opacity="{op}"/>'


# ----------------------------------------------------------------- humanoid kit

SH_L, SH_R = (-44, -196), (44, -196)
HIP_L, HIP_R = (-20, -112), (20, -112)

ARMS = {
    "down": [(-58, -160), (-62, -122)],
    "hip": [(-88, -160), (-52, -128)],
    "up": [(-76, -240), (-82, -296)],
    "out": [(-92, -200), (-138, -212)],
    "point": [(-98, -214), (-150, -240)],
    "wave": [(-92, -226), (-88, -284)],
    "front": [(-74, -166), (-36, -150)],
    "aim": [(-96, -200), (-150, -200)],
}
LEGS = {
    "stand": [(-26, -58), (-30, -12)],
    "wide": [(-42, -60), (-56, -12)],
    "run_back": [(-36, -60), (-84, -42)],
    "run_front": [(-64, -84), (-58, -26)],
    "jump": [(-44, -80), (-30, -46)],
    "kneel": [(-46, -72), (-60, -12)],
}


def mirror(pts):
    return [(-x, y) for x, y in pts]


def arm(side, pose, color, glove, w=24):
    pts = ARMS[pose]
    sh = SH_L
    if side == "R":
        pts, sh = mirror(pts), SH_R
    hx, hy = pts[-1]
    return limb([sh] + pts, color, w) + f'<circle cx="{hx}" cy="{hy}" r="16" fill="{glove}" stroke="{INK}" stroke-width="5"/>'


def leg(side, pose, color, boot, w=28):
    pts = LEGS[pose]
    hip = HIP_L
    if side == "R":
        pts, hip = mirror(pts), HIP_R
    fx, fy = pts[-1]
    toe = 9 if fx >= 0 else -9
    if pose == "run_front":
        toe = -toe
    return limb([hip] + pts, color, w) + (
        f'<ellipse cx="{fx + toe}" cy="{fy + 2}" rx="24" ry="14" fill="{boot}" stroke="{INK}" stroke-width="5"/>'
    )


def torso(suit, shade, accent, emblem=""):
    body = "M -46,-206 C -56,-170 -50,-140 -38,-108 L 38,-108 C 50,-140 56,-170 46,-206 C 20,-218 -20,-218 -46,-206 Z"
    return (
        f'<path d="{body}" fill="{suit}"/>'
        f'<path d="M 18,-212 C 40,-182 42,-140 32,-108 L 38,-108 C 50,-140 56,-170 46,-206 Z" fill="{shade}"/>'
        f'<path d="{body}" fill="none" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
        f'<rect x="-41" y="-130" width="82" height="15" rx="4" fill="{accent}" stroke="{INK}" stroke-width="4"/>'
        f'<rect x="-9" y="-133" width="18" height="21" rx="3" fill="#fde68a" stroke="{INK}" stroke-width="4"/>'
        + emblem
    )


def eyes(look=(0.4, 0), mood="happy", y=-266):
    lx, ly = look
    out = ""
    for ex in (-21, 21):
        out += f'<ellipse cx="{ex}" cy="{y}" rx="12" ry="14" fill="{WHITE}" stroke="{INK}" stroke-width="3.5"/>'
        out += f'<circle cx="{ex + lx * 5:.1f}" cy="{y + 1 + ly * 4:.1f}" r="6.8" fill="{INK}"/>'
        out += f'<circle cx="{ex + lx * 5 - 2.4:.1f}" cy="{y - 2 + ly * 4:.1f}" r="2.3" fill="{WHITE}"/>'
    if mood == "determined":
        out += f'<path d="M -36,{y - 20} L -10,{y - 14}" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
        out += f'<path d="M 36,{y - 20} L 10,{y - 14}" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
    elif mood == "happy":
        out += f'<path d="M -34,{y - 22} Q -22,{y - 30} -10,{y - 22}" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
        out += f'<path d="M 34,{y - 22} Q 22,{y - 30} 10,{y - 22}" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
    elif mood == "surprised":
        out += f'<path d="M -34,{y - 26} Q -22,{y - 36} -10,{y - 26}" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
        out += f'<path d="M 34,{y - 26} Q 22,{y - 36} 10,{y - 26}" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
    return out


def mouth(kind="grin"):
    if kind == "grin":
        return f'<path d="M -22,-241 Q 0,-212 22,-241 Q 0,-233 -22,-241 Z" fill="{WHITE}" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>'
    if kind == "smile":
        return f'<path d="M -16,-238 Q 0,-224 16,-238" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
    if kind == "shout":
        return f'<ellipse cx="0" cy="-232" rx="14" ry="12" fill="#7a1d3a" stroke="{INK}" stroke-width="4.5"/>'
    if kind == "o":
        return f'<ellipse cx="0" cy="-234" rx="8" ry="9" fill="#7a1d3a" stroke="{INK}" stroke-width="4"/>'
    if kind == "smirk":
        return f'<path d="M -14,-236 Q 4,-228 18,-242" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
    return ""


def head(skin, look=(0.4, 0), mood="happy", mouth_kind="grin", mask=None, under="", over=""):
    out = under
    out += f'<rect x="-13" y="-218" width="26" height="18" fill="{skin}" stroke="{INK}" stroke-width="4"/>'
    for ex in (-56, 56):
        out += f'<circle cx="{ex}" cy="-260" r="11" fill="{skin}" stroke="{INK}" stroke-width="4.5"/>'
    out += f'<circle cx="0" cy="-266" r="57" fill="{skin}" stroke="{INK}" stroke-width="6"/>'
    out += f'<ellipse cx="-34" cy="-242" rx="9" ry="5.5" fill="#f472b6" opacity="0.45"/><ellipse cx="34" cy="-242" rx="9" ry="5.5" fill="#f472b6" opacity="0.45"/>'
    if mask:
        out += (
            f'<path d="M -50,-276 Q -26,-296 0,-282 Q 26,-296 50,-276 Q 48,-250 26,-249 Q 10,-249 0,-260 '
            f'Q -10,-249 -26,-249 Q -48,-250 -50,-276 Z" fill="{mask}" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>'
        )
    out += eyes(look, mood)
    out += mouth(mouth_kind)
    out += over
    return out


def figure(c, arms=("down", "down"), legs=("stand", "stand"), look=(0.4, 0), mood="happy", mouth_kind="grin", back="", front="", hair_under="", hair_over=""):
    """Generic chibi hero. c = colour dict. Feet sit at y=0."""
    return (
        back
        + leg("L", legs[0], c["suit"], c["boot"])
        + leg("R", legs[1], c["suit"], c["boot"])
        + torso(c["suit"], c["shade"], c["accent"], c.get("emblem", ""))
        + arm("L", arms[0], c["suit"], c["glove"])
        + arm("R", arms[1], c["suit"], c["glove"])
        + head(c["skin"], look, mood, mouth_kind, c.get("mask"), hair_under, hair_over)
        + front
    )


# ----------------------------------------------------------------- the heroes

ZAYD = {
    "suit": "#0fb5a6", "shade": "#0b8f84", "accent": "#facc15", "glove": "#facc15", "boot": "#1e3a8a",
    "skin": SKIN["a"], "mask": "#1e3a8a",
}
ZAYD["emblem"] = (
    f'<rect x="-19" y="-188" width="38" height="38" rx="7" fill="#facc15" stroke="{INK}" stroke-width="4"/>'
    f'<path d="M -10,-179 H 10 L -10,-159 H 10" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
)
ZAYD_HAIR = (
    f'<path d="M -60,-262 C -70,-318 -24,-342 0,-336 C 28,-344 72,-320 60,-262 C 52,-286 36,-298 20,-290 '
    f'C 8,-304 -12,-302 -22,-291 C -38,-300 -54,-286 -60,-262 Z" fill="#2b1a12" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
    '<path d="M -18,-330 q 10,-6 20,0" fill="none" stroke="#5b3a26" stroke-width="5" stroke-linecap="round"/>'
)


def zayd_cape(sway=1.0):
    s = sway
    return (
        f'<path d="M -44,-202 C -96,-150 {-118 * s:.0f},-80 {-138 * s:.0f},-22 L {-70 * s:.0f},-44 L 0,-28 L {64 * s:.0f},-46 '
        f'L {118 * s:.0f},-30 C {104 * s:.0f},-90 92,-150 44,-202 Z" fill="#1e3a8a" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
        f'<path d="M {-80 * s:.0f},-110 h 30 v 24 h 30 M {40 * s:.0f},-120 v 26 h 30 M {-30 * s:.0f},-70 h 40 v -20" fill="none" '
        f'stroke="#facc15" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>'
    )


def zayd(arms=("hip", "up"), legs=("wide", "wide"), look=(0.4, 0), mood="happy", mouth_kind="grin", glow=False, cape=1.0):
    over = ZAYD_HAIR
    if glow:
        over += (
            '<ellipse cx="-21" cy="-266" rx="14" ry="16" fill="#fde047"/><ellipse cx="21" cy="-266" rx="14" ry="16" fill="#fde047"/>'
            '<ellipse cx="-21" cy="-266" rx="7" ry="8" fill="#fff"/><ellipse cx="21" cy="-266" rx="7" ry="8" fill="#fff"/>'
        )
    return figure(ZAYD, arms, legs, look, mood, mouth_kind, back=zayd_cape(cape), hair_over=over)


ARROW = {
    "suit": "#2563eb", "shade": "#1d4ed8", "accent": "#67e8f9", "glove": "#1e293b", "boot": "#1e293b",
    "skin": SKIN["b"], "mask": None,
}
ARROW["emblem"] = f'<path d="M -16,-150 L 14,-180 M 14,-180 l -14,2 M 14,-180 l -2,14" stroke="#67e8f9" stroke-width="6" stroke-linecap="round" fill="none"/>'
ARROW_HOOD = (
    f'<path d="M -72,-248 C -80,-330 -34,-356 0,-354 C 34,-356 80,-330 72,-248 C 68,-220 52,-208 42,-214 '
    f'C 54,-240 54,-304 0,-314 C -54,-304 -54,-240 -42,-214 C -52,-208 -68,-220 -72,-248 Z" fill="#2563eb" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
    f'<path d="M -26,-312 Q 0,-322 26,-312" fill="none" stroke="#67e8f9" stroke-width="4" stroke-linecap="round"/>'
)


def bow(drawn=True):
    # bow held in the viewer-left hand at (-150,-200) when arm pose is "aim"
    string_x = -96 if drawn else -150
    return (
        f'<path d="M -150,-292 Q -206,-200 -150,-108" fill="none" stroke="{INK}" stroke-width="16" stroke-linecap="round"/>'
        f'<path d="M -150,-292 Q -206,-200 -150,-108" fill="none" stroke="#22d3ee" stroke-width="9" stroke-linecap="round"/>'
        f'<path d="M -150,-292 L {string_x},-200 L -150,-108" fill="none" stroke="#e0f2fe" stroke-width="3"/>'
        + (
            f'<path d="M {string_x},-200 L -250,-200" stroke="#fef08a" stroke-width="8" stroke-linecap="round"/>'
            f'<path d="M -262,-200 l 24,-14 l 0,28 Z" fill="#fef08a" stroke="{INK}" stroke-width="3"/>'
            if drawn
            else ""
        )
    )


def quiver():
    return (
        f'<rect x="30" y="-236" width="30" height="88" rx="10" transform="rotate(18 45 -190)" fill="#7c2d12" stroke="{INK}" stroke-width="5"/>'
        f'<path d="M 46,-244 l 10,-26 M 58,-240 l 16,-22 M 34,-246 l 4,-28" stroke="#fef08a" stroke-width="6" stroke-linecap="round"/>'
    )


def arrowlight(drawn=True, mood="determined", look=(-0.6, 0)):
    return figure(ARROW, ("aim", "front"), ("wide", "wide"), look, mood, "smirk", back=quiver(), hair_over=ARROW_HOOD, front=bow(drawn))


BUBBLE = {
    "suit": "#06b6d4", "shade": "#0891b2", "accent": "#f472b6", "glove": "#f9a8d4", "boot": "#f472b6",
    "skin": SKIN["c"], "mask": "#f472b6",
}
BUBBLE["emblem"] = (
    f'<circle cx="0" cy="-170" r="17" fill="#e0f2fe" stroke="{INK}" stroke-width="4"/>'
    f'<circle cx="-5" cy="-175" r="5" fill="#ffffff"/>'
)
BUBBLE_HAIR_BACK = (
    f'<circle cx="-56" cy="-312" r="27" fill="#3b2416" stroke="{INK}" stroke-width="5"/>'
    f'<circle cx="56" cy="-312" r="27" fill="#3b2416" stroke="{INK}" stroke-width="5"/>'
)
BUBBLE_HAIR = (
    f'<path d="M -58,-268 C -64,-322 -20,-336 0,-332 C 22,-336 64,-322 58,-268 C 40,-296 14,-300 0,-292 C -16,-300 -42,-296 -58,-268 Z" '
    f'fill="#3b2416" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
    f'<circle cx="-40" cy="-300" r="8" fill="#67e8f9" stroke="{INK}" stroke-width="3"/><circle cx="40" cy="-300" r="8" fill="#67e8f9" stroke="{INK}" stroke-width="3"/>'
)


def bubble_dome(r=230, cy=-170):
    return (
        f'<circle cx="0" cy="{cy}" r="{r}" fill="#a5f3fc" opacity="0.28" stroke="#22d3ee" stroke-width="8"/>'
        f'<path d="M {-r * 0.62:.0f},{cy - r * 0.55:.0f} A {r} {r} 0 0 1 {-r * 0.1:.0f},{cy - r * 0.86:.0f}" fill="none" stroke="#ffffff" stroke-width="14" stroke-linecap="round" opacity="0.8"/>'
        f'<circle cx="{r * 0.55:.0f}" cy="{cy - r * 0.55:.0f}" r="12" fill="#ffffff" opacity="0.8"/>'
    )


def bubbleguard(dome=True, arms=("up", "up"), mood="happy", mouth_kind="grin", look=(0, -0.3)):
    body = figure(BUBBLE, arms, ("stand", "stand"), look, mood, mouth_kind, hair_under=BUBBLE_HAIR_BACK, hair_over=BUBBLE_HAIR)
    return body + (bubble_dome() if dome else "")


ZIG = {
    "suit": "#9333ea", "shade": "#7e22ce", "accent": "#fde047", "glove": "#fde047", "boot": "#f97316",
    "skin": SKIN["d"], "mask": None,
}
ZIG["emblem"] = f'<path d="M -6,-196 L -18,-166 L 0,-166 L -10,-138 L 20,-176 L 2,-176 L 12,-196 Z" fill="#fde047" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
ZIG_HAIR = (
    f'<path d="M -60,-264 C -62,-310 -30,-336 0,-334 L -30,-352 L 14,-344 L -4,-364 L 44,-338 C 66,-322 68,-290 60,-262 '
    f'C 44,-292 20,-300 0,-296 C -24,-300 -46,-290 -60,-264 Z" fill="#7c2d12" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
    f'<rect x="-48" y="-312" width="96" height="24" rx="12" fill="#1e293b" stroke="{INK}" stroke-width="4"/>'
    f'<circle cx="-22" cy="-300" r="13" fill="#5eead4" stroke="{INK}" stroke-width="4"/><circle cx="22" cy="-300" r="13" fill="#5eead4" stroke="{INK}" stroke-width="4"/>'
)


def rainbow_trail(length=260):
    cols = ["#ef4444", "#f97316", "#facc15", "#22c55e", "#3b82f6", "#a855f7"]
    out = ""
    for i, col in enumerate(cols):
        y = -230 + i * 16
        out += f'<path d="M -30,{y} C {-length * 0.4:.0f},{y - 30} {-length * 0.7:.0f},{y + 30} {-length:.0f},{y}" fill="none" stroke="{col}" stroke-width="14" stroke-linecap="round" opacity="0.9"/>'
    return out


def zigzag(trail=True, arms=("out", "point"), mood="happy", mouth_kind="grin", look=(1, 0)):
    back = rainbow_trail() if trail else ""
    return figure(ZIG, arms, ("run_back", "run_front"), look, mood, mouth_kind, back=back, hair_over=ZIG_HAIR)


def dragon_head(x, y, ang, scale=1.0, look=1):
    """One of Dragoncrest's three helmet dragons (Flicker, Flame and Fluff)."""
    return (
        f'<g transform="translate({x},{y}) rotate({ang}) scale({scale})">'
        f'<path d="M 0,0 C -6,-40 -4,-70 10,-96" fill="none" stroke="{INK}" stroke-width="34" stroke-linecap="round"/>'
        f'<path d="M 0,0 C -6,-40 -4,-70 10,-96" fill="none" stroke="#22c55e" stroke-width="24" stroke-linecap="round"/>'
        f'<ellipse cx="22" cy="-104" rx="34" ry="24" fill="#22c55e" stroke="{INK}" stroke-width="5"/>'
        f'<path d="M 6,-124 l -10,-18 l 18,8 Z M 22,-126 l 0,-20 l 12,16 Z" fill="#facc15" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
        f'<circle cx="{18 + look * 4}" cy="-110" r="8" fill="#ffffff" stroke="{INK}" stroke-width="3"/>'
        f'<circle cx="{20 + look * 6}" cy="-110" r="4" fill="{INK}"/>'
        f'<path d="M 40,-98 q 8,4 14,0" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
        f'<circle cx="50" cy="-106" r="2.5" fill="{INK}"/>'
        f'<path d="M 54,-94 q 14,4 20,-6 q -4,14 -16,14 Z" fill="#ef4444" stroke="{INK}" stroke-width="3"/>'
        "</g>"
    )


def stretch_arm(length=420, fist_color="#64748b"):
    """Dragoncrest's coiled Stretch-Punch reaching to the viewer's right."""
    out = ""
    seg = 34
    n = max(4, int(length / seg))
    for i in range(n):
        x = 60 + i * seg
        y = -176 - math.sin(i / 2.2) * 6
        out += f'<rect x="{x - 4}" y="{y - 22}" width="{seg + 2}" height="44" rx="14" fill="#cbd5e1" stroke="{INK}" stroke-width="5"/>'
    fx = 60 + n * seg + 26
    out += (
        f'<rect x="{fx - 36}" y="-222" width="82" height="76" rx="24" fill="{fist_color}" stroke="{INK}" stroke-width="6"/>'
        f'<path d="M {fx + 8},-214 v 60 M {fx + 26},-214 v 60" stroke="{INK}" stroke-width="4" opacity="0.6"/>'
    )
    return out


def dragoncrest(punch=0, mood="happy", look=(0.6, 0)):
    """Gentle giant in grey armour. punch>0 adds the Stretch-Punch arm."""
    armor, armor_d = "#94a3b8", "#64748b"
    out = (
        limb([(-30, -150), (-46, -80), (-60, -14)], armor, 46)
        + limb([(30, -150), (44, -80), (54, -14)], armor, 46)
        + f'<rect x="-104" y="-38" width="84" height="38" rx="14" fill="{armor_d}" stroke="{INK}" stroke-width="6"/>'
        + f'<rect x="22" y="-38" width="84" height="38" rx="14" fill="{armor_d}" stroke="{INK}" stroke-width="6"/>'
        + f'<path d="M -86,-300 C -100,-230 -84,-170 -58,-134 L 58,-134 C 84,-170 100,-230 86,-300 C 40,-322 -40,-322 -86,-300 Z" fill="{armor}" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
        + f'<path d="M 34,-316 C 82,-290 92,-210 58,-134 L 72,-134 C 98,-176 104,-250 86,-300 Z" fill="{armor_d}"/>'
        + f'<rect x="-46" y="-248" width="92" height="64" rx="14" fill="#22c55e" stroke="{INK}" stroke-width="6"/>'
        + f'<path d="M -28,-216 l 14,-16 l 14,16 l 14,-16 l 14,16" fill="none" stroke="#14532d" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
        + limb([(-84, -276), (-122, -222), (-104, -170)], armor, 40)
        + f'<rect x="-136" y="-188" width="62" height="56" rx="18" fill="{armor_d}" stroke="{INK}" stroke-width="6"/>'
    )
    if punch:
        out += limb([(84, -276), (70, -210), (66, -178)], armor, 40) + stretch_arm(punch)
    else:
        out += limb([(84, -276), (122, -222), (104, -170)], armor, 40)
        out += f'<rect x="74" y="-188" width="62" height="56" rx="18" fill="{armor_d}" stroke="{INK}" stroke-width="6"/>'
    # helmet + visor
    out += (
        f'<path d="M -66,-322 C -70,-392 -30,-416 0,-414 C 30,-416 70,-392 66,-322 C 40,-308 -40,-308 -66,-322 Z" fill="{armor}" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
        f'<rect x="-48" y="-378" width="96" height="30" rx="15" fill="{INK}"/>'
    )
    lx = look[0] * 8
    out += (
        f'<rect x="{-36 + lx:.0f}" y="-370" width="26" height="14" rx="7" fill="#86efac"/>'
        f'<rect x="{10 + lx:.0f}" y="-370" width="26" height="14" rx="7" fill="#86efac"/>'
    )
    if mood == "happy":
        out += f'<path d="M -20,-332 Q 0,-322 20,-332" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
    else:
        out += f'<path d="M -20,-328 L 20,-332" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
    # three helmet dragons + red flame tufts (from the owner sketch)
    out = (
        f'<path d="M -78,-374 q -34,-6 -40,18 q 14,-10 26,0 q -10,-26 14,-18 Z" fill="#ef4444" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
        f'<path d="M 78,-374 q 34,-6 40,18 q -14,-10 -26,0 q 10,-26 -14,-18 Z" fill="#ef4444" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
        + dragon_head(-36, -400, -24, 0.9, -1)
        + dragon_head(0, -410, 2, 1.0, 1)
        + dragon_head(36, -400, 26, 0.9, 1)
        + out
    )
    return out


# ----------------------------------------------------------------- villains


def yeti(mood="grumpy", arms="up", glitch=True):
    """Blizzardbyte, the Glitch Yeti. Feet at y=0, ~470 tall."""
    fur, fur_d, face = "#f1f5f9", "#cbd5e1", "#bae6fd"
    zig = " ".join(f"{-150 + i * 20},{-60 + (14 if i % 2 else 0)}" for i in range(16))
    out = (
        f'<rect x="-120" y="-90" width="80" height="90" rx="26" fill="{fur}" stroke="{INK}" stroke-width="7"/>'
        f'<rect x="40" y="-90" width="80" height="90" rx="26" fill="{fur}" stroke="{INK}" stroke-width="7"/>'
        f'<path d="M -150,-60 C -176,-200 -150,-330 -96,-380 C -40,-420 40,-420 96,-380 C 150,-330 176,-200 150,-60 Z" fill="{fur}" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>'
        f'<polyline points="{zig}" fill="none" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
        f'<path d="M 60,-400 C 140,-340 170,-200 150,-60 L 120,-60 C 140,-180 120,-320 60,-400 Z" fill="{fur_d}"/>'
        f'<path d="M -84,-336 C -84,-380 84,-380 84,-336 C 84,-262 -84,-262 -84,-336 Z" fill="{face}" stroke="{INK}" stroke-width="6"/>'
    )
    # ice crown
    out += (
        f'<path d="M -70,-396 L -54,-460 L -30,-410 L 0,-480 L 30,-410 L 54,-460 L 70,-396 Z" fill="#7dd3fc" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
        f'<path d="M -2,-470 L 8,-430" stroke="#ffffff" stroke-width="5" stroke-linecap="round"/>'
    )
    # face
    brow = 10 if mood == "grumpy" else -6
    out += (
        f'<circle cx="-34" cy="-334" r="16" fill="#ffffff" stroke="{INK}" stroke-width="4"/><circle cx="34" cy="-334" r="16" fill="#ffffff" stroke="{INK}" stroke-width="4"/>'
        f'<circle cx="-30" cy="-330" r="8" fill="{INK}"/><circle cx="38" cy="-330" r="8" fill="{INK}"/>'
        f'<path d="M -58,{-362 - brow} L -14,-356" stroke="{INK}" stroke-width="9" stroke-linecap="round"/>'
        f'<path d="M 58,{-362 - brow} L 14,-356" stroke="{INK}" stroke-width="9" stroke-linecap="round"/>'
        f'<ellipse cx="0" cy="-306" rx="16" ry="11" fill="#475569"/>'
    )
    if mood == "grumpy":
        out += f'<path d="M -34,-282 Q 0,-298 34,-282" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/><path d="M -18,-288 l 6,10 l 6,-10 M 6,-290 l 6,10 l 6,-10" fill="#ffffff" stroke="{INK}" stroke-width="3"/>'
    else:
        out += f'<ellipse cx="0" cy="-282" rx="20" ry="14" fill="#7a1d3a" stroke="{INK}" stroke-width="5"/>'
    # arms
    if arms == "up":
        out += limb([(-128, -250), (-196, -320), (-200, -400)], fur, 54) + limb([(128, -250), (196, -320), (200, -400)], fur, 54)
        out += f'<circle cx="-200" cy="-410" r="34" fill="{fur_d}" stroke="{INK}" stroke-width="7"/><circle cx="200" cy="-410" r="34" fill="{fur_d}" stroke="{INK}" stroke-width="7"/>'
    else:
        out += limb([(-128, -250), (-190, -190), (-180, -120)], fur, 54) + limb([(128, -250), (190, -190), (180, -120)], fur, 54)
        out += f'<circle cx="-182" cy="-110" r="34" fill="{fur_d}" stroke="{INK}" stroke-width="7"/><circle cx="182" cy="-110" r="34" fill="{fur_d}" stroke="{INK}" stroke-width="7"/>'
    if glitch:
        rnd = random.Random(11)
        for _ in range(16):
            x, y = rnd.uniform(-140, 130), rnd.uniform(-260, -80)
            s = rnd.choice([12, 16, 20])
            col = rnd.choice(["#f97316", "#f472b6", "#a855f7", "#22d3ee"])
            out += f'<rect x="{x:.0f}" y="{y:.0f}" width="{s}" height="{s}" fill="{col}" stroke="{INK}" stroke-width="3"/>'
    return out


def robo_beast(mouth_open=True, smoke=True):
    """Grumblejaw, the junkyard Robo-Beast. Feet at y=0, ~520 tall."""
    m, m_d, m_l = "#9ca3af", "#6b7280", "#d1d5db"
    out = (
        # tank-tread feet
        f'<rect x="-190" y="-80" width="150" height="80" rx="38" fill="#374151" stroke="{INK}" stroke-width="7"/>'
        f'<rect x="40" y="-80" width="150" height="80" rx="38" fill="#374151" stroke="{INK}" stroke-width="7"/>'
        + "".join(f'<circle cx="{cx}" cy="-40" r="14" fill="{m_l}" stroke="{INK}" stroke-width="4"/>' for cx in (-160, -115, -70, 70, 115, 160))
        # body
        + f'<rect x="-150" y="-280" width="300" height="210" rx="40" fill="{m}" stroke="{INK}" stroke-width="8"/>'
        + f'<rect x="60" y="-276" width="86" height="200" rx="36" fill="{m_d}"/>'
        + f'<rect x="-150" y="-280" width="300" height="210" rx="40" fill="none" stroke="{INK}" stroke-width="8"/>'
        + f'<circle cx="0" cy="-180" r="40" fill="#fbbf24" stroke="{INK}" stroke-width="6"/><path d="M -16,-196 L 4,-180 L -10,-172 L 14,-156" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="{m_l}" stroke="{INK}" stroke-width="3"/>' for x, y in ((-126, -256), (126, -256), (-126, -96), (126, -96)))
        # little arms
        + limb([(-150, -220), (-210, -200), (-226, -150)], m, 34)
        + limb([(150, -220), (210, -200), (226, -150)], m, 34)
        + f'<path d="M -246,-150 l 20,24 l 20,-24" fill="{m_d}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
        + f'<path d="M 206,-150 l 20,24 l 20,-24" fill="{m_d}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
    )
    # big head with a huge underbite jaw
    out += (
        f'<rect x="-170" y="-500" width="340" height="170" rx="46" fill="{m}" stroke="{INK}" stroke-width="8"/>'
        f'<path d="M -150,-470 L -40,-440 M 150,-470 L 40,-440" stroke="{INK}" stroke-width="12" stroke-linecap="round"/>'
        f'<rect x="-108" y="-438" width="60" height="34" rx="10" fill="#ef4444" stroke="{INK}" stroke-width="5"/>'
        f'<rect x="48" y="-438" width="60" height="34" rx="10" fill="#ef4444" stroke="{INK}" stroke-width="5"/>'
        f'<rect x="-90" y="-430" width="18" height="14" rx="4" fill="#fecaca"/><rect x="66" y="-430" width="18" height="14" rx="4" fill="#fecaca"/>'
    )
    jaw_y = -312 if mouth_open else -340
    out += (
        f'<rect x="-190" y="{jaw_y}" width="380" height="64" rx="24" fill="{m_d}" stroke="{INK}" stroke-width="8"/>'
        + "".join(f'<path d="M {x},{jaw_y + 4} l 14,-30 l 14,30 Z" fill="#ffffff" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>' for x in (-160, -110, 82, 132))
    )
    if mouth_open:
        out += f'<rect x="-140" y="-340" width="280" height="30" fill="#7c2d12" stroke="{INK}" stroke-width="5"/>'
    # smokestack ears
    out += (
        f'<rect x="-196" y="-560" width="44" height="90" rx="8" fill="{m_d}" stroke="{INK}" stroke-width="6"/>'
        f'<rect x="152" y="-560" width="44" height="90" rx="8" fill="{m_d}" stroke="{INK}" stroke-width="6"/>'
    )
    if smoke:
        for cx, cy, r in ((-174, -590, 26), (-200, -630, 20), (-160, -660, 16), (174, -590, 26), (204, -628, 20), (166, -662, 15)):
            out += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#e5e7eb" stroke="{INK}" stroke-width="4"/>'
    return out


def serpent(mood="cheeky", splash=True):
    """Splashfang, the wave serpent. Head at origin-ish, body curls left. ~ 700 wide."""
    out = ""
    body = "M -640,40 C -560,-120 -440,120 -330,-10 C -240,-120 -150,40 -60,-60"
    out += f'<path d="{body}" fill="none" stroke="{INK}" stroke-width="104" stroke-linecap="round"/>'
    out += f'<path d="{body}" fill="none" stroke="#2563eb" stroke-width="88" stroke-linecap="round"/>'
    out += f'<path d="{body}" fill="none" stroke="#93c5fd" stroke-width="22" stroke-linecap="round" stroke-dasharray="26 22" transform="translate(0,18)"/>'
    # dorsal fins
    for x, y in ((-560, -70), (-430, 40), (-300, -50), (-180, -40)):
        out += f'<path d="M {x - 22},{y - 30} l 22,-50 l 22,50 Z" fill="#22d3ee" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
    # head
    out += (
        f'<path d="M -110,-60 C -110,-170 70,-190 120,-110 C 160,-60 140,-10 70,-10 L -40,-6 C -90,-6 -110,-30 -110,-60 Z" fill="#2563eb" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>'
        f'<path d="M -40,-150 l -10,-54 l 34,40 l 16,-58 l 22,58 l 34,-42 l -6,58 Z" fill="#22d3ee" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
        f'<circle cx="34" cy="-104" r="30" fill="#ffffff" stroke="{INK}" stroke-width="5"/><circle cx="44" cy="-100" r="14" fill="{INK}"/><circle cx="38" cy="-106" r="5" fill="#ffffff"/>'
        f'<path d="M 4,-140 L 60,-128" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>'
        f'<path d="M -20,-40 C 30,-26 90,-30 128,-56" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
        f'<path d="M 70,-36 l 8,30 l 14,-32 Z" fill="#ffffff" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
        f'<circle cx="108" cy="-84" r="5" fill="{INK}"/>'
    )
    if mood == "cheeky":
        out += f'<path d="M 100,-46 q 20,10 34,-4 q -6,22 -26,20 Z" fill="#f472b6" stroke="{INK}" stroke-width="4"/>'
    if splash:
        for x, y, r in ((-660, 0, 30), (-610, -60, 20), (160, -40, 22), (190, -90, 14), (-700, 60, 16)):
            out += f'<circle cx="{x}" cy="{y}" r="{r}" fill="#bfdbfe" stroke="{INK}" stroke-width="4"/>'
    return out


def glitchling(color="#84cc16", sword=True, mood="silly"):
    """Tiny pixel minion with a foam pool-noodle sword. Feet at y=0, ~110 tall."""
    out = (
        f'<rect x="-22" y="-26" width="14" height="26" fill="{color}" stroke="{INK}" stroke-width="4"/>'
        f'<rect x="8" y="-26" width="14" height="26" fill="{color}" stroke="{INK}" stroke-width="4"/>'
        f'<rect x="-40" y="-104" width="80" height="80" rx="10" fill="{color}" stroke="{INK}" stroke-width="5"/>'
        f'<rect x="-26" y="-84" width="18" height="18" fill="#ffffff" stroke="{INK}" stroke-width="3"/><rect x="8" y="-84" width="18" height="18" fill="#ffffff" stroke="{INK}" stroke-width="3"/>'
        f'<rect x="-20" y="-78" width="8" height="8" fill="{INK}"/><rect x="14" y="-78" width="8" height="8" fill="{INK}"/>'
    )
    out += (
        f'<path d="M -14,-48 h 28" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
        if mood == "silly"
        else f'<ellipse cx="0" cy="-46" rx="9" ry="7" fill="{INK}"/>'
    )
    if sword:
        out += (
            f'<path d="M 40,-60 L 70,-120" stroke="{INK}" stroke-width="22" stroke-linecap="round"/>'
            f'<path d="M 40,-60 L 70,-120" stroke="#f472b6" stroke-width="14" stroke-linecap="round"/>'
            f'<rect x="32" y="-66" width="20" height="10" rx="3" fill="#facc15" stroke="{INK}" stroke-width="3" transform="rotate(-62 42 -61)"/>'
        )
    return out


# ----------------------------------------------------------------- scenery


def maze_floor(w, h, horizon, base="#1e1b4b", line="#22d3ee"):
    out = f'<rect y="{horizon}" width="{w}" height="{h - horizon}" fill="{base}"/>'
    vx = w / 2
    for i in range(-16, 17):
        x2 = vx + i * 120
        out += f'<line x1="{vx}" y1="{horizon}" x2="{x2}" y2="{h}" stroke="{line}" stroke-width="3" opacity="0.55"/>'
    y = horizon + 8
    step = 8
    while y < h:
        out += f'<line x1="0" y1="{y:.0f}" x2="{w}" y2="{y:.0f}" stroke="{line}" stroke-width="3" opacity="0.55"/>'
        step *= 1.32
        y += step
    return out


def maze_walls(x, y, cell, grid, color="#a78bfa", sw=10, seed=21):
    """Draws a small random maze (recursive backtracker) as glowing walls."""
    rnd = random.Random(seed)
    cols, rows = grid
    walls = {(c, r): {"N", "S", "E", "W"} for c in range(cols) for r in range(rows)}
    seen = {(0, 0)}
    stack = [(0, 0)]
    dirs = {"N": (0, -1, "S"), "S": (0, 1, "N"), "E": (1, 0, "W"), "W": (-1, 0, "E")}
    while stack:
        c, r = stack[-1]
        opts = [(d, c + dx, r + dy, o) for d, (dx, dy, o) in dirs.items() if (c + dx, r + dy) in walls and (c + dx, r + dy) not in seen]
        if not opts:
            stack.pop()
            continue
        d, nc, nr, o = rnd.choice(opts)
        walls[(c, r)].discard(d)
        walls[(nc, nr)].discard(o)
        seen.add((nc, nr))
        stack.append((nc, nr))
    walls[(0, 0)].discard("W")
    walls[(cols - 1, rows - 1)].discard("E")
    d = ""
    for (c, r), ws in walls.items():
        x0, y0 = x + c * cell, y + r * cell
        if "N" in ws:
            d += f"M {x0},{y0} h {cell} "
        if "W" in ws:
            d += f"M {x0},{y0} v {cell} "
        if r == rows - 1 and "S" in ws:
            d += f"M {x0},{y0 + cell} h {cell} "
        if c == cols - 1 and "E" in ws:
            d += f"M {x0 + cell},{y0} v {cell} "
    return (
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw + 10}" stroke-linecap="round" opacity="0.35"/>'
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>'
    )


def lighthouse(x, y, s=1.0, beam=True):
    """Lighthouse HQ. (x, y) is the base centre."""
    inner = ""
    if beam:
        inner += '<polygon points="0,-470 900,-640 900,-300" fill="#fef9c3" opacity="0.45"/><polygon points="0,-470 -900,-620 -900,-330" fill="#fef9c3" opacity="0.3"/>'
    inner += (
        f'<path d="M -90,0 L -60,-400 L 60,-400 L 90,0 Z" fill="#f8fafc" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>'
        f'<path d="M -84,-80 L 84,-80 L 78,-160 L -78,-160 Z M -74,-240 L 74,-240 L 69,-320 L -69,-320 Z" fill="#14b8a6" stroke="{INK}" stroke-width="5"/>'
        f'<rect x="-22" y="-62" width="44" height="62" rx="20" fill="#1e3a8a" stroke="{INK}" stroke-width="5"/>'
        f'<rect x="-80" y="-420" width="160" height="26" rx="8" fill="#1e3a8a" stroke="{INK}" stroke-width="6"/>'
        f'<rect x="-50" y="-500" width="100" height="80" rx="10" fill="#fde047" stroke="{INK}" stroke-width="6"/>'
        f'<path d="M -50,-470 h 100 M -16,-500 v 80 M 16,-500 v 80" stroke="{INK}" stroke-width="4"/>'
        f'<path d="M -64,-500 L 0,-556 L 64,-500 Z" fill="#ef4444" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
        f'<rect x="-24" y="-200" width="48" height="26" rx="6" fill="#bae6fd" stroke="{INK}" stroke-width="4"/>'
    )
    return place(inner, x, y, s)


def compass_core(x, y, s=1.0, wobble=False, magnets=False, glow=True):
    inner = ""
    if glow:
        inner += '<circle r="210" fill="#fde68a" opacity="0.35"/><circle r="160" fill="#fef3c7" opacity="0.5"/>'
    inner += (
        f'<circle r="120" fill="#1e3a8a" stroke="{INK}" stroke-width="10"/>'
        f'<circle r="96" fill="#312e81" stroke="#facc15" stroke-width="8"/>'
    )
    rot = 24 if wobble else 0
    inner += (
        f'<g transform="rotate({rot})"><polygon points="0,-90 22,0 0,90 -22,0" fill="#facc15" stroke="{INK}" stroke-width="6"/>'
        f'<polygon points="0,-90 22,0 -22,0" fill="#ef4444" stroke="{INK}" stroke-width="6"/></g>'
        f'<circle r="14" fill="#ffffff" stroke="{INK}" stroke-width="5"/>'
    )
    for a in range(0, 360, 90):
        inner += f'<g transform="rotate({a})"><rect x="-10" y="-138" width="20" height="26" rx="4" fill="#22d3ee" stroke="{INK}" stroke-width="4"/></g>'
    if magnets:
        for a, col in ((40, "#ef4444"), (160, "#94a3b8"), (280, "#38bdf8")):
            inner += (
                f'<g transform="rotate({a}) translate(0,-150)">'
                f'<path d="M -30,0 v -40 a 30 30 0 0 1 60 0 v 40 h -18 v -40 a 12 12 0 0 0 -24 0 v 40 Z" fill="{col}" stroke="{INK}" stroke-width="5"/>'
                f'<rect x="-30" y="-6" width="18" height="16" fill="#e5e7eb" stroke="{INK}" stroke-width="4"/><rect x="12" y="-6" width="18" height="16" fill="#e5e7eb" stroke="{INK}" stroke-width="4"/></g>'
            )
    return place(inner, x, y, s)


def snow_field(w, h, horizon):
    out = f'<rect y="{horizon}" width="{w}" height="{h - horizon}" fill="#f8fafc"/>'
    out += f'<path d="M 0,{horizon} C {w * 0.2},{horizon - 60} {w * 0.4},{horizon + 30} {w * 0.6},{horizon - 40} C {w * 0.8},{horizon - 90} {w * 0.9},{horizon + 10} {w},{horizon - 30} V {h} H 0 Z" fill="#e2e8f0"/>'
    for x, y, rx in ((180, h - 90, 110), (720, h - 60, 150), (980, h - 140, 90)):
        out += f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx * 0.24:.0f}" fill="#7dd3fc" stroke="{INK}" stroke-width="4" opacity="0.9"/>'
    return out


def snowflakes(w, h, n=40, seed=8):
    rnd = random.Random(seed)
    return "".join(
        f'<circle cx="{rnd.uniform(0, w):.0f}" cy="{rnd.uniform(0, h):.0f}" r="{rnd.uniform(3, 8):.1f}" fill="#ffffff" opacity="0.9"/>'
        for _ in range(n)
    )


def stars(w, h, n=50, seed=4, top=None):
    rnd = random.Random(seed)
    top = top or h
    return "".join(
        f'<circle cx="{rnd.uniform(0, w):.0f}" cy="{rnd.uniform(0, top):.0f}" r="{rnd.uniform(1.5, 4):.1f}" fill="#fef9c3" opacity="{rnd.uniform(0.5, 1):.2f}"/>'
        for _ in range(n)
    )


def frame(w, h, sw=14):
    return f'<rect x="{sw / 2}" y="{sw / 2}" width="{w - sw}" height="{h - sw}" fill="none" stroke="{INK}" stroke-width="{sw}"/>'


# ----------------------------------------------------------------- portraits


def portrait(name, c1, c2, art, title, dark=False):
    W, H = 800, 1000
    body = rays(W, H, W / 2, H * 0.42, c1, c2, 22)
    body += f'<rect width="{W}" height="{H}" fill="url(#{"dotsDark" if dark else "dots"})"/>'
    body += f'<ellipse cx="{W / 2}" cy="{H - 110}" rx="300" ry="46" fill="{INK}" opacity="0.28"/>'
    body += art
    body += frame(W, H)
    return svg(W, H, body, title)


def build_portraits(out: Path):
    heroes = {
        "zayd": ("#fde047", "#fbbf24", place(zayd(("hip", "up"), ("wide", "wide"), (0.2, -0.2)), 400, 890, 2.3), "Super Zayd, leader of the Maze Guardians, raising a fist in a teal and gold suit with a blue maze cape"),
        "dragoncrest": ("#bbf7d0", "#86efac", place(dragoncrest(), 400, 900, 1.68), "Dragoncrest, a gentle giant in grey armour whose helmet carries three small green dragons"),
        "arrowlight": ("#bfdbfe", "#93c5fd", place(arrowlight(), 470, 890, 2.1), "Arrowlight in a blue hood drawing a glowing bow"),
        "bubbleguard": ("#fbcfe8", "#f9a8d4", place(bubbleguard(), 400, 860, 1.7), "Bubbleguard in an aqua suit inside a shimmering protective bubble"),
        "zigzag": ("#e9d5ff", "#d8b4fe", place(zigzag(), 420, 880, 2.1), "Zigzag the speedster running with a rainbow trail behind her"),
    }
    for slug, (c1, c2, art, alt) in heroes.items():
        (out / "heroes" / f"{slug}.svg").write_text(portrait(slug, c1, c2, art, alt))
    villains = {
        "blizzardbyte": ("#1e3a8a", "#1e40af", place(yeti(), 400, 930, 1.4) + snowflakes(800, 1000, 36), "Blizzardbyte, a big grumpy yeti with an ice crown and glitchy coloured pixels in his fur"),
        "grumblejaw": ("#3f3f46", "#52525b", place(robo_beast(), 400, 950, 1.12), "Grumblejaw, a junkyard robot beast with tank treads, red eyes and a huge underbite jaw"),
        "splashfang": ("#0c4a6e", "#075985", place(serpent(), 610, 640, 0.8), "Splashfang, a cheeky blue sea serpent with a single goofy fang"),
    }
    for slug, (c1, c2, art, alt) in villains.items():
        (out / "villains" / f"{slug}.svg").write_text(portrait(slug, c1, c2, art, alt, dark=True))


# ----------------------------------------------------------------- panels (1200 x 800)

PW, PH = 1200, 800


def panel(body, title, defs=""):
    return svg(PW, PH, body + frame(PW, PH), title, defs)


def p01_lighthouse():
    defs = (
        '<linearGradient id="dawn" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#4c1d95"/><stop offset="0.55" stop-color="#db2777"/><stop offset="1" stop-color="#fb923c"/></linearGradient>'
    )
    b = f'<rect width="{PW}" height="{PH}" fill="url(#dawn)"/>' + stars(PW, PH, 40, 2, 260)
    b += '<circle cx="980" cy="470" r="120" fill="#fde047" opacity="0.95"/>'
    b += maze_floor(PW, PH, 520, "#2e1065", "#f0abfc")
    b += lighthouse(600, 620, 0.85)
    b += maze_walls(40, 600, 46, (5, 4), "#22d3ee", 8, 3) + maze_walls(930, 600, 46, (5, 4), "#22d3ee", 8, 5)
    b += place(zayd(("wave", "hip"), ("stand", "stand"), (0.5, 0)), 420, 760, 0.62)
    b += place(zigzag(False, ("front", "up"), "happy", "grin", (-1, 0)), 800, 760, 0.62, flip=True)
    # pancake stack for Zigzag
    b += "".join(f'<ellipse cx="822" cy="{548 - i * 13}" rx="40" ry="12" fill="#f59e0b" stroke="{INK}" stroke-width="4"/>' for i in range(5))
    b += f'<rect x="810" y="474" width="24" height="12" rx="3" fill="#fde68a" stroke="{INK}" stroke-width="3"/>'
    b += caption("MAZEVERSE — 7:59 A.M.", 30, 28, 30)
    return panel(b, "Dawn over Lighthouse HQ in the middle of a glowing maze, with Super Zayd waving and Zigzag balancing a stack of pancakes", defs)


def p02_alarm():
    b = f'<rect width="{PW}" height="{PH}" fill="#0f172a"/>'
    b += '<path d="M 0,0 L 600,0 L 420,800 L 0,800 Z" fill="#ef4444" opacity="0.18"/>'
    b += f'<rect x="300" y="60" width="760" height="420" rx="24" fill="#082f49" stroke="{INK}" stroke-width="10"/>'
    b += f'<rect x="300" y="60" width="760" height="420" rx="24" fill="none" stroke="#22d3ee" stroke-width="4"/>'
    b += maze_walls(360, 100, 52, (13, 7), "#22d3ee", 6, 14)
    for x, y in ((470, 190), (900, 230), (640, 400)):
        b += burst(x, y, 52, 30, "#ef4444", 10, 5, x)
        b += words("!", 56, x, y + 20, fill=WHITE, sw=8)
    b += place(zayd(("hip", "point"), ("stand", "stand"), (1, -0.4), "determined", "shout", cape=0.8), 200, 790, 0.95)
    b += place(dragoncrest(0, "worried", (-0.8, 0)), 1010, 800, 0.66)
    b += burst(150, 120, 120, 76, "#facc15", 14, 7, 2)
    b += words("WEE-OO!", 46, 150, 136, fill="#ef4444", sw=12)
    return panel(b, "Alarm at headquarters: a glowing maze map flashes three red warning signs while Zayd points at it and Dragoncrest looks worried")


def p06_maze_sight():
    b = f'<rect width="{PW}" height="{PH}" fill="#1e1b4b"/>'
    b += maze_walls(40, 40, 60, (19, 12), "#6d28d9", 8, 31)
    b += (
        '<path d="M 70,770 C 200,600 320,640 420,520 S 560,360 600,300" fill="none" stroke="#fde047" stroke-width="14" stroke-linecap="round" stroke-dasharray="2 22"/>'
        '<path d="M 600,300 C 700,240 860,260 1000,160" fill="none" stroke="#fde047" stroke-width="14" stroke-linecap="round" stroke-dasharray="2 22"/>'
        '<path d="M 600,300 C 520,220 380,200 240,120" fill="none" stroke="#fde047" stroke-width="14" stroke-linecap="round" stroke-dasharray="2 22"/>'
    )
    b += burst(240, 120, 70, 50, "#e0f2fe", 12, 6, 7) + words("*", 90, 240, 160, fill="#38bdf8", sw=8)
    b += burst(1000, 160, 70, 50, "#bfdbfe", 12, 6, 8)
    b += f'<path d="M 952,170 q 24,-30 48,0 t 48,0" fill="none" stroke="#2563eb" stroke-width="10" stroke-linecap="round"/>'
    b += compass_core(600, 300, 0.45, wobble=True, magnets=False, glow=True)
    b += place(zayd(("up", "point"), ("wide", "wide"), (0, -0.6), "determined", "smile", glow=True), 600, 800, 1.05)
    b += caption("MAZE-SIGHT: ACTIVATED!", 700, 690, 32)
    return panel(b, "Zayd uses Maze-Sight: his eyes glow gold and golden dotted paths light up across a purple maze toward the ice zone and the sea zone")


def p09_bubble():
    b = rays(PW, PH, 600, 420, "#cffafe", "#a5f3fc", 26) + f'<rect width="{PW}" height="{PH}" fill="url(#dots)"/>'
    b += snow_field(PW, PH, 640)
    b += place(yeti("surprised", "down", True), 1060, 760, 0.62)
    b += place(bubbleguard(True, ("up", "up"), "happy", "grin", (0.6, -0.2)), 470, 720, 1.0)
    for x, y, r in ((760, 220, 40), (820, 400, 34), (700, 120, 30)):
        b += f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffffff" stroke="{INK}" stroke-width="5"/>'
        b += f'<path d="M {x + r + 10},{y} h 60 M {x + r + 12},{y + 16} h 40" stroke="{INK}" stroke-width="5" stroke-linecap="round" opacity="0.6"/>'
    b += burst(250, 130, 130, 88, "#f472b6", 14, 7, 12)
    b += words("BOING!", 64, 250, 152, fill="#fde047", sw=14)
    return panel(b, "Bubbleguard holds up a giant bubble that bounces snowballs back toward a surprised yeti")


def p10_bridge():
    defs = '<linearGradient id="chasm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#312e81"/><stop offset="1" stop-color="#020617"/></linearGradient>'
    b = f'<rect width="{PW}" height="{PH}" fill="url(#chasm)"/>' + stars(PW, PH, 70, 9)
    b += f'<path d="M 0,520 L 300,520 L 340,800 L 0,800 Z" fill="#4c1d95" stroke="{INK}" stroke-width="8"/>'
    b += f'<path d="M 1200,460 L 900,460 L 870,800 L 1200,800 Z" fill="#4c1d95" stroke="{INK}" stroke-width="8"/>'
    b += compass_core(1040, 270, 0.85, wobble=True, magnets=True)
    b += '<path d="M 300,520 Q 600,420 900,460" fill="none" stroke="#fef08a" stroke-width="40" stroke-linecap="round" opacity="0.45"/>'
    b += '<path d="M 300,520 Q 600,420 900,460" fill="none" stroke="#fef9c3" stroke-width="16" stroke-linecap="round"/>'
    b += place(arrowlight(False, "happy", (0.6, 0)), 190, 520, 0.6, flip=True)
    b += place(zayd(("hip", "point"), ("run_back", "run_front"), (1, -0.2), "determined", "grin", cape=1.2), 560, 470, 0.55)
    b += place(dragoncrest(0, "happy", (1, 0)), 420, 498, 0.4)
    b += balloon(640, 40, 340, 130, ["READY? ON THREE!"], (600, 300), 30)
    b += balloon(60, 60, 380, 150, ["ON three, or", "AFTER three?"], (360, 300), 30)
    return panel(b, "Arrowlight shoots a glowing light-bridge over a dark chasm; Zayd and Dragoncrest race across toward the Compass Core, which has three Scramble Magnets stuck to it", defs)


def p11_restored():
    b = rays(PW, PH, 600, 400, "#fde047", "#facc15", 30)
    b += f'<rect width="{PW}" height="{PH}" fill="url(#dots)"/>'
    b += speed_lines(600, 400, 230, 900, 60, "#ffffff", 3, 6)
    b += compass_core(600, 420, 1.1, wobble=False, magnets=False, glow=True)
    b += place(yeti("surprised", "up", False), 150, 260, 0.32)
    b += place(robo_beast(True, False), 1030, 230, 0.26)
    b += place(serpent("cheeky", False), 1040, 690, 0.28, flip=True)
    for x, y in ((110, 90), (250, 120), (980, 70), (1130, 120), (930, 600)):
        b += f'<polygon points="{star_points(x, y, 5, 18, 8, -math.pi / 2)}" fill="#ffffff" stroke="{INK}" stroke-width="3"/>'
    b += burst(600, 110, 210, 130, "#ef4444", 16, 8, 21)
    b += words("KA-WHOOMP!", 64, 600, 132, fill="#fde047", sw=14)
    return panel(b, "The Compass Core blazes back to life and the three villains go tumbling away in a burst of light")


def p12_finale():
    defs = (
        '<linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#f97316"/><stop offset="0.5" stop-color="#ec4899"/><stop offset="1" stop-color="#7c3aed"/></linearGradient>'
    )
    b = f'<rect width="{PW}" height="{PH}" fill="url(#dusk)"/>'
    b += '<circle cx="600" cy="560" r="230" fill="#fde047" opacity="0.85"/>'
    b += maze_floor(PW, PH, 600, "#3b0764", "#f9a8d4")
    b += place(dragoncrest(0, "happy", (0, 0)), 600, 760, 0.56)
    b += place(arrowlight(False, "happy", (0.4, 0)), 410, 760, 0.6)
    b += place(bubbleguard(False, ("wave", "hip"), "happy", "grin", (0.2, 0)), 790, 760, 0.62)
    b += place(zigzag(False, ("up", "hip"), "happy", "grin", (-0.4, 0)), 980, 760, 0.6, flip=True)
    b += place(zayd(("up", "hip"), ("wide", "wide"), (0, -0.2), "happy", "grin"), 210, 760, 0.66)
    # cracked mirror teaser
    b += f'<g transform="translate(1080,130) rotate(8)"><rect x="-70" y="-90" width="140" height="180" rx="70" fill="#e0e7ff" stroke="{INK}" stroke-width="8"/>'
    b += f'<path d="M -10,-86 L 8,-30 L -18,6 L 14,40 L -4,88 M 8,-30 L 40,-12 M -18,6 L -50,20" fill="none" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/></g>'
    b += caption("THE MAZEVERSE IS SAFE… FOR NOW.", 30, 28, 30)
    return panel(b, "Sunset group pose of all five Maze Guardians in front of a giant sun, while a cracked mirror glints in the corner", defs)


# ----------------------------------------------------------------- cover, banner, map, brand


def cover():
    W, H = 1200, 1800
    b = rays(W, H, 600, 820, "#7c3aed", "#6d28d9", 30) + f'<rect width="{W}" height="{H}" fill="url(#dots)"/>'
    b += maze_floor(W, H, 1250, "#2e1065", "#22d3ee")
    b += place(robo_beast(True, True), 230, 900, 0.62)
    b += place(yeti("grumpy", "up", True), 980, 890, 0.62)
    b += place(serpent("cheeky", True), 760, 560, 0.5)
    b += f'<rect x="0" y="0" width="{W}" height="380" fill="{INK}" opacity="0.55"/>'
    b += words("SUPER ZAYD'S", 96, 600, 150, fill="#fde047", sw=18, tracking=2)
    b += words("MAZE GUARDIANS", 112, 600, 290, fill="#ffffff", sw=20, tracking=2)
    b += place(dragoncrest(0, "happy", (0.2, 0)), 330, 1500, 1.0)
    b += place(arrowlight(), 940, 1500, 0.95, flip=True)
    b += place(zigzag(True, ("out", "point")), 330, 1700, 0.72)
    b += place(bubbleguard(False, ("hip", "up")), 900, 1700, 0.82)
    b += place(zayd(("hip", "up"), ("wide", "wide"), (0, -0.2)), 600, 1720, 1.55)
    b += burst(1060, 470, 110, 80, "#facc15", 14, 8, 30)
    b += words("#1", 92, 1060, 502, fill="#ef4444", sw=14)
    b += f'<rect x="0" y="{H - 90}" width="{W}" height="90" fill="#facc15" stroke="{INK}" stroke-width="10"/>'
    b += words("THE GREAT MAZE SCRAMBLE", 56, 600, H - 26, fill=INK, stroke=None, font=BOLD_I, tracking=2)
    b += frame(W, H, 20)
    return svg(W, H, b, "Issue 1 cover: the five Maze Guardians in front, with Grumblejaw, Blizzardbyte and Splashfang looming behind them")


def banner():
    W, H = 1600, 800
    defs = '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1e1b4b"/><stop offset="1" stop-color="#7c3aed"/></linearGradient>'
    b = f'<rect width="{W}" height="{H}" fill="url(#sky)"/>' + stars(W, H, 90, 13, 420)
    b += maze_floor(W, H, 560, "#2e1065", "#22d3ee")
    b += lighthouse(800, 600, 0.72)
    b += place(dragoncrest(0, "happy", (0.4, 0)), 360, 780, 0.8)
    b += place(arrowlight(), 1290, 770, 0.74, flip=True)
    b += place(bubbleguard(False, ("up", "hip")), 560, 790, 0.7)
    b += place(zigzag(True, ("out", "point")), 1050, 790, 0.7)
    b += place(zayd(("hip", "up"), ("wide", "wide"), (0, -0.2)), 800, 790, 0.95)
    return svg(W, H, b, "The five Maze Guardians line up in front of Lighthouse HQ on a glowing maze at night", defs)


def maze_map():
    W, H = 1200, 900
    b = f'<rect width="{W}" height="{H}" fill="#1e1b4b"/>'
    b += maze_walls(30, 30, 57.5, (20, 14), "#4c1d95", 7, 77)
    zones = [
        (300, 230, "#e0f2fe", "#0284c7", "FROST FIELDS"),
        (900, 230, "#e5e7eb", "#64748b", "RUSTBOLT JUNKYARD"),
        (300, 670, "#c4b5fd", "#2563eb", "SPLASH SEA"),
        (900, 670, "#fbcfe8", "#db2777", "NEON CITY"),
    ]
    for x, y, c1, c2, label in zones:
        b += f'<rect x="{x - 210}" y="{y - 150}" width="420" height="300" rx="40" fill="{c1}" stroke="{INK}" stroke-width="8"/>'
        b += f'<rect x="{x - 210}" y="{y - 150}" width="420" height="300" rx="40" fill="url(#dotsDark)"/>'
        b += words(label, 32, x, y + 126, fill=c2, sw=9)
    # zone icons
    b += f'<polygon points="{star_points(300, 210, 6, 70, 26, -math.pi / 2)}" fill="#ffffff" stroke="{INK}" stroke-width="6"/>'
    b += f'<circle cx="900" cy="210" r="62" fill="#9ca3af" stroke="{INK}" stroke-width="7"/><circle cx="900" cy="210" r="24" fill="#e5e7eb" stroke="{INK}" stroke-width="6"/>'
    b += "".join(f'<rect x="890" y="134" width="20" height="26" fill="#9ca3af" stroke="{INK}" stroke-width="5" transform="rotate({a} 900 210)"/>' for a in range(0, 360, 45))
    b += f'<path d="M 210,650 q 45,-60 90,0 t 90,0" fill="none" stroke="#1d4ed8" stroke-width="18" stroke-linecap="round"/><path d="M 210,600 q 45,-60 90,0 t 90,0" fill="none" stroke="#60a5fa" stroke-width="14" stroke-linecap="round"/>'
    b += "".join(f'<rect x="{x}" y="{620 - hgt}" width="44" height="{hgt}" fill="#a855f7" stroke="{INK}" stroke-width="5"/>' for x, hgt in ((820, 70), (868, 120), (916, 90), (964, 60)))
    b += f'<circle cx="600" cy="450" r="130" fill="#312e81" stroke="{INK}" stroke-width="8"/>'
    b += compass_core(600, 450, 0.55, glow=False)
    b += words("COMPASS CORE", 30, 600, 616, fill="#fde047", sw=8)
    b += frame(W, H, 16)
    return svg(W, H, b, "Map of the Mazeverse: four zones (Frost Fields, Rustbolt Junkyard, Splash Sea and Neon City) around the Compass Core")


def badge():
    W = H = 256
    b = (
        f'<rect x="8" y="8" width="240" height="240" rx="56" fill="#6d28d9" stroke="{INK}" stroke-width="14"/>'
        f'<rect x="40" y="40" width="176" height="176" rx="24" fill="none" stroke="#22d3ee" stroke-width="10" stroke-dasharray="120 26"/>'
        f'<path d="M 76,86 H 180 L 76,170 H 180" fill="none" stroke="{INK}" stroke-width="40" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M 76,86 H 180 L 76,170 H 180" fill="none" stroke="#facc15" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><title>Maze Guardians Z badge</title>{b}</svg>\n'


def social_card():
    W, H = 1200, 630
    b = rays(W, H, 900, 330, "#7c3aed", "#6d28d9", 26) + f'<rect width="{W}" height="{H}" fill="url(#dots)"/>'
    b += words("SUPER ZAYD'S", 64, 330, 170, fill="#fde047", sw=14)
    b += words("MAZE", 120, 330, 300, fill="#ffffff", sw=18)
    b += words("GUARDIANS", 96, 330, 410, fill="#ffffff", sw=16)
    b += caption("ISSUE #1 — READ FREE!", 120, 460, 34)
    b += place(dragoncrest(0, "happy", (-0.3, 0)), 1040, 640, 0.66)
    b += place(zayd(("hip", "up"), ("wide", "wide"), (-0.3, -0.2)), 830, 640, 0.95)
    b += frame(W, H, 16)
    return svg(W, H, b, "Super Zayd's Maze Guardians: Issue 1, read free")


PANELS = {
    "p01-lighthouse": p01_lighthouse,
    "p02-alarm": p02_alarm,
    "p06-maze-sight": p06_maze_sight,
    "p09-bubble-boing": p09_bubble,
    "p10-light-bridge": p10_bridge,
    "p11-core-restored": p11_restored,
    "p12-finale": p12_finale,
}


def main(out_dir: str) -> None:
    out = Path(out_dir)
    for sub in ("heroes", "villains", "panels", "brand"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    build_portraits(out)
    for slug, fn in PANELS.items():
        (out / "panels" / f"{slug}.svg").write_text(fn())
    (out / "panels" / "cover-issue-1.svg").write_text(cover())
    (out / "brand" / "banner.svg").write_text(banner())
    (out / "brand" / "mazeverse-map.svg").write_text(maze_map())
    (out / "brand" / "badge.svg").write_text(badge())
    card = out / "brand" / "social-card.svg"
    card.write_text(social_card())
    try:
        subprocess.run(["rsvg-convert", "-w", "1200", "-o", str(out / "brand" / "social-card.png"), str(card)], check=True)
        card.unlink()
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("rsvg-convert not found: kept social-card.svg; convert it to PNG before publishing")
    print("art written to", out)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
