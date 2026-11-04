# Import the Pygame library to create the game window,
# draw game objects, handle keyboard input, and manage game events.
import pygame

# Import the random module to generate random numbers,
# choose random rewards, and determine monster positions.
import random

# Import the math module to perform mathematical operations
# such as calculations involving angles, distances, and geometry.
import math

# ============================================================
# 1. INITIALIZATION
# ============================================================

# Initialize all Pygame modules.
pygame.init()

# Create the game window.
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Monster vs Hero")

# Create a clock to control the frame rate.
clock = pygame.time.Clock()

# Font used to display game information.
font = pygame.font.SysFont(None, 36)


# ============================================================
# 2. HERO CONFIGURATION
# ============================================================

# Store the hero's position using a Vector2 object.
player_pos = pygame.Vector2(640, 620)

# Hero properties.
player_radius = 25
player_speed = 300
player_hp = 100


# ============================================================
# 3. MONSTER CONFIGURATION
# ============================================================

# Initial monster position.
monster_pos = pygame.Vector2(640, 100)

# Monster properties.
monster_radius = 50
monster_hp = 100
monster_speed = 55


# ============================================================
# 4. BULLETS CONFIGURATION
# ============================================================

# Lists containing the active bullets.
hero_bullets = []
monster_bullets = []

# Timers used to control shooting and collision intervals.
hero_shoot_timer = 0
monster_shoot_timer = 0
collision_timer = 0


# ============================================================
# 5. WEAPONS CONFIGURATION
# ============================================================

# Each weapon has different properties:
# damage: amount of damage caused by one bullet.
# speed: bullet movement speed.
# cooldown: delay between two shots.
# radius: bullet size.
# color: bullet color.

weapons = {
    1: {
        "name": "Normal",
        "damage": 10,
        "speed": 500,
        "cooldown": 0.25,
        "radius": 8,
        "color": "yellow"
    },

    2: {
        "name": "Rapid Fire",
        "damage": 5,
        "speed": 600,
        "cooldown": 0.10,
        "radius": 6,
        "color": "cyan"
    },

    3: {
        "name": "Power",
        "damage": 25,
        "speed": 350,
        "cooldown": 0.60,
        "radius": 12,
        "color": "orange"
    }
}

# Normal weapon is selected at the beginning.
current_weapon = 1


# ============================================================
# 6. REWARDS CONFIGURATION
# ============================================================

# List containing the rewards available in the game.
rewards = []

# There are two reward types:
# "health": restores the hero's health.
# "score": increases the player's score.


# ============================================================
# 7. GAME LEVELS CONFIGURATION
# ============================================================

# Initial game level and maximum number of levels.
level = 1
max_level = 3

# Player score.
score = 0

# Game state variables.
running = True
game_over = False
victory = False


# ============================================================
# 8. FUNCTIONS
# ============================================================

# ------------------------------------------------------------
# Function: draw_text()
# Purpose:
# Display text on the game screen.
#
# Parameters:
# text  : The message to display.
# x, y  : Screen coordinates.
# color : Text color.
# ------------------------------------------------------------

def draw_text(text, x, y, color="white"):

    # Convert the text into a drawable Pygame surface.
    image = font.render(text, True, color)

    # Display the text at the specified position.
    screen.blit(image, (x, y))


# ------------------------------------------------------------
# Function: spawn_reward()
# Purpose:
# Generate a random reward when the monster is defeated.
#
# Parameters:
# position : The position where the reward appears.
#
# The reward can be:
# Health reward (+25 HP)
# Score reward (+50 points)
# ------------------------------------------------------------

def spawn_reward(position):

    # Randomly choose between health and score rewards.
    reward_type = random.choice(["health", "score"])

    # Add the reward to the rewards list.
    rewards.append({
        "pos": position.copy(),
        "type": reward_type,
        "value": 25 if reward_type == "health" else 50
    })


# ------------------------------------------------------------
# Function: setup_level()
# Purpose:
# Initialize the monster for the current level.
#
# The monster becomes stronger at each new level.
# Its position is selected randomly.
# ------------------------------------------------------------

def setup_level():

    # Allow the function to modify global monster variables.
    global monster_pos, monster_hp, monster_speed
    global monster_radius, monster_shoot_timer

    # Generate a random position for the monster.
    monster_pos = pygame.Vector2(
        random.randint(100, 1180),
        random.randint(80, 250)
    )

    # Increase monster health according to the current level.
    monster_hp = 100 + (level - 1) * 50

    # Increase monster movement speed at each level.
    monster_speed = 55 + (level - 1) * 25

    # Set the monster's radius.
    monster_radius = 50

    # Reset the monster shooting timer.
    monster_shoot_timer = 0


# ============================================================
# 9. INITIAL GAME SETUP
# ============================================================

