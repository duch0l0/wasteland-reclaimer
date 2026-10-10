"""
Интерфейс: меню действий по ПКМ (как в Fallout 2), кража через меню, вкладка «Персонаж» в журнале
(все перки и навыки с описаниями), подсказки навыков и перков в рюкзаке.

    .venv/bin/python tests/test_ctxmenu.py
"""
import os
import sys
import tempfile

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame  # noqa: E402

pygame.mouse.get_focused = lambda: True

from src.game import Game, saveload  # noqa: E402
from src.combat import tile_of, rect_pos_for_tile  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()
failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


MOUSE = [(-50, -50)]
pygame.mouse.get_pos = lambda: MOUSE[0]


def fr(g, n=3):
    for _ in range(n):
        g.update(16)
        g.draw()


def screen_pos_of(g, ent):
    for sy in range(0, 600, 6):
        for sx in range(0, 1280, 6):
            if g.entity_at_screen((sx, sy)) is ent:
                return (sx, sy)
    return None


SHOTS = sys.argv[1] if len(sys.argv) > 1 else None
g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 5
g.enter_location("hub")
g.slides = None
for e in g.enemies:
    e.alive = False
fr(g)
npc = next(n for n in g.npcs if n.npc_id == "spice_seller")
t = tile_of(npc)
g.player.rect.topleft = rect_pos_for_tile(g.player, (t[0] - 3, t[1]))
fr(g, 5)
pos = screen_pos_of(g, npc)
ok(pos is not None, "житель виден на экране")
g.handle_click(pos, 3)
labels = [l for l, _ in g.ctx_menu["items"]] if g.ctx_menu else []
ok(labels[:1] == ["Говорить"] and any(l.startswith("Обокрасть") for l in labels) and "Напасть" in labels,
   f"ПКМ по жителю — меню: {labels}")
ok(g.modal_open(), "пока меню открыто — мир не кликается")
fr(g, 2)
if SHOTS:
    pygame.image.save(g.screen, os.path.join(SHOTS, "ctx_menu.png"))
g.handle_key(pygame.K_ESCAPE)
ok(g.ctx_menu is None, "Esc закрывает меню")
g.handle_click(screen_pos_of(g, npc), 3)
g.handle_click((5, 5), 1)
ok(g.ctx_menu is None, "клик мимо закрывает меню")

g.handle_click(screen_pos_of(g, npc), 3)
g.handle_key(pygame.K_3)            # Обокрасть
for _ in range(900):
    g.update(16)
    if g.loot:
        break
g.draw()
ok(g.loot and g.loot["box"].get("pocket") is npc, "«Обокрасть» — подошёл и открыл карманы торговца")
if SHOTS:
    pygame.image.save(g.screen, os.path.join(SHOTS, "ctx_pocket.png"))
g.loot = None

g.handle_click(screen_pos_of(g, npc), 3)
g.handle_key(pygame.K_2)            # Осмотреть
ok(g.speech and "Обокрасть" in g.log_lines[-1], "«Осмотреть» — облачко со словами жителя и подсказка про карманы")

# ящик
box = g.level.containers[0]
bt = box["tiles"][0]
g.player.rect.topleft = rect_pos_for_tile(g.player, (bt[0] - 2, bt[1]))
fr(g, 5)
spot = None
for sy in range(0, 600, 4):
    for sx in range(0, 1280, 4):
        o = g.object_at_screen((sx, sy))
        if o and o[1] is box:
            spot = (sx, sy)
            break
    if spot:
        break
g.handle_click(spot, 3)
ok(g.ctx_menu and [l for l, _ in g.ctx_menu["items"]] == ["Обыскать", "Осмотреть"], "ПКМ по ящику — обыскать / осмотреть")
g.ctx_menu = None

# журнал: вкладка «Персонаж»
for pid in ("action_boy", "bonus_move", "thick_skin", "sharp_eye"):
    g.player.perks[pid] = 1
g.player.perks["steady_hand"] = 1
g.journal_open = True
g.handle_key(pygame.K_TAB)
g.handle_key(pygame.K_TAB)
ok(g.journal_tab == "char", "Tab: задания → репутация → персонаж")
fr(g, 1)
from src.ui.journal_ui import character_lines  # noqa: E402
text = " ".join(t for _, t in character_lines(g))
ok("Толстокожий" in text and "+10 к классу брони" in text and "нажать K" in text, "все перки с описаниями и как воровать")
if SHOTS:
    pygame.image.save(g.screen, os.path.join(SHOTS, "journal_char.png"))
g.journal_open = False

# рюкзак: наведение на перк — описание справа; клик — журнал
g.open_inventory()
fr(g, 1)
found = None
for sy in range(380, 600, 3):
    MOUSE[0] = (40, sy)
    g.draw()
    if "Перк" in pygame.image.tostring(g.screen, "RGB")[:0].decode() or False:
        pass
from src.ui import common  # noqa: E402
for sy in range(380, 600, 3):
    MOUSE[0] = (60, sy)
    g.draw()
    key = common.hotspot_at((60, sy))
    if callable(key) and getattr(key, "__name__", "") == "<lambda>":
        found = sy
if SHOTS and found:
    MOUSE[0] = (60, found)
    g.draw()
    pygame.image.save(g.screen, os.path.join(SHOTS, "inv_perk.png"))
ok(found is not None, "строки перков в рюкзаке кликабельны")
common.hotspot_at((60, found))()
ok(g.journal_open and g.journal_tab == "char" and not g.inv_open, "клик по перку — журнал, вкладка «Персонаж»")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
