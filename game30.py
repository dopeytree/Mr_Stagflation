import pygame
import random
import sys
import numpy as np
import time

# Initialize Pygame
pygame.init()
pygame.font.init()  # Ensure font module is initialized

# Fonts (load Matrix Code NFI from the fonts directory)
try:
    font = pygame.font.SysFont("Menlo", 27)  # Main font for "SPACE DOGE", splash screen text
    small_font = pygame.font.Font("/Users/ed/Downloads/Game/fonts/MatrixCodeNFI.ttf", 16)  # Smaller font for departments and Matrix characters
    big_font = pygame.font.SysFont("Menlo", 54)  # Larger font for splash screen "DOGE" and "Paused"
except FileNotFoundError:
    print("Matrix font not found, falling back to Menlo")
    font = pygame.font.SysFont("Menlo", 27)
    small_font = pygame.font.SysFont("Menlo", 16)
    big_font = pygame.font.SysFont("Menlo", 54)

# Screen settings
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paperwork Invaders")

# Colors
RED = (255, 0, 0)         # Unused now, but kept for reference
WHITE = (255, 255, 255)   # Unused now, but kept for reference
YELLOW = (255, 255, 0)    # Unused now, but kept for reference
BLACK = (0, 0, 0)         # Background for text boxes
ORANGE = (255, 165, 0)    # Unused now, but kept for reference
TURQUOISE = (64, 224, 208)  # Unused now, but kept for reference
GOLD = (255, 215, 0)      # DOGE splash screen
BROWN = (165, 42, 42)     # Brown explosion for player hit
MATRIX_GREEN = (0, 200, 0)  # Matrix-inspired green for text

# Load background image
background_image = pygame.image.load("background.png").convert()  # Load your image
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Scale to 800x600

# Dim the background image by 65% (multiply RGB values by 0.35 for splash, 0.5 for game)
dimmed_background_splash = background_image.copy()
dimmed_background_game = background_image.copy()
for x in range(WIDTH):
    for y in range(HEIGHT):
        r, g, b, a = dimmed_background_splash.get_at((x, y))
        dimmed_background_splash.set_at((x, y), (int(r * 0.35), int(g * 0.35), int(b * 0.35), a))
        r, g, b, a = dimmed_background_game.get_at((x, y))
        dimmed_background_game.set_at((x, y), (int(r * 0.5), int(g * 0.5), int(b * 0.5), a))

# Matrix-like characters for the digital rain effect (avoiding squares)
MATRIX_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()-+=[]{}|;:,.<>?アィウェオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"

# Generate sound effects (unchanged from previous version)
def generate_shoot_sound():
    sample_rate = 44100
    duration = 0.15
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    freq = np.linspace(600, 300, len(t))
    audio = 32767 * np.sin(2 * np.pi * freq * t) * np.exp(-t * 8)
    return pygame.mixer.Sound(buffer=audio.astype(np.int16))

def generate_hit_sound():
    sample_rate = 44100
    duration = 0.15
    samples = int(sample_rate * duration)
    audio = np.random.randint(-32768, 32767, samples) * np.exp(-np.linspace(0, 5, samples))
    return pygame.mixer.Sound(buffer=audio.astype(np.int16))

def generate_modem_music():
    sample_rate = 44100
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio = np.zeros(len(t))
    for freq_start, freq_end in [(300, 700), (900, 500), (600, 800)]:
        freq = np.linspace(freq_start, freq_end, len(t))
        audio += 5000 * np.sin(2 * np.pi * freq * t)
    audio += np.random.randint(-2000, 2000, len(t))
    audio = np.clip(audio, -32768, 32767)
    return pygame.mixer.Sound(buffer=audio.astype(np.int16))

