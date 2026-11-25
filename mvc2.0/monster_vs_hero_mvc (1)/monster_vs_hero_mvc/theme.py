"""
THEME
=====
Loads every visual asset + UI color palette from a single theme folder.
The view talks to ThemeManager only - it never imports images by name.

Folder layout (one theme = one folder under assets/themes/<name>/):

    assets/themes/<name>/
        theme.json                <-- palette + meta
        backgrounds/background.png
        players/player.png
        monsters/monster.png
        monsters/boss.png
        bullets/bullet_hero.png
        bullets/bullet_monster.png
        rewards/reward_health.png
        rewards/reward_score.png
        rewards/reward_rapid.png

To swap the look of the game you only need to:
  - drop another folder next to default/neon/retro, OR
  - pass --theme <name> on the command line, OR
  - call ThemeManager(theme_name).load(pygame_display) at runtime.

No game-logic code (model.py, controller.py) needs to change.
"""

import os
import json
import pygame


# Default palette - used if a theme.json is missing or partial.
DEFAULT_PALETTE = {
    "panel_bg":     [10, 20, 45, 210],
    "panel_border": [90, 170, 220],
    "text":         [230, 245, 255],
    "accent":       [255, 220, 40],
    "health":       [50, 255, 150],
    "danger":       [255, 55, 95],
    "info":         [35, 220, 255],
}


def themes_dir():
    """Absolute path to assets/themes/ inside the project."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "assets", "themes")


def list_themes():
    """Return the names of every theme folder shipped with the project."""
    base = themes_dir()
    if not os.path.isdir(base):
        return []
    return sorted(
        name for name in os.listdir(base)
        if os.path.isdir(os.path.join(base, name))
    )


class ThemeManager:
    """Owns all surfaces + colors for one visual theme."""

    # Logical asset name -> (subfolder, filename). Centralised so the
    # view never hard-codes paths.
    ASSET_MAP = {
        "background":      ("backgrounds", "background.png"),
        "player":          ("players",     "player.png"),
        "monster":         ("monsters",    "monster.png"),
        "boss":            ("monsters",    "boss.png"),
        "bullet_hero":     ("bullets",     "bullet_hero.png"),
        "bullet_monster":  ("bullets",     "bullet_monster.png"),
        "reward_health":   ("rewards",     "reward_health.png"),
        "reward_score":    ("rewards",     "reward_score.png"),
        "reward_rapid":    ("rewards",     "reward_rapid.png"),
    }

    def __init__(self, name="default"):
        self.name = name
        self.path = os.path.join(themes_dir(), name)
        if not os.path.isdir(self.path):
            raise FileNotFoundError(
                f"Theme '{name}' not found under {themes_dir()}. "
                f"Available: {list_themes()}"
            )
        self.palette = dict(DEFAULT_PALETTE)
        self.images = {}
        self._load_palette()

    # ------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------

    def _load_palette(self):
        meta_path = os.path.join(self.path, "theme.json")
        if not os.path.isfile(meta_path):
            return
        with open(meta_path) as f:
            data = json.load(f)
        for key, value in data.get("palette", {}).items():
            self.palette[key] = value

    def load(self, target_sizes=None):
        """Load every image into VRAM-friendly surfaces.

        target_sizes: optional dict mapping logical asset name ->
        (w, h). If omitted, original sizes are kept (except the
        background, which is scaled to the screen inside the view).
        """
        target_sizes = target_sizes or {}
        for logical, (sub, fname) in self.ASSET_MAP.items():
            path = os.path.join(self.path, sub, fname)
            if not os.path.isfile(path):
                raise FileNotFoundError(
                    f"Theme '{self.name}' is missing asset: {sub}/{fname}"
                )
            surf = pygame.image.load(path).convert_alpha()
            if logical in target_sizes:
                w, h = target_sizes[logical]
                surf = pygame.transform.smoothscale(surf, (w, h))
            self.images[logical] = surf
        return self

    # ------------------------------------------------------------
    # Access
    # ------------------------------------------------------------

    def image(self, logical_name):
        return self.images[logical_name]

    def color(self, key):
        return tuple(self.palette.get(key, DEFAULT_PALETTE.get(key)))

    def __repr__(self):
        return f"<ThemeManager '{self.name}' ({len(self.images)} images)>"
