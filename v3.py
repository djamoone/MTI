
import pygame
import random
import math

pygame.init()

# ============================================================
# CONFIGURATION
# ============================================================

WIDTH, HEIGHT = 1280, 720
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monster vs Hero")

clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 28)
big_font = pygame.font.SysFont("arial", 58)
small_font = pygame.font.SysFont("arial", 20)

WHITE = (255, 255, 255)
BLACK = (20, 20, 30)
RED = (240, 60, 60)
GREEN = (40, 220, 100)
YELLOW = (255, 220, 40)
CYAN = (50, 220, 255)
ORANGE = (255, 145, 40)
PURPLE = (65, 15, 105)

# ============================================================
# WEAPONS
# ============================================================

WEAPONS = {
    1: {
        "name": "Normal",
        "damage": 10,
        "speed": 500,
        "cooldown": 0.25,
        "radius": 7,
        "color": YELLOW
    },
    2: {
        "name": "Rapid Fire",
        "damage": 5,
        "speed": 600,
        "cooldown": 0.10,
        "radius": 5,
        "color": CYAN
    },
    3: {
        "name": "Power",
        "damage": 25,
        "speed": 350,
        "cooldown": 0.60,
        "radius": 12,
        "color": ORANGE
    }
}

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


def random_spawn_position():
    # Spawn enemies away from the player.
    while True:
        pos = pygame.Vector2(
            random.randint(60, WIDTH - 60),
            random.randint(80, HEIGHT - 60)
        )

        if pos.distance_to(player.pos) > 250:
            return pos


# ============================================================
# PLAYER CLASS
# ============================================================

class Player:
    def __init__(self):
        self.radius = 23
        self.speed = 300
        self.max_hp = 100
        self.hp = self.max_hp

        self.pos = pygame.Vector2(WIDTH / 2, HEIGHT - 100)

        # Initial shooting direction: upward.
        self.direction = pygame.Vector2(0, -1)

        self.weapon_id = 1
        self.shoot_timer = 0
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

        # Normalize diagonal movement.
        if movement.length_squared() > 0:
            movement = movement.normalize()
            self.direction = movement

        self.pos += movement * self.speed * dt

        # Keep the player inside the screen.
        self.pos.x = max(
            self.radius, min(WIDTH - self.radius, self.pos.x)
        )
        self.pos.y = max(
            self.radius, min(HEIGHT - self.radius, self.pos.y)
        )

    def shoot(self, dt, bullets):
        self.shoot_timer += dt

        weapon = WEAPONS[self.weapon_id]

        if self.shoot_timer >= weapon["cooldown"]:
            self.shoot_timer = 0

            bullets.append({
                "pos": self.pos + self.direction * self.radius,
                "velocity": self.direction * weapon["speed"],
                "damage": weapon["damage"],
                "radius": weapon["radius"],
                "color": weapon["color"]
            })

    def take_damage(self, amount):
        if self.damage_timer <= 0:
            self.hp = max(0, self.hp - amount)
            self.damage_timer = 0.6

    def update_timers(self, dt):
        self.damage_timer = max(0, self.damage_timer - dt)

    def draw(self):
        # Flash when damaged.
        color = RED

        if self.damage_timer > 0:
            color = WHITE if int(self.damage_timer * 15) % 2 else RED

        pygame.draw.circle(
            screen, color, self.pos, self.radius
        )

        pygame.draw.circle(
            screen, BLACK, self.pos, self.radius, 3
        )

        # Draw a line indicating the facing direction.
        endpoint = self.pos + self.direction * 35

        pygame.draw.line(
            screen, WHITE, self.pos, endpoint, 4
        )


# ============================================================
# ENEMY CLASS
# ============================================================

class Enemy:
    def __init__(self, level):
        self.pos = random_spawn_position()

        # Two enemy types with different behaviors.
        self.enemy_type = random.choice(["chaser", "shooter"])

        self.radius = 27 if self.enemy_type == "chaser" else 23

        self.max_hp = 35 + level * 15
        self.hp = self.max_hp

        self.speed = (
            65 + level * 15
            if self.enemy_type == "chaser"
            else 45 + level * 8
        )

        self.damage = 10 + level * 2
        self.shoot_timer = random.uniform(0.5, 1.5)

    def update(self, player, bullets, dt, level):
        direction = player.pos - self.pos
        distance = direction.length()

        if distance > 0:
            direction = direction.normalize()

        if self.enemy_type == "chaser":
            # Chasers continuously pursue the player.
            self.pos += direction * self.speed * dt

        else:
            # Shooters maintain distance and attack from range.
            if distance > 270:
                self.pos += direction * self.speed * dt
            elif distance < 160:
                self.pos -= direction * self.speed * dt

            self.shoot_timer -= dt

            cooldown = max(0.45, 1.8 - level * 0.2)

            if self.shoot_timer <= 0 and distance > 0:
                bullet_speed = 180 + level * 20

                bullets.append({
                    "pos": self.pos.copy(),
                    "velocity": direction * bullet_speed,
                    "damage": self.damage,
                    "radius": 8,
                    "color": ORANGE
                })

                self.shoot_timer = cooldown

    def draw(self):
        if self.enemy_type == "chaser":
            color = GREEN
        else:
            color = (80, 170, 255)

        pygame.draw.circle(
            screen, color, self.pos, self.radius
        )

        pygame.draw.circle(
            screen, BLACK, self.pos, self.radius, 3
        )

        # Eyes.
        eye_offset = self.radius * 0.35

        pygame.draw.circle(
            screen, RED,
            (int(self.pos.x - eye_offset),
             int(self.pos.y - eye_offset)),
            5
        )

        pygame.draw.circle(
            screen, RED,
            (int(self.pos.x + eye_offset),
             int(self.pos.y - eye_offset)),
            5
        )

        # Enemy health bar.
        draw_health_bar(
            int(self.pos.x - self.radius),
            int(self.pos.y - self.radius - 12),
            self.radius * 2,
            7,
            self.hp,
            self.max_hp,
            RED
        )


