"""
VIEW
====
Owns the screen, fonts, all images, and the rendering loop.
The view never mutates the model. It reads model attributes,
draws sprites, blits the information panel, and emits sounds
via the SoundManager by diffing the model's event queue.

All visual assets come from the ThemeManager; swapping themes
does not require any change in this file. The view is also
reused as-is by a different model (e.g. SpaceDefenderModel)
as long as that model exposes the same public attributes.
"""

import math
import pygame

from model import WIDTH, HEIGHT, PLAYFIELD_W, PANEL_WIDTH, WEAPONS
from theme import ThemeManager
from sound import SoundManager


class GameView:
    """Owns the screen, fonts, theme, sounds. Renders model state."""

    # Layout constants for the right-hand info panel.
    PANEL_X = PLAYFIELD_W
    PANEL_W = PANEL_WIDTH
    PADDING = 14

    # Logical asset name -> on-screen size. Used both at startup and
    # whenever the user switches theme at runtime via set_theme().
    ASSET_SIZES = {
        "background":     (PLAYFIELD_W, HEIGHT),
        "player":         (64, 82),
        "monster":        (54, 54),
        "boss":           (112, 96),
        "bullet_hero":    (16, 28),
        "bullet_monster": (16, 26),
        "reward_health":  (38, 38),
        "reward_score":   (38, 38),
        "reward_rapid":   (38, 38),
    }

    def __init__(self, theme_name="default", enable_sound=True):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Monster vs Hero")

        self.font         = pygame.font.SysFont("consolas", 18)
        self.font_bold    = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_big     = pygame.font.SysFont("consolas", 40, bold=True)
        self.font_title   = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_small   = pygame.font.SysFont("consolas", 14)
        self.font_panel_h = pygame.font.SysFont("consolas", 16, bold=True)

        # Theme + sounds are the ONLY things that know about external files.
        self.theme_name = theme_name
        self.theme = ThemeManager(theme_name).load(target_sizes=self.ASSET_SIZES)
        self.sounds = SoundManager(enabled=enable_sound)

        # Sound name -> model event name(s) that trigger it.
        self._event_sound_map = {
            "shoot":     "shoot",
            "hit":       "hit",
            "kill":      "explosion",
            "boss_dead": "explosion",
            "player_hit":"hit",
            "pickup":    "pickup",
            "levelup":   "levelup",
            "gameover":  "gameover",
            "victory":   "victory",
            "start":     "menu_select",
            "pause":     "menu_select",
            "resume":    "menu_select",
            "theme_switch": "menu_select",
        }

    # --------------------------------------------------------
    # Live theme switching
    # --------------------------------------------------------
    # The user can press T (next) or Shift+T (previous) at any time
    # during the game to swap every sprite and the UI palette without
    # restarting. Model state is untouched - only the view reloads.

    def set_theme(self, theme_name):
        """Reload all images + palette from a different theme folder."""
        from theme import list_themes
        available = list_themes()
        if theme_name not in available:
            print(f"[theme] '{theme_name}' not found; "
                  f"available: {available}")
            return False
        self.theme = ThemeManager(theme_name).load(
            target_sizes=self.ASSET_SIZES
        )
        self.theme_name = theme_name
        pygame.display.set_caption(
            f"Monster vs Hero - theme: {theme_name}"
        )
        self.sounds.play("menu_select")
        print(f"[theme] switched to '{theme_name}'")
        return True

    def cycle_theme(self, direction=1):
        """Switch to the next (direction=+1) or previous (direction=-1)
        theme in alphabetical order. Wraps around."""
        from theme import list_themes
        available = list_themes()
        if len(available) < 2:
            return
        try:
            idx = available.index(self.theme_name)
        except ValueError:
            idx = 0
        new_idx = (idx + direction) % len(available)
        self.set_theme(available[new_idx])

    # --------------------------------------------------------
    # Text + bar helpers
    # --------------------------------------------------------

    def _draw_text(self, text, x, y, color=None, font=None):
        if color is None:
            color = self.theme.color("text")
        if font is None:
            font = self.font
        image = font.render(str(text), True, color)
        self.screen.blit(image, (x, y))

    def _draw_bar(self, x, y, w, h, value, maximum, color):
        bg = (0, 0, 0, 180)
        bar_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(bar_surf, bg, (0, 0, w, h), border_radius=h // 2)
        self.screen.blit(bar_surf, (x, y))

        ratio = max(0, min(1, value / maximum)) if maximum else 0
        if ratio:
            pygame.draw.rect(
                self.screen, color,
                (x, y, int(w * ratio), h),
                border_radius=h // 2
            )
        pygame.draw.rect(
            self.screen, self.theme.color("panel_border"),
            (x, y, w, h), 1, border_radius=h // 2
        )

    # --------------------------------------------------------
    # Entity drawing
    # --------------------------------------------------------

    def _draw_player(self, player):
        angle = -math.degrees(
            math.atan2(player.direction.x, -player.direction.y)
        )
        rotated = pygame.transform.rotate(self.theme.image("player"), angle)
        rect = rotated.get_rect(
            center=(int(player.pos.x), int(player.pos.y))
        )
        self.screen.blit(rotated, rect)

    def _draw_enemy(self, enemy):
        image = self.theme.image("boss" if enemy.boss else "monster")
        rect = image.get_rect(
            center=(int(enemy.pos.x), int(enemy.pos.y))
        )
        self.screen.blit(image, rect)

        bar_width = 76 if enemy.boss else 48
        bar_color = self.theme.color("accent" if enemy.boss else "danger")
        # Clamp the health bar so it never spills past the left edge of
        # the playfield (it can when an enemy is hugging that wall).
        bar_x = int(enemy.pos.x - bar_width / 2)
        bar_x = max(2, min(bar_x, PLAYFIELD_W - bar_width - 2))
        self._draw_bar(
            bar_x,
            int(enemy.pos.y - enemy.radius - 15),
            bar_width, 6,
            enemy.hp, enemy.max_hp, bar_color
        )

    def _draw_reward(self, reward):
        y = reward.pos.y + math.sin(reward.phase) * 5
        image = self.theme.image(f"reward_{reward.reward_type}")
        rect = image.get_rect(center=(int(reward.pos.x), int(y)))
        self.screen.blit(image, rect)

    def _draw_bullet(self, bullet):
        if bullet["owner"] == "hero":
            image = self.theme.image("bullet_hero")
            rect = image.get_rect(
                center=(int(bullet["pos"].x), int(bullet["pos"].y))
            )
            self.screen.blit(image, rect)
        else:
            angle = -math.degrees(
                math.atan2(bullet["velocity"].x, -bullet["velocity"].y)
            )
            rotated = pygame.transform.rotate(
                self.theme.image("bullet_monster"), angle
            )
            rect = rotated.get_rect(
                center=(int(bullet["pos"].x), int(bullet["pos"].y))
            )
            self.screen.blit(rotated, rect)

    def _draw_particle(self, particle):
        if particle.life > 0:
            radius = max(
                1, int(particle.radius * particle.life / particle.max_life)
            )
            pygame.draw.circle(
                self.screen, particle.color,
                (int(particle.pos.x), int(particle.pos.y)),
                radius
            )

    # --------------------------------------------------------
    # Information panel (right side)
    # --------------------------------------------------------
    # The panel is the single place where score, health, status,
    # level, weapon, enemies remaining and controls are shown.
    # It reads only from the model and the theme, so the same panel
    # works for every game that follows the model interface.

    def _draw_info_panel(self, model):
        x = self.PANEL_X
        w = self.PANEL_W
        text_color = self.theme.color("text")
        accent     = self.theme.color("accent")
        info_color = self.theme.color("info")
        danger     = self.theme.color("danger")
        health_col = self.theme.color("health")

        # Panel background. We fill the panel area with an OPAQUE base
        # color first, then blit a semi-transparent overlay on top so
        # the playfield isn't visible through the panel AND no stale
        # text from a previous frame (e.g. after a live theme switch)
        # ghosts through the 82%-opaque overlay.
        bg = self.theme.color("panel_bg")
        base = (bg[0], bg[1], bg[2]) if len(bg) >= 3 else (10, 20, 45)
        pygame.draw.rect(self.screen, base, (x, 0, w, HEIGHT))
        overlay = pygame.Surface((w, HEIGHT), pygame.SRCALPHA)
        overlay.fill(bg)
        self.screen.blit(overlay, (x, 0))
        # Left border line.
        pygame.draw.line(
            self.screen, self.theme.color("panel_border"),
            (x, 0), (x, HEIGHT), 2
        )

        cx = x + self.PADDING
        cw = w - 2 * self.PADDING
        y = 14

        # --- Title block ---
        # Use a smaller title font so long names ("MONSTER VS HERO",
        # "SPACE DEFENDER") fit inside the 280px panel.
        self._draw_text(model.title, cx, y, accent, self.font_title)
        y += 30
        self._draw_text("INFO PANEL", cx, y, info_color, self.font_panel_h)
        y += 22

        # Separator.
        pygame.draw.line(
            self.screen, self.theme.color("panel_border"),
            (cx, y), (cx + cw, y), 1
        )
        y += 10

        # --- STATUS (menu / playing / paused / game_over / victory) ---
        status_label = {
            "menu":      ("MENU",      info_color),
            "playing":   ("PLAYING",   health_col),
            "paused":    ("PAUSED",    accent),
            "game_over": ("GAME OVER", danger),
            "victory":   ("VICTORY",   health_col),
        }.get(model.state, ("?", text_color))
        self._draw_text("STATUS", cx, y, text_color, self.font_small)
        y += 16
        self._draw_text(status_label[0], cx, y, status_label[1], self.font_bold)
        y += 30

        # --- SCORE ---
        self._draw_text("SCORE", cx, y, text_color, self.font_small)
        y += 16
        self._draw_text(
            f"{model.player.score:06d}", cx, y, accent, self.font_big
        )
        y += 46

        # --- HEALTH ---
        self._draw_text("HEALTH", cx, y, text_color, self.font_small)
        y += 16
        hp_ratio_color = health_col if model.player.hp > 35 else danger
        self._draw_bar(
            cx, y, cw, 18,
            model.player.hp, model.player.max_hp, hp_ratio_color
        )
        y += 22
        self._draw_text(
            f"{model.player.hp} / {model.player.max_hp} HP",
            cx, y, text_color, self.font
        )
        y += 28

        # --- LEVEL + ENEMIES LEFT ---
        self._draw_text("LEVEL", cx, y, text_color, self.font_small)
        self._draw_text("ENEMIES", cx + 140, y, text_color, self.font_small)
        y += 16
        self._draw_text(
            f"{model.level} / {model.max_level}",
            cx, y, info_color, self.font_bold
        )
        total_remaining = len(model.enemies) + model.monsters_left_to_spawn
        self._draw_text(
            f"{total_remaining}", cx + 140, y, info_color, self.font_bold
        )
        y += 30

        # --- WEAPON ---
        self._draw_text("WEAPON", cx, y, text_color, self.font_small)
        y += 16
        weapons_table = getattr(model, "WEAPONS", WEAPONS)
        weapon_name = weapons_table.get(
            model.player.weapon_id, {"name": "?"}
        )["name"]
        self._draw_text(weapon_name, cx, y, info_color, self.font_bold)
        y += 24

        if model.player.rapid_timer > 0:
            self._draw_text(
                f"RAPID: {model.player.rapid_timer:.1f}s",
                cx, y, self.theme.color("accent"), self.font_small
            )
            y += 18

        # --- SOUND + THEME STATE ---
        y += 6
        pygame.draw.line(
            self.screen, self.theme.color("panel_border"),
            (cx, y), (cx + cw, y), 1
        )
        y += 8
        snd_state = "MUTED" if self.sounds.muted else "ON"
        snd_color = danger if self.sounds.muted else health_col
        self._draw_text("SOUND", cx, y, text_color, self.font_small)
        self._draw_text(snd_state, cx + 140, y, snd_color, self.font_bold)
        y += 20
        # Current theme name + a hint that T cycles it.
        self._draw_text("THEME", cx, y, text_color, self.font_small)
        self._draw_text(
            self.theme_name, cx + 140, y, accent, self.font_bold
        )
        y += 20
        self._draw_text(
            "(T to switch, Shift+T back)",
            cx, y, info_color, self.font_small
        )
        y += 22

        # --- PROGRESS (kills / required + level bar) ---
        self._draw_text("PROGRESS", cx, y, text_color, self.font_small)
        y += 16
        kills_req = max(1, getattr(model, "kills_required", 0))
        self._draw_text(
            f"Kills: {model.kills} / {kills_req}",
            cx, y, info_color, self.font
        )
        y += 22
        # Level progress bar.
        self._draw_bar(
            cx, y, cw, 10,
            model.kills, kills_req, accent
        )
        y += 18

        # --- CONTROLS (bottom-anchored) ---
        controls = [
            "Move:    Arrows / WASD",
            "Shoot:   SPACE",
            "Weapon:  1 / 2 / 3",
            "Theme:   T / Shift+T",
            "Mute:    M",
            "Pause:   ESC",
            "Restart: R",
        ]
        y = HEIGHT - 18 * len(controls) - 20
        pygame.draw.line(
            self.screen, self.theme.color("panel_border"),
            (cx, y - 8), (cx + cw, y - 8), 1
        )
        self._draw_text("CONTROLS", cx, y - 26,
                        info_color, self.font_panel_h)
        for line in controls:
            self._draw_text(line, cx, y, text_color, self.font_small)
            y += 18

    # --------------------------------------------------------
    # Overlays for menu / pause / game over / victory
    # --------------------------------------------------------

    def _draw_overlay(self, model):
        overlay = pygame.Surface((PLAYFIELD_W, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if model.state == "menu":
            title, subtitle = model.title, "Press ENTER to start"
        elif model.state == "paused":
            title, subtitle = "PAUSED", "Press ENTER to resume"
        elif model.state == "game_over":
            title, subtitle = "GAME OVER", "Press ENTER or R to restart"
        else:  # victory
            title, subtitle = "YOU WIN!", "Press ENTER or R to play again"

        title_image = self.font_big.render(
            title, True, self.theme.color("accent")
        )
        self.screen.blit(
            title_image,
            (PLAYFIELD_W // 2 - title_image.get_width() // 2, 260)
        )
        subtitle_image = self.font.render(
            subtitle, True, self.theme.color("text")
        )
        self.screen.blit(
            subtitle_image,
            (PLAYFIELD_W // 2 - subtitle_image.get_width() // 2, 340)
        )
        self._draw_text(
            f"Score: {model.player.score}",
            PLAYFIELD_W // 2 - 60, 395
        )
        self._draw_text(
            "ESC: Pause / Quit",
            PLAYFIELD_W // 2 - 90, 440,
            self.theme.color("text"), self.font_small
        )

    # --------------------------------------------------------
    # Sound: drain the model's event queue and trigger audio
    # --------------------------------------------------------

    def _play_model_events(self, model):
        for ev in model.consume_events():
            snd = self._event_sound_map.get(ev)
            if snd:
                self.sounds.play(snd)

    # --------------------------------------------------------
    # Main draw entry point (called by controller every frame)
    # --------------------------------------------------------

    def draw(self, model):
        # Background is the size of the playfield only.
        self.screen.blit(self.theme.image("background"), (0, 0))

        # Animated scanline for the neon vibe.
        scan_y = pygame.time.get_ticks() // 18 % HEIGHT
        pygame.draw.line(
            self.screen, (20, 70, 120),
            (0, scan_y), (PLAYFIELD_W, scan_y), 1
        )

        for reward in model.rewards:
            self._draw_reward(reward)

        for bullet in model.hero_bullets + model.enemy_bullets:
            self._draw_bullet(bullet)

        for enemy in model.enemies:
            self._draw_enemy(enemy)

        for particle in model.particles:
            self._draw_particle(particle)

        self._draw_player(model.player)

        # Info panel always visible, even in menu state.
        self._draw_info_panel(model)

        if model.state != "playing":
            self._draw_overlay(model)

        # Pump sounds for events that happened during this frame's update.
        self._play_model_events(model)

        pygame.display.flip()
