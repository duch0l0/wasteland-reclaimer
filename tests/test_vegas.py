"""
Руины Вегаса (tools/build_vegas.py) — без окна: «Три Короны» — Сапоги, Змеи, Ладони; секреты Корон и совет на
Стрипе; башня Vault-Tec, замок «Ноля» (питание, коды, двое из Списка), капсула и судьба десяти контейнеров.

    .venv/bin/python tests/test_vegas.py
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
        while g.perk_choices:          # новый уровень за квесты — выбрать первое
            g.handle_key(pygame.K_1)


def goto(g, t):
    g.player.rect.topleft = rect_pos_for_tile(g.player, t)
    g.snap_camera()
    fr(g)


def portal(g, to):
    return next(p for p in g.level.portals if p["to"] == to)


def stand_near(g, t):
    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1)):
        c = (t[0] + dx, t[1] + dy)
        if not g.level.is_wall(*c):
            g.player.rect.topleft = rect_pos_for_tile(g.player, c)
            g.snap_camera()
            return


g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 6


def say(part):
    opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
    idx = next((i for i, l in enumerate(opts) if part in l), None)
    assert idx is not None, f"нет реплики «{part}» среди {opts}"
    g.handle_key(pygame.K_1 + idx)
    fr(g, 1)


def talk(nid):
    g.dialogue.active_node = None
    npc = next(n for n in g.npcs if n.npc_id == nid)
    stand_near(g, tile_of(npc))
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active(), nid














g.flags["know_zero"] = True
g.sync_story()
ok("vegas_strip" in g.worldmap.known, "узнал про «Ноль» — Вегас на карте")
g.enter_location("vegas_strip")
fr(g)
ok(g.loc.id == "vegas_strip" and g.level.night, "Стрип ночью")
for to in ("vegas_boots", "vegas_snakes", "vegas_palms"):
    goto(g, sorted(portal(g, to)["tiles"])[0])
    ok(g.loc.id == to, f"район: {g.loc.name}")
    goto(g, sorted(next(p for p in g.level.portals if p["to"] == "vegas_strip")["tiles"])[0])
    ok(g.loc.id == "vegas_strip", "обратно на Стрип")

# Сапоги: подкова и вор-ребёнок — отпустить; Змеи: подвал; Ладони: книги
goto(g, sorted(portal(g, "vegas_boots")["tiles"])[0])
talk("hank_spur")
say("Найду вора")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "vegas_strip")["tiles"])[0])
goto(g, sorted(portal(g, "vegas_snakes")["tiles"])[0])
talk("snake_kid")
say("Отдай подкову")
ok(g.inventory.has("подкова Шпоры") and g.flags.get("boots_thief_spared"), "воришка отпущен, подкова у героя")
g.dialogue.active_node = None

# секреты трёх Корон — из терминалов
import json as _json
_T = _json.load(open("data/terminals.json", encoding="utf-8"))["terminals"]
for tid, flag in (("palms_infirmary", "boots_secret"), ("snakes_ledger", "snakes_secret"), ("agatha_salon", "palms_secret")):
    entry = _T[tid]["entries"][1]                 # запись под паролем — открывается взломом терминала
    assert entry.get("lock") and {"type": "set_flag", "flag": flag} in entry["effects"], tid
    g.flags[flag] = True
ok(g.flags.get("boots_secret") and g.flags.get("snakes_secret") and g.flags.get("palms_secret"), "секреты трёх Корон")

# совет Корон на Стрипе — Короны объединяются
goto(g, sorted(portal(g, "vegas_strip")["tiles"])[0])
g.player.skills["speech"] = 90
talk("judge_sol")
say("Созови совет")
say("культ идёт")
say("Пусть так")
ok(g.flags.get("crowns_united") and g.flags.get("boots_power") and g.flags.get("snakes_passage"), "три Короны за одним столом")

# питание на башню, змеиные ходы — в башню, лифт — к «Нолю»
g.dialogue.active_node = None
g.open_terminal("boots_power")
g.term_open_entry(1)
g.close_terminal()
ok(g.flags.get("zero_power"), "Сапоги дают ток в башню")
goto(g, sorted(portal(g, "vegas_snakes")["tiles"])[0])
goto(g, sorted(portal(g, "vegas_tunnels")["tiles"])[0])
ok(g.loc.id == "vegas_tunnels", "змеиные ходы")
for e in g.enemies:
    e.alive = False
goto(g, sorted(portal(g, "vegas_tower")["tiles"])[0])
ok(g.loc.id == "vegas_tower", "подвал башни Vault-Tec")
for e in g.enemies:
    e.alive = False
goto(g, sorted(portal(g, "vegas_zero")["tiles"])[0])
ok(g.loc.id == "vegas_zero", "лифт — вниз, к шлюзу «Ноля»")
for e in g.enemies:
    e.alive = False

# замок: коды совета, сетчатка Хьюго, голос Коббса
g.flags["hugo_joins"] = True
g.flags["cobbs_clear"] = True
g.open_terminal("zero_door")
for _ in range(3):
    g.term_open_entry(1)
g.close_terminal()
ok(g.flags.get("zero_open"), "замок «Ноля»: питание, коды и двое из Списка")
goto(g, sorted(portal(g, "vegas_vault")["tiles"])[0])
ok(g.loc.id == "vegas_vault", "внутри «Ноля»: десять контейнеров и капсула")
talk("cooper_zero")
say("Делай")
ok(g.flags.get("sleeper_dead") and g.flags.get("cooper_friend"), "Купер у капсулы — член совета Vault-Tec больше не проснётся")
g.dialogue.active_node = None
g.open_terminal("zero_vault")
g.term_open_entry(1)
g.close_terminal()
ok(g.flags.get("zero_fate"), "судьба последней партии ВРЭ решена")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
