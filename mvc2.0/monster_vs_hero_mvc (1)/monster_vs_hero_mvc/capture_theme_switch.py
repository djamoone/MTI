"""
capture_theme_switch.py
-----------------------
Demonstrates the live theme switch: starts a game, advances ~3s,
then captures three screenshots of the SAME model state with each
of the three themes applied. Proves that switching theme at runtime
doesn't disturb the gameplay state.
"""

import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"]  = "dummy"

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pygame
from theme import list_themes
from view import GameView
from model import GameModel

OUT = os.path.join(HERE, "screenshots")
os.makedirs(OUT, exist_ok=True)


def fake_keys():
    pressed = {pygame.K_RIGHT: True, pygame.K_SPACE: True}

    class _Keys:
        def __getitem__(self, k):
            return pressed.get(k, False)
    return _Keys()


def main():
    pygame.init()
    try:
        model = GameModel()
        view = GameView(theme_name="default", enable_sound=False)
        model.reset()
        keys = fake_keys()
        # Advance gameplay a bit so we have enemies + bullets on screen.
        for _ in range(180):
            pygame.event.pump()
            model.update(1 / 60, keys)
            view.draw(model)
        # Now switch themes and capture the SAME state in each.
        for theme_name in list_themes():
            view.set_theme(theme_name)
            view.draw(model)   # redraw with new theme
            path = os.path.join(OUT, f"theme_demo_{theme_name}.png")
            pygame.image.save(view.screen, path)
            print(f"  saved {path}")
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
