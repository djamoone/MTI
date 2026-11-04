import pygame
import random

# Initialize all imported Pygame modules.
pygame.init()


# ============================================================
# CONFIGURATION
# ============================================================

# Window dimensions.
WIDTH = 1280
HEIGHT = 720

# Maximum number of frames displayed per second.
FPS = 60

# RGB colors used throughout the game.
BACKGROUND = (65, 15, 105)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 40, 40)
GREEN = (30, 200, 70)
ORANGE = (255, 100, 40)
YELLOW = (255, 215, 0)


# Dictionary containing the characteristics of each weapon.
# Each weapon has a unique ID and a set of attributes.
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

# The Weapon class represents a weapon that can be used by the hero.
# It stores weapon information and creates bullets according to
# the selected weapon's characteristics.

class Weapon:

    # Constructor: initializes a weapon using its unique ID.
    def __init__(self, weapon_id):

        # Store the weapon identifier.
        self.weapon_id = weapon_id

        # Retrieve the corresponding weapon configuration.
        self.data = WEAPONS[weapon_id]

    # Property: returns the weapon's name.
    # @property allows us to access name like an attribute:
    # hero.weapon.name instead of hero.weapon.name().
    @property
    def name(self):
        return self.data["name"]

    # Creates a bullet using the current weapon's properties.
    # position represents the initial position of the bullet.
    def create_bullet(self, position):

        # Return a new Bullet object.
        return Bullet(
            position=position,

            # Negative Y velocity makes the bullet move upward.
            velocity=pygame.Vector2(0, -self.data["speed"]),

            # Copy the weapon's damage.
            damage=self.data["damage"],

            # Copy the weapon's bullet radius.
            radius=self.data["radius"],

            # Copy the weapon's color.
            color=self.data["color"],

            # Identify the hero as the bullet owner.
            owner="hero",
        )


# ============================================================
# BULLET CLASS
# ============================================================

# The Bullet class represents every projectile in the game.
# Both the hero and the monster use this class.
# The owner attribute determines who fired the bullet.

class Bullet:

    # Constructor: initializes a bullet with all its properties.
    def __init__(
        self, position, velocity, damage, radius, color, owner
    ):

        # Store the bullet's position as a Vector2 object.
        self.position = pygame.Vector2(position)

        # Store its movement direction and speed.
        self.velocity = pygame.Vector2(velocity)

        # Amount of damage inflicted when hitting a target.
        self.damage = damage

        # Bullet size.
        self.radius = radius

        # Bullet appearance.
        self.color = color

        # Identify the entity that created this bullet.
        self.owner = owner

        # Indicates whether the bullet is still active.
        self.alive = True

    # Updates the bullet's position according to elapsed time.
    # dt represents the time elapsed since the previous frame.
    def update(self, dt):

        # Calculate the new position using velocity and time.
        # This makes movement independent of the FPS.
        self.position += self.velocity * dt

        # Check whether the bullet has left the game window.
        # If so, mark it as inactive.
        if (
            self.position.x < -self.radius
            or self.position.x > WIDTH + self.radius
            or self.position.y < -self.radius
            or self.position.y > HEIGHT + self.radius
        ):
            self.alive = False

    # Checks whether the bullet collides with another object.
    # position: target's position.
    # target_radius: target's collision radius.
    def hits(self, position, target_radius):

        # Calculate the distance between the bullet and target.
        # A collision occurs when the distance is smaller than
        # the sum of their radii.
        return (
            self.position.distance_to(position)
            < self.radius + target_radius
        )

    # Displays the bullet on the screen.
    def draw(self, screen):

        # Draw a filled circle representing the bullet.
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.position.x), int(self.position.y)),
            self.radius,
        )


# ============================================================
# HERO CLASS
# ============================================================

# The Hero class represents the player-controlled character.
# It manages movement, health, weapons, shooting and appearance.

