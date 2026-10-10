"""
Ринг «Скам-Питта» (docs/city_plan.md, этап 2): бой на кулаках до нокаута — никто не умирает, ставки,
договор с Гизмо «лечь в третьем раунде», лестница из пяти бойцов до чемпиона.

    .venv/bin/python tests/test_ring.py
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


def talk(g, nid):
    g.dialogue.active_node = None
    npc = next(n for n in g.npcs if n.npc_id == nid)
    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1)):
        c = (tile_of(npc)[0] + dx, tile_of(npc)[1] + dy)
        if not g.level.is_wall(*c):
            g.player.rect.topleft = rect_pos_for_tile(g.player, c)
            break
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active(), nid


def say(g, part):
    opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
    idx = next((i for i, l in enumerate(opts) if part in l), None)
    assert idx is not None, f"нет реплики «{part}» среди {opts}"
    g.handle_key(pygame.K_1 + idx)
    fr(g, 1)


def go(g, lid):
    g.dialogue.active_node = None
    g.enter_location(lid)
    g.slides = None
    for e in g.enemies:
        e.alive = False
    fr(g)


def read(g, item):
    g.item_action(item)[1]()
    g.close_terminal()


def take(g, title):
    box = next(c for c in g.level.containers if c["name"] == title)
    for t in box["tiles"]:
        for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, -1)):
            c = (t[0] + dx, t[1] + dy)
            if not g.level.is_wall(*c) and c not in box["tiles"]:
                g.player.rect.topleft = rect_pos_for_tile(g.player, c)
                g.handle_key(pygame.K_e)
                fr(g, 1)
                if g.loot:
                    g.handle_key(pygame.K_r)
                    g.loot = None
                return



from src.combat import chebyshev  # noqa: E402


def box(g, max_frames=20000):
    """Драться, пока гонг не прозвучит: подойти вплотную и бить."""
    for _ in range(max_frames):
        if not g.ring:
            return
        c = g.combat
        if c.active and c.player_can_act() and c.busy_ms <= 0:
            opp = g.ring["opp"]
            me, it = tile_of(g.player), tile_of(opp)
            if chebyshev(me, it) <= 1:
                c.target = opp
                if g.player.ap >= c.attack_cost(g.player):
                    c.player_attack()
                else:
                    g.handle_key(pygame.K_r)
            else:
                dx = (it[0] > me[0]) - (it[0] < me[0])
                dy = (it[1] > me[1]) - (it[1] < me[1])
                before = g.player.ap
                c.player_step(dx, dy)
                if g.player.ap == before:
                    g.handle_key(pygame.K_r)
        g.update(16)
        while g.perk_choices:
            g.handle_key(pygame.K_1)


def fresh():
    g = Game(intro=False)
    go(g, "junktown_skum")
    for n in list(g.npcs):
        if n.npc_id not in ("neal",):
            g.npcs.remove(n)
    return g


# ---- победа: кулаки, ставка, никто не умер
g = fresh()
g.player.max_hp = g.player.hp = 400
g.player.skills["melee"] = 150
g.inventory.add("крышки", 50)
g.player.weapon = "machete" if "machete" in __import__("src.weapons", fromlist=["WEAPONS"]).WEAPONS else g.player.weapon
w0 = g.player.weapon
talk(g, "neal"); say(g, "ринге"); say(g, "следующий"); say(g, "Ставлю на себя 50")
ok(g.ring and g.combat.active and g.player.weapon == "melee", "бой начался, в руках только кулаки")
c0 = g.inventory.count("крышки")
box(g)
ok(g.flags.get("ring_wins") == 1 and g.inventory.count("крышки") - c0 == 40 + 100, "нокаут Мясника Бо: приз 40 и ставка вдвое")
ok(g.player.weapon == w0 and not any(getattr(e, "ring", False) for e in g.enemies), "оружие вернулось, боец ушёл с ринга")

# ---- поражение: нокаут, а не смерть
g = fresh()
g.player.max_hp = g.player.hp = 12
g.player.skills["melee"] = 5
g.flags["ring_wins"] = 4
talk(g, "neal"); say(g, "ринге"); say(g, "следующий"); say(g, "Без ставки")
box(g)
ok(g.player.alive and g.player.hp >= 1 and not g.game_over and g.flags.get("ring_losses") == 1, "Бык Маккой отправил в нокаут — живой, 1 HP")
ok(g.flags.get("ring_wins") == 4, "лестница не сдвинулась — можно прийти ещё")

# ---- Гизмо просит лечь в третьем раунде
g = fresh()
g.player.max_hp = g.player.hp = 400
g.player.skills["melee"] = 30
g.flags["ring_wins"] = 2
talk(g, "neal"); say(g, "ринге"); say(g, "следующий"); say(g, "готов"); say(g, "Лягу")
c0 = g.inventory.count("крышки")
box(g)
ok(g.flags.get("ring_dived") and g.inventory.count("крышки") - c0 == 300 and g.flags.get("ring_wins") == 2, "лёг в третьем раунде — триста от Гизмо")

g = fresh()
g.player.max_hp = g.player.hp = 400
g.player.skills["melee"] = 150
g.player.base_damage = 60
g.flags["ring_wins"] = 2
talk(g, "neal"); say(g, "ринге"); say(g, "следующий"); say(g, "готов"); say(g, "Лягу")
box(g)
ok(g.flags.get("ring_crossed_gizmo") and g.flags.get("ring_wins") == 3, "согласился лечь — и вырубил Изо раньше: Гизмо обманут")

# ---- путь до чемпиона
g = fresh()
g.player.max_hp = g.player.hp = 1000
g.player.skills["melee"] = 150
g.player.base_damage = 60
m0 = g.player.skill("melee")
for i in range(5):
    talk(g, "neal"); say(g, "ринге"); say(g, "следующий")
    if i == 2:
        say(g, "готов"); say(g, "ложусь только спать")
    say(g, "Без ставки")
    box(g)
    g.player.hp = g.player.max_hp
ok(g.flags.get("ring_champion") and g.inventory.has("пояс чемпиона Джанктауна") and g.player.skill("melee") == m0 + 10,
   "пять нокаутов — чемпион Джанктауна, пояс и +10 к Рукопашной")
talk(g, "neal")
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok(not any("ринге" in o for o in opts), "чемпиону больше не с кем драться")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
