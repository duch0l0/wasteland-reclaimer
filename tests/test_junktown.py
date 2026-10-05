"""
Джанктаун (tools/build_junktown.py) — без окна: улица за стеной из хлама, казино «Гизмо», клиника Анны Шоу,
подвал с архивом, бар «Скам-Питт», ратуша, свалка.

  - по трассе на восток — двор старой школы, через дверь — здание; мисс Лейн и терминал директора;
  - люк в подвал деда закрыт, пока не прочитана записка в его терминале; в подвале — сундук и терминал;
  - люк в подвал салуна — после разговора с Мо; внизу Тесс.

    .venv/bin/python tests/test_junktown.py
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



# Джанктаун открывается на карте после Хаба
g.enter_location("hub")
fr(g)
g.sync_story()
ok("junktown" in g.worldmap.known, "после Хаба на карте — Джанктаун")
g.enter_location("junktown")
fr(g)
ok(g.loc.id == "junktown" and len(g.npcs) >= 8, "Джанктаун: улица, жители")
ok(all(g.level.is_wall(4, y) for y in (10, 20, 35, 45)), "стена из хлама — не пройти")
for to in ("junktown_casino", "junktown_hall", "junktown_store", "junktown_clinic", "junktown_skum"):
    goto(g, sorted(portal(g, to)["tiles"])[0])
    ok(g.loc.id == to, f"вход: {g.loc.name}")
    g.dialogue.active_node = None
    goto(g, sorted(next(p for p in g.level.portals if p["to"] == "junktown")["tiles"])[0])
    ok(g.loc.id == "junktown", "обратно на улицу")

# путь через долг: Рурк в баре, книга Гизмо, мэр
goto(g, sorted(portal(g, "junktown_skum")["tiles"])[0])
talk("hunter_rourke")
say("Кто тебя нанял")
say("Понятно")
ok(g.flags.get("know_rourke_cult"), "Рурк: белая тесёмка — его кредитор культ")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "junktown")["tiles"])[0])
goto(g, sorted(portal(g, "junktown_casino")["tiles"])[0])
talk("gizmo")
say("продал долг")
say("Где")
say("...")
ok(g.flags.get("know_gizmo_book"), "Гизмо проговорился о долговой книге")

# клиника: подвал закрыт, пока Анна не доверяет
g.dialogue.active_node = None
goto(g, sorted(portal(g, "junktown")["tiles"])[0])
goto(g, sorted(portal(g, "junktown_clinic")["tiles"])[0])
goto(g, sorted(portal(g, "junktown_cellar")["tiles"])[0])
ok(g.loc.id == "junktown_clinic", "люк в подвал заперт")
g.flags["know_baker"] = True
g.dialogue.active_node = None
talk("anna_shaw")
say("внук Эймоса")
say("Посмотрю")
ok(g.flags.get("anna_trust"), "Анна Шоу — ветеран Марипозы — доверяет внуку Рида")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "junktown_cellar")["tiles"])[0])
ok(g.loc.id == "junktown_cellar", "через люк — в подвал клиники")
g.open_terminal("anna_archive")
g.term_open_entry(2)
g.close_terminal()
ok(g.flags.get("know_cobbs_necropolis"), "архив Анны: Коббс ушёл к гулям в Некрополь")

# свалка за восточными воротами
g.dialogue.active_node = None
goto(g, sorted(portal(g, "junktown_clinic")["tiles"])[0])
goto(g, sorted(portal(g, "junktown")["tiles"])[0])
goto(g, sorted(portal(g, "junktown_dump")["tiles"])[0])
ok(g.loc.id == "junktown_dump", "на восток — свалка")
ok(any(c["name"] == "ящик наёмников" for c in g.level.containers), "на свалке — стоянка наёмников с распиской")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