# ============================================================
# REWARDS
# ============================================================

class Reward:
    def __init__(self, position):
        self.pos = position.copy()
        self.reward_type = random.choice(["health", "score"])
        self.radius = 15

    def collect(self, player, game):
        if self.reward_type == "health":
            player.hp = min(player.max_hp, player.hp + 25)
        else:
            game["score"] += 50

    def draw(self):
        if self.reward_type == "health":
            color = GREEN
            symbol = "+"
        else:
            color = YELLOW
            symbol = "$"

        pygame.draw.circle(
            screen, color, self.pos, self.radius
        )

        pygame.draw.circle(
            screen, WHITE, self.pos, self.radius, 2
        )

        image = small_font.render(symbol, True, BLACK)

        screen.blit(
            image,
            (self.pos.x - image.get_width() / 2,
             self.pos.y - image.get_height() / 2)
        )


# ============================================================
# GAME SETUP
# ============================================================

player = Player()

hero_bullets = []
enemy_bullets = []
enemies = []
rewards = []

game = {
    "score": 0,
    "level": 1,
    "max_level": 3,
    "kills": 0,
    "kills_required": 3,
    "state": "menu"
}


def setup_level():
    enemies.clear()
    hero_bullets.clear()
    enemy_bullets.clear()

    level = game["level"]

    # More enemies appear at higher levels.
    number_of_enemies = 2 + level

    for _ in range(number_of_enemies):
        enemies.append(Enemy(level))

    game["kills_required"] = number_of_enemies
    game["kills"] = 0


def restart_game():
    global player

    player = Player()

    hero_bullets.clear()
    enemy_bullets.clear()
    enemies.clear()
    rewards.clear()

    game["score"] = 0
    game["level"] = 1
    game["kills"] = 0
    game["state"] = "playing"

    setup_level()


# ============================================================
# MAIN GAME LOOP
# ============================================================

running = True

