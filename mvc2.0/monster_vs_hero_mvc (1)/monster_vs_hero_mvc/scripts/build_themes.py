"""
build_themes.py
===============
Populates assets/themes/<name>/... from the original Monster vs Hero art.

- default: 1:1 copy of the original art (the project's baseline look).
- neon:    dark gradient background, hue-shifted glowing sprites.
- retro:   green-tinted pixel-art look with a starfield background.

Run from the project root:
    python scripts/build_themes.py
"""

import os
import math
import shutil
from PIL import Image, ImageFilter, ImageDraw

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------

HERE        = os.path.dirname(os.path.abspath(__file__))
PROJECT     = os.path.dirname(HERE)
SRC         = "/home/z/my-project/upload/extracted/monstervshero mvc/assets"
THEMES      = os.path.join(PROJECT, "assets", "themes")

ORIG = {
    "backgrounds/background.png": "background.png",
    "players/player.png":         "player.png",
    "monsters/monster.png":       "monster.png",
    "monsters/boss.png":          "boss.png",
    "bullets/bullet_hero.png":    "bullet_hero.png",
    "bullets/bullet_monster.png": "bullet_monster.png",
    "rewards/reward_health.png":  "reward_health.png",
    "rewards/reward_score.png":   "reward_score.png",
    "rewards/reward_rapid.png":   "reward_rapid.png",
}


def copy_default():
    theme = os.path.join(THEMES, "default")
    for dst_rel, src_name in ORIG.items():
        shutil.copyfile(
            os.path.join(SRC, src_name),
            os.path.join(theme, dst_rel),
        )
    print(f"[default] copied {len(ORIG)} assets")


# ------------------------------------------------------------------
# Color helpers
# ------------------------------------------------------------------

def hsv_to_rgb(h, s, v):
    """h in degrees, s/v in [0,1]. Returns (r,g,b) ints."""
    h = (h % 360) / 60.0
    i = int(h)
    f = h - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    if i == 0:   r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else:        r, g, b = v, p, q
    return int(r * 255), int(g * 255), int(b * 255)


def rgb_to_hsv(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r, g, b), min(r, g, b)
    df = mx - mn
    if df == 0:    h = 0
    elif mx == r:  h = (60 * ((g - b) / df) % 360)
    elif mx == g:  h = (60 * ((b - r) / df + 2))
    else:          h = (60 * ((r - g) / df + 4))
    s = 0 if mx == 0 else df / mx
    return h, s, mx


def shift_hue(img, deg):
    """Rotate hue of every non-transparent pixel by `deg` degrees."""
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            H, S, V = rgb_to_hsv(r, g, b)
            H = (H + deg) % 360
            r2, g2, b2 = hsv_to_rgb(H, S, V)
            px[x, y] = (r2, g2, b2, a)
    return img


def recolor_brightness(img, factor):
    """Multiply every non-transparent pixel's RGB by `factor` (clamped)."""
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            px[x, y] = (
                min(255, int(r * factor)),
                min(255, int(g * factor)),
                min(255, int(b * factor)),
                a,
            )
    return img


# ------------------------------------------------------------------
# Neon theme: dark gradient bg + hue-shifted glowing sprites
# ------------------------------------------------------------------

def make_neon_background(w, h):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / h
        # Deep purple at the top to near-black at the bottom.
        r = int(35 + (1 - t) * 30)
        g = int(10 + (1 - t) * 8)
        b = int(60 + (1 - t) * 35)
        for x in range(w):
            px[x, y] = (r, g, b)
    # Add a faint grid for the synthwave vibe.
    draw = ImageDraw.Draw(img)
    for x in range(0, w, 80):
        draw.line([(x, 0), (x, h)], fill=(45, 18, 80), width=1)
    for y in range(0, h, 80):
        draw.line([(0, y), (w, y)], fill=(45, 18, 80), width=1)
    return img


