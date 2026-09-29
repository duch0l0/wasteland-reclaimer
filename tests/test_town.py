"""
Проверка города без окна: бот ходит мышью, находит квестовых NPC, обыскивает,
дерётся, выходит на карту мира. Запуск из папки game_project:

    .venv/bin/python tests/test_town.py

Печатает OK/FAIL по каждой проверке; код выхода 1, если что-то не прошло.
"""
import os
import random
import sys
import time

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame  # noqa: E402

MOUSE = [(0, 0)]
pygame.mouse.get_pos = lambda: MOUSE[0]
pygame.mouse.get_focused = lambda: True

from src.game import Game  # noqa: E402
from src.combat import tile_of, rect_pos_for_tile, chebyshev, has_los  # noqa: E402
from src.entities import sprite_of  # noqa: E402
from src import settings as S  # noqa: E402

T = S.TILE
failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


random.seed(5)
g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 6  # проверяем карту, а не выживание


def fr(n=1):
    for _ in range(n):
        g.update(16)
        g.draw()
        if g.perk_choices:
            g.handle_key(pygame.K_1)


def click(pos, button=1):
    MOUSE[0] = pos
    g.draw()
    g.handle_click(pos, button)
    fr(1)


def fight():
    c = g.combat
    n = 0
    while c.active:
        if c.player_can_act():
            left = c.enemies_in_combat()
            t = c.target if c.target in left else (left[0] if left else None)
            if t is None:
                fr(1)
                continue
            c.target = t
            if c.can_attack(g.player, t)[0] and g.player.ap >= c.attack_cost(g.player):
                c.player_attack(0)
            elif g.player.ap >= 1:
                step = c._path_next_step(g.player, t)
                c.player_step(*step) if step else c.end_turn()
            else:
                c.end_turn()
        fr(1)
        n += 1
        if n == 39000:
            cur = c.current
            print("  ЗАВИС:", "ход:", cur and cur.name, "busy", c.busy_ms, "tweens", len(c.tweens),
                  "герой ОД", g.player.ap, "can_act", c.player_can_act(), "anim", g.player.anim.action, g.player.anim.once,
                  "attacking", g.player.attacking, [(e.name, tile_of(e), e.ap, e.anim.once) for e in c.enemies_in_combat()],
                  "герой", tile_of(g.player), "модалки", dict(dlg=g.dialogue.is_active(), craft=g.craft_open, inv=g.inv_open, trade=bool(g.trade), perk=bool(g.perk_choices), term=bool(g.term), slides=bool(g.slides), journal=g.journal_open, loot=bool(g.loot), menu=g.menu and g.menu["screen"]), g.log_lines[-3:])
        assert n < 40000, "бой завис"


def walk_to_npc(npc):
    """Как игрок: кликает по NPC на экране, а если его не видно — идёт в его сторону."""
    for _ in range(30):
        g.snap_camera()
        fr(1)
        _, r = sprite_of(npc, g.cam)
        from src.ui.common import hotspot_at
        covered = hotspot_at(r.center) is not None  # под миникартой или другим окном
        if covered or not pygame.Rect(0, 0, S.SCREEN_W, S.SCREEN_H - 104).collidepoint(r.center):
            px, py = tile_of(g.player)
            nx, ny = tile_of(npc)
            step = (px + max(-8, min(8, nx - px)), py + max(-4, min(4, ny - py)))
            if covered:  # подойти вплотную — камера сдвинется, NPC выйдет из-под миникарты
                step = (nx, ny + 2)
            g._go_to(lambda c, s=step: chebyshev(c, s) <= 1)
        else:
            click(r.center)
            if os.environ.get("DEBUG_WALK"):
                print("  клик по", npc.npc_id, "hint:", g.cursor_hint() and g.cursor_hint()[0], "autowalk:", bool(g.autowalk),
                      "герой", tile_of(g.player), "npc", tile_of(npc), g.log_lines[-1][:60])
        for _ in range(700):
            fr(1)
            if g.combat.active:
                fight()
            if g.dialogue.is_active():
                return True
            if not g.autowalk:
                break
    return False


t0 = time.time()
lv = g.level
ok(g.loc.name == "Пятнадцатая", f"старт в городе: {len(lv.objects)} объектов, {len(lv.containers)} мест для обыска")
bad = {"cobble", "dirt_slabs", "metal_sheet", "dirt_planks"}
ok(not any(n in bad for n, _ in lv.decals) and not any(o["name"] in bad for o in lv.objects),
   "квадратных кусков земли нет")