class Hero:

    # Constructor: initializes the hero and its attributes.
    def __init__(self):

        # Hero's collision radius.
        self.radius = 25

        # Hero's movement speed in pixels per second.
        self.speed = 300

        # Maximum health points.
        self.max_hp = 100

        # Current health points.
        self.hp = self.max_hp

        # Initial position of the hero.
        self.position = pygame.Vector2(640, 620)

        # Assign the first weapon by default.
        self.weapon = Weapon(1)

        # Timer used to control the shooting frequency.
        self.shoot_timer = 0

    # Handles movement using the keyboard.
    # keys contains the current keyboard state.
    # dt represents elapsed time between frames.
    def move(self, keys, dt):

        # Initialize a movement direction with no displacement.
        direction = pygame.Vector2(0, 0)

        # Move upward.
        if keys[pygame.K_UP]:
            direction.y -= 1

        # Move downward.
        if keys[pygame.K_DOWN]:
            direction.y += 1

        # Move left.
        if keys[pygame.K_LEFT]:
            direction.x -= 1

        # Move right.
        if keys[pygame.K_RIGHT]:
            direction.x += 1

        # Normalize the direction vector.
        # This prevents the hero from moving faster diagonally.
        if direction.length_squared() > 0:
            direction = direction.normalize()

            # Update the hero's position.
            self.position += direction * self.speed * dt

        # Restrict horizontal movement to the screen boundaries.
        self.position.x = max(
            self.radius,
            min(WIDTH - self.radius, self.position.x),
        )

        # Restrict vertical movement to the screen boundaries.
        self.position.y = max(
            self.radius,
            min(HEIGHT - self.radius, self.position.y),
        )

    # Controls the hero's shooting mechanism.
    # dt: elapsed time.
    # shooting: indicates whether SPACE is being held.
    def update_shooting(self, dt, shooting):

        # Increase the shooting timer.
        self.shoot_timer += dt

        # A bullet can only be created when:
        # 1. The player is holding SPACE.
        # 2. The weapon cooldown has elapsed.
        if (
            shooting
            and self.shoot_timer >= self.weapon.data["cooldown"]
        ):

            # Reset the timer after shooting.
            self.shoot_timer = 0

            # Set the bullet's initial position above the hero.
            bullet_position = pygame.Vector2(
                self.position.x,
                self.position.y - self.radius,
            )

            # Create and return a bullet using the current weapon.
            return self.weapon.create_bullet(bullet_position)

        # Return None when no bullet is created.
        return None

    # Reduces the hero's health when damage is received.
    def take_damage(self, amount):

        # Health cannot become negative.
        self.hp = max(0, self.hp - amount)

    # Restores the hero's health.
    def heal(self, amount):

        # Health cannot exceed the maximum health.
        self.hp = min(self.max_hp, self.hp + amount)

    # Changes the currently equipped weapon.
    def change_weapon(self, weapon_id):

        # Verify that the selected weapon exists.
        if weapon_id in WEAPONS:

            # Create a new Weapon object.
            self.weapon = Weapon(weapon_id)

            # Reset the shooting timer.
            self.shoot_timer = 0

    # Draws the hero on the screen.
    def draw(self, screen):

        # Draw the hero's body.
        pygame.draw.circle(
            screen, RED, self.position, self.radius
        )

        # Draw a black outline around the hero.
        pygame.draw.circle(
            screen, BLACK, self.position, self.radius, 3
        )


# ============================================================
# MONSTER CLASS
# ============================================================

# The Monster class represents the enemy controlled by the game.
# It follows the hero, shoots projectiles and becomes stronger
# when the player advances to a new level.