def generate_drum_beat():
    sample_rate = 44100
    duration = 4.0  # 4-second loop for a mellow 120 BPM beat
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio = np.zeros((len(t), 2))  # Stereo
    beat_interval = 0.5  # 120 BPM = 2 beats per second
    for i in range(int(duration / beat_interval)):
        time = i * beat_interval
        start = int(time * sample_rate)
        end = int((time + 0.2) * sample_rate)
        if end <= len(t):
            freq = 100  # Bass drum
            audio[start:end, 0] += 15000 * np.sin(2 * np.pi * freq * t[start:end]) * np.exp(-t[start:end] * 5)
            audio[start:end, 1] += 15000 * np.sin(2 * np.pi * freq * t[start:end]) * np.exp(-t[start:end] * 5)
    audio = np.clip(audio, -32768, 32767).astype(np.int16)
    return pygame.mixer.Sound(buffer=audio.tobytes())

def generate_die_sound():
    sample_rate = 44100
    duration = 0.3
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    freq = np.linspace(200, 50, len(t))
    audio = 32767 * np.sin(2 * np.pi * freq * t) * np.exp(-t * 4)
    return pygame.mixer.Sound(buffer=audio.astype(np.int16))

def generate_bonus_life_sound():
    sample_rate = 44100
    duration = 0.2
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    freq = np.linspace(800, 1000, len(t))
    audio = 32767 * np.sin(2 * np.pi * freq * t) * np.exp(-t * 3)
    return pygame.mixer.Sound(buffer=audio.astype(np.int16))

shoot_sound = generate_shoot_sound()
hit_sound = generate_hit_sound()
modem_music = generate_modem_music()
drum_beat = generate_drum_beat()
die_sound = generate_die_sound()
bonus_life_sound = generate_bonus_life_sound()

# Load soundtrack
try:
    soundtrack = pygame.mixer.Sound("soundtrack.wav")
except pygame.error:
    print("Error: soundtrack.wav not found. Using drum beat instead.")
    soundtrack = drum_beat  # Fallback to drum beat if soundtrack fails

# Player settings (simple vertical line or small rectangle in Matrix green)
PLAYER_WIDTH = 8  # Thin vertical line or small rectangle
PLAYER_HEIGHT = 20
player_x = WIDTH // 2 - PLAYER_WIDTH // 2
player_y = HEIGHT - 40
player_speed = 5

# Bullet settings
BULLET_WIDTH = 5
BULLET_HEIGHT = 10
bullet_speed = 7
bullets = []

# Paperwork enemy settings
PAPER_WIDTH = 60
LINE_SPACING = 15  # Reduced spacing for thinner appearance
paper_speed = 1.5
papers = []
COLUMNS = 5
COLUMN_WIDTH = WIDTH // COLUMNS

# Explosion settings
explosions = []

# Government department abbreviations (updated to official abbreviations, limited to 3-4 characters, expanded to 50 based on X and web data)
PAPER_WORDS = [
    "CIA", "FBI", "IRS", "DOD", "DHS", "DOJ", "VA", "HHS", "DEA", "ATF",
    "SEC", "FTC", "TSA", "ICE", "FEMA", "NOAA", "NASA", "EPA", "NSA", "DIA",
    "DARPA", "DCSA", "USDA", "DOT", "DOE", "DOC", "HUD", "DOL", "DOS", "SSA",
    "OPM", "SBA", "BOP", "NCA", "USAID", "TREAS", "DOS",
    "DOC", "DOH", "USDA", "DOJ", "DHS", "DOED", "USDT"
]  # Updated to official abbreviations (e.g., "DOH" for Department of Health, "DOT" for Department of Transportation, "ED" for Education, "DOED" for Department of Education)

# In the game loop, update the small_font_score definition:
#small_font_score = pygame.font.Font("fonts/MatrixCodeNFI.ttf", 20)  # Score, lives, and pause text

# Fonts (unchanged from previous, but score/lives/pause will remain reduced)
#font = pygame.font.SysFont("Menlo", 27)  # Use Arial, size 27
#small_font = pygame.font.SysFont("Menlo", 18)  # Smaller font for departments and Matrix characters
#big_font = pygame.font.SysFont("Menlo", 54)  # Larger font for splash screen

# Game variables
score = 0
lives = 3  # Start with 3 lives
MAX_LIVES = 5  # Maximum lives to prevent stacking
clock = pygame.time.Clock()
animation_timer = 0  # Global timer for animation

