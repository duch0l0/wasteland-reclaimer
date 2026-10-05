"""
Зайзикс (tools/build_zzyzx.py) — без окна: бульвар, купальни, «Замок», цистерна и правда о воде.

  - по трассе на восток — двор старой школы, через дверь — здание; мисс Лейн и терминал директора;
  - люк в подвал деда закрыт, пока не прочитана записка в его терминале; в подвале — сундук и терминал;
  - люк в подвал салуна — после разговора с Мо; внизу Тесс.

    .venv/bin/python tests/test_fifteen.py
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


g.reveal_location("zzyzx")
g.enter_location("zzyzx")
fr(g)
ok(g.loc.id == "zzyzx" and len(g.npcs) >= 7, "Зайзикс: бульвар, жители и паломники")
ok(len(g.level.blocked) > 0 and any(p["to"] == "zzyzx_bath" for p in g.level.portals), "озеро непроходимо, есть вход в купальни")
goto(g, sorted(portal(g, "zzyzx_bath")["tiles"])[0])
ok(g.loc.id == "zzyzx_bath", "через дверь — в купальни")
talk("nurse_ava")
say("Давно")
say("в воде")
say("Посмотрю")
ok(g.flags.get("ava_asked") and g.flags.get("know_no_kids"), "сестра Ава: в Зайзиксе давно не рождаются дети")
hatch = portal(g, "zzyzx_cistern")
g.dialogue.active_node = None
goto(g, sorted(hatch["tiles"])[0])
ok(g.loc.id == "zzyzx_bath", "люк насосной заперт без ключа")
goto(g, sorted(portal(g, "zzyzx")["tiles"])[0])
talk("gus")
say("Что под купальнями")
say("Сестра Ава просила")
say("Спасибо")
ok(g.inventory.has("ключ от насосной"), "Гас отдал ключ от насосной")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "zzyzx_bath")["tiles"])[0])
goto(g, (34, 13))
goto(g, sorted(portal(g, "zzyzx_cistern")["tiles"])[0])
ok(g.loc.id == "zzyzx_cistern", "по ключу — вниз, в цистерну")
for e in g.enemies:
    e.alive = False
g.open_terminal("zz_cistern")
g.term_open_entry(0)
g.close_terminal()
ok(g.flags.get("know_clean_slate"), "терминал: фильтр Vault-Tec «Чистый лист» делает людей бесплодными")
g.enter_location("zzyzx")
fr(g)
talk("springer")
ok(any("правду" in g.dialogue.option_label(o) for o in g.dialogue.visible_options()), "Спрингер признаётся, если знаешь правду")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "zzyzx_hotel")["tiles"])[0])
ok(g.loc.id == "zzyzx_hotel" and any(n.npc_id == "guest_widow" for n in g.npcs), "«Замок» Спрингера: холл, номера, вдова")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
