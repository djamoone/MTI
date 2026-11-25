# Monster vs Hero - MVC Edition

A top-down arena shooter refactored into strict **Model - View - Controller**,
with **themeable assets**, **procedurally generated sound effects**, a
**dedicated information panel**, and a **second game** that reuses the same
View and Controller without any changes to either file.

```
                       +-----------------+
   keyboard / mouse -->|   Controller    |---update(dt, keys)--+
                       |  (input + loop) |                     |
                       +-----------------+                     |
                            |   ^                               |
                       view |   | model                         v
                            v   |                          +----------+
                       +-----------+                      |   Model  |
                       |   View    |<--- read state -----| (game    |
                       | (render + |                     |  logic)  |
                       |  sounds + |                     +----------+
                       |  theme)   |
                       +-----------+
                            |
                            v
                       screen + speakers
```

The Controller never renders and never decides game rules. The View never
mutates state. The Model never imports pygame images, fonts, or sounds.
This is what lets us plug in a completely different game (Space Defender)
just by swapping the Model.

---

## Project layout

```
monster_vs_hero_mvc/
├── main.py                     # Entry point. Parses --game / --theme / --no-sound.
├── controller.py               # Generic input handler + main loop.
├── view.py                     # Renders any compatible Model + draws the info panel.
├── model.py                    # Monster vs Hero game state + logic.
├── model_space_defender.py     # SECOND game - reuses View + Controller as-is.
├── theme.py                    # Loads every image + palette from a theme folder.
├── sound.py                    # Loads WAVs and plays them. Mute-aware.
├── smoke_test.py               # Headless test that runs every game x theme combo.
├── capture_screens.py          # Saves a screenshot of each combo for visual QA.
├── scripts/
│   ├── build_themes.py         # Regenerates the default/neon/retro theme folders.
│   └── build_sounds.py         # Regenerates the WAV files in assets/sounds/.
├── screenshots/                # Sample renders of each combo.
└── assets/
    ├── themes/
    │   ├── default/            # 1:1 copy of the original Monster vs Hero art.
    │   │   ├── theme.json      # Palette: panel bg, accent, health, danger, etc.
    │   │   ├── backgrounds/background.png
    │   │   ├── players/player.png
    │   │   ├── monsters/{monster.png, boss.png}
    │   │   ├── bullets/{bullet_hero.png, bullet_monster.png}
    │   │   └── rewards/{reward_health.png, reward_score.png, reward_rapid.png}
    │   ├── neon/               # Synthwave palette + hue-shifted glowing sprites.
    │   └── retro/              # Green CRT phosphor look.
    └── sounds/
        ├── shoot.wav  hit.wav  explosion.wav  pickup.wav
        ├── levelup.wav  gameover.wav  victory.wav  menu_select.wav
```

---

## Requirement coverage

| Requirement (from the brief) | Where it is implemented |
| --- | --- |
| **Separate resources into independent folders: player images, monsters, bullets, backgrounds, sounds.** | `assets/themes/<theme>/{backgrounds,players,monsters,bullets,rewards}/` and `assets/sounds/`. See `theme.py:ThemeManager.ASSET_MAP`. |
| **Player / monster / bullet images can be changed without modifying behavior code.** | Drop new PNGs into the corresponding subfolder of any theme. The Model and Controller never reference image files - only the View does, through the ThemeManager. |
| **Background and visual appearance can be changed independently of game logic.** | Switch theme with `--theme neon` or `--theme retro`. No `.py` file edit needed. The Model is unaware that themes exist. |
| **Information panel showing score, health, and game status.** | `view.py:GameView._draw_info_panel`. Right-hand 280 px panel: TITLE, STATUS, SCORE, HEALTH bar+number, LEVEL, ENEMIES left, WEAPON, SOUND state, PROGRESS bar, CONTROLS. |
| **Rendering separated from game logic and input handling.** | `model.py` (logic) / `view.py` (rendering) / `controller.py` (input). No file imports another's internals. |
| **MVC architecture.** | Same three files. The Controller calls `model.update(dt, keys)` then `view.draw(model)`. |
| **Optional: reuse View and Controller with a different Model.** | `model_space_defender.py` defines `SpaceDefenderModel`, a falling-asteroids defence game. `main.py --game space` runs it with the same View + Controller used by Monster vs Hero. |

---

## Running

```bash
# Requires Python 3.10+ and pygame-ce (or vanilla pygame >= 2.1).
pip install pygame-ce

# Monster vs Hero (default theme, sound on)
python main.py

# Pick game + theme explicitly
python main.py --game monster --theme default
python main.py --game monster --theme neon
python main.py --game monster --theme retro
python main.py --game space   --theme neon

# List available themes
python main.py --list-themes

# Headless server or no audio device
python main.py --no-sound
```

### In-game controls

| Key | Action |
| --- | --- |
| Arrows / WASD | Move |
| SPACE | Shoot (hold) |
| 1 / 2 / 3 | Switch weapon |
| **T / Shift+T** | **Cycle to next / previous theme (live, no restart)** |
| ESC | Pause / resume / quit |
| M | Mute / unmute |
| R | Restart (after game over or victory) |
| ENTER | Start / restart / resume |

---

## How the theme system works