class Monster:

    # Constructor: initializes a monster according to the level.
    def __init__(self, level):

        # Monster's collision radius.
        self.radius = 50

        # Generate a random initial position.
        self.position = pygame.Vector2(
            random.randint(100, WIDTH - 100),
            random.randint(80, 250),
        )

        # Increase maximum health with each new level.
        self.max_hp = 100 + (level - 1) * 50

        # Set current health to maximum health.
        self.hp = self.max_hp

        # Increase movement speed with each level.
        self.speed = 55 + (level - 1) * 25

        # Timer controlling the monster's shooting frequency.
        self.shoot_timer = 0

        # Store the current level.
        self.level = level

    # Makes the monster move toward a target.
    # target represents the hero's position.
    def move_toward(self, target, dt):

        # Calculate the direction from the monster to the target.
        direction = target - self.position

        # Normalize the direction to obtain a unit vector.
        if direction.length_squared() > 0:
            direction = direction.normalize()

            # Move the monster toward the hero.
            self.position += direction * self.speed * dt

    # Creates a projectile directed toward the hero.
    def shoot(self, target, dt):

        # Increase the shooting timer.
        self.shoot_timer += dt

        # Calculate the cooldown.
        # Higher levels reduce the time between shots.
        # max() guarantees a minimum cooldown of 0.30 seconds.
        cooldown = max(
            0.30, 0.80 - (self.level - 1) * 0.15
        )

        # Wait until the cooldown has elapsed.
        if self.shoot_timer < cooldown:
            return None

        # Reset the timer before creating a new bullet.
        self.shoot_timer = 0

        # Calculate the direction toward the hero.
        direction = target - self.position

        # Avoid normalization of a zero-length vector.
        if direction.length_squared() == 0:
            direction = pygame.Vector2(0, 1)
        else:
            direction = direction.normalize()

        # Increase projectile speed at higher levels.
        bullet_speed = 220 + (self.level - 1) * 40

        # Return a new monster projectile.
        return Bullet(
            position=self.position,
            velocity=direction * bullet_speed,
            damage=10,
            radius=9,
            color=ORANGE,
            owner="monster",
        )

    # Reduces monster health after being hit.
    def take_damage(self, amount):

        # Prevent health from becoming negative.
        self.hp = max(0, self.hp - amount)

    # Displays the monster and its facial features.
    def draw(self, screen):

        # Draw the monster's body.
        pygame.draw.circle(
            screen, GREEN, self.position, self.radius
        )

        # Draw the black outline.
        pygame.draw.circle(
            screen, BLACK, self.position, self.radius, 4
        )

        # ---------------- MONSTER EYES ----------------

        # Draw the left eye.
        pygame.draw.circle(
            screen,
            "red",
            (
                int(self.position.x - 17),
                int(self.position.y - 10),
            ),
            8,
        )

        # Draw the right eye.
        pygame.draw.circle(
            screen,
            "red",
            (
                int(self.position.x + 17),
                int(self.position.y - 10),
            ),
            8,
        )

        # ---------------- MONSTER MOUTH ----------------

        # Draw a horizontal line representing the mouth.
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

# The Reward class represents collectible objects.
# A reward can restore the hero's health or increase the score.

class Reward:

    # Constructor: initializes a reward at a given position.
    def __init__(self, position):

        # Store the reward's position.
        self.position = pygame.Vector2(position)

        # Randomly select the reward type.
        self.reward_type = random.choice(["health", "score"])

        # Assign a value depending on the reward type.
        self.value = 25 if self.reward_type == "health" else 50

        # Reward's collision radius.
        self.radius = 18

    # Applies the reward when the hero collects it.
    # hero: the player object.
    # game: the current Game object.
    def collect(self, hero, game):

        # Restore health if the reward is a health bonus.
        if self.reward_type == "health":
            hero.heal(self.value)

        # Otherwise, increase the player's score.
        else:
            game.score += self.value

    # Draws the reward on the screen.
    def draw(self, screen, font):

        # Convert coordinates into integers for drawing.
        x = int(self.position.x)
        y = int(self.position.y)

        # Choose the color and symbol according to reward type.
        if self.reward_type == "health":
            color = (0, 255, 100)
            symbol = "+"
        else:
            color = YELLOW
            symbol = "$"

        # Draw the reward's circular background.
        pygame.draw.circle(
            screen, color, (x, y), self.radius
        )

        # Draw a white outline.
        pygame.draw.circle(
            screen, WHITE, (x, y), self.radius, 2
        )

        # Render the reward symbol as text.
        image = font.render(symbol, True, BLACK)

        # Center the symbol inside the reward.
        screen.blit(image, image.get_rect(center=(x, y)))


# ============================================================
# GAME CLASS
# ============================================================

# The Game class is the central controller of the application.
# It manages:
# - Game initialization.
# - Events and keyboard input.
# - Game logic and object interactions.
# - Collisions and level progression.
# - Rendering and user interface.
# - The main game loop.

