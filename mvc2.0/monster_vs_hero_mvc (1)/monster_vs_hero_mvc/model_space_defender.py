"""
MODEL: SPACE DEFENDER (optional second game)
============================================
A different game that REUSES the existing View and Controller without
any change to either file. This demonstrates the payoff of MVC:
- Controller is generic (drives any model with the standard interface).
- View is generic (renders any model whose entities expose the
  expected attributes - pos/radius/hp/etc.).
- Only the Model changes -> new game.

Differences from Monster vs Hero:
  - Player is a fixed turret at the bottom that always shoots upward.
  - Enemies are asteroids that fall straight down and split when hit.
  - Three weapons behave differently (laser, dual cannon, plasma bomb).
  - No boss; instead the last level is a meteor storm.

Run it with:
    python main.py --game space
"""

import math
import random
import pygame

from model import (
    WIDTH, HEIGHT, PLAYFIELD_W, PANEL_WIDTH, FPS, MAX_LEVEL,
    EXPLOSION_COLORS_KILL, EXPLOSION_COLORS_HIT, EXPLOSION_COLORS_REWARD,
    Particle,
)


WEAPONS_SPACE = {
    1: {"name": "Laser",  "damage": 18, "speed": 720, "cooldown": 0.20, "count": 1},
    2: {"name": "Dual",   "damage": 11, "speed": 600, "cooldown": 0.18, "count": 2},
    3: {"name": "Plasma", "damage": 26, "speed": 420, "cooldown": 0.42, "count": 1},
}


class SpacePlayer:
    """Turret-style player. Always points up; moves only horizontally."""

    def __init__(self):
        self.radius = 22
        self.speed = 380
        self.max_hp = 100
        self.hp = self.max_hp
        self.score = 0
        self.pos = pygame.Vector2(PLAYFIELD_W / 2, HEIGHT - 95)
        self.direction = pygame.Vector2(0, -1)
        self.weapon_id = 1
        self.shoot_timer = 0
        self.rapid_timer = 0
        self.damage_timer = 0

    def move(self, keys, dt):
        mv = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            mv.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            mv.x += 1
        # Vertical nudge for tactical repositioning.
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            mv.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            mv.y += 1
        if mv.length_squared() > 0:
            mv = mv.normalize()
        self.pos += mv * self.speed * dt
        self.pos.x = max(self.radius, min(PLAYFIELD_W - self.radius, self.pos.x))
        self.pos.y = max(HEIGHT - 250, min(HEIGHT - self.radius, self.pos.y))
        # Always faces up so the hero sprite looks correct.
        self.direction = pygame.Vector2(0, -1)

    def shoot(self, dt, bullets, events):
        self.shoot_timer += dt
        weapon = WEAPONS_SPACE[self.weapon_id]
        cooldown = weapon["cooldown"] * (0.5 if self.rapid_timer > 0 else 1.0)
        if self.shoot_timer < cooldown:
            return
        self.shoot_timer = 0
        count = weapon["count"]
        for i in range(count):
            offset_x = (i - (count - 1) / 2) * 18
            bullets.append({
                "pos": self.pos + pygame.Vector2(offset_x, -self.radius),
                "velocity": pygame.Vector2(0, -1) * weapon["speed"],
                "damage": weapon["damage"],
                "radius": 8,
                "owner": "hero",
            })
        events.append("shoot")

    def take_damage(self, amount):
        if self.damage_timer <= 0:
            self.hp = max(0, self.hp - amount)
            self.damage_timer = 0.6

    def update_timers(self, dt):
        self.damage_timer = max(0, self.damage_timer - dt)
        self.rapid_timer = max(0, self.rapid_timer - dt)


