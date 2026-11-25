"""
MAIN
====
Entry point. Initializes pygame, builds the model/view/controller,
and starts the controller's main loop.

  Model      -> GameModel      / SpaceDefenderModel (game state + logic)
  View       -> GameView       (screen, fonts, theme, sounds, rendering)
  Controller -> GameController (input + main loop)

Run:
    python main.py                                  # Monster vs Hero, default theme
    python main.py --game monster --theme default
    python main.py --game space   --theme neon
    python main.py --list-themes
    python main.py --no-sound

The same View and Controller drive BOTH games - only the Model changes.
"""

import argparse

import pygame

from model import GameModel
from model_space_defender import SpaceDefenderModel
from view import GameView
from controller import GameController
from theme import list_themes


GAMES = {
    "monster": GameModel,
    "space":   SpaceDefenderModel,
}


def parse_args():
    p = argparse.ArgumentParser(description="Monster vs Hero - MVC edition.")
    p.add_argument(
        "--game", choices=sorted(GAMES.keys()), default="monster",
        help="which Model to use (Controller and View are reused)",
    )
    p.add_argument(
        "--theme", default="default",
        help="visual theme folder under assets/themes/",
    )
    p.add_argument(
        "--no-sound", action="store_true",
        help="disable the audio mixer",
    )
    p.add_argument(
        "--list-themes", action="store_true",
        help="print available themes and exit",
    )
    return p.parse_args()


def main():
    args = parse_args()

    if args.list_themes:
        print("Available themes:")
        for name in list_themes():
            print(f"  - {name}")
        return

    pygame.init()
    pygame.display.set_mode((1, 1))  # needed before mixer init on some platforms

    model = GAMES[args.game]()
    view = GameView(theme_name=args.theme, enable_sound=not args.no_sound)
    controller = GameController(model, view)
    controller.run()


if __name__ == "__main__":
    main()
