import sys
import math
import pygame
import sounds

# ---------- constants ----------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

GRAVITY = 0.7
PLAYER_SPEED = 5
JUMP_POWER = -15
PLAYER_WIDTH = 30
SMALL_HEIGHT = 40
BIG_HEIGHT = 64

TILE_SIZE = 40
COIN_SIZE = 20

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
FLAG_X = 6680  # near end of world

# ---------- player ----------
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, SMALL_HEIGHT)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.alive = True
        self.won = False
        self.coins = 0
        self.lives = 3
        self.speed = PLAYER_SPEED
        self.jump_power = JUMP_POWER
        self.facing = 1
        self.big = False
        self.hit_flash = 0
        self.fire = False
        self.star = 0
        self.fireballs = []
        self.fire_cooldown = 0

    def update(self, platforms, coins, enemies, mushrooms, mushroom_bricks, fire_flowers, fire_flower_bricks, stars, star_bricks, world_width):
        if not self.alive:
            return

        self.rect.x += self.vx
        for _, rect in platforms:
            if self.rect.colliderect(rect):
                if self.vx > 0:
                    self.rect.right = rect.left
                elif self.vx < 0:
                    self.rect.left = rect.right

        self.vy += GRAVITY
        self.rect.y += self.vy
        self.on_ground = False
        for kind, rect in platforms[:]:
            if self.rect.colliderect(rect):
                if self.vy > 0:
                    self.rect.bottom = rect.top
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = rect.bottom
                    self.vy = 0
                    # hit brick from below
                    if kind == 'brick':
                        sounds.play('brick')
                        # find matching mushroom (keep mushroom in list so it spawns)
                        for idx, mb in enumerate(mushroom_bricks):
                            (bx, by), mushroom = mb
                            brick_rect = pygame.Rect(bx * TILE_SIZE, by * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                            if brick_rect == rect:
                                mushroom.emerge()
                                mushroom_bricks.pop(idx)
                                break
                        # fire flower
                        for idx, fb in enumerate(fire_flower_bricks):
                            (bx, by), flower = fb
                            brick_rect = pygame.Rect(bx * TILE_SIZE, by * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                            if brick_rect == rect:
                                flower.emerge()
                                fire_flower_bricks.pop(idx)
                                break
                        # star
                        for idx, sb in enumerate(star_bricks):
                            (bx, by), star = sb
                            brick_rect = pygame.Rect(bx * TILE_SIZE, by * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                            if brick_rect == rect:
                                star.emerge()
                                star_bricks.pop(idx)
                                break
                        platforms.remove((kind, rect))

        if self.rect.top > 900:
            self.alive = False
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > world_width:
            self.rect.right = world_width

        for c in coins[:]:
            if self.rect.colliderect(c):
                coins.remove(c)
                self.coins += 1
                sounds.play('coin')

        # mushroom pickup
        for m in mushrooms[:]:
            if m.active and self.rect.colliderect(m.rect):
                mushrooms.remove(m)
                if not self.big:
                    self.big = True
                    old_bottom = self.rect.bottom
                    self.rect.height = BIG_HEIGHT
                    self.rect.bottom = old_bottom
                    sounds.play('powerup')
                else:
                    self.coins += 10
                    sounds.play('coin')

        # star timer
        if self.star > 0:
            self.star -= 1

        # fire flower pickup
        for f in fire_flowers[:]:
            if f.active and self.rect.colliderect(f.rect):
                fire_flowers.remove(f)
                self.fire = True
                self.big = True
                old_bottom = self.rect.bottom
                self.rect.height = BIG_HEIGHT
                self.rect.bottom = old_bottom
                sounds.play('powerup')
                sounds.play('powerup2')

        # star pickup
        for s in stars[:]:
            if s.active and self.rect.colliderect(s.rect):
                stars.remove(s)
                self.star = 600
                sounds.play('star')

        # enemy collision (big = 2 hits, small = instant death)
        for e in enemies:
            if not e.alive:
                continue
            if self.rect.colliderect(e.rect):
                if self.star > 0:
                    e.alive = False
                    self.coins += 5
                    sounds.play('stomp')
                elif self.vy > 3 and self.rect.bottom - e.rect.top < 20:
                    e.alive = False
                    self.vy = -10
                    self.coins += 5
                    sounds.play('stomp')
                elif self.hit_flash <= 0:
                    if self.big:
                        self.big = False
                        self.fire = False
                        old_bottom = self.rect.bottom
                        self.rect.height = SMALL_HEIGHT
                        self.rect.bottom = old_bottom
                        self.vy = -8
                        self.hit_flash = 45
                        sounds.play('death')
                    else:
                        self.alive = False
                        sounds.play('death')

    def jump(self):
        if self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False
            sounds.play('jump')

    def shoot_fireball(self):
        if not self.fire or self.fire_cooldown > 0:
            return
        self.fire_cooldown = 20
        x = self.rect.right if self.facing > 0 else self.rect.left - 12
        y = self.rect.centery - 4
        self.fireballs.append([x, y, self.facing * 7, 0])
        sounds.play('fireball')

    def update_fireballs(self, platforms, enemies):
        self.fire_cooldown = max(0, self.fire_cooldown - 1)
        for fb in self.fireballs[:]:
            fb[0] += fb[2]
            fb[1] += fb[3]
            fb[3] += GRAVITY * 0.5
            fb_rect = pygame.Rect(fb[0], fb[1], 12, 12)
            # hit enemies
            for e in enemies:
                if e.alive and fb_rect.colliderect(e.rect):
                    e.alive = False
                    self.coins += 5
                    sounds.play('stomp')
                    self.fireballs.remove(fb)
                    break
            else:
                # hit platforms
                hit = False
                for _, rect in platforms:
                    if fb_rect.colliderect(rect):
                        hit = True
                        break
                if hit or fb[0] < -50 or fb[0] > 8000:
                    self.fireballs.remove(fb)

    def draw(self, screen, camera_x):
        if self.hit_flash > 0:
            self.hit_flash -= 1
            if self.hit_flash // 4 % 2 == 0:
                return
        if self.star > 0 and self.star // 6 % 2 == 0:
            return
        x = self.rect.x - camera_x
        y = self.rect.y
        body_h = self.rect.h
        pygame.draw.rect(screen, RED, (x - 2, y - 6, self.rect.w + 4, 10))
        pygame.draw.rect(screen, RED, (x + 2, y - 10, 14, 6))
        face_h = 14 if not self.big else 18
        pygame.draw.rect(screen, (255, 200, 150), (x + 4, y + 2, self.rect.w - 8, face_h))
        eye_x = x + 21 if self.facing > 0 else x + 5
        pygame.draw.circle(screen, BLACK, (eye_x, y + 8), 3)
        shirt_h = 12 if not self.big else 22
        pygame.draw.rect(screen, RED, (x, y + 2 + face_h, self.rect.w, shirt_h))
        pants_y = y + 2 + face_h + shirt_h
        pygame.draw.rect(screen, BLUE, (x, pants_y, self.rect.w, body_h - (pants_y - y) - 10))
        pygame.draw.circle(screen, YELLOW, (x + 8, pants_y + 8), 2)
        pygame.draw.circle(screen, YELLOW, (x + self.rect.w - 8, pants_y + 8), 2)
        arm_y = y + face_h + 4
        pygame.draw.rect(screen, (255, 200, 150), (x - 3, arm_y, 6, 10))
        pygame.draw.rect(screen, (255, 200, 150), (x + self.rect.w - 3, arm_y, 6, 10))
        pygame.draw.rect(screen, BROWN, (x + 2, y + self.rect.h - 6, 12, 6))
        pygame.draw.rect(screen, BROWN, (x + self.rect.w - 14, y + self.rect.h - 6, 12, 6))

        # fireballs
        for fb in self.fireballs:
            fx = fb[0] - camera_x
            fy = fb[1]
            pygame.draw.circle(screen, ORANGE, (int(fx + 6), int(fy + 6)), 6)
            pygame.draw.circle(screen, YELLOW, (int(fx + 6), int(fy + 6)), 3)

# ---------- mushroom ----------
class Mushroom:
    def __init__(self, x, y, brick_top):
        self.rect = pygame.Rect(x, brick_top + 10, 30, 30)
        self.vx = 2
        self.vy = 0
        self.active = False
        self.emerging = False
        self.emerge_vy = -4
        self.brick_top = brick_top

    def emerge(self):
        self.emerging = True

    def update(self, platforms):
        if not self.active:
            if not self.emerging:
                return
            # rising out of the brick at constant speed
            self.rect.y -= 2
            if self.rect.y <= self.brick_top - self.rect.height:
                self.rect.y = self.brick_top - self.rect.height
                self.active = True
                self.vy = 0
            return

        self.rect.x += self.vx
        for _, rect in platforms:
            if self.rect.colliderect(rect):
                if self.vx > 0:
                    self.rect.right = rect.left
                elif self.vx < 0:
                    self.rect.left = rect.right
                self.vx *= -1

        self.vy += GRAVITY
        self.rect.y += self.vy
        for _, rect in platforms:
            if self.rect.colliderect(rect):
                if self.vy > 0:
                    self.rect.bottom = rect.top
                    self.vy = 0
                elif self.vy < 0:
                    self.rect.top = rect.bottom
                    self.vy = 0

    def draw(self, screen, camera_x):
        if not self.active and not self.emerging:
            return
        x = self.rect.x - camera_x
        y = self.rect.y
        pygame.draw.ellipse(screen, RED, (x, y, self.rect.w, self.rect.h))
        pygame.draw.circle(screen, WHITE, (x + self.rect.w // 2, y + 10), 5)
        pygame.draw.circle(screen, BLACK, (x + self.rect.w // 2 - 6, y + 8), 3)
        pygame.draw.circle(screen, BLACK, (x + self.rect.w // 2 + 6, y + 8), 3)

# ---------- fire flower ----------
class FireFlower:
    def __init__(self, x, y, brick_top):
        self.rect = pygame.Rect(x, brick_top + 10, 30, 30)
        self.active = False
        self.emerging = False
        self.brick_top = brick_top

    def emerge(self):
        self.emerging = True

    def update(self):
        if not self.active:
            if not self.emerging:
                return
            self.rect.y -= 2
            if self.rect.y <= self.brick_top - self.rect.height:
                self.rect.y = self.brick_top - self.rect.height
                self.active = True

    def draw(self, screen, camera_x):
        if not self.active and not self.emerging:
            return
        x = self.rect.x - camera_x
        y = self.rect.y
        # stem
        pygame.draw.rect(screen, GREEN, (x + 13, y + 14, 4, 16))
        # petals
        for i in range(6):
            a = i * 60
            px = x + 15 + int(10 * math.cos(math.radians(a)))
            py = y + 8 + int(10 * math.sin(math.radians(a)))
            pygame.draw.circle(screen, ORANGE, (px, py), 6)
        # center
        pygame.draw.circle(screen, YELLOW, (x + 15, y + 8), 6)

# ---------- star ----------
class Star:
    def __init__(self, x, y, brick_top):
        self.rect = pygame.Rect(x, brick_top + 10, 30, 30)
        self.vx = 2
        self.vy = 0
        self.active = False
        self.emerging = False
        self.brick_top = brick_top
        self.t = 0

    def emerge(self):
        self.emerging = True

    def update(self, platforms):
        self.t += 1
        if not self.active:
            if not self.emerging:
                return
            self.rect.y -= 2
            if self.rect.y <= self.brick_top - self.rect.height:
                self.rect.y = self.brick_top - self.rect.height
                self.active = True
                self.vy = 0
            return

        self.rect.x += self.vx
        for _, rect in platforms:
            if self.rect.colliderect(rect):
                if self.vx > 0:
                    self.rect.right = rect.left
                elif self.vx < 0:
                    self.rect.left = rect.right
                self.vx *= -1

        self.vy += GRAVITY
        self.rect.y += self.vy
        for _, rect in platforms:
            if self.rect.colliderect(rect):
                if self.vy > 0:
                    self.rect.bottom = rect.top
                    self.vy = 0
                elif self.vy < 0:
                    self.rect.top = rect.bottom
                    self.vy = 0

    def draw(self, screen, camera_x):
        if not self.active and not self.emerging:
            return
        x = self.rect.x - camera_x
        y = self.rect.y
        cx = x + 15
        cy = y + 15
        pts = []
        for i in range(10):
            a = math.pi * i / 5 - math.pi / 2 + self.t * 0.05
            r = 13 if i % 2 == 0 else 6
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        pygame.draw.polygon(screen, YELLOW, pts)
        pygame.draw.polygon(screen, (255, 240, 100), pts, 2)

# ---------- enemies ----------
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 34, 34)
        self.vx = -1
        self.vy = 0
        self.alive = True

    def update(self, platforms, world_width):
        if not self.alive:
            return

        self.rect.x += self.vx
        for _, rect in platforms:
            if self.rect.colliderect(rect):
                if self.vx > 0:
                    self.rect.right = rect.left
                elif self.vx < 0:
                    self.rect.left = rect.right
                self.vx *= -1

        self.vy += GRAVITY
        self.rect.y += self.vy
        for _, rect in platforms:
            if self.rect.colliderect(rect):
                if self.vy > 0:
                    self.rect.bottom = rect.top
                    self.vy = 0
                elif self.vy < 0:
                    self.rect.top = rect.bottom
                    self.vy = 0

        # turn around at ledges
        front_x = self.rect.right + 2 if self.vx > 0 else self.rect.left - 2
        foot_y = self.rect.bottom + 2
        has_support = any(rect.collidepoint(front_x, foot_y) for _, rect in platforms)
        if not has_support:
            self.vx *= -1

        if self.rect.left < 0:
            self.rect.left = 0
            self.vx *= -1
        if self.rect.right > world_width:
            self.rect.right = world_width
            self.vx *= -1

    def draw(self, screen, camera_x):
        x = self.rect.x - camera_x
        y = self.rect.y
        pygame.draw.ellipse(screen, BROWN, (x, y, self.rect.w, self.rect.h))
        pygame.draw.rect(screen, BLACK, (x + 4, y + self.rect.h - 6, 10, 6))
        pygame.draw.rect(screen, BLACK, (x + self.rect.w - 14, y + self.rect.h - 6, 10, 6))
        pygame.draw.circle(screen, WHITE, (x + 10, y + 10), 4)
        pygame.draw.circle(screen, WHITE, (x + self.rect.w - 10, y + 10), 4)
        pygame.draw.circle(screen, BLACK, (x + 12, y + 11), 2)
        pygame.draw.circle(screen, BLACK, (x + self.rect.w - 8, y + 11), 2)

# ---------- level ----------
LEVEL_DEFS = [
    {
        'cols': 170, 'rows': 15,
        'pits': [(45, 48), (80, 83), (115, 118), (145, 148)],
        'bricks': [(12, 11, 6), (36, 13, 1), (37, 12, 1), (38, 11, 1), (39, 10, 1),
                   (52, 11, 6), (72, 12, 5), (90, 11, 5), (110, 12, 4),
                   (124, 11, 6), (143, 12, 4), (155, 11, 6)],
        'pipes': [(25, 13, 2), (30, 13, 2), (63, 13, 2), (100, 13, 2),
                  (136, 13, 2), (163, 13, 2)],
        'coins': [(13, 10), (14, 10), (15, 10), (16, 10), (39, 11), (40, 10),
                  (53, 10), (54, 10), (55, 10), (56, 10), (73, 11), (74, 11), (75, 11),
                  (91, 10), (92, 10), (93, 10), (102, 12), (111, 11), (112, 11),
                  (125, 10), (126, 10), (127, 10), (128, 10), (144, 11), (145, 11),
                  (156, 10), (157, 10), (158, 10), (159, 10)],
        'mushrooms': [(13, 11), (156, 11)],
        'fire_flowers': [(52, 11)],
        'stars': [(90, 11)],
        'enemies': [(900, 0), (1250, 0), (1550, 0), (1850, 0), (2150, 0),
                    (2450, 0), (2750, 0), (3050, 0), (3350, 0), (3650, 0)],
        'player_start': (100, 400),
        'flag_x': 6680,
    },
    {
        'cols': 150, 'rows': 15,
        'pits': [(30, 33), (70, 74), (110, 114)],
        'bricks': [(10, 11, 4), (22, 12, 4), (45, 11, 5), (60, 12, 3),
                   (85, 11, 4), (100, 10, 3), (125, 11, 5)],
        'pipes': [(18, 13, 3), (40, 13, 2), (55, 13, 2), (95, 13, 3), (135, 13, 2)],
        'coins': [(11, 10), (12, 10), (13, 10), (23, 11), (25, 11), (46, 10), (47, 10),
                  (48, 10), (61, 11), (62, 11), (86, 10), (87, 10), (101, 9), (102, 9),
                  (126, 10), (127, 10)],
        'mushrooms': [(45, 11), (125, 11)],
        'fire_flowers': [(22, 12)],
        'stars': [(85, 11)],
        'enemies': [(700, 0), (1000, 0), (1350, 0), (1700, 0), (2100, 0), (2500, 0)],
        'player_start': (100, 400),
        'flag_x': 5920,
    },
    {
        'cols': 130, 'rows': 15,
        'pits': [(25, 29), (60, 65), (95, 100)],
        'bricks': [(8, 11, 5), (20, 12, 3), (35, 11, 4), (50, 10, 3),
                   (70, 12, 4), (85, 11, 5), (110, 11, 4)],
        'pipes': [(15, 13, 2), (45, 13, 3), (75, 13, 2), (105, 13, 2)],
        'coins': [(9, 10), (10, 10), (11, 10), (21, 11), (22, 11), (36, 10), (37, 10),
                  (51, 9), (52, 9), (71, 11), (72, 11), (86, 10), (87, 10), (111, 10), (112, 10)],
        'mushrooms': [(35, 11), (110, 11)],
        'fire_flowers': [(50, 10)],
        'stars': [(70, 12)],
        'enemies': [(600, 0), (900, 0), (1250, 0), (1600, 0), (2000, 0)],
        'player_start': (100, 400),
        'flag_x': 5120,
    },
]


def load_level(level_idx=0):
    data = LEVEL_DEFS[level_idx]
    cols = data['cols']
    rows = data['rows']
    T = TILE_SIZE

    grid = [[' ' for _ in range(cols)] for _ in range(rows)]
    for x in range(cols):
        grid[rows - 1][x] = '1'

    for pit in data['pits']:
        for x in range(pit[0], pit[1]):
            grid[rows - 1][x] = ' '

    for x, y, w in data['bricks']:
        for i in range(w):
            if 0 <= x + i < cols and 0 <= y < rows:
                grid[y][x + i] = '2'

    for x, y, h in data['pipes']:
        for j in range(h):
            if 0 <= x < cols and 0 <= y - j < rows:
                grid[y - j][x] = '3'

    platforms = []
    coins = []
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            rect = pygame.Rect(x * T, y * T, T, T)
            if ch == '1':
                platforms.append(("ground", rect))
            elif ch == '2':
                platforms.append(("brick", rect))
            elif ch == '3':
                platforms.append(("pipe", rect))

    for x, y in data['coins']:
        if 0 <= x < cols and 0 <= y < rows:
            coins.append(pygame.Rect(x * T + 10, y * T + 10, COIN_SIZE, COIN_SIZE))

    mushrooms = []
    mushroom_bricks = []
    for bx, by in data['mushrooms']:
        m = Mushroom(bx * T + 5, by * T + 5, by * T)
        mushrooms.append(m)
        mushroom_bricks.append(((bx, by), m))

    fire_flowers = []
    fire_flower_bricks = []
    for bx, by in data.get('fire_flowers', []):
        f = FireFlower(bx * T + 5, by * T + 5, by * T)
        fire_flowers.append(f)
        fire_flower_bricks.append(((bx, by), f))

    stars = []
    star_bricks = []
    for bx, by in data.get('stars', []):
        s = Star(bx * T + 5, by * T + 5, by * T)
        stars.append(s)
        star_bricks.append(((bx, by), s))

    ground_y = (rows - 1) * T - 34
    enemy_xy = [(x, ground_y) for x, _ in data['enemies']]
    enemies = [Enemy(x, y) for x, y in enemy_xy]

    player_start = data['player_start']
    world_width = cols * T
    world_height = rows * T
    return platforms, coins, enemies, mushrooms, mushroom_bricks, fire_flowers, fire_flower_bricks, stars, star_bricks, enemy_xy, player_start, world_width, world_height


# ---------- drawing ----------
def draw_world(screen, platforms, coins, enemies, mushrooms, fire_flowers, stars, player, camera_x, flag_x):
    screen.fill(SKY_BLUE)

    # clouds
    for cx, cy in [(120, 80), (420, 60), (700, 100), (1200, 70), (1800, 90)]:
        pygame.draw.ellipse(screen, WHITE, (cx - camera_x, cy, 60, 30))
        pygame.draw.ellipse(screen, WHITE, (cx - camera_x + 20, cy - 15, 50, 30))
        pygame.draw.ellipse(screen, WHITE, (cx - camera_x + 40, cy + 5, 40, 25))

    for kind, rect in platforms:
        x = rect.x - camera_x
        y = rect.y
        if kind == "ground":
            pygame.draw.rect(screen, GREEN, (x, y, rect.w, rect.h))
            pygame.draw.rect(screen, (0, 100, 0), (x, y, rect.w, 6))
        elif kind == "brick":
            pygame.draw.rect(screen, BROWN, (x, y, rect.w, rect.h))
            pygame.draw.rect(screen, (100, 60, 30), (x, y, rect.w, 3))
            pygame.draw.rect(screen, (100, 60, 30), (x, y + rect.h - 3, rect.w, 3))
            pygame.draw.line(screen, (100, 60, 30), (x + rect.w // 2, y), (x + rect.w // 2, y + rect.h), 2)
        elif kind == "pipe":
            pygame.draw.rect(screen, GREEN, (x, y, rect.w, rect.h))
            pygame.draw.rect(screen, (0, 150, 0), (x, y, 10, rect.h))
            pygame.draw.rect(screen, (0, 100, 0), (x, y + rect.h - 8, rect.w, 8))
        elif kind == "platform":
            pygame.draw.rect(screen, (120, 120, 120), (x, y, rect.w, rect.h))
            pygame.draw.rect(screen, (80, 80, 80), (x, y, rect.w, 4))

    for c in coins:
        x = c.x - camera_x
        y = c.y
        pygame.draw.circle(screen, YELLOW, (x + COIN_SIZE // 2, y + COIN_SIZE // 2), COIN_SIZE // 2)
        pygame.draw.circle(screen, (255, 240, 100), (x + COIN_SIZE // 2, y + COIN_SIZE // 2), COIN_SIZE // 2 - 3)
        pygame.draw.circle(screen, (200, 150, 0), (x + COIN_SIZE // 2, y + COIN_SIZE // 2), COIN_SIZE // 2, 2)

    for m in mushrooms:
        m.draw(screen, camera_x)

    for f in fire_flowers:
        f.draw(screen, camera_x)

    for s in stars:
        s.draw(screen, camera_x)

    for e in enemies:
        if e.alive:
            e.draw(screen, camera_x)

    # flagpole
    fx = flag_x - camera_x
    pygame.draw.rect(screen, (0, 150, 0), (fx, 100, 6, 460))
    pygame.draw.circle(screen, YELLOW, (fx + 3, 100), 8)
    pygame.draw.polygon(screen, RED, [(fx + 6, 120), (fx + 56, 140), (fx + 6, 160)])

    player.draw(screen, camera_x)

    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Coins: {player.coins}    Lives: {player.lives}", True, BLACK)
    screen.blit(score_text, (10, 10))

# ---------- main ----------
def main():
    pygame.init()
    pygame.key.set_repeat(0, 0)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Mario - Pygame Edition")
    clock = pygame.time.Clock()

    sounds.init()
    platforms, coins, enemies, mushrooms, mushroom_bricks, fire_flowers, fire_flower_bricks, stars, star_bricks, enemy_xy, player_start, world_width, world_height = load_level()
    player = Player(*player_start)
    lives = player.lives
    camera_x = 0
    state = "menu"
    current_level = 0
    flag_x = FLAG_X

    running = True
    while running:
        clock.tick(FPS)

        if state == "menu":
            screen.fill(WHITE)
            font = pygame.font.Font(None, 72)
            title = font.render("Super Mario Pygame", True, RED)
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
            font2 = pygame.font.Font(None, 32)
            instr = font2.render("Enter = Start    Arrows = Move    Space = Jump", True, BLACK)
            screen.blit(instr, (SCREEN_WIDTH // 2 - instr.get_width() // 2, 280))
            font3 = pygame.font.Font(None, 24)
            sub = font3.render(f"Level {current_level + 1} of {len(LEVEL_DEFS)} — Reach the flag!", True, (80, 80, 80))
            screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 340))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        state = "playing"
                        platforms, coins, enemies, mushrooms, mushroom_bricks, fire_flowers, fire_flower_bricks, stars, star_bricks, enemy_xy, player_start, world_width, world_height = load_level(current_level)
                        flag_x = LEVEL_DEFS[current_level]['flag_x']
                        player = Player(*player_start)
                        lives = player.lives
            continue

        if state == "gameover":
            screen.fill(BLACK)
            font = pygame.font.Font(None, 72)
            text = font.render("GAME OVER", True, RED)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250))
            font2 = pygame.font.Font(None, 36)
            restart = font2.render("Press R to restart", True, WHITE)
            screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 350))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        state = "menu"
            continue

        if state == "win":
            screen.fill((0, 100, 0))
            font = pygame.font.Font(None, 72)
            text = font.render("YOU WIN!", True, YELLOW)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250))
            font2 = pygame.font.Font(None, 36)
            sub = font2.render(f"Coins collected: {player.coins}", True, WHITE)
            screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 340))
            font3 = pygame.font.Font(None, 28)
            again = font3.render("Press R to play again", True, WHITE)
            screen.blit(again, (SCREEN_WIDTH // 2 - again.get_width() // 2, 400))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        state = "menu"
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_x:
                    player.shoot_fireball()
                if event.key == pygame.K_ESCAPE:
                    state = "menu"

        keys = pygame.key.get_pressed()
        player.vx = 0
        if keys[pygame.K_LEFT]:
            player.vx = -player.speed
            player.facing = -1
        if keys[pygame.K_RIGHT]:
            player.vx = player.speed
            player.facing = 1

        player.update(platforms, coins, enemies, mushrooms, mushroom_bricks, fire_flowers, fire_flower_bricks, stars, star_bricks, world_width)
        player.update_fireballs(platforms, enemies)
        for m in mushrooms:
            m.update(platforms)
        for f in fire_flowers:
            f.update()
        for s in stars:
            s.update(platforms)
        for e in enemies:
            e.update(platforms, world_width)

        camera_x = player.rect.centerx - SCREEN_WIDTH // 2
        camera_x = max(0, min(camera_x, world_width - SCREEN_WIDTH))

        if not player.alive:
            lives -= 1
            sounds.play('death')
            if lives <= 0:
                state = "gameover"
                sounds.play('gameover')
            else:
                player = Player(*player_start)
                player.lives = lives
                # reset enemies to original positions and revive them
                for i, e in enumerate(enemies):
                    e.rect.x, e.rect.y = enemy_xy[i]
                    e.alive = True
                    e.vx = -1
                    e.vy = 0

        if player.rect.right >= world_width - 10:
            if current_level < len(LEVEL_DEFS) - 1:
                current_level += 1
                platforms, coins, enemies, mushrooms, mushroom_bricks, fire_flowers, fire_flower_bricks, stars, star_bricks, enemy_xy, player_start, world_width, world_height = load_level(current_level)
                flag_x = LEVEL_DEFS[current_level]['flag_x']
                player = Player(*player_start)
                player.lives = lives
                sounds.play('powerup')
                print(f"Level {current_level + 1}!")
            else:
                state = "win"
                sounds.play('win'); sounds.play('win2'); sounds.play('win3'); sounds.play('win4')
                print("You win!")

        draw_world(screen, platforms, coins, enemies, mushrooms, fire_flowers, stars, player, camera_x, flag_x)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()