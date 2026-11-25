"""
CONTROLLER
==========
Owns the main loop and input handling. Bridges the model and the view.

The controller:
  - reads keyboard/mouse input,
  - translates it into model actions (reset / pause / switch weapon / etc.),
  - asks the model to update itself with the current frame's input,
  - asks the view to draw the model.

The controller contains NO game rules and NO rendering code. It works
with ANY model that exposes the standard interface
(state, player, reset, pause, resume, update) and ANY view that
exposes draw(model) + sounds.toggle_mute().
"""

import pygame

from model import FPS


class GameController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.clock = pygame.time.Clock()
        self.running = True

    # --------------------------------------------------------
    # Input -> model actions
    # --------------------------------------------------------

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                if self.model.state == "playing":
                    self.model.pause()
                elif self.model.state == "paused":
                    self.model.resume()
                else:
                    self.running = False

            elif event.key == pygame.K_RETURN:
                if self.model.state in ("menu", "game_over", "victory"):
                    self.model.reset()
                elif self.model.state == "paused":
                    self.model.resume()

            elif event.key == pygame.K_r and self.model.state in (
                "game_over", "victory"
            ):
                self.model.reset()

            elif event.key == pygame.K_m:
                # Global mute toggle handled by the view's sound manager.
                if hasattr(self.view, "sounds"):
                    self.view.sounds.toggle_mute()

            elif event.key == pygame.K_t:
                # Live theme switching. Works in every state (menu,
                # playing, paused, game_over, victory) because it only
                # touches the view - the model is untouched.
                if hasattr(self.view, "cycle_theme"):
                    shift = bool(event.mod & pygame.KMOD_SHIFT)
                    self.view.cycle_theme(direction=-1 if shift else +1)

            elif self.model.state == "playing":
                # Weapon switching - generic: pass any 1..9 through to
                # the model via set_weapon if it implements it; otherwise
                # set weapon_id directly (Monster vs Hero style).
                if pygame.K_1 <= event.key <= pygame.K_9:
                    wid = event.key - pygame.K_0
                    if hasattr(self.model, "set_weapon"):
                        self.model.set_weapon(wid)
                    else:
                        if hasattr(self.model.player, "weapon_id"):
                            self.model.player.weapon_id = wid

    # --------------------------------------------------------
    # Main loop
    # --------------------------------------------------------

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000, 0.04)

            self._handle_events()

            keys = pygame.key.get_pressed()
            self.model.update(dt, keys)

            self.view.draw(self.model)

        pygame.quit()
