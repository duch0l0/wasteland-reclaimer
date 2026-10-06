"""
«Посейдон-7» (tools/build_poseidon.py) — без окна: станция Анклава: Холлис и его сделка, паладин Дарнелл в клетке,
директива об «очищении», угон винтокрыла.

    .venv/bin/python tests/test_poseidon.py
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















g.flags["know_poseidon"] = True
g.sync_story()
ok("poseidon7" in g.worldmap.known, "канал «П-7» — станция Анклава на карте")
g.enter_location("poseidon7")
fr(g)
ok(not any(e.hostile for e in g.enemies), "шагоход у ворот молчит, пока нет тревоги")
ok(not g.flags.get("p7_storm_won"), "станция не «зачищена» просто от входа")
goto(g, sorted(portal(g, "poseidon7_base")["tiles"])[0])
ok(g.loc.id == "poseidon7", "без приглашения на станцию не пускают")
talk("enclave_gate")
say("коменданту")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "poseidon7_base")["tiles"])[0])
ok(g.loc.id == "poseidon7_base", "солдат пропускает к коменданту")

# узел связи: директива об «очищении»
g.open_terminal("p7_comm")
g.term_open_entry(1)
g.close_terminal()
ok(g.flags.get("know_enclave_purge"), "директива: модифицированный ВРЭ уничтожит всех «носителей мутаций»")

# Холлис отпускает Дарнелла — и сделка остаётся на столе
g.player.skills["speech"] = 80
talk("hollis_p7")
say("Говори, что предлагаешь")
say("Отпустите Дарнелла")
say("Посмотрим")
ok(g.flags.get("darnell_free"), "Холлис отпускает паладина Дарнелла")
g.dialogue.active_node = None
talk("darnell")
say("Иди")
ok(g.flags.get("darnell_home"), "Дарнелл идёт домой — к Лире и Братству")

# ангар: код винтокрыла — угнать с контейнерами
g.dialogue.active_node = None
goto(g, sorted(portal(g, "poseidon7_hangar")["tiles"])[0])
ok(g.loc.id == "poseidon7_hangar", "лифт в ангар")
g.inventory.add("код винтокрыла", 1)
g.open_terminal("p7_vertibird")
g.term_open_entry(1)
g.close_terminal()
ok(g.flags.get("p7_vertibird_stolen") and g.flags.get("enclave_hostile"), "винтокрыл угнан — Анклав теперь враг")
ok(all(e.hostile for e in g.enemies if e.alive), "тревога: солдаты в ангаре открывают огонь")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
