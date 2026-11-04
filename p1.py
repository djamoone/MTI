
import pygame
import random

pygame.init()
# ============================================================
# CONFIGURATION
# ============================================================

WIDTH = 1280
HEIGHT = 720
FPS = 60

BACKGROUND = (65, 15, 105)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 40, 40)
GREEN = (30, 200, 70)
ORANGE = (255, 100, 40)
YELLOW = (255, 215, 0)

WEAPONS = {
    1: {
        "name": "Normal",
        "damage": 10,
        "speed": 500,
        "cooldown": 0.25,
        "radius": 8,
        "color": (255, 255, 0),
    },
    2: {
        "name": "Rapid Fire",
        "damage": 5,
        "speed": 600,
        "cooldown": 0.10,
        "radius": 6,
        "color": (0, 255, 255),
    },
    3: {
        "name": "Power",
        "damage": 25,
        "speed": 350,
        "cooldown": 0.60,
        "radius": 12,
        "color": (255, 165, 0),
    },
}


# ============================================================
# WEAPON CLASS
# ============================================================

class Weapon:
    def __init__(self, weapon_id):
        self.weapon_id = weapon_id
        self.data = WEAPONS[weapon_id]

    @property
    def name(self):
        return self.data["name"]

    def create_bullet(self, position):
        return Bullet(
            position=position,
            velocity=pygame.Vector2(0, -self.data["speed"]),
            damage=self.data["damage"],
            radius=self.data["radius"],
            color=self.data["color"],
            owner="hero",
        )


# ============================================================
# BULLET CLASS
# ============================================================

class Bullet:
    def __init__(
        self, position, velocity, damage, radius, color, owner
    ):
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)
        self.damage = damage
        self.radius = radius
        self.color = color
        self.owner = owner
        self.alive = True

    def update(self, dt):
        self.position += self.velocity * dt

        if (
            self.position.x < -self.radius
            or self.position.x > WIDTH + self.radius
            or self.position.y < -self.radius
            or self.position.y > HEIGHT + self.radius
        ):
            self.alive = False

    def hits(self, position, target_radius):
        return (
            self.position.distance_to(position)
            < self.radius + target_radius
        )

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.position.x), int(self.position.y)),
            self.radius,
        )


# ============================================================
# HERO CLASS
# ============================================================

class Hero:
    def __init__(self):
        self.radius = 25
        self.speed = 300

        self.max_hp = 100
        self.hp = self.max_hp

        self.position = pygame.Vector2(640, 620)

        self.weapon = Weapon(1)
        self.shoot_timer = 0

    def move(self, keys, dt):
        direction = pygame.Vector2(0, 0)

        if keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_DOWN]:
            direction.y += 1
        if keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_RIGHT]:
            direction.x += 1

        # Normalize movement to prevent faster diagonal movement.
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.position += direction * self.speed * dt

        # Keep the hero inside the screen.
        self.position.x = max(
            self.radius,
            min(WIDTH - self.radius, self.position.x),
        )
        self.position.y = max(
            self.radius,
            min(HEIGHT - self.radius, self.position.y),
        )

    def update_shooting(self, dt, shooting):
        self.shoot_timer += dt

        # Shoot only while SPACE is held.
        if (
            shooting
            and self.shoot_timer >= self.weapon.data["cooldown"]
        ):
            self.shoot_timer = 0

            bullet_position = pygame.Vector2(
                self.position.x,
                self.position.y - self.radius,
            )

            return self.weapon.create_bullet(bullet_position)

        return None

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def change_weapon(self, weapon_id):
        if weapon_id in WEAPONS:
            self.weapon = Weapon(weapon_id)
            self.shoot_timer = 0

    def draw(self, screen):
        pygame.draw.circle(
            screen, RED, self.position, self.radius
        )
        pygame.draw.circle(
            screen, BLACK, self.position, self.radius, 3
        )


# ============================================================
# MONSTER CLASS
# ============================================================

