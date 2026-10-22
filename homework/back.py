
# import pygame
# import random
# import math

# pygame.init()

# screen = pygame.display.set_mode((1280, 720))
# pygame.display.set_caption("Monster vs Hero")

# clock = pygame.time.Clock()
# font = pygame.font.SysFont(None, 36)

# # Hero
# player_pos = pygame.Vector2(640, 620)
# player_radius = 25
# player_speed = 300
# player_hp = 100

# # Monster
# monster_pos = pygame.Vector2(640, 100)
# monster_radius = 50
# monster_hp = 100

# # Bullets
# hero_bullets = []
# monster_bullets = []

# hero_shoot_timer = 0
# monster_shoot_timer = 0

# score = 0
# running = True
# game_over = False
# victory = False


# def draw_text(text, x, y, color="white"):
#     image = font.render(text, True, color)
#     screen.blit(image, (x, y))


# while running:
#     dt = clock.tick(60) / 1000

#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_ESCAPE:
#                 running = False

#             if event.key == pygame.K_SPACE and not game_over:
#                 hero_bullets.append(
#                     pygame.Vector2(player_pos.x, player_pos.y - 25)
#                 )

#     keys = pygame.key.get_pressed()

#     if not game_over:
#         # Move hero
#         if keys[pygame.K_w]:
#             player_pos.y -= player_speed * dt
#         if keys[pygame.K_s]:
#             player_pos.y += player_speed * dt
#         if keys[pygame.K_a]:
#             player_pos.x -= player_speed * dt
#         if keys[pygame.K_d]:
#             player_pos.x += player_speed * dt

#         # Keep hero inside screen
#         player_pos.x = max(25, min(1255, player_pos.x))
#         player_pos.y = max(25, min(695, player_pos.y))

#         # Hero automatic shooting
#         hero_shoot_timer += dt
#         if hero_shoot_timer >= 0.25:
#             hero_bullets.append(
#                 pygame.Vector2(player_pos.x, player_pos.y - 25)
#             )
#             hero_shoot_timer = 0

#         # Monster shoots toward hero
#         monster_shoot_timer += dt

#         if monster_shoot_timer >= 0.8:
#             direction = player_pos - monster_pos

#             if direction.length_squared() > 0:
#                 direction = direction.normalize()

#             monster_bullets.append(
#                 [monster_pos.copy(), direction * 220]
#             )

#             monster_shoot_timer = 0

#         # Move hero bullets and damage monster
#         for bullet in hero_bullets[:]:
#             bullet.y -= 500 * dt

#             if bullet.distance_to(monster_pos) < monster_radius:
#                 hero_bullets.remove(bullet)
#                 monster_hp -= 10
#                 score += 10

#             elif bullet.y < 0:
#                 hero_bullets.remove(bullet)

#         # Move monster bullets and damage hero
#         for bullet in monster_bullets[:]:
#             pos, velocity = bullet
#             pos += velocity * dt

#             if pos.distance_to(player_pos) < player_radius:
#                 monster_bullets.remove(bullet)
#                 player_hp -= 10

#             elif (
#                 pos.x < 0 or pos.x > 1280
#                 or pos.y < 0 or pos.y > 720
#             ):
#                 monster_bullets.remove(bullet)

#         # Check who wins
#         if monster_hp <= 0:
#             monster_hp = 0
#             victory = True
#             game_over = True

#         if player_hp <= 0:
#             player_hp = 0
#             victory = False
#             game_over = True

#     # Draw background
#     screen.fill((65, 15, 105))

#     # Draw hero
#     pygame.draw.circle(
#         screen, (255, 40, 40), player_pos, player_radius
#     )
#     pygame.draw.circle(
#         screen, "black", player_pos, player_radius, 3
#     )

#     # Draw monster
#     pygame.draw.circle(
#         screen, (30, 200, 70), monster_pos, monster_radius
#     )
#     pygame.draw.circle(
#         screen, "black", monster_pos, monster_radius, 4
#     )

