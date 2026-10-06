"""
Дымовой тест: в каждую локацию игры можно войти, отрисовать её и сохраниться — без падений.
Плюс все три концовки на пульте Марипозы дают эпилог.

    .venv/bin/python tests/test_all_locations.py
"""
import glob
import json
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
from src.location import LOCATION_DEFS  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()
failed = []


def ok(cond, msg):
    if not cond:
        print("FAIL " + msg)
        failed.append(msg)


g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 6
count = 0
for lid, d in LOCATION_DEFS.items():
    if not isinstance(d, dict) or not d.get("map"):
        continue
    try:
        g.enter_location(lid)
        while g.slides:
            g.update(5000)
            g.slides_next()
        for _ in range(3):
            g.update(16)
            g.draw()
        ok(g.loc.id == lid, f"вход: {lid}")
        count += 1
    except Exception as ex:                      # noqa: BLE001
        ok(False, f"{lid}: {type(ex).__name__}: {ex}")
print(f"локаций открыто: {count}")
try:
    g.save_game("1")
except Exception as ex:                          # noqa: BLE001
    ok(False, f"сохранение: {ex}")

# три концовки
for flag, ending in (("order_contact", "ending_ash"), ("fort_bos", "ending_steel"), ("p7_deal_done", "ending_hands")):
    g2 = Game(intro=False)
    g2.flags.update({flag: True, "mariposa_unlocked": True})
    g2.enter_location("mariposa_vats")
    g2.open_terminal("mariposa_core")
    label = {"ending_ash": "Пепел", "ending_steel": "Сталь", "ending_hands": "Чужие руки"}[ending]
    idx = next((k for k, (_, e) in enumerate(g2.term_entries()) if label in e.get("label", "")), None)
    ok(idx is not None, f"на пульте есть концовка «{label}»")
    if idx is not None:
        g2.term_open_entry(idx)
        g2.close_terminal()
        ok(g2.flags.get(ending) and g2.slides and g2.slides["id"] == "epilogue", f"концовка «{label}» и эпилог")
        texts = " ".join(p["text"] for sl in g2.slides["list"] for p in sl["parts"])
        ok(label.split()[0] in texts, f"эпилог «{label}» рассказывает о своей концовке")

# диалоги: ни одна реплика не ведёт в несуществующий узел (иначе игра падает посреди разговора)
_D = json.load(open("data/dialogues.json", encoding="utf-8"))
_bad = [f"{tid}/{nid} → {o['next']}" for tid, t in _D.items() for nid, n in t["nodes"].items()
        for o in n.get("options", []) if o.get("next") and o["next"] not in t["nodes"]]
_bad += [f"{tid}: старт {e['node']}" for tid, t in _D.items()
         for e in (t["start"] if isinstance(t["start"], list) else [{"node": t["start"]}]) if e["node"] not in t["nodes"]]
ok(not _bad, f"все переходы в диалогах ведут в существующие узлы ({_bad[:3]})")

# взлом: пароль помещается в строку дампа, и для его длины есть слова-обманки (иначе взлом — в одно нажатие)
from src.game.terminals import HACK_WORDS, DUMP_COLS  # noqa: E402
_T = json.load(open("data/terminals.json", encoding="utf-8"))["terminals"]
_locks = [(tid, e["lock"]) for tid, t in _T.items() for e in t["entries"] if e.get("lock")]
_bad = [f"{tid}: {lk['password']}" for tid, lk in _locks
        if len(lk["password"]) > DUMP_COLS or len(HACK_WORDS.get(len(lk["password"]), [])) < 8]
ok(not _bad, f"все пароли взламываются по-честному ({_bad[:4]})")

# порталы: точка прибытия не лежит на выходе (иначе героя мотает туда-обратно и в локацию не попасть)
_M = {os.path.basename(f)[:-5]: json.load(open(f, encoding="utf-8")) for f in glob.glob("data/maps/*.json")}
_bad = []
for _a, _m in _M.items():
    for _p in _m.get("portals", []):
        _b, _at = _p["to"], _p.get("at")
        if _b in _M and _at:
            if any(list(_at) in [list(t) for t in q["tiles"]] for q in _M[_b].get("portals", [])) or \
                    list(_at) in [list(t) for t in _M[_b].get("exits", [])]:
                _bad.append(f"{_a}→{_b} {_at}")
ok(not _bad, f"прибытие по порталу не на выходе ({_bad[:3]})")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