def spawn_paper():
    column = random.randint(0, COLUMNS - 1)
    x = column * COLUMN_WIDTH + (COLUMN_WIDTH - PAPER_WIDTH) // 2
    # Ensure stack size is between 3 and 25 lines
    stack_size = random.randint(3, 25)  # Minimum 3, maximum 25 lines
    height = stack_size * LINE_SPACING
    word = random.choice(PAPER_WORDS)
    # Initialize matrix_chars as a list of strings (each string is a row of chars or dept name)
    matrix_chars = []
    # Ensure department name is shown once per stack: use "_FBI____" to fill 8 characters
    dept_line = f"_{word}_" + "_" * (8 - len(word) - 2)  # e.g., "_FBI____" or "_CIA___" for 8 chars
    matrix_chars.append(dept_line)  # Single line for department name
    for _ in range(stack_size - 1):  # Add random Matrix chars for remaining lines
        matrix_chars.append("".join(random.choice(MATRIX_CHARS) for _ in range(8)))  # Random Matrix chars
    papers.append([x, -height, column, stack_size, word, random.choice([True, False]), matrix_chars])

def draw_player():
    # Draw a simple vertical line or small rectangle as the player in Matrix green
    pygame.draw.rect(screen, MATRIX_GREEN, (player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT))  # Simple vertical line or thin rectangle

    # Add "SPACE DOGE" next to the player in Matrix green
    space_text = font.render("SPACE", True, MATRIX_GREEN)  # Text for spacebar
    doge_text = font.render("DOGE", True, MATRIX_GREEN)  # "DOGE" in uppercase
    # Position "SPACE" and "DOGE" to the right of the player with a small gap
    space_rect = space_text.get_rect(topleft=(player_x + PLAYER_WIDTH + 10, player_y))  # 10px gap to right of player
    doge_rect = doge_text.get_rect(topleft=(space_rect.right + 10, player_y))  # 10px gap after "SPACE"
    screen.blit(space_text, space_rect)
    screen.blit(doge_text, doge_rect)

def draw_bullet(bullet):
    pygame.draw.rect(screen, MATRIX_GREEN, (bullet[0], bullet[1], BULLET_WIDTH, BULLET_HEIGHT))  # Matrix green bullets

def draw_paper(paper):
    global animation_timer
    x, y, _, stack_size, word, _, matrix_chars = paper
    
    # Update Matrix characters based on animation timer for a cascading effect
    animation_timer += 1
    if animation_timer % 5 == 0:  # Update every 5 frames for smooth animation
        for i in range(stack_size):  # Update all lines, including department name
            if i == 0:  # Department name line (first line)
                dept_line = f"_{word}_" + "_" * (8 - len(word) - 2)  # e.g., "_FBI____" or "_CIA___" for 8 chars
                matrix_chars[i] = dept_line
            else:
                # Generate a new row of 8 random characters for non-department lines
                matrix_chars[i] = "".join(random.choice(MATRIX_CHARS) for _ in range(8))
    
    # Draw animated Matrix characters for each line (including department names) in Matrix green
    for i in range(stack_size):
        text = small_font.render(matrix_chars[i], True, MATRIX_GREEN)
        screen.blit(text, (x, y + i * LINE_SPACING))