class Monster:
    def __init__(self, level):
        self.radius = 50

        self.position = pygame.Vector2(
            random.randint(100, WIDTH - 100),
            random.randint(80, 250),
        )

        self.max_hp = 100 + (level - 1) * 50
        self.hp = self.max_hp

        self.speed = 55 + (level - 1) * 25
        self.shoot_timer = 0
        self.level = level

    def move_toward(self, target, dt):
        direction = target - self.position

        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.position += direction * self.speed * dt

    def shoot(self, target, dt):
        self.shoot_timer += dt

        cooldown = max(
            0.30, 0.80 - (self.level - 1) * 0.15
        )

        if self.shoot_timer < cooldown:
            return None

        self.shoot_timer = 0

        direction = target - self.position

        if direction.length_squared() == 0:
            direction = pygame.Vector2(0, 1)
        else:
            direction = direction.normalize()

        bullet_speed = 220 + (self.level - 1) * 40

        return Bullet(
            position=self.position,
            velocity=direction * bullet_speed,
            damage=10,
            radius=9,
            color=ORANGE,
            owner="monster",
        )

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def draw(self, screen):
        pygame.draw.circle(
            screen, GREEN, self.position, self.radius
        )
        pygame.draw.circle(
            screen, BLACK, self.position, self.radius, 4
        )

        # Monster eyes.
        pygame.draw.circle(
            screen,
            "red",
            (
                int(self.position.x - 17),
                int(self.position.y - 10),
            ),
            8,
        )
        pygame.draw.circle(
            screen,
            "red",
            (
                int(self.position.x + 17),
                int(self.position.y - 10),
            ),
            8,
        )

        # Monster mouth.
        pygame.draw.line(
            screen,
            BLACK,
            (
                int(self.position.x - 20),
                int(self.position.y + 20),
            ),
            (
                int(self.position.x + 20),
                int(self.position.y + 20),
            ),
            5,
        )


# ============================================================
# REWARD CLASS
# ============================================================

class Reward:
    def __init__(self, position):
        self.position = pygame.Vector2(position)
        self.reward_type = random.choice(["health", "score"])
        self.value = 25 if self.reward_type == "health" else 50
        self.radius = 18

    def collect(self, hero, game):
        if self.reward_type == "health":
            hero.heal(self.value)
        else:
            game.score += self.value

    def draw(self, screen, font):
        x = int(self.position.x)
        y = int(self.position.y)

        if self.reward_type == "health":
            color = (0, 255, 100)
            symbol = "+"
        else:
            color = YELLOW
            symbol = "$"

        pygame.draw.circle(
            screen, color, (x, y), self.radius
        )
        pygame.draw.circle(
            screen, WHITE, (x, y), self.radius, 2
        )

        image = font.render(symbol, True, BLACK)
        screen.blit(image, image.get_rect(center=(x, y)))


