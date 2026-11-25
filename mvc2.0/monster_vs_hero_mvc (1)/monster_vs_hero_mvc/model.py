"""
MODEL
=====
Pure game state and logic. Knows nothing about rendering, assets,
sounds, or the screen.

Contains:
  - Player, Enemy, Particle, Reward entities (data + update logic only)
  - GameModel: the full game state with an `update(dt, keys)` method
  - plus a `consume_events()` hook that the View uses to detect what
    changed (so it can play sounds / spawn extra effects) without the
    Model ever depending on the View.

The controller calls model.update(); the view reads the model to draw.
Any other model that exposes the same public attributes
(player, enemies, hero_bullets, enemy_bullets, rewards, particles,
level, max_level, kills, kills_required, monsters_left_to_spawn,
state, ...) and the same methods (reset/pause/resume/update/
consume_events) can be driven by the same Controller and View,
producing a different game without rewriting either of them.
"""

import math
import random
import pygame


# ============================================================
# CONFIGURATION (shared constants)
# ============================================================

WIDTH, HEIGHT = 1280, 720
# Playfield is the whole window MINUS the right-side info panel.
# Keeping the playfield in the model lets us reuse the same view panel
# across multiple games without overlap.
PANEL_WIDTH = 280
PLAYFIELD_W = WIDTH - PANEL_WIDTH
PLAYFIELD_H = HEIGHT

FPS = 60
MAX_LEVEL = 5

# Weapon stats only - NO image references here (those live in the view).
WEAPONS = {
    1: {"name": "Normal", "damage": 20, "speed": 570, "cooldown": 0.28, "count": 1},
    2: {"name": "Rapid",  "damage": 9,  "speed": 650, "cooldown": 0.10, "count": 1},
    3: {"name": "Spread", "damage": 14, "speed": 500, "cooldown": 0.34, "count": 3},
}


# ============================================================
# ENTITIES (model layer - state + logic, no drawing)
# ============================================================

