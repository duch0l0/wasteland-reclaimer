"""
Карманы (K у жителя): стащить ключ, попасться с поличным, подбросить динамит или улику.
Навык «Ловкость рук», свидетели, стража, сейфы по ключу из кармана, подстава в детективе.

    .venv/bin/python tests/test_pickpocket.py
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

pygame.mouse.get_pos = lambda: (-50, -50)
pygame.mouse.get_focused = lambda: True

from src.game import Game, saveload  # noqa: E402
from src.combat import tile_of, rect_pos_for_tile  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()
failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


def fr(g, n=3):
    for _ in range(n):
        g.update(16)
        g.draw()
        while g.perk_choices:
            g.handle_key(pygame.K_1)


def near(g, nid, side=(0, -1)):
    npc = next(n for n in g.npcs if n.npc_id == nid)
    t = tile_of(npc)
    for dx, dy in (side, (1, 0), (-1, 0), (0, 1)):
        c = (t[0] + dx, t[1] + dy)
        if not g.level.is_wall(*c):
            g.player.rect.topleft = rect_pos_for_tile(g.player, c)
            break
    fr(g, 1)
    return npc


def go(g, lid):
    g.dialogue.active_node = None
    g.enter_location(lid)
    g.slides = None
    fr(g)


import random  # noqa: E402

# ---- стащить ключ у Декера: мастер-карманник, никого рядом
g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 5
g.player.skills["steal"] = 150
go(g, "hub_old")
for n in list(g.npcs):
    if n.npc_id != "decker":
        g.npcs.remove(n)              # без свидетелей
near(g, "decker")
g.handle_key(pygame.K_k)
ok(g.loot and g.loot["box"].get("pocket") is not None and "ключ от сейфа Декера" in g.loot["box"]["loot"], "K у Декера — его карманы")
dk = next(n for n in g.npcs if n.npc_id == "decker")
master = g.steal_chance(dk, "ключ от сейфа Декера")
g.player.skills["steal"] = 20
novice = g.steal_chance(dk, "ключ от сейфа Декера")
novice_caps = g.steal_chance(dk, "крышки")
g.player.skills["steal"] = 90
pro = g.steal_chance(dk, "ключ от сейфа Декера")
ok(master <= 60 and novice <= 5 and novice_caps <= 15 and 25 <= pro <= 50,
   f"сюжетный ключ стерегут: новичок {novice}%, мастер-90 {pro}%, предел {master}%; крышки новичку {novice_caps}%")
g.player.skills["steal"] = 150
random.randint = lambda a, b: a            # бросок удался
g.loot_take("ключ от сейфа Декера")
after = g.steal_chance(dk, "крышки")
g.player.skills["steal"] = 90
ok(g.steal_chance(dk, "крышки") < pro + 45 and g.flags.get("pocket_heat_decker") == 1, f"после кражи Декер насторожился (крышки мастеру-90: {g.steal_chance(dk, 'крышки')}%)")
g.player.skills["steal"] = 150
ok(g.inventory.has("ключ от сейфа Декера"), "ключ от сейфа стащен")
g.loot = None
box = next(c for c in g.level.containers if c["name"] == "сейф Декера")
ok(g.check_condition(box["requires"]), "сейф Декера открывается его же ключом — без отмычки")
g.flags.pop("pocket_decker", None)

# ---- попасться: без навыка, при свидетелях
g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 5
g.player.skills["steal"] = 0
go(g, "hub")
npc = near(g, "arms_seller")
g.handle_key(pygame.K_k)
chance = g.steal_chance(npc, "крышки")
random.randint = lambda a, b: b            # бросок провален
for _ in range(10):
    if not g.loot:
        break
    g.loot_take("крышки")
ok(chance <= 25 and g.flags.get("arms_seller_robbed") and g.flags.get("caught_stealing"), f"неумеха при свидетелях (шанс {chance}%) — пойман")
g.open_trade("arms_seller")
ok(not g.trade, "обворованный торговец больше не торгует")
g.loot = None
g.handle_key(pygame.K_k)
ok(not g.loot, "к пойманному на краже второй раз не подобраться")
other = next(n for n in g.npcs if n.npc_id != "arms_seller")
g.player.rect.topleft = rect_pos_for_tile(g.player, (tile_of(other)[0], tile_of(other)[1] - 1))
g.player.skills["steal"] = 120
w1 = g.steal_chance(other, "крышки")
g.flags.pop("wary_hub", None)
w0 = g.steal_chance(other, "крышки")
ok(w0 - w1 == 25 or (w1 == 3 and w0 > 3), f"после поимки весь город настороже ({w0}% → {w1}%)")

# ---- динамит в кармане
g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 5
g.player.skills["steal"] = 150
g.inventory.add("динамит", 1)
go(g, "goodsprings")
for n in list(g.npcs):
    if n.npc_id != "gs_old":
        g.npcs.remove(n)
near(g, "gs_old")
g.handle_key(pygame.K_k)
random.randint = lambda a, b: a
g.loot_put("динамит")
g.loot = None
ok(g.bombs and not g.inventory.has("динамит"), "динамит подброшен — фитиль тлеет")
g.player.rect.topleft = rect_pos_for_tile(g.player, (tile_of(g.player)[0] - 10, tile_of(g.player)[1]))
k0 = g.karma
for _ in range(260):
    g.update(16)
ok(g.flags.get("killed_gs_old") and not any(n.npc_id == "gs_old" for n in g.npcs) and g.karma < k0,
   "взрыв: старика Изи больше нет, карма вниз")

# ---- подстава в детективе
g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 5
g.player.skills["steal"] = 150
g.inventory.add("фартук в крови", 1)
go(g, "goodsprings_saloon")
for n in list(g.npcs):
    if n.npc_id not in ("luis_cards", "deputy_abby"):
        g.npcs.remove(n)
near(g, "luis_cards")
g.handle_key(pygame.K_k)
g.loot_put("фартук в крови")
g.loot = None
ok(g.flags.get("murder_framed_luis"), "фартук с ножом подброшен Луису")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