# ============================================================
# GAME CLASS
# ============================================================

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Monster vs Hero")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.big_font = pygame.font.SysFont(None, 64)

        self.running = True
        self.max_level = 3

        self.reset_game()

    def reset_game(self):
        self.hero = Hero()

        self.level = 1
        self.score = 0

        self.monster = Monster(self.level)

        self.hero_bullets = []
        self.monster_bullets = []
        self.rewards = []

        self.collision_timer = 0

        self.paused = False
        self.game_over = False
        self.victory = False

    def setup_next_level(self):
        self.hero_bullets.clear()
        self.monster_bullets.clear()

        self.level += 1
        self.monster = Monster(self.level)

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:

                # ESC pauses/resumes during gameplay.
                if event.key == pygame.K_ESCAPE:
                    if not self.game_over:
                        self.paused = not self.paused
                    else:
                        self.running = False

                elif event.key == pygame.K_q:
                    self.running = False

                elif event.key == pygame.K_r:
                    if self.game_over:
                        self.reset_game()

                # Weapon selection.
                elif not self.paused and not self.game_over:
                    if event.key == pygame.K_1:
                        self.hero.change_weapon(1)

                    elif event.key == pygame.K_2:
                        self.hero.change_weapon(2)

                    elif event.key == pygame.K_3:
                        self.hero.change_weapon(3)

    # --------------------------------------------------------
    # UPDATE GAME
    # --------------------------------------------------------

    def update(self, dt):
        # Freeze all gameplay while paused or game over.
        if self.paused or self.game_over:
            return

        keys = pygame.key.get_pressed()

        # ---------------- HERO MOVEMENT ----------------

        self.hero.move(keys, dt)

        # ---------------- HERO SHOOTING ----------------
        # Hold SPACE to shoot; release to stop.

        shooting = keys[pygame.K_SPACE]

        hero_bullet = self.hero.update_shooting(dt, shooting)

        if hero_bullet is not None:
            self.hero_bullets.append(hero_bullet)

        # ---------------- MONSTER MOVEMENT ----------------

        self.monster.move_toward(self.hero.position, dt)

        # ---------------- MONSTER SHOOTING ----------------

        monster_bullet = self.monster.shoot(
            self.hero.position, dt
        )

        if monster_bullet is not None:
            self.monster_bullets.append(monster_bullet)

        # ---------------- HERO BULLETS ----------------

        for bullet in self.hero_bullets:
            bullet.update(dt)

            if (
                bullet.alive
                and bullet.hits(
                    self.monster.position,
                    self.monster.radius,
                )
            ):
                self.monster.take_damage(bullet.damage)
                self.score += 10
                bullet.alive = False

        self.hero_bullets = [
            bullet for bullet in self.hero_bullets
            if bullet.alive
        ]

        # ---------------- MONSTER BULLETS ----------------

        for bullet in self.monster_bullets:
            bullet.update(dt)

            if (
                bullet.alive
                and bullet.hits(
                    self.hero.position,
                    self.hero.radius,
                )
            ):
                self.hero.take_damage(bullet.damage)
                bullet.alive = False

        self.monster_bullets = [
            bullet for bullet in self.monster_bullets
            if bullet.alive
        ]

        # ---------------- PHYSICAL COLLISION ----------------

        self.collision_timer = max(
            0, self.collision_timer - dt
        )

        distance = self.monster.position.distance_to(
            self.hero.position
        )

        if (
            distance < self.monster.radius + self.hero.radius
            and self.collision_timer <= 0
        ):
            self.hero.take_damage(10)
            self.collision_timer = 0.7

        # ---------------- MONSTER DEFEATED ----------------

        if self.monster.hp <= 0:
            # Create a reward at the defeated monster's position.
            self.rewards.append(Reward(self.monster.position))

            if self.level < self.max_level:
                self.setup_next_level()
            else:
                self.victory = True
                self.game_over = True

        # ---------------- COLLECT REWARDS ----------------

        for reward in self.rewards[:]:
            if (
                reward.position.distance_to(self.hero.position)
                < self.hero.radius + reward.radius
            ):
                reward.collect(self.hero, self)
                self.rewards.remove(reward)

        # ---------------- HERO DEFEATED ----------------

        if self.hero.hp <= 0:
            self.game_over = True
            self.victory = False

    # --------------------------------------------------------
    # DRAWING HELPERS
    # --------------------------------------------------------

    def draw_text(
        self, text, x, y, color=WHITE, big=False
    ):
        selected_font = self.big_font if big else self.font
        image = selected_font.render(text, True, color)
        self.screen.blit(image, (x, y))

    def draw_health_bar(
        self, x, y, width, height, hp, max_hp, color
    ):
        pygame.draw.rect(
            self.screen, BLACK, (x, y, width, height)
        )

        ratio = max(0, min(1, hp / max_hp))
        fill_width = int((width - 4) * ratio)

        pygame.draw.rect(
            self.screen,
            color,
            (x + 2, y + 2, fill_width, height - 4),
        )

    def draw_hud(self):
        # Hero health.
        self.draw_health_bar(
            20, 20, 204, 24,
            self.hero.hp, self.hero.max_hp, RED
        )

        self.draw_text(
            f"Hero HP: {self.hero.hp}", 20, 50
        )

        # Monster health.
        self.draw_health_bar(
            900, 20, 204, 24,
            self.monster.hp, self.monster.max_hp, GREEN
        )

        self.draw_text(
            f"Monster HP: {max(0, self.monster.hp)}",
            900, 50
        )

        # Score and level.
        self.draw_text(f"Score: {self.score}", 550, 20)

        self.draw_text(
            f"Level: {self.level}/{self.max_level}",
            550, 55
        )

        # Controls.
        self.draw_text(
            f"Weapon: {self.hero.weapon.name}", 20, 100
        )
        self.draw_text("Move: Arrow Keys", 20, 140)
        self.draw_text("Shoot: Hold SPACE", 20, 175)
        self.draw_text("Weapons: 1 / 2 / 3", 20, 210)
        self.draw_text("ESC: Pause / Resume", 20, 245)

    def draw_overlay(self, title, color, lines):
        overlay = pygame.Surface(
            (WIDTH, HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 175))
        self.screen.blit(overlay, (0, 0))

        title_image = self.big_font.render(
            title, True, color
        )

        self.screen.blit(
            title_image,
            title_image.get_rect(
                center=(WIDTH // 2, 280)
            ),
        )

        for index, line in enumerate(lines):
            image = self.font.render(line, True, WHITE)

            self.screen.blit(
                image,
                image.get_rect(
                    center=(
                        WIDTH // 2,
                        350 + index * 45,
                    )
                ),
            )

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    def draw(self):
        self.screen.fill(BACKGROUND)

        self.hero.draw(self.screen)
        self.monster.draw(self.screen)

        for bullet in self.hero_bullets:
            bullet.draw(self.screen)

        for bullet in self.monster_bullets:
            bullet.draw(self.screen)

        for reward in self.rewards:
            reward.draw(self.screen, self.font)

        self.draw_hud()

        # Pause overlay.
        if self.paused and not self.game_over:
            self.draw_overlay(
                "PAUSED",
                YELLOW,
                [
                    "Press ESC to resume",
                    "Press Q to quit",
                ],
            )

        # Victory or defeat overlay.
        elif self.game_over:
            if self.victory:
                title = "YOU WIN!"
                color = YELLOW
            else:
                title = "GAME OVER!"
                color = RED

            self.draw_overlay(
                title,
                color,
                [
                    f"Final Score: {self.score}",
                    "Press R to restart",
                    "Press Q or ESC to quit",
                ],
            )

        pygame.display.flip()

    # --------------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------------

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000, 0.05)

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    game = Game()
    game.run()