#     # Monster eyes
#     pygame.draw.circle(
#         screen, "red", (int(monster_pos.x - 17),
#                         int(monster_pos.y - 10)), 8
#     )
#     pygame.draw.circle(
#         screen, "red", (int(monster_pos.x + 17),
#                         int(monster_pos.y - 10)), 8
#     )

#     # Monster mouth
#     pygame.draw.line(
#         screen, "black",
#         (int(monster_pos.x - 20), int(monster_pos.y + 20)),
#         (int(monster_pos.x + 20), int(monster_pos.y + 20)), 5
#     )

#     # Draw hero bullets
#     for bullet in hero_bullets:
#         pygame.draw.circle(
#             screen, "yellow",
#             (int(bullet.x), int(bullet.y)), 8
#         )

#     # Draw monster bullets
#     for bullet in monster_bullets:
#         pos, velocity = bullet
#         pygame.draw.circle(
#             screen, (255, 100, 40),
#             (int(pos.x), int(pos.y)), 9
#         )

#     # Hero health bar
#     pygame.draw.rect(screen, "black", (20, 20, 204, 24))
#     pygame.draw.rect(
#         screen, "red",
#         (22, 22, 2 * player_hp, 20)
#     )
#     draw_text(f"Hero HP: {player_hp}", 20, 50)

#     # Monster health bar
#     pygame.draw.rect(screen, "black", (900, 20, 204, 24))
#     pygame.draw.rect(
#         screen, "green",
#         (902, 22, 2 * monster_hp, 20)
#     )
#     draw_text(f"Monster HP: {monster_hp}", 900, 50)

#     draw_text(f"Score: {score}", 550, 20)

#     if game_over:
#         if victory:
#             draw_text("YOU WIN!", 555, 320, "yellow")
#         else:
#             draw_text("GAME OVER!", 530, 320, "red")

#         draw_text("Press ESC to quit", 520, 365)

#     pygame.display.flip()

# pygame.quit()

import pygame
import random
import math

pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Monster vs Hero")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# -------------------- Hero --------------------

player_pos = pygame.Vector2(640, 620)
player_radius = 25
player_speed = 300
player_hp = 100

# -------------------- Monster --------------------

monster_pos = pygame.Vector2(640, 100)
monster_radius = 50
monster_hp = 100
monster_speed = 55

# -------------------- Bullets --------------------

hero_bullets = []
monster_bullets = []

hero_shoot_timer = 0
monster_shoot_timer = 0
collision_timer = 0

# -------------------- Weapons --------------------

weapons = {
    1: {"name": "Normal", "damage": 10, "speed": 500,
        "cooldown": 0.25, "radius": 8, "color": "yellow"},

    2: {"name": "Rapid Fire", "damage": 5, "speed": 600,
        "cooldown": 0.10, "radius": 6, "color": "cyan"},

    3: {"name": "Power", "damage": 25, "speed": 350,
        "cooldown": 0.60, "radius": 12, "color": "orange"}
}

current_weapon = 1

# -------------------- Rewards --------------------

rewards = []

# Reward types:
# "health" = restore health
# "score" = bonus points

# -------------------- Game Levels --------------------

level = 1
max_level = 3
score = 0

running = True
game_over = False
victory = False


def draw_text(text, x, y, color="white"):
    image = font.render(text, True, color)
    screen.blit(image, (x, y))


def spawn_reward(position):
    reward_type = random.choice(["health", "score"])

    rewards.append({
        "pos": position.copy(),
        "type": reward_type,
        "value": 25 if reward_type == "health" else 50
    })


def setup_level():
    global monster_pos, monster_hp, monster_speed
    global monster_radius, monster_shoot_timer

    monster_pos = pygame.Vector2(
        random.randint(100, 1180),
        random.randint(80, 250)
    )

    monster_hp = 100 + (level - 1) * 50
    monster_speed = 55 + (level - 1) * 25
    monster_radius = 50

    monster_shoot_timer = 0


setup_level()

# -------------------- Main Game Loop --------------------