# Prepare the first monster before starting the game.
setup_level()


# ============================================================
# 10. MAIN GAME LOOP
# ============================================================

# The main loop runs continuously until the player quits.
while running:

    # Calculate elapsed time between frames in seconds.
    # This makes movement independent of the frame rate.
    dt = clock.tick(60) / 1000

    # --------------------------------------------------------
    # A. EVENT HANDLING
    # --------------------------------------------------------

    # Read all events generated by the user.
    for event in pygame.event.get():

        # Close the game when the window is closed.
        if event.type == pygame.QUIT:
            running = False

        # Handle keyboard events.
        if event.type == pygame.KEYDOWN:

            # ESC key: quit the game.
            if event.key == pygame.K_ESCAPE:
                running = False

            # Select the Normal weapon.
            if event.key == pygame.K_1:
                current_weapon = 1

            # Select the Rapid Fire weapon.
            if event.key == pygame.K_2:
                current_weapon = 2

            # Select the Power weapon.
            if event.key == pygame.K_3:
                current_weapon = 3

            # ------------------------------------------------
            # RESTART GAME
            # ------------------------------------------------

            # Press R to restart after victory or defeat.
            if event.key == pygame.K_r and game_over:

                # Reset hero position and health.
                player_pos = pygame.Vector2(640, 620)
                player_hp = 100

                # Remove all existing bullets and rewards.
                hero_bullets.clear()
                monster_bullets.clear()
                rewards.clear()

                # Reset all timers.
                hero_shoot_timer = 0
                monster_shoot_timer = 0
                collision_timer = 0

                # Reset score, level, and selected weapon.
                score = 0
                level = 1
                current_weapon = 1

                # Reset game state.
                game_over = False
                victory = False

                # Generate the first monster again.
                setup_level()

    # Get the current state of the keyboard.
    keys = pygame.key.get_pressed()

    # Update the game only when it is not over.
    if not game_over:

        # ====================================================
        # B. HERO MOVEMENT
        # ====================================================

        # Move the hero upward.
        if keys[pygame.K_UP]:
            player_pos.y -= player_speed * dt

        # Move the hero downward.
        if keys[pygame.K_DOWN]:
            player_pos.y += player_speed * dt

        # Move the hero to the left.
        if keys[pygame.K_LEFT]:
            player_pos.x -= player_speed * dt

        # Move the hero to the right.
        if keys[pygame.K_RIGHT]:
            player_pos.x += player_speed * dt

        # Keep the hero inside the game window.
        player_pos.x = max(25, min(1255, player_pos.x))
        player_pos.y = max(25, min(695, player_pos.y))


        # ====================================================
        # C. HERO SHOOTING
        # ====================================================

        # Get the properties of the selected weapon.
        weapon = weapons[current_weapon]

        # The hero shoots only while SPACE is held.
        if keys[pygame.K_SPACE]:

            # Increase the shooting timer.
            hero_shoot_timer += dt

            # Check whether the weapon cooldown has elapsed.
            if hero_shoot_timer >= weapon["cooldown"]:

                # Create a new bullet above the hero.
                hero_bullets.append({
                    "pos": pygame.Vector2(
                        player_pos.x,
                        player_pos.y - player_radius
                    ),

                    # Copy the selected weapon's properties.
                    "damage": weapon["damage"],
                    "speed": weapon["speed"],
                    "radius": weapon["radius"],
                    "color": weapon["color"]
                })

                # Reset the timer after shooting.
                hero_shoot_timer = 0

        else:
            # Reset the timer so the next shot can occur
            # immediately when SPACE is pressed.
            hero_shoot_timer = weapon["cooldown"]


        # ====================================================
        # D. MONSTER PURSUIT
        # ====================================================

        # Calculate the direction from the monster to the hero.
        direction = player_pos - monster_pos

        # Avoid normalizing a zero-length vector.
        if direction.length_squared() > 0:

            # Normalize the direction to obtain a unit vector.
            direction = direction.normalize()

            # Move the monster toward the hero.
            monster_pos += direction * monster_speed * dt


        # ====================================================
        # E. MONSTER SHOOTING
        # ====================================================

        # Increase the monster shooting timer.
        monster_shoot_timer += dt

        # Calculate the shooting interval.
        # Higher levels make the monster shoot more frequently.
        monster_cooldown = max(
            0.30,
            0.80 - (level - 1) * 0.15
        )

        # Check whether the monster can shoot.
        if monster_shoot_timer >= monster_cooldown:

            # Calculate the direction toward the hero.
            direction = player_pos - monster_pos

            # Normalize the direction vector.
            if direction.length_squared() > 0:
                direction = direction.normalize()

            # Create a monster bullet.
            # Its speed increases at higher levels.
            monster_bullets.append([
                monster_pos.copy(),
                direction * (220 + (level - 1) * 40)
            ])

            # Reset the monster shooting timer.
            monster_shoot_timer = 0


        # ====================================================
        # F. MOVE HERO BULLETS
        # ====================================================

        # Iterate over a copy because bullets may be removed.
        for bullet in hero_bullets[:]:

            # Move the bullet upward.
            bullet["pos"].y -= bullet["speed"] * dt

            # Check whether the bullet hits the monster.
            if bullet["pos"].distance_to(monster_pos) < (
                monster_radius + bullet["radius"]
            ):

                # Reduce monster health.
                monster_hp -= bullet["damage"]

                # Increase the score.
                score += 10

                # Remove the bullet after collision.
                hero_bullets.remove(bullet)

            # Remove bullets that leave the top of the screen.
            elif bullet["pos"].y < 0:
                hero_bullets.remove(bullet)


        # ====================================================
        # G. MOVE MONSTER BULLETS
        # ====================================================

        # Update each monster bullet.
        for bullet in monster_bullets[:]:

            # Extract the bullet position and velocity.
            pos, velocity = bullet

            # Update its position.
            pos += velocity * dt

            # Check whether the bullet hits the hero.
            if pos.distance_to(player_pos) < player_radius + 9:

                # Reduce hero health.
                player_hp -= 10

                # Remove the bullet after hitting the hero.
                monster_bullets.remove(bullet)

            # Remove bullets that leave the game window.
            elif (
                pos.x < 0 or pos.x > 1280
                or pos.y < 0 or pos.y > 720
            ):
                monster_bullets.remove(bullet)


        # ====================================================
        # H. MONSTER COLLISION WITH HERO
        # ====================================================

        # Decrease the collision timer.
        # This prevents continuous damage every frame.
        collision_timer = max(0, collision_timer - dt)

        # Check whether the monster touches the hero.
        if (
            monster_pos.distance_to(player_pos)
            < monster_radius + player_radius
            and collision_timer == 0
        ):

            # Reduce hero health.
            player_hp -= 10

            # Wait 0.7 seconds before allowing another
            # contact-damage event.
            collision_timer = 0.7


        # ====================================================
        # I. MONSTER DEFEATED
        # ====================================================

        # Check whether the monster has lost all its health.
        if monster_hp <= 0:

            # Generate a reward at the monster's position.
            spawn_reward(monster_pos)

            # Clear existing bullets.
            hero_bullets.clear()
            monster_bullets.clear()

            # Move to the next level if possible.
            if level < max_level:

                # Increase the level.
                level += 1

                # Generate a stronger monster.
                setup_level()

            else:
                # The final monster has been defeated.
                victory = True
                game_over = True


        # ====================================================
        # J. COLLECT REWARDS
        # ====================================================

        # Check all available rewards.
        for reward in rewards[:]:

            # Check whether the hero touches the reward.
            if reward["pos"].distance_to(player_pos) < (
                player_radius + 18
            ):

                # Health reward: restore health.
                if reward["type"] == "health":

                    # Maximum hero health is 100.
                    player_hp = min(
                        100,
                        player_hp + reward["value"]
                    )

                # Score reward: increase score.
                elif reward["type"] == "score":
                    score += reward["value"]

                # Remove the collected reward.
                rewards.remove(reward)


        # ====================================================
        # K. CHECK HERO HEALTH
        # ====================================================

        # Check whether the hero has lost all health.
        if player_hp <= 0:

            # Prevent negative health values.
            player_hp = 0

            # The player has lost.
            victory = False
            game_over = True


    # ========================================================
    # 11. RENDERING
    # ========================================================

    # Clear the screen before drawing the current frame.
    screen.fill((65, 15, 105))


    # --------------------------------------------------------
    # A. DRAW HERO
    # --------------------------------------------------------

    # Draw the hero as a red circle.
    pygame.draw.circle(
        screen,
        (255, 40, 40),
        player_pos,
        player_radius
    )

    # Draw a black outline around the hero.
    pygame.draw.circle(
        screen,
        "black",
        player_pos,
        player_radius,
        3
    )


    # --------------------------------------------------------
    # B. DRAW MONSTER
    # --------------------------------------------------------

    # Draw the monster as a green circle.
    pygame.draw.circle(
        screen,
        (30, 200, 70),
        monster_pos,
        monster_radius
    )

    # Draw a black outline around the monster.
    pygame.draw.circle(
        screen,
        "black",
        monster_pos,
        monster_radius,
        4
    )

    # Draw the monster's left eye.
    pygame.draw.circle(
        screen,
        "red",
        (int(monster_pos.x - 17), int(monster_pos.y - 10)),
        8
    )

    # Draw the monster's right eye.
    pygame.draw.circle(
        screen,
        "red",
        (int(monster_pos.x + 17), int(monster_pos.y - 10)),
        8
    )

    # Draw the monster's mouth.
    pygame.draw.line(
        screen,
        "black",
        (int(monster_pos.x - 20), int(monster_pos.y + 20)),
        (int(monster_pos.x + 20), int(monster_pos.y + 20)),
        5
    )


    # --------------------------------------------------------
    # C. DRAW HERO BULLETS
    # --------------------------------------------------------

    # Draw every bullet fired by the hero.
    for bullet in hero_bullets:

        pygame.draw.circle(
            screen,
            bullet["color"],
            (
                int(bullet["pos"].x),
                int(bullet["pos"].y)
            ),
            bullet["radius"]
        )


    # --------------------------------------------------------
    # D. DRAW MONSTER BULLETS
    # --------------------------------------------------------

    # Draw every bullet fired by the monster.
    for bullet in monster_bullets:

        # Extract the bullet position and velocity.
        pos, velocity = bullet

        pygame.draw.circle(
            screen,
            (255, 100, 40),
            (int(pos.x), int(pos.y)),
            9
        )


    # --------------------------------------------------------
    # E. DRAW REWARDS
    # --------------------------------------------------------

    # Draw all rewards currently available.
    for reward in rewards:

        # Convert reward coordinates to integers.
        x = int(reward["pos"].x)
        y = int(reward["pos"].y)

        # Choose a color according to the reward type.
        if reward["type"] == "health":
            color = (0, 255, 100)
        else:
            color = (255, 215, 0)

        # Draw the reward circle and its white outline.
        pygame.draw.circle(
            screen,
            color,
            (x, y),
            18
        )

        pygame.draw.circle(
            screen,
            "white",
            (x, y),
            18,
            2
        )

        # Display the reward symbol.
        if reward["type"] == "health":
            draw_text("+", x - 7, y - 12, "black")
        else:
            draw_text("$", x - 7, y - 12, "black")


    # --------------------------------------------------------
    # F. DRAW HERO HEALTH BAR
    # --------------------------------------------------------

    # Draw the black background of the health bar.
    pygame.draw.rect(
        screen,
        "black",
        (20, 20, 204, 24)
    )

    # Draw the red part according to the hero's health.
    pygame.draw.rect(
        screen,
        "red",
        (22, 22, 2 * player_hp, 20)
    )

    # Display the numerical health value.
    draw_text(
        f"Hero HP: {player_hp}",
        20,
        50
    )


    # --------------------------------------------------------
    # G. DRAW MONSTER HEALTH BAR
    # --------------------------------------------------------

    # Draw the black background of the monster health bar.
    pygame.draw.rect(
        screen,
        "black",
        (900, 20, 204, 24)
    )

    # Calculate the monster's health bar width.
    # Maximum monster health depends on the current level.
    monster_bar_width = max(
        0,
        int(
            200 * monster_hp /
            (100 + (level - 1) * 50)
        )
    )

    # Draw the green health bar.
    pygame.draw.rect(
        screen,
        "green",
        (902, 22, monster_bar_width, 20)
    )

    # Display the monster's health.
    draw_text(
        f"Monster HP: {max(0, monster_hp)}",
        900,
        50
    )


    # --------------------------------------------------------
    # H. DISPLAY GAME INFORMATION
    # --------------------------------------------------------

    # Display the player's score.
    draw_text(
        f"Score: {score}",
        550,
        20
    )

    # Display the current level.
    draw_text(
        f"Level: {level}/{max_level}",
        550,
        55
    )

    # Display the selected weapon.
    draw_text(
        f"Weapon: {weapons[current_weapon]['name']}",
        20,
        100
    )

    # Display keyboard instructions.
    draw_text(
        "Move: Arrow Keys",
        20,
        140
    )

    draw_text(
        "Weapons: 1 / 2 / 3",
        20,
        175
    )


    # --------------------------------------------------------
    # I. GAME OVER / VICTORY SCREEN
    # --------------------------------------------------------

    # Display the final message when the game ends.
    if game_over:

        # Display victory message.
        if victory:
            draw_text(
                "YOU WIN!",
                555,
                300,
                "yellow"
            )

        # Display defeat message.
        else:
            draw_text(
                "GAME OVER!",
                530,
                300,
                "red"
            )

        # Display final score.
        draw_text(
            f"Final Score: {score}",
            530,
            345
        )

        # Display restart instruction.
        draw_text(
            "Press R to restart",
            515,
            390
        )

        # Display quit instruction.
        draw_text(
            "Press ESC to quit",
            520,
            430
        )


    # ========================================================
    # 12. UPDATE DISPLAY
    # ========================================================

    # Update the display with everything drawn in this frame.
    pygame.display.flip()


# ============================================================
# 13. QUIT GAME
# ============================================================

# Close Pygame and release its resources.
pygame.quit()