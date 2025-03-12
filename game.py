import pygame
import random
import time

# Initialize Pygame and mixer
pygame.init()
try:
    pygame.mixer.init()
    sound_enabled = True
except pygame.error as e:
    print(f"Warning: Could not initialize mixer: {e}")
    print("Game will run without sound.")
    sound_enabled = False

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Race Car Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load assets with error handling
try:
    player_img = pygame.image.load("sport-car-isolated-on-transparent-background-3d-rendering-illustration-free-png.webp").convert_alpha()
    enemy_img = pygame.image.load("realistic-sport-car-isolated-on-background-3d-rendering-illustration-png.webp").convert_alpha()
    road_img = pygame.image.load("pngtree-straight-road-png-image_3252059.jpg").convert()
    player_img = pygame.transform.scale(player_img, (50, 100))
    enemy_img = pygame.transform.scale(enemy_img, (50, 100))
    road_img = pygame.transform.scale(road_img, (WIDTH, HEIGHT))
    if sound_enabled:
        pygame.mixer.music.load("background_music.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        crash_sound = pygame.mixer.Sound("crash.wav")
        enemy_spawn_sound = pygame.mixer.Sound("spawn.wav")
except pygame.error as e:
    print(f"Error loading assets: {e}")
    pygame.quit()
    exit()

# Player car
player_width, player_height = player_img.get_size()
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 10
player_speed = 5

# Enemy cars
enemy_width, enemy_height = enemy_img.get_size()
enemy_speed = 3
enemies = [{"x": random.randint(0, WIDTH - enemy_width), "y": -enemy_height} for _ in range(3)]

# Score and road
score = 0
start_time = time.time()
road_y = 0
road_speed = 3

# CRUD Functions
def create_score(score):
    with open("highscores.txt", "a") as file:
        file.write(f"{score}\n")

def read_scores():
    try:
        with open("highscores.txt", "r") as file:
            return sorted([int(line.strip()) for line in file], reverse=True)[:5]
    except FileNotFoundError:
        return []

def update_score(old_score, new_score):
    scores = read_scores()
    if old_score in scores:
        scores[scores.index(old_score)] = new_score
        with open("highscores.txt", "w") as file:
            for s in scores:
                file.write(f"{s}\n")

def delete_score(score_to_delete):
    scores = read_scores()
    if score_to_delete in scores:
        scores.remove(score_to_delete)
        with open("highscores.txt", "w") as file:
            for s in scores:
                file.write(f"{s}\n")

# Menu function
def show_menu():
    menu_running = True
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 30)
    while menu_running:
        screen.blit(road_img, (0, 0))
        title = font.render("Race Car Game", True, WHITE)
        start_text = font.render("Press SPACE to Start", True, WHITE)
        instructions = small_font.render("Use LEFT/RIGHT arrows to move, avoid enemy cars!", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
        screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT//2 + 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return True
    return False

# High score screen
def show_high_scores(score):
    hs_running = True
    font = pygame.font.SysFont(None, 36)
    while hs_running:
        screen.blit(road_img, (0, 0))
        title = font.render("High Scores", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        scores = read_scores()
        for i, s in enumerate(scores):
            score_text = font.render(f"{i+1}. {s}", True, WHITE)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 150 + i*40))
        last_score = font.render(f"Your Score: {score}", True, WHITE)
        screen.blit(last_score, (WIDTH//2 - last_score.get_width()//2, 400))
        restart_text = font.render("Press SPACE to Restart", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 450))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return True
    return False

# Main game loop
game_running = True
while game_running:
    if not show_menu():
        break

    # Reset game state
    player_x = WIDTH // 2 - player_width // 2
    enemies = [{"x": random.randint(0, WIDTH - enemy_width), "y": -enemy_height} for _ in range(3)]
    start_time = time.time()
    score = 0
    road_y = 0

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game_running = False

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
            player_x += player_speed

        # Enemy movement (AI)
        for enemy in enemies:
            distance_to_player = abs(enemy["y"] - player_y)
            dynamic_speed = enemy_speed + (1 - distance_to_player / HEIGHT) * 2
            enemy["y"] += dynamic_speed
            if enemy["x"] < player_x:
                enemy["x"] += min(enemy_speed, player_x - enemy["x"])
            elif enemy["x"] > player_x:
                enemy["x"] -= min(enemy_speed, enemy["x"] - player_x)
            if enemy["x"] < 0:
                enemy["x"] = 0
            if enemy["x"] > WIDTH - enemy_width:
                enemy["x"] = WIDTH - enemy_width
            if enemy["y"] > HEIGHT:
                enemy["y"] = -enemy_height
                enemy["x"] = random.randint(0, WIDTH - enemy_width)
                if sound_enabled:
                    pygame.mixer.Sound.play(enemy_spawn_sound)

        # Score update
        score = int(time.time() - start_time)

        # Collision
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy["x"], enemy["y"], enemy_width, enemy_height)
            if player_rect.colliderect(enemy_rect):
                if sound_enabled:
                    pygame.mixer.Sound.play(crash_sound)
                create_score(score)
                pygame.time.delay(1000)
                running = False

        # Draw
        road_y += road_speed
        if road_y >= HEIGHT:
            road_y = 0
        screen.blit(road_img, (0, road_y))
        screen.blit(road_img, (0, road_y - HEIGHT))
        screen.blit(player_img, (player_x, player_y))
        for enemy in enemies:
            screen.blit(enemy_img, (enemy["x"], enemy["y"]))

        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    if game_running and not show_high_scores(score):
        break

pygame.quit()