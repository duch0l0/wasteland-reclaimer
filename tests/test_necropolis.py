"""
Некрополь (tools/build_necropolis.py) — без окна: руины Бейкерсфилда, Зал Мёртвых, Водораздел, квартира Коббса,
подземка гулей, Убежище 12. Насос чинится платой из Убежища — и Сет отказывается отдать Коббса культу.

  - по трассе на восток — двор старой школы, через дверь — здание; мисс Лейн и терминал директора;
  - люк в подвал деда закрыт, пока не прочитана записка в его терминале; в подвале — сундук и терминал;
  - люк в подвал салуна — после разговора с Мо; внизу Тесс.

    .venv/bin/python tests/test_necropolis.py
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




# Некрополь открывается после Джанктауна
g.enter_location("junktown")
fr(g)
g.sync_story()
ok("necropolis" in g.worldmap.known, "после Джанктауна на карте — Некрополь")
g.enter_location("necropolis")
fr(g)
for e in g.enemies:
    e.hostile = False
ok(g.loc.id == "necropolis" and len(g.npcs) >= 10, "Некрополь: бульвар, жители-гули")
for to in ("necropolis_hall", "necropolis_cobbs"):
    goto(g, sorted(portal(g, to)["tiles"])[0])
    ok(g.loc.id == to, f"вход: {g.loc.name}")
    g.dialogue.active_node = None
    goto(g, sorted(next(p for p in g.level.portals if p["to"] == "necropolis")["tiles"])[0])
    ok(g.loc.id == "necropolis", "обратно на бульвар")

# Коббс: правда о годе и внук Рида
g.flags["know_baker"] = True
goto(g, sorted(portal(g, "necropolis_cobbs")["tiles"])[0])
talk("cobbs")
say("2121")
say("внук Эймоса")
say("Не заберут")
ok(g.flags.get("cobbs_clear") and g.flags.get("cobbs_job"), "капрал Коббс узнал, какой год, и про голосовой замок")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "necropolis")["tiles"])[0])

# посланница культа и механик Водораздела
talk("cult_envoy")
say("Какой дар")
say("Понятно")
ok(g.flags.get("know_set_deal"), "культ меняет насос на Коббса")
g.dialogue.active_node = None
talk("harry_mech")
say("Где взять")
say("Схожу")
ok(g.flags.get("v12_way"), "Гарри: запасные платы — в Убежище 12")

# подземка -> канализация -> Убежище 12 -> плата
g.dialogue.active_node = None
goto(g, sorted(portal(g, "necropolis_under")["tiles"])[0])
ok(g.loc.id == "necropolis_under", "через люк — в подземку")
for e in g.enemies:
    e.alive = False
goto(g, sorted(portal(g, "vault12")["tiles"])[0])
ok(g.loc.id == "vault12", "через приоткрытую дверь — в Убежище 12")
for e in g.enemies:
    e.alive = False
g.open_terminal("v12_overseer")
g.term_open_entry(0)
g.close_terminal()
ok(g.flags.get("know_v12_truth"), "смотритель: дверь не закрылась по приказу Vault-Tec")
g.inventory.add("плата водоочистки", 1)
goto(g, sorted(portal(g, "necropolis_under")["tiles"])[0])
goto(g, sorted(portal(g, "necropolis")["tiles"])[0])
ok(g.loc.id == "necropolis", "наверх, к Водоразделу")
talk("harry_mech")
say("Вот плата")
say("Пей")
ok(g.flags.get("watershed_fixed"), "насос Водораздела починен")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "necropolis_hall")["tiles"])[0])
talk("set")
say("сделка")
say("уже починен")
say("удовольствием")
ok(g.flags.get("set_refuses"), "Сет отказывается отдать Коббса культу")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
