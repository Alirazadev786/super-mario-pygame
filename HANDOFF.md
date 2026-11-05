"# SuperMario Handoff Summary
# Created: Nov 2, 2025
# Purpose: Full context for continuing work in a NEW chat. Read this file first.

## Project Overview
- Super Mario-style 2D platformer (Pygame)
- Latest version: **v3** (incredibly improved level, physics, enemies, win state)

## File Locations (ALL IMPORTANT)
| File | Path |
|---|---|
| Main game source | `~/Desktop/SuperMario/src/super_mario.py` |
| Backup v3 copy | `~/Desktop/SuperMario/src/super_mario_v3.py` |
| Build script | `~/Desktop/SuperMario/src/build_app.py` |
| Test script (v2) | `~/Desktop/SuperMario/src/test_game.py` |
| Test script (v3) | `~/Desktop/SuperMario/src/test_v3.py` |
| Final DMG | `~/Desktop/SuperMario/super_mario.dmg` (26MB) |
| Installed app | `/Applications/SuperMario.app` |
| DMG staging folder | `~/Desktop/SuperMario/final_build/` |

## Verified State (all confirmed before handoff)
- DMG internal game file MD5 == `13524266308f369179ec282a350d8e8f`
- Installed app super_mario.py MD5 == `13524266308f369179ec282a350d8e8f`
- Installed app launch test: `GAME_RUNNING_OK`
- Local `super_mario.py` == `super_mario_v3.py` (same content)

## Game Features (v3)
- Level: 170 columns = 6800px world width, 15 rows = 600px height
- Platforms: 216 | Coins: 29 | Enemies: 12
- Pits (gaps) at columns: 45-48, 80-83, 115-118, 145-148
- Structures: bricks (reachable rows), pipes (2-3 tall), staircase, flagpole at x=6680
  - Bricks break when hit from below (original Mario style)
  - 6 hidden mushrooms inside bricks (13,11), (53,11), (92,11), (125,11), (156,11), (74,12)
  - Mushroom grows player to BIG (64px tall), second mushroom gives +10 coins
- Combat: stomp from above = kill enemy (+5 coins); side hit = player death
  - BIG player survives 1 hit (shrinks to small); small player dies on side hit
  - Stomp bounce is higher (vy = -10) for easier chains
- Lives system: 3 lives; death respawns at start; enemies reset to original positions on respawn
- Win: reaching right edge (~ x >= world_width - 10) triggers WIN screen
- Camera: follows player, clamped to world bounds
- Controls: Arrows move, Space jump, Enter start, R restart, Esc menu

## Key Code Notes
- Python: `/opt/homebrew/bin/python3.13` (Homebrew)
- pygame 2.6.1 installed in venv at `/Applications/SuperMario.app/Contents/Resources/venv/`
- To run source directly: `~/Desktop/SuperMario/src/venv` doesn't exist; use installed app venv or:
  `~/Desktop/Mark-LV-main/.venv/bin/python ~/Desktop/SuperMario/src/super_mario.py`
- Build DMG from source: `cd ~/Desktop/SuperMario/src && ~/Desktop/Mark-LV-main/.venv/bin/python build_app.py`

## How to Run / Test
- Installed app: `open /Applications/SuperMario.app`
- Headless test: `cd ~/Desktop/SuperMario/src && SDL_VIDEODRIVER=dummy ~/Desktop/Mark-LV-main/.venv/bin/python test_v3.py`
- MD5 check: `md5 -q ~/Desktop/SuperMario/src/super_mario_v3.py`
- Expected: `13524266308f369179ec282a350d8e8f`

## Recent Fix History (v1 -> v3)
1. v1: Player drew without camera offset -> character appeared broken/offscreen
9. Jump power increased: -13 -> -15 (for tall walls with coins)
10. Bricks break from below (platform removed, mushroom emerges)
11. Mushroom power-up: grow to 64px, 2-hit system (big->small->death)
12. Enemies reset to original positions on respawn (no more instant deaths)
13. Hit flash animation when big player gets hit
2. Fixed: player.draw(screen, camera_x)
3. Fixed: continuous jump spam -> pygame.key.set_repeat(0,0)
4. Fixed: enemies floating -> added gravity + platform collision in Enemy class
5. Fixed: level too tall (31 rows=1240px > screen 600px) -> redesigned to 15 rows
6. Fixed: lives reset on respawn -> tracked via external `lives` variable
7. Added win state screen (was just returning to menu)
8. v3: full Mario-style level redesign (longer, pits, stairs, 12 enemies, flagpole)

## Remaining / Potential Next Steps
- [ ] Add sound effects
- [ ] Add animations (walking, jumping)
- [x] Add power-ups (mushroom grow/shrink, 2-hit system)
- [ ] Add star power-up (invincibility)
- [ ] More levels / world progression
- [ ] High score persistence
"