class Asteroid:
    """Falling asteroid. Larger ones split into two smaller ones."""

    SIZES = {"large": 36, "medium": 24, "small": 15}

    def __init__(self, level, size="large", pos=None):
        self.size = size
        self.radius = self.SIZES[size]
        self.boss = False  # so the view uses the regular monster sprite

        self.max_hp = {
            "large":  60 + level * 18,
            "medium": 30 + level * 10,
            "small":  15 + level * 5,
        }[size]
        self.hp = self.max_hp

        self.speed = random.uniform(70, 130) + level * 8
        self.damage = 18 if size == "large" else 12
        self.touch_cooldown = 0
        self.shoot_timer = 0
        self.shoot_interval = 999   # asteroids don't shoot

        self.pos = pos.copy() if pos else pygame.Vector2(
            random.randint(60, PLAYFIELD_W - 60),
            -self.radius
        )
        # Slight horizontal drift.
        self._vx = random.uniform(-30, 30)
        # Rotation phase for visual flavor (the view draws us as the
        # monster sprite but we still want motion to feel alive).
        self.phase = random.random() * math.tau

    def update(self, player, bullets, dt, level):
        self.pos.y += self.speed * dt
        self.pos.x += self._vx * dt
        # Bounce off the side walls.
        if self.pos.x < self.radius:
            self.pos.x = self.radius
            self._vx *= -1
        if self.pos.x > PLAYFIELD_W - self.radius:
            self.pos.x = PLAYFIELD_W - self.radius
            self._vx *= -1
        self.phase += dt * 2
        self.touch_cooldown = max(0, self.touch_cooldown - dt)


class Meteor(Particle):
    """Tiny cosmetic meteor particle - reuses Particle rendering."""
    pass


class SpaceReward:
    """Same shape as Monster vs Hero's Reward - so the view can render it."""

    TYPES = ["health", "score", "rapid"]

    def __init__(self, position):
        self.pos = position.copy()
        self.reward_type = random.choices(
            self.TYPES, weights=[3, 4, 3]
        )[0]
        self.radius = 19
        self.phase = random.random() * math.tau

    def update(self, dt):
        self.phase += dt * 3
        self.pos.y += 35 * dt   # slowly drifts down

    def collect(self, player):
        if self.reward_type == "health":
            player.hp = min(player.max_hp, player.hp + 25)
        elif self.reward_type == "score":
            player.score += 100
        else:
            player.rapid_timer = 6


