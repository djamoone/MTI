
import pygame
import random
from abc import ABC, abstractmethod

pygame.init()

# ============================================================
# CONFIGURATION
# ============================================================

WIDTH, HEIGHT = 1280, 720
FPS = 60

WHITE = (255, 255, 255)
BLACK = (20, 20, 30)
RED = (240, 60, 60)
GREEN = (40, 220, 100)
YELLOW = (255, 220, 40)
CYAN = (50, 220, 255)
ORANGE = (255, 145, 40)
PURPLE = (65, 15, 105)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monster vs Hero")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 28)
big_font = pygame.font.SysFont("arial", 58)
small_font = pygame.font.SysFont("arial", 20)


# ============================================================
# INTERFACES - ISP
# ============================================================

class Damageable(ABC):
    """Interface for objects that can receive damage."""

    @abstractmethod
    def take_damage(self, amount):
        pass


class Weapon(ABC):
    """Interface for all weapons."""

    @abstractmethod
    def shoot(self, position, direction):
        pass

    @abstractmethod
    def update(self, dt):
        pass


class Reward(ABC):
    """Interface for collectible rewards."""

    @abstractmethod
    def collect(self, player, game):
        pass


class Enemy(ABC):
    """Common abstraction for all enemy types."""

    def __init__(self, position, level):
        self.pos = pygame.Vector2(position)
        self.max_hp = 35 + level * 15
        self.hp = self.max_hp
        self.damage = 10 + level * 2
        self.radius = 25

    @abstractmethod
    def update(self, player, bullets, dt, level):
        pass

    @abstractmethod
    def get_color(self):
        pass

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def is_dead(self):
        return self.hp <= 0


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def draw_text(text, x, y, color=WHITE, selected_font=None):
    selected_font = selected_font or font
    image = selected_font.render(str(text), True, color)
    screen.blit(image, (x, y))


def draw_health_bar(x, y, width, height, hp, max_hp, color):
    pygame.draw.rect(screen, BLACK, (x, y, width, height))

    ratio = max(0, min(1, hp / max_hp))

    pygame.draw.rect(
        screen,
        color,
        (x + 2, y + 2, int((width - 4) * ratio), height - 4)
    )


# ============================================================
# BULLET CLASS
# ============================================================

class Bullet:
    def __init__(self, position, velocity, damage, radius, color):
        self.pos = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)
        self.damage = damage
        self.radius = radius
        self.color = color

    def update(self, dt):
        self.pos += self.velocity * dt

    def is_outside(self):
        return (
            self.pos.x < 0 or self.pos.x > WIDTH
            or self.pos.y < 0 or self.pos.y > HEIGHT
        )


# ============================================================
# WEAPONS - OCP
# ============================================================

class BaseWeapon(Weapon):
    def __init__(self, name, damage, speed, cooldown, radius, color):
        self.name = name
        self.damage = damage
        self.speed = speed
        self.cooldown = cooldown
        self.radius = radius
        self.color = color
        self.timer = 0

    def update(self, dt):
        self.timer += dt

    def shoot(self, position, direction):
        if self.timer < self.cooldown:
            return None

        self.timer = 0

        return Bullet(
            position + direction * 23,
            direction * self.speed,
            self.damage,
            self.radius,
            self.color
        )


class NormalWeapon(BaseWeapon):
    def __init__(self):
        super().__init__("Normal", 10, 500, 0.25, 7, YELLOW)


class RapidFireWeapon(BaseWeapon):
    def __init__(self):
        super().__init__("Rapid Fire", 5, 600, 0.10, 5, CYAN)


class PowerWeapon(BaseWeapon):
    def __init__(self):
        super().__init__("Power", 25, 350, 0.60, 12, ORANGE)


# ============================================================
# WEAPON FACTORY - DIP / OCP
# ============================================================

class WeaponFactory:
    def __init__(self):
        self.weapons = {
            1: NormalWeapon,
            2: RapidFireWeapon,
            3: PowerWeapon
        }

    def create(self, weapon_id):
        weapon_class = self.weapons.get(weapon_id)
        return weapon_class() if weapon_class else None

    def get_name(self, weapon_id):
        weapon_class = self.weapons.get(weapon_id)
        return weapon_class().name if weapon_class else "Unknown"