def draw_explosion(explosion, color):
    x, y, timer, max_size = explosion
    radius = min(5 + (timer * (max_size / 15)), max_size)
    # Create a circular pattern of "=" characters
    for angle in range(0, 360, 15):  # Draw every 15 degrees for simplicity
        rad = np.radians(angle)
        dist = radius * random.uniform(0.8, 1.2)  # Slight randomness for organic look
        px = x + PAPER_WIDTH // 2 + dist * np.cos(rad)
        py = y + dist * np.sin(rad)
        equals_text = small_font.render("==============", True, MATRIX_GREEN)  # Long string of "="
        screen.blit(equals_text, (px - equals_text.get_width() // 2, py - equals_text.get_height() // 2))

def reset_game():
    global player_x, bullets, papers, explosions, score, lives, show_start, paused, animation_timer
    player_x = WIDTH // 2 - PLAYER_WIDTH // 2
    bullets = []
    papers = []
    explosions = []
    score = 0
    lives = 3  # Reset to 3 lives
    show_start = True
    paused = False
    animation_timer = 0  # Reset animation timer
    pygame.mixer.stop()  # Stop all sounds when resetting
    return False

def check_extra_life(paper_bonus):
    global lives, score
    if score > 0 and score % 100 == 0 and paper_bonus and random.random() < 0.5 and lives < MAX_LIVES:
        lives += 1
        bonus_life_sound.play()

def draw_start_screen():
    screen.blit(dimmed_background_splash, (0, 0))  # Show dimmed background at 65% on splash screen
    doge_text = big_font.render("DOGE", True, GOLD)
    doge_rect = doge_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(doge_text, doge_rect)
    
    slash_text = font.render("///////////////////////////////////////////////////", True, WHITE)
    screen.blit(slash_text, (WIDTH // 2 - slash_text.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(slash_text, (WIDTH // 2 - slash_text.get_width() // 2, HEIGHT // 2 + 60))
    
    vert_line = font.render("|                                                        |", True, WHITE)
    screen.blit(vert_line, (WIDTH // 2 - vert_line.get_width() // 2, HEIGHT // 2 - 45))
    screen.blit(vert_line, (WIDTH // 2 - vert_line.get_width() // 2, HEIGHT // 2 - 15))
    screen.blit(vert_line, (WIDTH // 2 - vert_line.get_width() // 2, HEIGHT // 2 + 15))
    screen.blit(vert_line, (WIDTH // 2 - vert_line.get_width() // 2, HEIGHT // 2 + 45))
    
    # Add extra line break and make "Press SPACE to Shoot Waste" Matrix green
    start_text = font.render("Press SPACE to Shoot Waste", True, MATRIX_GREEN)
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 105))  # Extra line break (moved down)

    # Add bottom row of $$$$$$$$ spanning the whole screen in Matrix green
    dollars_text = font.render("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", True, MATRIX_GREEN)
    screen.blit(dollars_text, (0, HEIGHT - 30))  # Position at bottom of screen

    modem_music.play()  # Play modem sound

# Game loop
running = True
spawn_timer = 0
game_active = False
show_start = True
paused = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if show_start:
                    show_start = False
                    game_active = True
                    pygame.mixer.stop()  # Stop modem sound
                    soundtrack.play(-1)  # Play soundtrack on loop
                elif game_active and not paused:
                    # Spawn bullet from the center of the player (top of the player)
                    bullet_x = player_x + PLAYER_WIDTH // 2 - BULLET_WIDTH // 2
                    bullet_y = player_y
                    bullets.append([bullet_x, bullet_y])
                    shoot_sound.play()
            if event.key == pygame.K_r and not game_active and not show_start:
                game_active = reset_game()
            if event.key == pygame.K_p and game_active:
                paused = not paused
                if paused:
                    pygame.mixer.pause()
                else:
                    pygame.mixer.unpause()

    if show_start:
        draw_start_screen()
    elif game_active:
        if not paused:
            screen.blit(dimmed_background_game, (0, 0))  # Draw dimmed background at 50%
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player_x > 0:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] and player_x < WIDTH - PLAYER_WIDTH:
                player_x += player_speed

            spawn_timer += 1
            if spawn_timer >= 45:
                spawn_paper()
                spawn_timer = 0

            bullets = [[b[0], b[1] - bullet_speed] for b in bullets]
            bullets = [b for b in bullets if b[1] > -BULLET_HEIGHT]

            papers = [[p[0], p[1] + paper_speed, p[2], p[3], p[4], p[5], p[6]] for p in papers]

            explosions = [[e[0], e[1], e[2] + 1, e[3]] for e in explosions]
            explosions = [e for e in explosions if e[2] < 15]

            for bullet in bullets[:]:
                for paper in papers[:]:
                    paper_x, paper_y, _, stack_size, _, _, matrix_chars = paper
                    paper_height = stack_size * LINE_SPACING
                    if (bullet[0] < paper_x + PAPER_WIDTH and 
                        bullet[0] + BULLET_WIDTH > paper_x and 
                        bullet[1] < paper_y + paper_height and 
                        bullet[1] + BULLET_HEIGHT > paper_y):
                        bullets.remove(bullet)
                        papers.remove(paper)
                        explosions.append([paper_x, paper_y + paper_height // 2, 0, PAPER_WIDTH])
                        hit_sound.play()
                        score += 1
                        check_extra_life(paper[5])  # Check for extra life after a kill
                        break

            for paper in papers[:]:
                if paper[1] + paper[3] * LINE_SPACING > HEIGHT:
                    papers.remove(paper)
                    lives -= 1
                    die_sound.play()  # Play die sound when losing a life
                    if lives <= 0:
                        game_active = False
                    explosions.append([paper[0], player_y + PLAYER_HEIGHT // 2, 0, PAPER_WIDTH])  # Brown explosion
                    break

            # Draw player (simple vertical line or rectangle) with "SPACE DOGE" next to it
            draw_player()
            for bullet in bullets:
                draw_bullet(bullet)
            for paper in papers:
                draw_paper(paper)
            for explosion in explosions:
                if explosion in [[e[0], e[1], e[2], e[3]] for e in explosions if e[0] == paper[0] and e[1] == player_y + PLAYER_HEIGHT // 2]:
                    draw_explosion(explosion, BROWN)  # Brown explosion for player hit
                else:
                    draw_explosion(explosion, MATRIX_GREEN)  # Matrix green explosion for paper hits

            # Display score, lives, and Pause indicator with Matrix green text on black background
            # Use smaller font (20, 75% of 27)
            small_font_score = pygame.font.SysFont("Arial", 20)  # Reduced by 25%
            padding = 10
            score_text = small_font_score.render(f"Score: {score}", True, MATRIX_GREEN)
            lives_text = small_font_score.render(f"Lives: {lives}", True, MATRIX_GREEN)
            pause_text = small_font_score.render("Pause", True, MATRIX_GREEN)  # Capitalized "Pause"
            
            score_surface = pygame.Surface((score_text.get_width() + 2 * padding, score_text.get_height() + 2 * padding))
            score_surface.fill(BLACK)
            lives_surface = pygame.Surface((lives_text.get_width() + 2 * padding, lives_text.get_height() + 2 * padding))
            lives_surface.fill(BLACK)
            pause_surface = pygame.Surface((pause_text.get_width() + 2 * padding, pause_text.get_height() + 2 * padding))
            pause_surface.fill(BLACK)
            
            score_surface.blit(score_text, (padding, padding))
            lives_surface.blit(lives_text, (padding, padding))
            pause_surface.blit(pause_text, (padding, padding))
            
            screen.blit(score_surface, (10, 10))
            screen.blit(lives_surface, (WIDTH - lives_surface.get_width() - 10, 10))
            screen.blit(pause_surface, (WIDTH // 2 - pause_surface.get_width() // 2, 10))

        else:
            # Paused state: dim the screen and show "Paused" in Matrix green
            screen.blit(dimmed_background_game, (0, 0))
            paused_text = big_font.render("Paused", True, MATRIX_GREEN)
            screen.blit(paused_text, (WIDTH // 2 - paused_text.get_width() // 2, HEIGHT // 2))

    if not game_active and not show_start:
        screen.blit(dimmed_background_game, (0, 0))  # Show dimmed background during game over
        game_over_text = font.render(f"Game Over! Score: {score}", True, MATRIX_GREEN)
        restart_text = font.render("Press R to Restart", True, MATRIX_GREEN)
        
        padding = 10
        game_over_surface = pygame.Surface((game_over_text.get_width() + 2 * padding, game_over_text.get_height() + 2 * padding))
        game_over_surface.fill(BLACK)
        restart_surface = pygame.Surface((restart_text.get_width() + 2 * padding, restart_text.get_height() + 2 * padding))
        restart_surface.fill(BLACK)
        
        game_over_surface.blit(game_over_text, (padding, padding))
        restart_surface.blit(restart_text, (padding, padding))
        
        # Add extra line break by increasing y offset
        screen.blit(game_over_surface, (WIDTH // 2 - game_over_surface.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(restart_surface, (WIDTH // 2 - restart_surface.get_width() // 2, HEIGHT // 2 + 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()