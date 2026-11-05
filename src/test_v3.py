import os, sys
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import super_mario as sm

platforms, coins, enemies, mushrooms, mushroom_bricks, enemy_xy, ps, ww, wh = sm.load_level()
p = sm.Player(*ps)

for f in range(300):
    p.vx = p.speed
    p.update(platforms, coins, enemies, mushrooms, mushroom_bricks, ww)
    for m in mushrooms:
        m.update(platforms)
    for e in enemies:
        e.update(platforms, ww)
    if not p.alive:
        print('Player died at frame', f, 'x=', p.rect.x)
        break

print('Frames OK:', f+1)
print('Coins:', p.coins)
print('Player pos:', p.rect.x, p.rect.y)
print('on_ground:', p.on_ground)
print('Enemies alive:', sum(1 for e in enemies if e.alive))
print('Mushrooms:', len(mushrooms), 'Mushroom bricks:', len(mushroom_bricks))
print('TEST_DONE')