# ============================================================
# PLAYER CLASS - SRP
# ============================================================

class Player(Damageable):
    def __init__(self, weapon_factory):
        self.radius = 23
        self.speed = 300
        self.max_hp = 100
        self.hp = self.max_hp

        self.pos = pygame.Vector2(WIDTH / 2, HEIGHT - 100)
        self.direction = pygame.Vector2(0, -1)

        self.weapon_factory = weapon_factory
        self.weapon_id = 1
        self.weapon = weapon_factory.create(1)

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

        self.pos.x = max(
            self.radius, min(WIDTH - self.radius, self.pos.x)
        )
        self.pos.y = max(
            self.radius, min(HEIGHT - self.radius, self.pos.y)
        )

    def change_weapon(self, weapon_id):
        weapon = self.weapon_factory.create(weapon_id)

        if weapon is not None:
            self.weapon_id = weapon_id
            self.weapon = weapon

    def shoot(self, bullets):
        bullet = self.weapon.shoot(self.pos, self.direction)

        if bullet is not None:
            bullets.append(bullet)

    def update(self, dt):
        self.weapon.update(dt)
        self.damage_timer = max(0, self.damage_timer - dt)

    def take_damage(self, amount):
        if self.damage_timer <= 0:
            self.hp = max(0, self.hp - amount)
            self.damage_timer = 0.6


# ============================================================
# ENEMY TYPES - OCP / LSP
# ============================================================

class ChaserEnemy(Enemy):
    def __init__(self, position, level):
        super().__init__(position, level)

        self.radius = 27
        self.speed = 65 + level * 15

    def update(self, player, bullets, dt, level):
        direction = player.pos - self.pos

        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.pos += direction * self.speed * dt

    def get_color(self):
        return GREEN


class ShooterEnemy(Enemy):
    def __init__(self, position, level):
        super().__init__(position, level)

        self.radius = 23
        self.speed = 45 + level * 8
        self.shoot_timer = random.uniform(0.5, 1.5)

    def update(self, player, bullets, dt, level):
        direction = player.pos - self.pos
        distance = direction.length()

        if distance > 0:
            direction = direction.normalize()

        if distance > 270:
            self.pos += direction * self.speed * dt

        elif distance < 160:
            self.pos -= direction * self.speed * dt

        self.shoot_timer -= dt

        cooldown = max(0.45, 1.8 - level * 0.2)

        if self.shoot_timer <= 0 and distance > 0:
            bullets.append(
                Bullet(
                    self.pos,
                    direction * (180 + level * 20),
                    self.damage,
                    8,
                    ORANGE
                )
            )

            self.shoot_timer = cooldown

    def get_color(self):
        return (80, 170, 255)


# ============================================================
# ENEMY FACTORY - DIP / OCP
# ============================================================

class EnemyFactory:
    def create(self, level, position):
        enemy_class = random.choice([
            ChaserEnemy,
            ShooterEnemy
        ])

        return enemy_class(position, level)

    def create_at_random_position(self, level, player):
        while True:
            position = pygame.Vector2(
                random.randint(60, WIDTH - 60),
                random.randint(80, HEIGHT - 60)
            )

            if position.distance_to(player.pos) > 250:
                return self.create(level, position)


# ============================================================
# REWARDS - OCP / LSP
# ============================================================

class HealthReward(Reward):
    def __init__(self, position):
        self.pos = pygame.Vector2(position)
        self.radius = 15

    def collect(self, player, game):
        player.hp = min(player.max_hp, player.hp + 25)


class ScoreReward(Reward):
    def __init__(self, position):
        self.pos = pygame.Vector2(position)
        self.radius = 15

    def collect(self, player, game):
        game.score += 50


# ============================================================
# REWARD FACTORY - DIP / OCP
# ============================================================

class RewardFactory:
    def __init__(self):
        self.reward_types = [
            HealthReward,
            ScoreReward
        ]

    def create(self, position):
        reward_class = random.choice(self.reward_types)
        return reward_class(position)


# ============================================================
# GAME DATA
# ============================================================