while running:
    dt = min(clock.tick(FPS) / 1000, 0.05)

    # --------------------------------------------------------
    # EVENTS AND CONTROLS
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                if game["state"] == "playing":
                    game["state"] = "paused"
                elif game["state"] == "paused":
                    game["state"] = "playing"
                else:
                    running = False

            if event.key == pygame.K_RETURN:
                if game["state"] in ("menu", "game_over", "victory"):
                    restart_game()
                elif game["state"] == "paused":
                    game["state"] = "playing"

            if game["state"] == "playing":

                if event.key == pygame.K_1:
                    player.weapon_id = 1

                elif event.key == pygame.K_2:
                    player.weapon_id = 2

                elif event.key == pygame.K_3:
                    player.weapon_id = 3

    # --------------------------------------------------------
    # GAME LOGIC
    # --------------------------------------------------------

    if game["state"] == "playing":

        keys = pygame.key.get_pressed()

        # Player movement and health timers.
        player.move(keys, dt)
        player.update_timers(dt)

        # Hold SPACE to shoot.
        if keys[pygame.K_SPACE]:
            player.shoot(dt, hero_bullets)

        # Update enemies.
        for enemy in enemies:
            enemy.update(player, enemy_bullets, dt, game["level"])

        # ----------------------------------------------------
        # MOVE HERO BULLETS AND CHECK COLLISIONS
        # ----------------------------------------------------

        for bullet in hero_bullets[:]:
            bullet["pos"] += bullet["velocity"] * dt

            if (
                bullet["pos"].x < 0
                or bullet["pos"].x > WIDTH
                or bullet["pos"].y < 0
                or bullet["pos"].y > HEIGHT
            ):
                hero_bullets.remove(bullet)
                continue

            for enemy in enemies[:]:
                distance = bullet["pos"].distance_to(enemy.pos)

                if distance < bullet["radius"] + enemy.radius:
                    enemy.hp -= bullet["damage"]

                    if bullet in hero_bullets:
                        hero_bullets.remove(bullet)

                    game["score"] += 10

                    if enemy.hp <= 0:
                        rewards.append(Reward(enemy.pos))
                        enemies.remove(enemy)

                        game["score"] += 100
                        game["kills"] += 1

                    break

        # ----------------------------------------------------
        # MOVE ENEMY BULLETS AND CHECK COLLISIONS
        # ----------------------------------------------------

        for bullet in enemy_bullets[:]:
            bullet["pos"] += bullet["velocity"] * dt

            if (
                bullet["pos"].x < 0
                or bullet["pos"].x > WIDTH
                or bullet["pos"].y < 0
                or bullet["pos"].y > HEIGHT
            ):
                enemy_bullets.remove(bullet)
                continue

            if bullet["pos"].distance_to(player.pos) < (
                player.radius + bullet["radius"]
            ):
                player.take_damage(bullet["damage"])
                enemy_bullets.remove(bullet)

        # ----------------------------------------------------
        # ENEMY-PLAYER COLLISION
        # ----------------------------------------------------

        for enemy in enemies:
            distance = enemy.pos.distance_to(player.pos)

            if distance < player.radius + enemy.radius:
                player.take_damage(enemy.damage)

        # ----------------------------------------------------
        # COLLECT REWARDS
        # ----------------------------------------------------

        for reward in rewards[:]:
            distance = reward.pos.distance_to(player.pos)

            if distance < player.radius + reward.radius:
                reward.collect(player, game)
                rewards.remove(reward)

        # ----------------------------------------------------
        # LEVEL PROGRESSION
        # ----------------------------------------------------

        if not enemies:
            if game["level"] < game["max_level"]:
                game["level"] += 1
                setup_level()
            else:
                game["state"] = "victory"

        # ----------------------------------------------------
        # GAME OVER
        # ----------------------------------------------------

        if player.hp <= 0:
            game["state"] = "game_over"

    # ========================================================
    # RENDERING
    # ========================================================

    screen.fill(PURPLE)

    # Background grid for a simple game arena.
    for x in range(0, WIDTH, 80):
        pygame.draw.line(
            screen, (80, 35, 115), (x, 0), (x, HEIGHT), 1
        )

    for y in range(0, HEIGHT, 80):
        pygame.draw.line(
            screen, (80, 35, 115), (0, y), (WIDTH, y), 1
        )

    # Draw rewards.
    for reward in rewards:
        reward.draw()

    # Draw player bullets.
    for bullet in hero_bullets:
        pygame.draw.circle(
            screen,
            bullet["color"],
            (int(bullet["pos"].x), int(bullet["pos"].y)),
            bullet["radius"]
        )

    # Draw enemy bullets.
    for bullet in enemy_bullets:
        pygame.draw.circle(
            screen,
            ORANGE,
            (int(bullet["pos"].x), int(bullet["pos"].y)),
            bullet["radius"]
        )

    # Draw enemies and player.
    for enemy in enemies:
        enemy.draw()

    player.draw()

    # --------------------------------------------------------
    # GAME INTERFACE
    # --------------------------------------------------------

    draw_health_bar(
        20, 20, 210, 25,
        player.hp, player.max_hp, RED
    )

    draw_text(
        f"Hero HP: {player.hp}",
        20, 52
    )

    draw_text(
        f"Score: {game['score']}",
        500, 20, YELLOW
    )

    draw_text(
        f"Level: {game['level']}/{game['max_level']}",
        500, 55
    )

    draw_text(
        f"Enemies: {len(enemies)}",
        500, 90
    )

    draw_text(
        f"Weapon: {WEAPONS[player.weapon_id]['name']}",
        20, 100
    )

    draw_text(
        "Move: Arrows / WASD",
        20, 140, WHITE, small_font
    )

    draw_text(
        "Shoot: SPACE",
        20, 165, WHITE, small_font
    )

    draw_text(
        "Weapons: 1 / 2 / 3",
        20, 190, WHITE, small_font
    )

    draw_text(
        "Pause: ESC",
        20, 215, WHITE, small_font
    )

    # --------------------------------------------------------
    # MENUS AND GAME STATES
    # --------------------------------------------------------

    if game["state"] != "playing":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        if game["state"] == "menu":
            title = "MONSTER VS HERO"
            subtitle = "Press ENTER to start"

        elif game["state"] == "paused":
            title = "PAUSED"
            subtitle = "Press ENTER to resume"

        elif game["state"] == "game_over":
            title = "GAME OVER"
            subtitle = "Press ENTER to restart"

        else:
            title = "YOU WIN!"
            subtitle = "Press ENTER to play again"

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
            f"Score: {game['score']}",
            WIDTH // 2 - 65, 395, WHITE
        )

        draw_text(
            "ESC: Pause / Quit",
            WIDTH // 2 - 90, 440, WHITE, small_font
        )

    pygame.display.flip()

pygame.quit()
