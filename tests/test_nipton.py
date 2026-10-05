"""
Ниптон (tools/build_nipton.py) — без окна: «Лотерея»: подстроенный жребий, вожак «женихов» — сын первой
проигравшей, брат Т. в шахте (Тобиас из Бейкера, если его пощадили).

    .venv/bin/python tests/test_nipton.py
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












g.flags["know_nipton_lottery"] = True
g.sync_story()
ok("nipton" in g.worldmap.known, "голоса Иезекииля — Ниптон на карте")
g.enter_location("nipton")
fr(g)
ok(g.loc.id == "nipton" and len(g.npcs) >= 8, "Ниптон: площадь с жребием, ратуша, сарай")

# ратуша: книга города — жребий подстроен; список из сейфа
goto(g, sorted(portal(g, "nipton_hall")["tiles"])[0])
ok(g.loc.id == "nipton_hall", "вход: ратуша")
g.open_terminal("nipton_ledger")
g.term_open_entry(1)
g.close_terminal()
ok(g.flags.get("know_lottery_rigged"), "книга: проигрывают должники, чужаки и вдовы с землёй")
g.inventory.add("список жребия", 1)
goto(g, sorted(portal(g, "nipton")["tiles"])[0])

# бабка Мэй — первая проигравшая и её сын
talk("np_old_mae")
say("Спасибо")
ok(g.flags.get("know_mary_hawthorne"), "Мэри Хоторн и её сын Кэл")
g.dialogue.active_node = None

# лагерь «женихов»: Кэл узнаёт правду и поворачивается против брата Т.
goto(g, sorted(portal(g, "nipton_camp")["tiles"])[0])
ok(g.loc.id == "nipton_camp", "лагерь «женихов»")
talk("groom_cal")
say("Мэри Хоторн")
say("Мэр выбирает")
say("Иди")
ok(g.flags.get("grooms_turned") and g.flags.get("nipton_decided"), "Кэл разрывает договор и идёт на брата Т.")

# брат Т. в шахте — Тобиас, если его пощадили в Бейкере
g.dialogue.active_node = None
g.flags["tobias_done"] = True
g.player.skills["speech"] = 80
goto(g, sorted(portal(g, "nipton_mine")["tiles"])[0])
ok(g.loc.id == "nipton_mine", "старая шахта")
talk("brother_t")
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok(any("Тобиас" in o for o in opts), "брат Т. — это Тобиас из Бейкера")
say("нужно в Ниптоне")
say("Не знаю")
say("...")
ok(g.flags.get("know_cult_race") and g.flags.get("brother_t_flees"), "гонка за «Ноль»: у культа голос Коббса, брат Т. уходит в Марипозу")

# второй путь: жетон с зазубриной — жребий вытягивает мэр
g.dialogue.active_node = None
g.flags.pop("nipton_decided", None)
g.inventory.add("жетон жребия", 1)
g.sync_story()
ok(g.flags.get("nipton_token_swapped"), "жетон мэра у героя — в барабане остался только его")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
