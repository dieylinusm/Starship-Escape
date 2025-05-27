import asyncio
import platform
import pygame
import random
import numpy as np
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Starship Escape")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

# Player settings
player_size = 40
player_speed = 5
player_pos = [WIDTH // 2, HEIGHT - 100]

# Asteroid settings
asteroid_min_size = 20
asteroid_max_size = 50
asteroid_speed = 3
asteroids = []

# Energy settings
energy_size = 15
energy_speed = 2
energies = []

# Particle settings for collection effect
particles = []

# Score and font
score = 0
font = pygame.font.SysFont("arial", 24)

# Sound setup (using NumPy for compatibility with Pyodide)
sample_rate = 44100
duration = 0.1
t = np.linspace(0, duration, int(sample_rate * duration))
sound_array = np.sin(2 * np.pi * 440 * t) * 32767
sound_array = np.column_stack((sound_array, sound_array)).astype(np.int16)
collect_sound = pygame.sndarray.make_sound(sound_array)

# Game state
running = True
game_over = False
clock = pygame.time.Clock()
FPS = 60

def setup():
    global asteroids, energies, particles, score, player_pos, running, game_over
    asteroids = []
    energies = []
    particles = []
    score = 0
    player_pos = [WIDTH // 2, HEIGHT - 100]
    running = True
    game_over = False
    # Spawn initial asteroids and energies
    for _ in range(5):
        spawn_asteroid()
        spawn_energy()

def spawn_asteroid():
    size = random.randint(asteroid_min_size, asteroid_max_size)
    x = random.randint(0, WIDTH - size)
    asteroids.append([x, -size, size])

def spawn_energy():
    x = random.randint(0, WIDTH - energy_size)
    energies.append([x, -energy_size])

def create_particles(x, y):
    for _ in range(10):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 3)
        particles.append([x, y, math.cos(angle) * speed, math.sin(angle) * speed, 20])

def update_loop():
    global running, game_over, score
    if not running:
        return

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                setup()

    if game_over:
        return

    # Move player with mouse
    player_pos[0] = pygame.mouse.get_pos()[0]
    player_pos[0] = max(player_size // 2, min(WIDTH - player_size // 2, player_pos[0]))

    # Update asteroids
    for asteroid in asteroids[:]:
        asteroid[1] += asteroid_speed
        if asteroid[1] > HEIGHT:
            asteroids.remove(asteroid)
            spawn_asteroid()

    # Update energies
    for energy in energies[:]:
        energy[1] += energy_speed
        if energy[1] > HEIGHT:
            energies.remove(energy)
            spawn_energy()

    # Update particles
    for particle in particles[:]:
        particle[0] += particle[2]
        particle[1] += particle[3]
        particle[4] -= 1
        if particle[4] <= 0:
            particles.remove(particle)

    # Collision detection
    player_rect = pygame.Rect(player_pos[0] - player_size // 2, player_pos[1] - player_size // 2, player_size, player_size)
    for asteroid in asteroids:
        asteroid_rect = pygame.Rect(asteroid[0] - asteroid[2] // 2, asteroid[1] - asteroid[2] // 2, asteroid[2], asteroid[2])
        if player_rect.colliderect(asteroid_rect):
            game_over = True
            break

    for energy in energies[:]:
        energy_rect = pygame.Rect(energy[0] - energy_size // 2, energy[1] - energy_size // 2, energy_size, energy_size)
        if player_rect.colliderect(energy_rect):
            energies.remove(energy)
            score += 10
            create_particles(energy[0], energy[1])
            collect_sound.play()
            spawn_energy()

    # Increment score based on survival time
    score += 0.1

    # Draw everything
    screen.fill(BLACK)
    # Draw player
    pygame.draw.rect(screen, WHITE, (player_pos[0] - player_size // 2, player_pos[1] - player_size // 2, player_size, player_size))
    # Draw asteroids
    for asteroid in asteroids:
        pygame.draw.circle(screen, GRAY, (int(asteroid[0]), int(asteroid[1])), asteroid[2] // 2)
    # Draw energies
    for energy in energies:
        pygame.draw.circle(screen, GREEN, (int(energy[0]), int(energy[1])), energy_size // 2)
    # Draw particles
    for particle in particles:
        pygame.draw.circle(screen, GREEN, (int(particle[0]), int(particle[1])), 2)
    # Draw score
    score_text = font.render(f"Score: {int(score)}", True, WHITE)
    screen.blit(score_text, (10, 10))
    # Draw game over
    if game_over:
        game_over_text = font.render("Game Over! Press R to Restart", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
    
    pygame.display.flip()

async def main():
    setup()
    while running:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