A **theme** is just a folder under `assets/themes/`. The ThemeManager
(`theme.py`) reads `theme.json` for the UI palette and walks a fixed
asset map to load every sprite.

To **add a new theme**:
1. Copy `assets/themes/default/` to `assets/themes/mytheme/`.
2. Replace any images you want to change. Keep the same filenames and
   logical subfolders (`backgrounds/`, `players/`, etc.).
3. Edit `mytheme/theme.json` to override any palette colors
   (`panel_bg`, `accent`, `health`, `danger`, `info`, ...).
4. Run `python main.py --theme mytheme`.

**No `.py` file needs to be touched.** The Model and Controller don't
know themes exist; the View only talks to `ThemeManager`.

The default / neon / retro themes that ship with the project are
(regenerable) outputs of `scripts/build_themes.py`:
- `default` is a 1:1 copy of the original game art.
- `neon` rotates hues and adds a soft glow + synthwave gradient.
- `retro` monochromes everything to a green CRT-phosphor ramp.

### Switching theme at runtime

You don't have to quit and relaunch to try a different look. While the
game is running (in any state - menu, playing, paused, game over, or
victory), press:

- **T** - cycle to the next theme (alphabetical, wraps around)
- **Shift+T** - cycle to the previous theme

The View's `set_theme(name)` / `cycle_theme(direction)` methods rebuild
the `ThemeManager` and reload every sprite + the palette from disk,
then the next `view.draw(model)` call paints the screen with the new
look. The **Model is never touched** - your score, health, level,
enemy positions, bullets in flight, etc. all stay exactly where they
were. The current theme name is shown in the info panel (THEME row)
and a small `menu_select` click is played on each switch so you get
audio feedback even when looking away.

This is the cleanest demonstration of MVC separation in the project:
changing the entire visual appearance is a View-only operation that
the Model and Controller don't even know happened.

---

## How the sound system works

Sound effects are procedurally synthesised WAVs in `assets/sounds/`
(regenerated by `scripts/build_sounds.py`). The SoundManager
(`sound.py`) loads them at startup and is **mute-aware**.

Crucially, the **Model knows nothing about audio**. Instead, the Model
publishes a small list of event strings ("shoot", "hit", "kill",
"pickup", "levelup", "gameover", "victory", "pause", "resume", ...)
through `model.consume_events()`. The View drains this queue each frame
and maps each event to a sound name. This keeps the Model pure while
still letting the audio react to gameplay.

To add a new sound:
1. Drop `mysound.wav` into `assets/sounds/`.
2. Add an entry to `SOUND_MAP` in `sound.py` (`"mysound": "mysound.wav"`).
3. Add an event name to the Model's `self._events` list at the right
   moment (e.g. `self._events.append("mysound")`).
4. Map it in `view.py:GameView._event_sound_map`.

---

## Adding a new game that reuses View + Controller

The View and Controller are written against a small **model interface**,
not against `GameModel` specifically. Any class that exposes:

| Attribute / method | Type / signature | Used for |
| --- | --- | --- |
| `title` | `str` | Panel + overlay title |
| `state` | `"menu" \| "playing" \| "paused" \| "game_over" \| "victory"` | Status display + overlay |
| `player` | object with `pos`, `direction`, `hp`, `max_hp`, `score`, `weapon_id`, `rapid_timer` | HUD + rendering |
| `enemies` | list of objects with `pos`, `radius`, `hp`, `max_hp`, `boss` | Rendering + panel |
| `hero_bullets`, `enemy_bullets` | lists of dicts with `pos`, `velocity`, `owner`, `radius` | Rendering |
| `rewards` | list of objects with `pos`, `phase`, `reward_type` | Rendering |
| `particles` | list of objects with `pos`, `life`, `max_life`, `radius`, `color` | Rendering |
| `level`, `max_level`, `kills`, `kills_required`, `monsters_left_to_spawn` | `int` | Panel |
| `WEAPONS` | `dict[int, {"name": str, ...}]` | Panel weapon name |
| `reset()`, `pause()`, `resume()` | methods | State transitions |
| `update(dt, keys)` | method | Per-frame logic |
| `consume_events() -> list[str]` | method | Sound + view-side reactions |

...can be dropped into `main.py:GAMES` and immediately runs with the
existing View and Controller. `model_space_defender.py` is a working
example: a different movement model (turret-style), different enemies
(asteroids that split when shot), different weapons (Laser / Dual /
Plasma), different progression (last level = meteor storm) - and zero
changes to `view.py` or `controller.py`.

To add your own:
1. Create `model_mygame.py` with a class that satisfies the interface
   above. Reuse `Particle`, the explosion color constants, etc. from
   `model.py`.
2. Register it in `main.py:GAMES = {"monster": GameModel, "space": SpaceDefenderModel, "mygame": MyGameModel}`.
3. Run `python main.py --game mygame`.

---

## Regenerating assets

```bash
# Rebuild every theme folder from the original art in upload/.
python scripts/build_themes.py

# Rebuild every WAV from scratch (numpy only - no external samples).
python scripts/build_sounds.py
```

---

## Headless testing

```bash
# Runs ~10 s of each (game, theme) combo under SDL's dummy driver.
python smoke_test.py

# Saves one screenshot per combo into screenshots/.
python capture_screens.py
```

The smoke test sets `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy`,
so it runs on CI / headless servers without a display or sound card.