class Player:
    def __init__(self):
        self.radius = 22
        self.speed = 330
        self.max_hp = 100
        self.hp = self.max_hp
        self.score = 0

        self.pos = pygame.Vector2(PLAYFIELD_W / 2, HEIGHT - 105)

        # Initial shooting direction: upward.
        self.direction = pygame.Vector2(0, -1)

        self.weapon_id = 1
        self.shoot_timer = 0
        self.rapid_timer = 0
        self.damage_timer = 0

    def move(self, keys, dt):
        movement = pygame.Vector2(0, 0)

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            movement.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            movement.y += 1
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            movement.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            movement.x += 1

        if movement.length_squared() > 0:
            movement = movement.normalize()
            self.direction = movement

        self.pos += movement * self.speed * dt
        self.pos.x = max(self.radius, min(PLAYFIELD_W - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(HEIGHT - self.radius, self.pos.y))

    def shoot(self, dt, bullets, events):
        self.shoot_timer += dt

        weapon = WEAPONS[self.weapon_id]
        cooldown = weapon["cooldown"]

        # Rapid-fire pickup halves the cooldown for a few seconds.
        if self.rapid_timer > 0:
            cooldown *= 0.42

        if self.shoot_timer < cooldown:
            return

        self.shoot_timer = 0

        count = weapon["count"]
        for i in range(count):
            angle = (i - (count - 1) / 2) * 0.17
            direction = self.direction.rotate_rad(angle)
            bullets.append({
                "pos": self.pos + self.direction * self.radius,
                "velocity": direction * weapon["speed"],
                "damage": weapon["damage"],
                "radius": 7,
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


class Enemy:
    def __init__(self, level, boss=False):
        self.boss = boss
        self.radius = 43 if boss else 23

        self.max_hp = (350 + level * 90) if boss else (35 + level * 15)
        self.hp = self.max_hp

        self.speed = (55 + level * 5) if boss else (
            random.randint(55, 95) + level * 7
        )

        self.damage = 15
        self.shoot_timer = random.uniform(0.3, 1.2)
        self.shoot_interval = 0.62 if boss else max(
            0.55, 1.45 - level * 0.12
        )
        self.touch_cooldown = 0

        # Spawn at the top of the arena.
        self.pos = pygame.Vector2(
            random.randint(80, PLAYFIELD_W - 80),
            random.randint(75, 190)
        )

    def update(self, player, bullets, dt, level):
        direction = player.pos - self.pos
        distance = direction.length()

        if distance > 0:
            direction = direction.normalize()
            self.pos += direction * self.speed * dt

            # Boss sways sideways for a more dynamic feel.
            if self.boss:
                self.pos.x += math.sin(
                    pygame.time.get_ticks() / 400
                ) * 35 * dt

        # Keep enemies inside the playfield.
        self.pos.x = max(self.radius, min(PLAYFIELD_W - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(HEIGHT - self.radius, self.pos.y))

        self.shoot_timer += dt
        self.touch_cooldown = max(0, self.touch_cooldown - dt)

        if self.shoot_timer >= self.shoot_interval:
            direction = player.pos - self.pos
            if direction.length_squared():
                direction = direction.normalize()

            if self.boss:
                # Boss fires a 3-shot spread.
                for spread in (-0.25, 0, 0.25):
                    velocity = direction.rotate_rad(spread) * 220
                    bullets.append({
                        "pos": self.pos.copy(),
                        "velocity": velocity,
                        "damage": 12,
                        "radius": 8,
                        "owner": "monster",
                    })
            else:
                bullets.append({
                    "pos": self.pos.copy(),
                    "velocity": direction * (190 + self.speed),
                    "damage": 10,
                    "radius": 8,
                    "owner": "monster",
                })

            self.shoot_timer = 0


class Particle:
    def __init__(self, pos, color):
        self.pos = pygame.Vector2(pos)

        angle = random.random() * math.tau
        speed = random.uniform(50, 260)
        self.vel = pygame.Vector2(
            math.cos(angle), math.sin(angle)
        ) * speed

        self.life = random.uniform(0.25, 0.7)
        self.max_life = self.life
        self.color = color
        self.radius = random.randint(2, 5)

    def update(self, dt):
        self.pos += self.vel * dt
        self.vel *= max(0, 1 - 2.2 * dt)
        self.life -= dt


class Reward:
    def __init__(self, position):
        self.pos = position.copy()
        self.reward_type = random.choices(
            ["health", "score", "rapid"],
            weights=[3, 4, 3]
        )[0]
        self.radius = 19
        self.phase = random.random() * math.tau

    def update(self, dt):
        # Float up and down gently.
        self.phase += dt * 3

    def collect(self, player):
        if self.reward_type == "health":
            player.hp = min(player.max_hp, player.hp + 25)
        elif self.reward_type == "score":
            player.score += 100
        else:
            player.rapid_timer = 6


# ============================================================
# GAME MODEL - the central state container
# ============================================================

# NOTE: particle colors are stored as game data here because the model
# decides which color explosion to spawn for each event (kill, hit, pickup).
# This is a pragmatic exception to strict MVC; the view still renders them.
EXPLOSION_COLORS_KILL = [(35, 220, 255), (255, 45, 190), (255, 190, 45)]
EXPLOSION_COLORS_HIT = [(255, 55, 95)]
EXPLOSION_COLORS_REWARD = [(50, 255, 150)]


class GameModel:
    """All game state + logic. The view reads this; the controller updates it."""

    # Friendly name shown in the info panel. Subclasses override this.
    title = "MONSTER VS HERO"
    # Weapon table - exposed so the view can show the correct name without
    # knowing which game is running.
    WEAPONS = WEAPONS

    def __init__(self):
        self.player = Player()
        self.enemies = []
        self.hero_bullets = []
        self.enemy_bullets = []
        self.rewards = []
        self.particles = []

        self.level = 1
        self.max_level = MAX_LEVEL
        self.kills = 0
        self.kills_required = 0
        self.monsters_left_to_spawn = 0
        self.spawn_timer = 0
        self.wave_started = False
        self.state = "menu"

        # Event queue - the view drains this each frame to fire sounds
        # and other view-only reactions. Pure strings; model has no
        # audio knowledge.
        self._events = []

    # --------------------------------------------------------
    # Events (View-only side channel - never mutates state)
    # --------------------------------------------------------

    def consume_events(self):
        """Return and clear the list of events that happened this frame."""
        if not self._events:
            return []
        ev = self._events
        self._events = []
        return ev

    # --------------------------------------------------------
    # State transitions (called by the controller)
    # --------------------------------------------------------

    def reset(self):
        self.player = Player()
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
        self.enemy_bullets.clear()

        if self.level == self.max_level:
            # Boss only on the last level.
            self.monsters_left_to_spawn = 1
        else:
            self.monsters_left_to_spawn = 3 + self.level * 2

        self.spawn_timer = -1.2
        self.wave_started = False
        self.kills = 0
        self.kills_required = self.monsters_left_to_spawn

    # --------------------------------------------------------
    # Internal helpers
    # --------------------------------------------------------

    def _create_explosion(self, pos, count, colors):
        for _ in range(count):
            self.particles.append(Particle(pos, random.choice(colors)))

    def _spawn_enemies(self, dt):
        if not self.wave_started:
            self.wave_started = True

        if self.monsters_left_to_spawn > 0:
            self.spawn_timer += dt
            interval = max(0.35, 1.15 - self.level * 0.1)

            if self.spawn_timer >= interval:
                is_boss = (
                    self.level == self.max_level
                    and self.monsters_left_to_spawn == 1
                )
                self.enemies.append(Enemy(self.level, is_boss))
                self.monsters_left_to_spawn -= 1
                self.spawn_timer = 0

    def _handle_collisions(self):
        # Player bullets hit monsters.
        for bullet in self.hero_bullets[:]:
            pos = bullet["pos"]

            if pos.x < -30 or pos.x > PLAYFIELD_W + 30 or pos.y < -40 or pos.y > HEIGHT + 40:
                self.hero_bullets.remove(bullet)
                continue

            for enemy in self.enemies[:]:
                if pos.distance_to(enemy.pos) < bullet["radius"] + enemy.radius:
                    enemy.hp -= bullet["damage"]

                    if bullet in self.hero_bullets:
                        self.hero_bullets.remove(bullet)

                    self.player.score += 10
                    self._events.append("hit")

                    if enemy.hp <= 0:
                        self.player.score += (
                            300 if enemy.boss else 100 * self.level
                        )

                        self._create_explosion(
                            enemy.pos,
                            28 if enemy.boss else 14,
                            EXPLOSION_COLORS_KILL
                        )

                        if random.random() < 0.65 or enemy.boss:
                            self.rewards.append(Reward(enemy.pos))

                        self.enemies.remove(enemy)
                        self.kills += 1
                        self._events.append("boss_dead" if enemy.boss else "kill")

                    break

        # Enemy bullets hit the player.
        for bullet in self.enemy_bullets[:]:
            pos = bullet["pos"]

            if pos.x < -30 or pos.x > PLAYFIELD_W + 30 or pos.y < -40 or pos.y > HEIGHT + 40:
                self.enemy_bullets.remove(bullet)
                continue

            if pos.distance_to(self.player.pos) < (
                self.player.radius + bullet["radius"]
            ):
                self.player.take_damage(bullet["damage"])
                self.enemy_bullets.remove(bullet)
                self._create_explosion(
                    self.player.pos, 7, EXPLOSION_COLORS_HIT
                )
                self._events.append("player_hit")

        # Monsters collide with the player (cooldown + knockback).
        for enemy in self.enemies:
            if (
                enemy.pos.distance_to(self.player.pos)
                < enemy.radius + self.player.radius
                and enemy.touch_cooldown <= 0
            ):
                self.player.take_damage(enemy.damage)
                enemy.touch_cooldown = 1.0

                knockback = enemy.pos - self.player.pos
                if knockback.length_squared():
                    enemy.pos += knockback.normalize() * 35
                else:
                    enemy.pos += pygame.Vector2(0, -35)

                self._events.append("player_hit")

        # Player collects rewards.
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
    # Main update entry point (called by controller every frame)
    # --------------------------------------------------------

    def update(self, dt, keys):
        if self.state != "playing":
            return

        # Player movement and timers.
        self.player.move(keys, dt)
        self.player.update_timers(dt)

        # Hold SPACE to shoot.
        if keys[pygame.K_SPACE]:
            self.player.shoot(dt, self.hero_bullets, self._events)

        # Spawn enemies over time.
        self._spawn_enemies(dt)

        # Update enemies.
        for enemy in self.enemies:
            enemy.update(self.player, self.enemy_bullets, dt, self.level)

        # Update rewards (for floating animation).
        for reward in self.rewards:
            reward.update(dt)

        # Update particles.
        for particle in self.particles[:]:
            particle.update(dt)
            if particle.life <= 0:
                self.particles.remove(particle)

        # Move bullets.
        for bullet in self.hero_bullets:
            bullet["pos"] += bullet["velocity"] * dt
        for bullet in self.enemy_bullets:
            bullet["pos"] += bullet["velocity"] * dt

        # Collisions.
        prev_level = self.level
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

        # Game over.
        if self.player.hp <= 0 and self.state == "playing":
            self.state = "game_over"
            self._events.append("gameover")