indoor_grass = [o["name"] for o in lv.objects
                if o["name"].startswith(("grass_", "bush_", "pole_", "sign_")) and
                any(lv.ground[y][x] == "c" for x, y in o["foot"])]
ok(not indoor_grass, f"в зданиях нет травы и знаков ({len(indoor_grass)})")

# здания замкнуты: из проходимого пола нельзя выйти на север, запад и восток мимо стены
# (на юг — только через двери, они в южной стене)
floor = {(x, y) for y in range(lv.height) for x in range(lv.width) if lv.ground[y][x] == "c"}
leaks = []
for x, y in floor:
    if lv.is_wall(x, y):
        continue  # пол под самой стеной
    for dx, dy in ((0, -1), (-1, 0), (1, 0)):
        n = (x + dx, y + dy)
        side_door = dx != 0 and lv.is_wall(x, y - 1) and lv.is_wall(x, y + 1)  # проём в боковой стене
        if n not in floor and not lv.is_wall(*n) and not side_door:
            leaks.append(n)
ok(not leaks, f"у зданий есть все стены (дыр: {len(leaks)}{', напр. ' + str(leaks[:3]) if leaks else ''})")

gena = next(n for n in g.npcs if n.npc_id == "gena")
ok(walk_to_npc(gena), "дошёл до Гены")
g.dialogue.close()
fr(1)
for nid, where in (("blondie", "у водокачки"), ("loner", "на свалке"), ("turtle", "в доме за дорогой")):
    npc = next(n for n in g.npcs if n.npc_id == nid)
    ok(walk_to_npc(npc), f"нашёл {npc.name} {where}")
    g.dialogue.close()
    fr(1)
ok({"gena", "blondie", "loner", "turtle"} <= lv.met, f"на миникарте отмечены: {sorted(lv.met)}")

box = next(o for o in lv.objects if o["container"] and not o["container"]["opened"]
           and o["name"].startswith(("locker", "filecab")))
bx, by = box["foot"][0]
spot = next((bx + dx, by + dy) for dy in (2, 3, 4) for dx in (0, 1, -1, 2, -2) if not lv.is_wall(bx + dx, by + dy))
g.player.rect.topleft = rect_pos_for_tile(g.player, spot)
g.snap_camera()
fr(1)
if g.combat.active:
    fight()
top = (box["rect"].centerx - int(g.cam.x), box["rect"].y + 12 - int(g.cam.y))
for attempt in range(5):  # рядом бродят мутанты — если начался бой, довоевать и кликнуть снова
    top = (box["rect"].centerx - int(g.cam.x), box["rect"].y + 12 - int(g.cam.y))
    click(top)
    for _ in range(900):
        fr(1)
        if box["container"]["opened"] or g.combat.active:
            break
    if g.combat.active:
        fight()
        g.snap_camera()
        continue
    if box["container"]["opened"]:
        break
ok(box["container"]["opened"] and g.loot, "клик по верху шкафчика — подошёл и открыл обыск")
if g.loot:
    g.handle_key(pygame.K_r)
    g.handle_key(pygame.K_ESCAPE)

wall = next(o for o in lv.objects if o["name"].startswith("wall_"))
wx, wy = wall["foot"][0]
ok(not has_los(lv, (wx * T + 24, (wy - 2) * T + 24), (wx * T + 24, (wy + 2) * T + 24)), "стена закрывает обзор")

for e in list(g.enemies):
    if not e.alive:
        continue
    g.player.rect.topleft = rect_pos_for_tile(g.player, tile_of(e))
    g.combat._snap_to_grid(g.player)
    g.snap_camera()
    fr(1)
    if not g.combat.active:
        g.combat.start(player_first=True)
    fight()
ok(all(not e.alive for e in g.enemies), f"все враги побеждены, уровень {g.player.level_sys.level}")

g.player.rect.topleft = rect_pos_for_tile(g.player, (45, 61))
g.held_letters.add(pygame.K_s)
for _ in range(300):
    fr(1)
    if g.mode == "world":
        break
g.held_letters.clear()
ok(g.mode == "world", "выход на юг — карта мира")
g.handle_key(pygame.K_e)
fr(1)
ok(g.mode == "local" and len(g.level.explored) > 500, "вернулся — разведанное помнится")
g.reveal_location("station")
g.enter_location("station")
fr(5)
ok(g.loc.id == "station", "заправка (текстовая карта) работает")

print(f"время {round(time.time() - t0)} с; не прошло: {len(failed)}")
sys.exit(1 if failed else 0)
