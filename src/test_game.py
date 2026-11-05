import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
import super_mario as sm

pygame.init()
screen = pygame.display.set_mode((sm.SCREEN_WIDTH, sm.SCREEN_HEIGHT))
clock = pygame.time.Clock()

# load level
platforms, coins, enemies, player_start, world_width, world_height = sm.load_level()
player = sm.Player(*player_start)
lives = player.lives
camera_x = 0
state = 'playing'

# simulate 120 frames (2 seconds)
frame_count = 0
for _ in range(120):
    clock.tick(sm.FPS)
    frame_count += 1

    # simulate player moving right
    player.vx = player.speed
    player.facing = 1
    player.update(platforms, coins, enemies, world_width)
    for e in enemies:
        e.update(platforms, world_width)

    # death check
    if not player.alive:
        lives -= 1
        if lives <= 0:
            state = 'gameover'
            break
        else:
            player = sm.Player(*player_start)
            player.lives = lives

# report
print('Frames simulated:', frame_count)
print('State:', state)
print('Player position:', player.rect.x, player.rect.y)
print('Player on_ground:', player.on_ground)
print('Player lives:', player.lives)
print('Coins collected:', player.coins)
print('Enemies alive:', sum(1 for e in enemies if e.alive))
print('SIMULATION_SUCCESS')

pygame.quit()
sys.exit(0)
