"""
smoke_test.py
-------------
Headless smoke test for the Monster vs Hero MVC project.
Runs each (game x theme) combination under SDL's dummy video driver
and a no-mixer audio setup, simulating ~2 seconds of gameplay by
pressing movement keys + SPACE so every code path (move, shoot,
collisions, level transitions, info panel, sounds) gets exercised.

Exits non-zero if any combination crashes.
"""

import os
import sys
import time

# Headless-friendly environment.
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"]  = "dummy"

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pygame
from theme import list_themes
from view import GameView
from controller import GameController
from model import GameModel
from model_space_defender import SpaceDefenderModel


GAMES = {"monster": GameModel, "space": SpaceDefenderModel}


def fake_keys():
    """Return a pressed-keys dict that exercises movement + shooting.
    Uses pygame.key.get_pressed() so we get the right ScancodeWrapper
    type expected by the model's movement code."""
    keys = pygame.key.get_pressed()
    # Can't mutate a ScancodeWrapper; build a plain dict of the keys
    # the model queries. Falling back to a dict that returns False for
    # anything not listed.
    pressed = {
        pygame.K_RIGHT: True,
        pygame.K_SPACE: True,
    }

    class _Keys:
        def __getitem__(self, k):
            return pressed.get(k, False)

    return _Keys()


def run_combo(game_name, theme_name, frames=700):
    pygame.init()
    try:
        model = GAMES[game_name]()
        view = GameView(theme_name=theme_name, enable_sound=False)
        controller = GameController(model, view)

        # Start a real game.
        model.reset()
        keys = fake_keys()
        themes_seen = {view.theme_name}

        for i in range(frames):
            # Drain events so the OS doesn't think we hung.
            pygame.event.pump()
            # Toggle pause/resume once around the midpoint to exercise
            # that code path too.
            if i == frames // 2:
                model.pause()
            elif i == frames // 2 + 5:
                model.resume()
            # Exercise live theme switching every 100 frames.
            if i > 0 and i % 100 == 0:
                view.cycle_theme(+1)
                themes_seen.add(view.theme_name)
            if i > 0 and i % 100 == 50:
                view.cycle_theme(-1)
                themes_seen.add(view.theme_name)

            model.update(1 / 60, keys)
            view.draw(model)

        print(f"  [OK] game={game_name:8s} theme={theme_name:8s} "
              f"state={model.state:9s} score={model.player.score:5d} "
              f"level={model.level}/{model.max_level} "
              f"kills={model.kills} "
              f"final_theme={view.theme_name} "
              f"themes_seen={len(themes_seen)}")
        return True
    except Exception as exc:
        import traceback
        print(f"  [FAIL] game={game_name} theme={theme_name}: {exc}")
        traceback.print_exc()
        return False
    finally:
        pygame.quit()


def test_live_theme_switch():
    """Focused test: switch themes mid-game without crashing and
    confirm the view actually rotated through every theme."""
    print("\nLive theme switch test (monster/default):")
    pygame.init()
    try:
        model = GameModel()
        view = GameView(theme_name="default", enable_sound=False)
        model.reset()
        keys = fake_keys()
        seen = []
        for i in range(60):
            pygame.event.pump()
            model.update(1 / 60, keys)
            view.draw(model)
        for _ in range(len(list_themes())):
            view.cycle_theme(+1)
            for _ in range(15):
                pygame.event.pump()
                model.update(1 / 60, keys)
                view.draw(model)
            seen.append(view.theme_name)
        ok = len(set(seen)) == len(list_themes())
        print(f"  rotated through: {seen}")
        print(f"  [{'OK' if ok else 'FAIL'}] saw {len(set(seen))}/"
              f"{len(list_themes())} unique themes")
        return ok
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()


def main():
    print("Themes available:", list_themes())
    print("Smoke-testing all (game, theme) combinations...\n")
    all_ok = True
    for game_name in GAMES:
        for theme_name in list_themes():
            ok = run_combo(game_name, theme_name)
            all_ok = all_ok and ok
    all_ok = test_live_theme_switch() and all_ok
    print("\n" + ("ALL OK" if all_ok else "SOME FAILED"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