class GameData:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.max_level = 3
        self.kills = 0
        self.kills_required = 3
        self.state = "menu"


# ============================================================
# COLLISION HANDLER - SRP
# ============================================================

class CollisionHandler:

    def check_collision(self, object_a, object_b):
        distance = object_a.pos.distance_to(object_b.pos)

        return distance < object_a.radius + object_b.radius

    def handle_hero_bullets(self, bullets, enemies):
        rewards = []
        score = 0
        kills = 0

        for bullet in bullets[:]:
            bullet.update(0)  # Position is updated by Game.

            if bullet.is_outside():
                bullets.remove(bullet)
                continue

            for enemy in enemies[:]:
                if self.check_collision(bullet, enemy):
                    enemy.take_damage(bullet.damage)
                    bullets.remove(bullet)
                    score += 10

                    if enemy.is_dead():
                        rewards.append(enemy.pos.copy())
                        enemies.remove(enemy)
                        score += 100
                        kills += 1

                    break

        return rewards, score, kills

    def handle_enemy_bullets(self, bullets, player):
        for bullet in bullets[:]:
            if self.check_collision(bullet, player):
                player.take_damage(bullet.damage)
                bullets.remove(bullet)

            elif bullet.is_outside():
                bullets.remove(bullet)

    def handle_enemy_player(self, enemies, player):
        for enemy in enemies:
            if self.check_collision(enemy, player):
                player.take_damage(enemy.damage)

    def handle_rewards(self, rewards, player, game):
        for reward in rewards[:]:
            if self.check_collision(reward, player):
                reward.collect(player, game)
                rewards.remove(reward)


# ============================================================
# RENDERERS - SRP
# ============================================================

class PlayerRenderer:
    def draw(self, player):
        color = RED

        if player.damage_timer > 0:
            color = (
                WHITE if int(player.damage_timer * 15) % 2
                else RED
            )

        pygame.draw.circle(
            screen, color, player.pos, player.radius
        )

        pygame.draw.circle(
            screen, BLACK, player.pos, player.radius, 3
        )

        endpoint = player.pos + player.direction * 35

        pygame.draw.line(
            screen, WHITE, player.pos, endpoint, 4
        )


class EnemyRenderer:
    def draw(self, enemy):
        pygame.draw.circle(
            screen, enemy.get_color(), enemy.pos, enemy.radius
        )

        pygame.draw.circle(
            screen, BLACK, enemy.pos, enemy.radius, 3
        )

        eye_offset = enemy.radius * 0.35

        pygame.draw.circle(
            screen, RED,
            (int(enemy.pos.x - eye_offset),
             int(enemy.pos.y - eye_offset)), 5
        )

        pygame.draw.circle(
            screen, RED,
            (int(enemy.pos.x + eye_offset),
             int(enemy.pos.y - eye_offset)), 5
        )

        draw_health_bar(
            int(enemy.pos.x - enemy.radius),
            int(enemy.pos.y - enemy.radius - 12),
            enemy.radius * 2, 7,
            enemy.hp, enemy.max_hp, RED
        )


class BulletRenderer:
    def draw(self, bullet):
        pygame.draw.circle(
            screen,
            bullet.color,
            (int(bullet.pos.x), int(bullet.pos.y)),
            bullet.radius
        )


class RewardRenderer:
    def draw(self, reward):
        if isinstance(reward, HealthReward):
            color, symbol = GREEN, "+"
        else:
            color, symbol = YELLOW, "$"

        pygame.draw.circle(
            screen, color, reward.pos, reward.radius
        )

        pygame.draw.circle(
            screen, WHITE, reward.pos, reward.radius, 2
        )

        image = small_font.render(symbol, True, BLACK)

        screen.blit(
            image,
            (reward.pos.x - image.get_width() / 2,
             reward.pos.y - image.get_height() / 2)
        )


