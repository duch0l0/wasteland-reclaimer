"""
Живое население (src/ambient.py), разговоры жителей (src/game/chatter.py), облачка в 2–3 строки.

    .venv/bin/python tests/test_ambient.py
"""
import json
import os
import random
import sys
import tempfile

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["WASTELAND_AMBIENT"] = "1"          # под headless население выключено по умолчанию — здесь включаем
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame  # noqa: E402

pygame.mouse.get_pos = lambda: (-50, -50)
pygame.mouse.get_focused = lambda: True

from src.game import Game, saveload  # noqa: E402
from src import ambient  # noqa: E402
from src.combat import tile_of  # noqa: E402
from src.ui.combat_ui import wrap_text, speech_ms  # noqa: E402
from src.ui.common import _font  # noqa: E402
from src import settings as S  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()
failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


# ---------------- облачка
pygame.init()
font = _font(18)
long = "Лом, химия, патроны — налетай! Рога не трогать, это не для красоты, а для дела. Эймос бы сейчас ворчал..."
lines = wrap_text(font, long, 240)
ok(2 <= len(lines) <= 3 and all(font.size(l)[0] <= 250 for l in lines), f"длинная реплика — {len(lines)} строки, не шире облачка")
ok(wrap_text(font, "Привет", 240) == ["Привет"], "короткая — одна строка")
ok(speech_ms(long) > speech_ms("Гав!") and speech_ms("Гав!") >= 2400, "время показа растёт с длиной фразы")

# ---------------- данные
amb = json.load(open("data/ambient.json", encoding="utf-8"))
chat = json.load(open("data/chatter.json", encoding="utf-8"))
ok(len(amb["jobs"]) >= 14 and len(amb["traits"]) >= 6, f"профессий {len(amb['jobs'])}, характеров {len(amb['traits'])}")
ok(all(len(j["barks"]) >= 5 for j in amb["jobs"].values()), "у каждой профессии есть набор своих реплик")
n_conv = sum(len(v) for v in chat.values())
hints = [c for v in chat.values() for c in v if c.get("hint")]
ok(n_conv >= 150 and len(hints) >= 12, f"разговоров {n_conv}, из них с подсказками {len(hints)}")
ok(all(all(r in ("A", "B", "C") for r, _ in c["lines"]) for v in chat.values() for c in v), "роли реплик — A/B/C")
for sp in amb["critters"].values():
    for sheet in sp["sheets"]:
        ok(os.path.isdir(f"assets/sprites/{sheet}/down"), f"спрайты зверя «{sheet}» нарисованы") if sheet.startswith(("cat", "chick", "brah", "dog_")) else None

# ---------------- расстановка
g = Game(intro=False)
rows = []
for lid in ("ruins", "needles", "hub", "junktown", "goodsprings", "catalina"):
    g.enter_location(lid)
    g.slides = None
    for _ in range(2):
        g.update(16)
    mine = [n for n in g.npcs if ambient.is_ambient(n.npc_id)]
    crit = [n for n in mine if ambient.is_critter(n.npc_id)]
    want = amb["locs"][lid]["people"] + sum(amb["locs"][lid]["critters"].values())
    ok(len(mine) >= want * 0.8, f"{lid}: население {len(mine)}/{want}, зверей {len(crit)}")
    ok(not any(g.level.is_wall(*tile_of(n)) for n in mine), f"{lid}: никто не стоит в стене")
    ok(len({n.name for n in mine if not ambient.is_critter(n.npc_id)}) >= len(mine) // 2, f"{lid}: имена разные")

g.enter_location("ruins")
g.slides = None
for _ in range(2):
    g.update(16)
n1 = [n.npc_id for n in g.npcs if ambient.is_ambient(n.npc_id)]
g.enter_location("ruins")
g.slides = None
n2 = [n.npc_id for n in g.npcs if ambient.is_ambient(n.npc_id)]
ok(n1 == n2, "расстановка одной локации — всегда одна и та же")

# ---------------- разговор по клику
human = next(n for n in g.npcs if ambient.is_ambient(n.npc_id) and not ambient.is_critter(n.npc_id))
g.player.rect.center = (human.rect.centerx - 30, human.rect.centery)
ok(g.talk_to(human, human.npc_id), "с жителем можно заговорить")
labels = [o["label"] for o in g.dialogue.visible_options()]
ok("Что нового в городе?" in labels and "Расскажи о себе." in labels, "есть «Что нового?» и «Расскажи о себе»")
g.dialogue.choose(labels.index("Что нового в городе?"))
ok(g.dialogue.is_active() and human.name in g.dialogue.current_node()["text"], "рассказывает слух от своего имени")
g.dialogue.close()
critter = next(n for n in g.npcs if ambient.is_critter(n.npc_id))
ok(g.talk_to(critter, critter.npc_id) and len(g.dialogue.visible_options()) == 1, "зверя можно погладить")
g.dialogue.close()

# ---------------- подслушанный разговор открывает подсказку
g.enter_location("baker")
g.slides = None
for _ in range(3):
    g.update(16)
conv = next(c for c in chat["@baker"] if c["id"] == "bk_gate")
a, b = [n for n in g.npcs if ambient.is_ambient(n.npc_id) and not ambient.is_critter(n.npc_id)][:2]
a.rect.topleft, b.rect.topleft = b.rect.topleft, b.rect.topleft
g.player.rect.center = (b.rect.centerx + 60, b.rect.centery)
g.chat_cd = 10 ** 9
g._chat_start(conv, a, b, None)
for _ in range(2000):
    g.update(16)
    if g.chat is None:
        break
ok(g.chat is None and g.flags.get("know_back_gate"), "подслушали про калитку — флаг know_back_gate взведён")
ok(any("подслушали" in l.lower() for l in g.log_lines[-8:]), "в журнале событий — что узнали")

# слишком далеко — не услышал
g.flags.pop("know_back_gate", None)
g.flags.pop("chat_heard_bk_gate", None)
g.player.rect.center = (b.rect.centerx + 40 * S.TILE, b.rect.centery)
g._chat_start(conv, a, b, None)
for _ in range(2000):
    g.update(16)
    if g.chat is None:
        break
ok(not g.flags.get("know_back_gate"), "если стоишь далеко — подсказку не получаешь")

# разговор об объекте на карте открывает точку мира
g.enter_location("needles")
g.slides = None
for _ in range(3):
    g.update(16)
rv = next(c for c in chat["@needles"] if c["id"] == "rv_toll")
a, b = [n for n in g.npcs if ambient.is_ambient(n.npc_id) and not ambient.is_critter(n.npc_id)][:2]
b.rect.topleft = a.rect.topleft
g.player.rect.center = (a.rect.centerx + 50, a.rect.centery)
g._chat_start(rv, a, b, None)
for _ in range(2000):
    g.update(16)
    if g.chat is None:
        break
ok("spot_toll" in g.worldmap.known, "слух о заставе — точка появилась на карте мира")

print()
print("ИТОГ: " + ("всё прошло" if not failed else f"не прошло: {len(failed)}"))
sys.exit(1 if failed else 0)