def build_neon():
    theme = os.path.join(THEMES, "neon")
    # Custom background.
    make_neon_background(1280, 720).save(
        os.path.join(theme, "backgrounds", "background.png")
    )
    # Hue-shifted glowing sprites. Different shift per family so the
    # neon theme still tells player/monster/bullet apart at a glance.
    shifts = {
        "players/player.png":         180,  # cyan
        "monsters/monster.png":       300,  # magenta
        "monsters/boss.png":           90,  # lime
        "bullets/bullet_hero.png":    180,
        "bullets/bullet_monster.png": 300,
        "rewards/reward_health.png":    0,  # keep red cross
        "rewards/reward_score.png":   180,
        "rewards/reward_rapid.png":    60,  # yellow-orange
    }
    for dst_rel, src_name in ORIG.items():
        if dst_rel == "backgrounds/background.png":
            continue
        img = Image.open(os.path.join(SRC, src_name))
        deg = shifts.get(dst_rel, 0)
        if deg:
            img = shift_hue(img, deg)
        # Soft glow: blur a bright copy and composite underneath.
        glow = img.filter(ImageFilter.GaussianBlur(3))
        glow = recolor_brightness(glow, 1.8)
        out = Image.new("RGBA", img.size, (0, 0, 0, 0))
        out.alpha_composite(glow)
        out.alpha_composite(img)
        out.save(os.path.join(theme, dst_rel))
    print("[neon] built")


# ------------------------------------------------------------------
# Retro theme: starfield bg + green-tinted pixel-art sprites
# ------------------------------------------------------------------

def make_retro_background(w, h):
    import random as _r
    rng = _r.Random(7)
    img = Image.new("RGB", (w, h), (5, 18, 8))  # very dark green
    px = img.load()
    # Sparse starfield.
    for _ in range(220):
        x, y = rng.randint(0, w - 1), rng.randint(0, h - 1)
        c = rng.choice([(80, 200, 120), (140, 220, 160), (50, 140, 80)])
        px[x, y] = c
    # Subtle CRT scanlines.
    for y in range(0, h, 4):
        for x in range(w):
            r, g, b = px[x, y]
            px[x, y] = (r // 2, g // 2, b // 2)
    return img


def build_retro():
    theme = os.path.join(THEMES, "retro")
    make_retro_background(1280, 720).save(
        os.path.join(theme, "backgrounds", "background.png")
    )
    # Green monochrome tint: map every pixel's brightness to a green ramp.
    ramp = [(int(20 + i * 0.9), int(60 + i * 0.7), int(30 + i * 0.4))
            for i in range(256)]
    for dst_rel, src_name in ORIG.items():
        if dst_rel == "backgrounds/background.png":
            continue
        img = Image.open(os.path.join(SRC, src_name)).convert("RGBA")
        px = img.load()
        w, h = img.size
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if a == 0:
                    continue
                # Use max channel as the brightness index.
                lum = max(r, g, b)
                gr, gg, gb = ramp[lum]
                px[x, y] = (gr, gg, gb, a)
        img.save(os.path.join(theme, dst_rel))
    print("[retro] built")


# ------------------------------------------------------------------

def write_theme_json(name, palette):
    """Write a small theme.json so the view can pick up theme-specific
    UI colors (background of the info panel, accent color, etc.)."""
    import json
    path = os.path.join(THEMES, name, "theme.json")
    with open(path, "w") as f:
        json.dump({
            "name": name,
            "palette": palette,
        }, f, indent=2)


if __name__ == "__main__":
    copy_default()
    build_neon()
    build_retro()

    write_theme_json("default", {
        "panel_bg":     [10, 20, 45, 210],
        "panel_border": [90, 170, 220],
        "text":         [230, 245, 255],
        "accent":       [255, 220, 40],
        "health":       [50, 255, 150],
        "danger":       [255, 55, 95],
        "info":         [35, 220, 255],
    })
    write_theme_json("neon", {
        "panel_bg":     [15, 5, 40, 220],
        "panel_border": [255, 45, 190],
        "text":         [220, 240, 255],
        "accent":       [35, 220, 255],
        "health":       [50, 255, 200],
        "danger":       [255, 70, 130],
        "info":         [255, 100, 220],
    })
    write_theme_json("retro", {
        "panel_bg":     [5, 18, 8, 220],
        "panel_border": [80, 200, 120],
        "text":         [140, 220, 160],
        "accent":       [200, 255, 120],
        "health":       [80, 255, 140],
        "danger":       [255, 120, 80],
        "info":         [120, 220, 180],
    })

    print("All themes built in:", THEMES)