class SpaceDefenderModel:
    """Falling-asteroids defence. Same public interface as GameModel."""

    title = "SPACE DEFENDER"
    max_level = MAX_LEVEL
    WEAPONS = WEAPONS_SPACE

    def __init__(self):
        self.player = SpacePlayer()
        self.enemies = []
        self.hero_bullets = []
        self.enemy_bullets = []   # unused but kept for view compatibility
        self.rewards = []
        self.particles = []

        self.level = 1
        self.kills = 0
        self.kills_required = 0
        self.monsters_left_to_spawn = 0
        self.spawn_timer = 0
        self.wave_started = False
        self.state = "menu"
        self._events = []

    # --------------------------------------------------------
    # Weapon selection (called by the generic controller)
    # --------------------------------------------------------

    def set_weapon(self, wid):
        if wid in WEAPONS_SPACE:
            self.player.weapon_id = wid

    # --------------------------------------------------------
    # Events
    # --------------------------------------------------------

    def consume_events(self):
        if not self._events:
            return []
        ev = self._events
        self._events = []
        return ev

    # --------------------------------------------------------
    # State transitions
    # --------------------------------------------------------

    def reset(self):
        self.player = SpacePlayer()
        self.enemies.clear()
        self.hero_bullets.clear()
        self.enemy_bullets.clear()
        self.rewards.clear()
        self.particles.clear()
        self.level = 1
        self.kills = 0
        self.state = "playing"
        self.setup_level()
        self._events.append("start")

    def pause(self):
        if self.state == "playing":
            self.state = "paused"
            self._events.append("pause")

    def resume(self):
        if self.state == "paused":
            self.state = "playing"
            self._events.append("resume")

    def setup_level(self):
        self.enemies.clear()
        self.hero_bullets.clear()
        # Last level = meteor storm: many small fast asteroids.
        if self.level == self.max_level:
            self.monsters_left_to_spawn = 14
        else:
            self.monsters_left_to_spawn = 4 + self.level * 2
        self.spawn_timer = -0.8
        self.wave_started = False
        self.kills = 0
        self.kills_required = self.monsters_left_to_spawn

    # --------------------------------------------------------
    # Internal helpers
    # --------------------------------------------------------

    def _create_explosion(self, pos, count, colors):
        for _ in range(count):
            self.particles.append(Particle(pos, random.choice(colors)))

    def _spawn_asteroids(self, dt):
        if not self.wave_started:
            self.wave_started = True
        if self.monsters_left_to_spawn <= 0:
            return
        self.spawn_timer += dt
        interval = max(0.30, 1.0 - self.level * 0.10)
        if self.spawn_timer >= interval:
            # Last level: all small. Otherwise: weighted by size.
            if self.level == self.max_level:
                size = "small"
            else:
                size = random.choices(
                    ["large", "medium", "small"],
                    weights=[3, 3, 2]
                )[0]
            self.enemies.append(Asteroid(self.level, size))
            self.monsters_left_to_spawn -= 1
            self.spawn_timer = 0

    def _handle_collisions(self):
        # Hero bullets hit asteroids.
        for bullet in self.hero_bullets[:]:
            pos = bullet["pos"]
            if pos.y < -40 or pos.x < -30 or pos.x > PLAYFIELD_W + 30:
                self.hero_bullets.remove(bullet)
                continue
            for asteroid in self.enemies[:]:
                if pos.distance_to(asteroid.pos) < (
                    bullet["radius"] + asteroid.radius
                ):
                    asteroid.hp -= bullet["damage"]
                    if bullet in self.hero_bullets:
                        self.hero_bullets.remove(bullet)
                    self.player.score += 5
                    self._events.append("hit")

                    if asteroid.hp <= 0:
                        self.player.score += 80
                        self._create_explosion(
                            asteroid.pos, 12, EXPLOSION_COLORS_KILL
                        )
                        # Large -> 2 medium, medium -> 2 small.
                        if asteroid.size == "large":
                            for _ in range(2):
                                self.enemies.append(Asteroid(
                                    self.level, "medium", asteroid.pos
                                ))
                        elif asteroid.size == "medium":
                            for _ in range(2):
                                self.enemies.append(Asteroid(
                                    self.level, "small", asteroid.pos
                                ))
                        if random.random() < 0.35:
                            self.rewards.append(SpaceReward(asteroid.pos))
                        self.enemies.remove(asteroid)
                        self.kills += 1
                        self._events.append("kill")
                    break

        # Asteroids hit the player.
        for asteroid in self.enemies:
            if (
                asteroid.pos.distance_to(self.player.pos)
                < asteroid.radius + self.player.radius
                and asteroid.touch_cooldown <= 0
            ):
                self.player.take_damage(asteroid.damage)
                asteroid.touch_cooldown = 1.0
                self._create_explosion(
                    self.player.pos, 8, EXPLOSION_COLORS_HIT
                )
                self._events.append("player_hit")

        # Rewards picked up.
        for reward in self.rewards[:]:
            if reward.pos.distance_to(self.player.pos) < (
                self.player.radius + reward.radius
            ):
                reward.collect(self.player)
                self.rewards.remove(reward)
                self._create_explosion(
                    self.player.pos, 10, EXPLOSION_COLORS_REWARD
                )
                self._events.append("pickup")

    # --------------------------------------------------------
    # Main update
    # --------------------------------------------------------

    def update(self, dt, keys):
        if self.state != "playing":
            return

        self.player.move(keys, dt)
        self.player.update_timers(dt)

        if keys[pygame.K_SPACE]:
            self.player.shoot(dt, self.hero_bullets, self._events)

        self._spawn_asteroids(dt)

        for enemy in self.enemies:
            enemy.update(self.player, self.enemy_bullets, dt, self.level)

        # Remove asteroids that fell off the bottom.
        for enemy in self.enemies[:]:
            if enemy.pos.y > HEIGHT + 60:
                self.enemies.remove(enemy)

        for reward in self.rewards:
            reward.update(dt)

        for particle in self.particles[:]:
            particle.update(dt)
            if particle.life <= 0:
                self.particles.remove(particle)

        for bullet in self.hero_bullets:
            bullet["pos"] += bullet["velocity"] * dt

        self._handle_collisions()

        # Level progression.
        if (
            self.wave_started
            and not self.enemies
            and self.monsters_left_to_spawn == 0
        ):
            if self.level < self.max_level:
                self.level += 1
                self.setup_level()
                self._events.append("levelup")
            else:
                self.state = "victory"
                self._events.append("victory")

        if self.player.hp <= 0 and self.state == "playing":
            self.state = "game_over"
            self._events.append("gameover")
