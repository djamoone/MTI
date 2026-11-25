"""
SOUND
=====
Loads WAV files from assets/sounds/ and plays them on demand.
The view (not the model!) decides which sound to play by observing
what changed in the model between two frames, so the model stays
pure - it knows nothing about audio.

Mixer init is best-effort: if audio is unavailable (headless server,
dummy driver), the manager silently no-ops instead of crashing.
"""

import os
import pygame


def sounds_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "assets", "sounds")


# Logical sound name -> filename. Centralised so callers never hard-code paths.
SOUND_MAP = {
    "shoot":       "shoot.wav",
    "hit":         "hit.wav",
    "explosion":   "explosion.wav",
    "pickup":      "pickup.wav",
    "levelup":     "levelup.wav",
    "gameover":    "gameover.wav",
    "victory":     "victory.wav",
    "menu_select": "menu_select.wav",
}


class SoundManager:
    def __init__(self, enabled=True, volume=0.55):
        self.enabled = enabled
        self.volume = volume
        self.muted = False
        self.sounds = {}
        self._mixer_ok = False

        if not enabled:
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16,
                                  channels=1, buffer=256)
            self._mixer_ok = True
            self._load_all()
        except pygame.error as exc:
            # Audio is optional; the game still runs without it.
            print(f"[sound] mixer unavailable, running silent: {exc}")
            self._mixer_ok = False

    # ------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------

    def _load_all(self):
        base = sounds_dir()
        for logical, fname in SOUND_MAP.items():
            path = os.path.join(base, fname)
            if not os.path.isfile(path):
                continue
            try:
                snd = pygame.mixer.Sound(path)
                snd.set_volume(self.volume)
                self.sounds[logical] = snd
            except pygame.error as exc:
                print(f"[sound] could not load {fname}: {exc}")

    # ------------------------------------------------------------
    # Playback
    # ------------------------------------------------------------

    def play(self, name):
        if not self._mixer_ok or self.muted:
            return
        snd = self.sounds.get(name)
        if snd is not None:
            snd.play()

    def toggle_mute(self):
        self.muted = not self.muted
        if self.muted and self._mixer_ok:
            pygame.mixer.stop()
        return self.muted