class UIRenderer:
    def draw(self, player, game, weapon_name, enemies):
        draw_health_bar(
            20, 20, 210, 25,
            player.hp, player.max_hp, RED
        )

        draw_text(f"Hero HP: {player.hp}", 20, 52)
        draw_text(f"Score: {game.score}", 500, 20, YELLOW)
        draw_text(
            f"Level: {game.level}/{game.max_level}", 500, 55
        )
        draw_text(f"Enemies: {len(enemies)}", 500, 90)

        draw_text(f"Weapon: {weapon_name}", 20, 100)

        draw_text(
            "Move: Arrows / WASD", 20, 140, WHITE, small_font
        )
        draw_text("Shoot: SPACE", 20, 165, WHITE, small_font)
        draw_text(
            "Weapons: 1 / 2 / 3", 20, 190, WHITE, small_font
        )
        draw_text("Pause: ESC", 20, 215, WHITE, small_font)

    def draw_overlay(self, game):
        overlay = pygame.Surface(
            (WIDTH, HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        messages = {
            "menu": ("MONSTER VS HERO", "Press ENTER to start"),
            "paused": ("PAUSED", "Press ENTER to resume"),
            "game_over": ("GAME OVER", "Press ENTER to restart"),
            "victory": ("YOU WIN!", "Press ENTER to play again")
        }

        title, subtitle = messages[game.state]

        title_image = big_font.render(title, True, YELLOW)

        screen.blit(
            title_image,
            (WIDTH // 2 - title_image.get_width() // 2, 260)
        )

        subtitle_image = font.render(subtitle, True, WHITE)

        screen.blit(
            subtitle_image,
            (WIDTH // 2 - subtitle_image.get_width() // 2, 340)
        )

        draw_text(
            f"Score: {game.score}",
            WIDTH // 2 - 65, 395, WHITE
        )

        draw_text(
            "ESC: Pause / Quit",
            WIDTH // 2 - 90, 440, WHITE, small_font
        )


# ============================================================
# GAME RENDERER - SRP
# ============================================================

class GameRenderer:
    def __init__(
        self,
        player_renderer,
        enemy_renderer,
        bullet_renderer,
        reward_renderer,
        ui_renderer
    ):
        self.player_renderer = player_renderer
        self.enemy_renderer = enemy_renderer
        self.bullet_renderer = bullet_renderer
        self.reward_renderer = reward_renderer
        self.ui_renderer = ui_renderer

    def draw_background(self):
        screen.fill(PURPLE)

        for x in range(0, WIDTH, 80):
            pygame.draw.line(
                screen, (80, 35, 115),
                (x, 0), (x, HEIGHT), 1
            )

        for y in range(0, HEIGHT, 80):
            pygame.draw.line(
                screen, (80, 35, 115),
                (0, y), (WIDTH, y), 1
            )

    def render(self, game):
        self.draw_background()

        for reward in game.rewards:
            self.reward_renderer.draw(reward)

        for bullet in game.hero_bullets:
            self.bullet_renderer.draw(bullet)

        for bullet in game.enemy_bullets:
            self.bullet_renderer.draw(bullet)

        for enemy in game.enemies:
            self.enemy_renderer.draw(enemy)

        self.player_renderer.draw(game.player)

        self.ui_renderer.draw(
            game.player,
            game.data,
            game.player.weapon.name,
            game.enemies
        )

        if game.data.state != "playing":
            self.ui_renderer.draw_overlay(game.data)

        pygame.display.flip()


# ============================================================
# INPUT HANDLER - SRP
# ============================================================

class InputHandler:
    def process_events(self, game):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                game.running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    if game.data.state == "playing":
                        game.data.state = "paused"

                    elif game.data.state == "paused":
                        game.data.state = "playing"

                    else:
                        game.running = False

                if event.key == pygame.K_RETURN:
                    if game.data.state in (
                        "menu", "game_over", "victory"
                    ):
                        game.restart()

                    elif game.data.state == "paused":
                        game.data.state = "playing"

                if game.data.state == "playing":

                    if event.key in (
                        pygame.K_1, pygame.K_2, pygame.K_3
                    ):
                        weapon_id = event.key - pygame.K_0
                        game.player.change_weapon(weapon_id)

    def update_player(self, game, dt):
        if game.data.state != "playing":
            return

        keys = pygame.key.get_pressed()

        game.player.move(keys, dt)

        if keys[pygame.K_SPACE]:
            game.player.shoot(game.hero_bullets)


# ============================================================
# MAIN GAME CLASS - DIP
# ============================================================

class Game:

    def __init__(
        self,
        enemy_factory,
        weapon_factory,
        reward_factory,
        collision_handler,
        input_handler,
        renderer
    ):
        self.enemy_factory = enemy_factory
        self.weapon_factory = weapon_factory
        self.reward_factory = reward_factory
        self.collision_handler = collision_handler
        self.input_handler = input_handler
        self.renderer = renderer

        self.data = GameData()

        self.player = Player(self.weapon_factory)

        self.hero_bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.rewards = []

        self.running = True

    def setup_level(self):
        self.enemies.clear()
        self.hero_bullets.clear()
        self.enemy_bullets.clear()

        number_of_enemies = 2 + self.data.level

        for _ in range(number_of_enemies):
            enemy = self.enemy_factory.create_at_random_position(
                self.data.level, self.player
            )
            self.enemies.append(enemy)

        self.data.kills_required = number_of_enemies
        self.data.kills = 0

    def restart(self):
        self.player = Player(self.weapon_factory)

        self.hero_bullets.clear()
        self.enemy_bullets.clear()
        self.enemies.clear()
        self.rewards.clear()

        self.data.score = 0
        self.data.level = 1
        self.data.kills = 0
        self.data.state = "playing"

        self.setup_level()

    def update(self, dt):
        if self.data.state != "playing":
            return

        self.player.update(dt)

        self.input_handler.update_player(self, dt)

        # Update enemies.
        for enemy in self.enemies:
            enemy.update(
                self.player,
                self.enemy_bullets,
                dt,
                self.data.level
            )

        # Update bullets.
        for bullet in self.hero_bullets[:]:
            bullet.update(dt)

            if bullet.is_outside():
                self.hero_bullets.remove(bullet)

        for bullet in self.enemy_bullets[:]:
            bullet.update(dt)

        # Handle hero bullet collisions.
        for bullet in self.hero_bullets[:]:
            for enemy in self.enemies[:]:

                if self.collision_handler.check_collision(
                    bullet, enemy
                ):
                    enemy.take_damage(bullet.damage)
                    self.hero_bullets.remove(bullet)

                    self.data.score += 10

                    if enemy.is_dead():
                        self.rewards.append(
                            self.reward_factory.create(enemy.pos)
                        )

                        self.enemies.remove(enemy)
                        self.data.score += 100
                        self.data.kills += 1

                    break

        # Handle enemy bullet collisions.
        self.collision_handler.handle_enemy_bullets(
            self.enemy_bullets, self.player
        )

        # Handle direct enemy contact.
        self.collision_handler.handle_enemy_player(
            self.enemies, self.player
        )

        # Collect rewards.
        self.collision_handler.handle_rewards(
            self.rewards, self.player, self.data
        )

        # Level progression.
        if not self.enemies:
            if self.data.level < self.data.max_level:
                self.data.level += 1
                self.setup_level()
            else:
                self.data.state = "victory"

        # Game over.
        if self.player.hp <= 0:
            self.data.state = "game_over"

    def run(self):
        while self.running:

            dt = min(clock.tick(FPS) / 1000, 0.05)

            self.input_handler.process_events(self)

            self.update(dt)

            self.renderer.render(self)

        pygame.quit()


# ============================================================
# DEPENDENCY INJECTION - DIP
# ============================================================

def main():

    weapon_factory = WeaponFactory()
    enemy_factory = EnemyFactory()
    reward_factory = RewardFactory()

    collision_handler = CollisionHandler()
    input_handler = InputHandler()

    player_renderer = PlayerRenderer()
    enemy_renderer = EnemyRenderer()
    bullet_renderer = BulletRenderer()
    reward_renderer = RewardRenderer()
    ui_renderer = UIRenderer()

    renderer = GameRenderer(
        player_renderer,
        enemy_renderer,
        bullet_renderer,
        reward_renderer,
        ui_renderer
    )

    game = Game(
        enemy_factory,
        weapon_factory,
        reward_factory,
        collision_handler,
        input_handler,
        renderer
    )

    game.run()


if __name__ == "__main__":
    main()