class Game:

    # Constructor: initializes the game environment.
    def __init__(self):

        # Create the game window.
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        # Set the window title.
        pygame.display.set_caption("Monster vs Hero")

        # Create a clock to control the frame rate.
        self.clock = pygame.time.Clock()

        # Create fonts for normal and large text.
        self.font = pygame.font.SysFont(None, 36)
        self.big_font = pygame.font.SysFont(None, 64)

        # Indicates whether the game is running.
        self.running = True

        # Define the maximum number of levels.
        self.max_level = 3

        # Initialize or reset the game state.
        self.reset_game()

    # Initializes all gameplay objects and variables.
    # This method is also used when restarting the game.
    def reset_game(self):

        # Create a new hero.
        self.hero = Hero()

        # Reset the level and score.
        self.level = 1
        self.score = 0

        # Create the first monster.
        self.monster = Monster(self.level)

        # Lists containing active projectiles.
        self.hero_bullets = []
        self.monster_bullets = []

        # List containing collectible rewards.
        self.rewards = []

        # Timer preventing continuous collision damage.
        self.collision_timer = 0

        # Reset game states.
        self.paused = False
        self.game_over = False
        self.victory = False

    # Prepares the game for the next level.
    def setup_next_level(self):

        # Remove all existing projectiles.
        self.hero_bullets.clear()
        self.monster_bullets.clear()

        # Increase the level.
        self.level += 1

        # Create a stronger monster.
        self.monster = Monster(self.level)

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    # Processes keyboard events and window events.
    def handle_events(self):

        # Retrieve all pending Pygame events.
        for event in pygame.event.get():

            # Close the game when the window is closed.
            if event.type == pygame.QUIT:
                self.running = False

            # Process individual key presses.
            elif event.type == pygame.KEYDOWN:

                # ESC: pause or resume the game.
                if event.key == pygame.K_ESCAPE:

                    # During gameplay, toggle the pause state.
                    if not self.game_over:
                        self.paused = not self.paused

                    # After the game ends, ESC quits.
                    else:
                        self.running = False

                # Q: quit the game.
                elif event.key == pygame.K_q:
                    self.running = False

                # R: restart after victory or defeat.
                elif event.key == pygame.K_r:
                    if self.game_over:
                        self.reset_game()

                # Weapon selection is available only during gameplay.
                elif not self.paused and not self.game_over:

                    # Select the Normal weapon.
                    if event.key == pygame.K_1:
                        self.hero.change_weapon(1)

                    # Select the Rapid Fire weapon.
                    elif event.key == pygame.K_2:
                        self.hero.change_weapon(2)

                    # Select the Power weapon.
                    elif event.key == pygame.K_3:
                        self.hero.change_weapon(3)

    # --------------------------------------------------------
    # UPDATE GAME
    # --------------------------------------------------------

    # Updates all game objects and applies the game rules.
    # dt represents the elapsed time between two frames.
    def update(self, dt):

        # Stop updating gameplay when paused or finished.
        if self.paused or self.game_over:
            return

        # Retrieve the current keyboard state.
        keys = pygame.key.get_pressed()

        # ---------------- HERO MOVEMENT ----------------

        # Update the hero's position.
        self.hero.move(keys, dt)

        # ---------------- HERO SHOOTING ----------------

        # SPACE must remain pressed to shoot.
        shooting = keys[pygame.K_SPACE]

        # Ask the hero to create a bullet if possible.
        hero_bullet = self.hero.update_shooting(dt, shooting)

        # Add the new bullet to the hero's projectile list.
        if hero_bullet is not None:
            self.hero_bullets.append(hero_bullet)

        # ---------------- MONSTER MOVEMENT ----------------

        # Make the monster follow the hero.
        self.monster.move_toward(self.hero.position, dt)

        # ---------------- MONSTER SHOOTING ----------------

        # Ask the monster to shoot toward the hero.
        monster_bullet = self.monster.shoot(
            self.hero.position, dt
        )

        # Add the new projectile to the monster's list.
        if monster_bullet is not None:
            self.monster_bullets.append(monster_bullet)

        # ---------------- HERO BULLETS ----------------

        # Update every bullet created by the hero.
        for bullet in self.hero_bullets:

            # Move the bullet and check screen boundaries.
            bullet.update(dt)

            # Check whether the bullet hits the monster.
            if (
                bullet.alive
                and bullet.hits(
                    self.monster.position,
                    self.monster.radius,
                )
            ):

                # Reduce the monster's health.
                self.monster.take_damage(bullet.damage)

                # Increase the score for a successful hit.
                self.score += 10

                # Remove the bullet after the collision.
                bullet.alive = False

        # Keep only bullets that are still active.
        self.hero_bullets = [
            bullet for bullet in self.hero_bullets
            if bullet.alive
        ]

        # ---------------- MONSTER BULLETS ----------------

        # Update every bullet created by the monster.
        for bullet in self.monster_bullets:

            # Move the bullet.
            bullet.update(dt)

            # Check whether it hits the hero.
            if (
                bullet.alive
                and bullet.hits(
                    self.hero.position,
                    self.hero.radius,
                )
            ):

                # Reduce the hero's health.
                self.hero.take_damage(bullet.damage)

                # Remove the projectile after hitting the hero.
                bullet.alive = False

        # Remove inactive monster projectiles.
        self.monster_bullets = [
            bullet for bullet in self.monster_bullets
            if bullet.alive
        ]

        # ---------------- PHYSICAL COLLISION ----------------

        # Decrease the collision protection timer.
        # max() prevents the timer from becoming negative.
        self.collision_timer = max(
            0, self.collision_timer - dt
        )

        # Calculate the distance between the hero and monster.
        distance = self.monster.position.distance_to(
            self.hero.position
        )

        # Check whether their collision circles overlap.
        if (
            distance < self.monster.radius + self.hero.radius
            and self.collision_timer <= 0
        ):

            # Inflict physical collision damage.
            self.hero.take_damage(10)

            # Wait 0.7 seconds before allowing another collision hit.
            self.collision_timer = 0.7

        # ---------------- MONSTER DEFEATED ----------------

        # Check whether the monster has no remaining health.
        if self.monster.hp <= 0:

            # Generate a reward at the monster's last position.
            self.rewards.append(Reward(self.monster.position))

            # Move to the next level if available.
            if self.level < self.max_level:
                self.setup_next_level()

            # Otherwise, the player wins.
            else:
                self.victory = True
                self.game_over = True

        # ---------------- COLLECT REWARDS ----------------

        # Use a copy of the list to safely remove collected rewards.
        for reward in self.rewards[:]:

            # Check the distance between the hero and the reward.
            if (
                reward.position.distance_to(self.hero.position)
                < self.hero.radius + reward.radius
            ):

                # Apply the reward.
                reward.collect(self.hero, self)

                # Remove the collected reward.
                self.rewards.remove(reward)

        # ---------------- HERO DEFEATED ----------------

        # Check whether the hero has lost all health.
        if self.hero.hp <= 0:

            # End the game and indicate defeat.
            self.game_over = True
            self.victory = False

    # --------------------------------------------------------
    # DRAWING HELPERS
    # --------------------------------------------------------

    # Displays text at a specific position.
    # big selects between normal and large fonts.
    def draw_text(
        self, text, x, y, color=WHITE, big=False
    ):

        # Choose the appropriate font.
        selected_font = self.big_font if big else self.font

        # Convert the string into a drawable Pygame surface.
        image = selected_font.render(text, True, color)

        # Display the text at the requested coordinates.
        self.screen.blit(image, (x, y))

    # Draws a health bar for the hero or monster.
    def draw_health_bar(
        self, x, y, width, height, hp, max_hp, color
    ):

        # Draw the background of the health bar.
        pygame.draw.rect(
            self.screen, BLACK, (x, y, width, height)
        )

        # Calculate the remaining health percentage.
        # The result is restricted between 0 and 1.
        ratio = max(0, min(1, hp / max_hp))

        # Calculate the width of the colored health section.
        fill_width = int((width - 4) * ratio)

        # Draw the current health.
        pygame.draw.rect(
            self.screen,
            color,
            (x + 2, y + 2, fill_width, height - 4),
        )

    # Displays the game's information and controls.
    # HUD means Heads-Up Display.
    def draw_hud(self):

        # ---------------- HERO HEALTH ----------------

        # Draw the hero's health bar.
        self.draw_health_bar(
            20, 20, 204, 24,
            self.hero.hp, self.hero.max_hp, RED
        )

        # Display the hero's current health.
        self.draw_text(
            f"Hero HP: {self.hero.hp}", 20, 50
        )

        # ---------------- MONSTER HEALTH ----------------

        # Draw the monster's health bar.
        self.draw_health_bar(
            900, 20, 204, 24,
            self.monster.hp, self.monster.max_hp, GREEN
        )

        # Display the monster's current health.
        self.draw_text(
            f"Monster HP: {max(0, self.monster.hp)}",
            900, 50
        )

        # ---------------- SCORE AND LEVEL ----------------

        # Display the player's score.
        self.draw_text(f"Score: {self.score}", 550, 20)

        # Display current level and maximum level.
        self.draw_text(
            f"Level: {self.level}/{self.max_level}",
            550, 55
        )

        # ---------------- GAME CONTROLS ----------------

        # Display the currently selected weapon.
        self.draw_text(
            f"Weapon: {self.hero.weapon.name}", 20, 100
        )

        # Explain the movement controls.
        self.draw_text("Move: Arrow Keys", 20, 140)

        # Explain the shooting control.
        self.draw_text("Shoot: Hold SPACE", 20, 175)

        # Explain the weapon selection controls.
        self.draw_text("Weapons: 1 / 2 / 3", 20, 210)

        # Explain the pause control.
        self.draw_text("ESC: Pause / Resume", 20, 245)

    # Creates a transparent overlay with a title and messages.
    # Used for pause, victory and defeat screens.
    def draw_overlay(self, title, color, lines):

        # Create a transparent surface covering the entire window.
        overlay = pygame.Surface(
            (WIDTH, HEIGHT), pygame.SRCALPHA
        )

        # Fill it with semi-transparent black.
        # The alpha value controls transparency.
        overlay.fill((0, 0, 0, 175))

        # Display the overlay above the game screen.
        self.screen.blit(overlay, (0, 0))

        # Render the main title.
        title_image = self.big_font.render(
            title, True, color
        )

        # Center the title horizontally.
        self.screen.blit(
            title_image,
            title_image.get_rect(
                center=(WIDTH // 2, 280)
            ),
        )

        # Display each message below the title.
        for index, line in enumerate(lines):

            # Convert the message into a Pygame surface.
            image = self.font.render(line, True, WHITE)

            # Center the message and separate each line.
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

    # Draws all objects and interface elements.
    # This method is responsible for visual presentation.
    def draw(self):

        # Clear the previous frame with the background color.
        self.screen.fill(BACKGROUND)

        # Draw the hero and monster.
        self.hero.draw(self.screen)
        self.monster.draw(self.screen)

        # Draw every active hero projectile.
        for bullet in self.hero_bullets:
            bullet.draw(self.screen)

        # Draw every active monster projectile.
        for bullet in self.monster_bullets:
            bullet.draw(self.screen)

        # Draw all available rewards.
        for reward in self.rewards:
            reward.draw(self.screen, self.font)

        # Display the health bars, score, level and controls.
        self.draw_hud()

        # ---------------- PAUSE SCREEN ----------------

        # Display the pause overlay when the game is paused.
        if self.paused and not self.game_over:

            self.draw_overlay(
                "PAUSED",
                YELLOW,
                [
                    "Press ESC to resume",
                    "Press Q to quit",
                ],
            )

        # ---------------- END GAME SCREEN ----------------

        # Display the victory or defeat screen.
        elif self.game_over:

            # Select the title and color based on the result.
            if self.victory:
                title = "YOU WIN!"
                color = YELLOW
            else:
                title = "GAME OVER!"
                color = RED

            # Display the final score and available actions.
            self.draw_overlay(
                title,
                color,
                [
                    f"Final Score: {self.score}",
                    "Press R to restart",
                    "Press Q or ESC to quit",
                ],
            )

        # Update the display to show the completed frame.
        pygame.display.flip()

    # --------------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------------

    # Main method responsible for executing the game.
    def run(self):

        # Continue running while the game is active.
        while self.running:

            # Calculate elapsed time in seconds.
            # The 0.05 limit avoids huge movements after a lag.
            dt = min(self.clock.tick(FPS) / 1000, 0.05)

            # Process keyboard and window events.
            self.handle_events()

            # Update movement, shooting, collisions and game state.
            self.update(dt)

            # Render all visual elements.
            self.draw()

        # Release Pygame resources when the game closes.
        pygame.quit()


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

# This condition ensures that the game starts only when
# this Python file is executed directly.
# It will not automatically start if imported as a module.

if __name__ == "__main__":

    # Create an instance of the Game class.
    game = Game()

    # Start the main game loop.
    game.run()