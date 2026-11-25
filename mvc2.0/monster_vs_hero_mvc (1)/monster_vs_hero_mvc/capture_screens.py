"""
capture_screens.py
------------------
Render one screenshot per (game, theme) combination so we can
visually verify the layout, info panel, and theme differences.
Headless: SDL dummy driver, no audio.
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
from model_space_defender import SpaceDefenderModel

OUT = os.path.join(HERE, "screenshots")
os.makedirs(OUT, exist_ok=True)

GAMES = {"monster": GameModel, "space": SpaceDefenderModel}


def fake_keys():
    pressed = {pygame.K_RIGHT: True, pygame.K_SPACE: True}

    class _Keys:
        def __getitem__(self, k):
            return pressed.get(k, False)

    return _Keys()


def capture(game_name, theme_name, frames=180):
    pygame.init()
    try:
        model = GAMES[game_name]()
        view = GameView(theme_name=theme_name, enable_sound=False)
        model.reset()
        keys = fake_keys()
        for _ in range(frames):
            pygame.event.pump()
            model.update(1 / 60, keys)
            view.draw(model)
        # Save the final frame.
        path = os.path.join(OUT, f"{game_name}_{theme_name}.png")
        pygame.image.save(view.screen, path)
        print(f"  saved {path}")
    finally:
        pygame.quit()


def main():
    print("Capturing screenshots...")
    for game_name in GAMES:
        for theme_name in list_themes():
            capture(game_name, theme_name)
    # Also capture the menu state for each game.
    pygame.init()
    try:
        for game_name in GAMES:
            model = GAMES[game_name]()
            view = GameView(theme_name="default", enable_sound=False)
            # Don't call reset() - stay in menu state.
            view.draw(model)
            path = os.path.join(OUT, f"{game_name}_menu.png")
            pygame.image.save(view.screen, path)
            print(f"  saved {path}")
            pygame.quit()
            pygame.init()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