while running:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            # Select weapons
            if event.key == pygame.K_1:
                current_weapon = 1

            if event.key == pygame.K_2:
                current_weapon = 2

            if event.key == pygame.K_3:
                current_weapon = 3

            # Restart the game
            if event.key == pygame.K_r and game_over:
                player_pos = pygame.Vector2(640, 620)
                player_hp = 100

                hero_bullets.clear()
                monster_bullets.clear()
                rewards.clear()

                hero_shoot_timer = 0
                monster_shoot_timer = 0
                collision_timer = 0

                score = 0
                level = 1
                current_weapon = 1

                game_over = False
                victory = False

                setup_level()

    keys = pygame.key.get_pressed()

    if not game_over:

        # -------------------- Move Hero --------------------

        if keys[pygame.K_UP]:
            player_pos.y -= player_speed * dt

        if keys[pygame.K_DOWN]:
            player_pos.y += player_speed * dt

        if keys[pygame.K_LEFT]:
            player_pos.x -= player_speed * dt

        if keys[pygame.K_RIGHT]:
            player_pos.x += player_speed * dt


        # Keep hero inside the screen
        player_pos.x = max(25, min(1255, player_pos.x))
        player_pos.y = max(25, min(695, player_pos.y))

        # -------------------- Hero Shooting --------------------

        hero_shoot_timer += dt

        weapon = weapons[current_weapon]

        if hero_shoot_timer >= weapon["cooldown"]:

            hero_bullets.append({
                "pos": pygame.Vector2(
                    player_pos.x, player_pos.y - player_radius
                ),
                "damage": weapon["damage"],
                "speed": weapon["speed"],
                "radius": weapon["radius"],
                "color": weapon["color"]
            })

            hero_shoot_timer = 0

        # -------------------- Monster Pursuit --------------------

        direction = player_pos - monster_pos

        if direction.length_squared() > 0:
            direction = direction.normalize()
            monster_pos += direction * monster_speed * dt

        # -------------------- Monster Shooting --------------------

        monster_shoot_timer += dt

        # The monster shoots faster at higher levels
        monster_cooldown = max(0.30, 0.80 - (level - 1) * 0.15)

        if monster_shoot_timer >= monster_cooldown:

            direction = player_pos - monster_pos

            if direction.length_squared() > 0:
                direction = direction.normalize()

            monster_bullets.append([
                monster_pos.copy(),
                direction * (220 + (level - 1) * 40)
            ])

            monster_shoot_timer = 0

        # -------------------- Move Hero Bullets --------------------

        for bullet in hero_bullets[:]:

            bullet["pos"].y -= bullet["speed"] * dt

            # Bullet hits monster
            if bullet["pos"].distance_to(monster_pos) < (
                monster_radius + bullet["radius"]
            ):

                monster_hp -= bullet["damage"]
                score += 10
                hero_bullets.remove(bullet)

            # Remove bullets outside the screen
            elif bullet["pos"].y < 0:
                hero_bullets.remove(bullet)

        # -------------------- Move Monster Bullets --------------------

        for bullet in monster_bullets[:]:

            pos, velocity = bullet
            pos += velocity * dt

            if pos.distance_to(player_pos) < player_radius + 9:

                player_hp -= 10
                monster_bullets.remove(bullet)

            elif (
                pos.x < 0 or pos.x > 1280
                or pos.y < 0 or pos.y > 720
            ):
                monster_bullets.remove(bullet)

        # -------------------- Monster Touches Hero --------------------

        collision_timer = max(0, collision_timer - dt)

        if (
            monster_pos.distance_to(player_pos)
            < monster_radius + player_radius
            and collision_timer == 0
        ):
            player_hp -= 10
            collision_timer = 0.7

        # -------------------- Monster Defeated --------------------

        if monster_hp <= 0:

            # Generate a reward at the monster's position
            spawn_reward(monster_pos)

            # Clear old bullets
            hero_bullets.clear()
            monster_bullets.clear()

            if level < max_level:
                level += 1
                setup_level()
            else:
                victory = True
                game_over = True

        # -------------------- Collect Rewards --------------------

        for reward in rewards[:]:

            if reward["pos"].distance_to(player_pos) < (
                player_radius + 18
            ):

                if reward["type"] == "health":
                    player_hp = min(100, player_hp + reward["value"])

                elif reward["type"] == "score":
                    score += reward["value"]

                rewards.remove(reward)

        # -------------------- Check Hero Health --------------------

        if player_hp <= 0:
            player_hp = 0
            victory = False
            game_over = True

    # ============================================================
    #                         RENDERING
    # ============================================================

    screen.fill((65, 15, 105))

    # -------------------- Draw Hero --------------------

    pygame.draw.circle(
        screen, (255, 40, 40), player_pos, player_radius
    )

    pygame.draw.circle(
        screen, "black", player_pos, player_radius, 3
    )

    # -------------------- Draw Monster --------------------

    pygame.draw.circle(
        screen, (30, 200, 70), monster_pos, monster_radius
    )

    pygame.draw.circle(
        screen, "black", monster_pos, monster_radius, 4
    )

    # Monster eyes
    pygame.draw.circle(
        screen, "red",
        (int(monster_pos.x - 17), int(monster_pos.y - 10)), 8
    )

    pygame.draw.circle(
        screen, "red",
        (int(monster_pos.x + 17), int(monster_pos.y - 10)), 8
    )

    # Monster mouth
    pygame.draw.line(
        screen, "black",
        (int(monster_pos.x - 20), int(monster_pos.y + 20)),
        (int(monster_pos.x + 20), int(monster_pos.y + 20)),
        5
    )

    # -------------------- Draw Hero Bullets --------------------

    for bullet in hero_bullets:

        pygame.draw.circle(
            screen,
            bullet["color"],
            (int(bullet["pos"].x), int(bullet["pos"].y)),
            bullet["radius"]
        )

    # -------------------- Draw Monster Bullets --------------------

    for bullet in monster_bullets:

        pos, velocity = bullet

        pygame.draw.circle(
            screen, (255, 100, 40),
            (int(pos.x), int(pos.y)), 9
        )

    # -------------------- Draw Rewards --------------------

    for reward in rewards:

        x = int(reward["pos"].x)
        y = int(reward["pos"].y)

        if reward["type"] == "health":
            color = (0, 255, 100)
        else:
            color = (255, 215, 0)

        pygame.draw.circle(screen, color, (x, y), 18)
        pygame.draw.circle(screen, "white", (x, y), 18, 2)

        if reward["type"] == "health":
            draw_text("+", x - 7, y - 12, "black")
        else:
            draw_text("$", x - 7, y - 12, "black")

    # -------------------- Hero Health Bar --------------------

    pygame.draw.rect(screen, "black", (20, 20, 204, 24))

    pygame.draw.rect(
        screen, "red",
        (22, 22, 2 * player_hp, 20)
    )

    draw_text(f"Hero HP: {player_hp}", 20, 50)

    # -------------------- Monster Health Bar --------------------

    pygame.draw.rect(screen, "black", (900, 20, 204, 24))

    monster_bar_width = max(
        0, int(200 * monster_hp / (100 + (level - 1) * 50))
    )

    pygame.draw.rect(
        screen, "green",
        (902, 22, monster_bar_width, 20)
    )

    draw_text(f"Monster HP: {max(0, monster_hp)}", 900, 50)

    # -------------------- Game Information --------------------

    draw_text(f"Score: {score}", 550, 20)
    draw_text(f"Level: {level}/{max_level}", 550, 55)

    draw_text(
        f"Weapon: {weapons[current_weapon]['name']}",
        20, 100
    )

    draw_text("Move: Arrow Keys", 20, 140)
    draw_text("Weapons: 1 / 2 / 3", 20, 175)

    # -------------------- Game Over / Victory --------------------

    if game_over:

        if victory:
            draw_text("YOU WIN!", 555, 300, "yellow")
        else:
            draw_text("GAME OVER!", 530, 300, "red")

        draw_text(f"Final Score: {score}", 530, 345)
        draw_text("Press R to restart", 515, 390)
        draw_text("Press ESC to quit", 520, 430)

    pygame.display.flip()

pygame.quit()
