"""
Журнал: у каждого города есть квест, каждая стадия достижима — флаг, по которому она открывается,
где-то в игре ставится (диалог, терминал или код). Плюс проверка баланса прокачки и торговли.

    .venv/bin/python tests/test_journal.py
"""
import json
import os
import re
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from src.game.quests import STORY_STEPS, QUESTS  # noqa: E402
from src import skills  # noqa: E402
from src.game.trade import speech_mult  # noqa: E402
from src.balance import act_of, scale_loot  # noqa: E402

failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


text = "".join(open(p, encoding="utf-8").read() for p in ("data/dialogues.json", "data/terminals.json"))
code = "".join(open(os.path.join(r, f), encoding="utf-8").read()
               for r, _, fs in os.walk("src") for f in fs if f.endswith(".py"))
set_flags = set(re.findall(r'"set_flag", "flag": "(\w+)"', text)) | set(re.findall(r'f\["(\w+)"\] = True', code)) \
    | set(re.findall(r'flags\["(\w+)"\] = True', code)) | set(re.findall(r'"(\w+)_left"', text))
set_flags |= {"game_ending", "ending_ash", "ending_steel", "ending_hands", "baker_done", "order_found"}
missing = []
for qid, steps in STORY_STEPS:
    ok(qid in QUESTS, f"квест {qid} описан в data/quests.json")
    for stage, cond in steps:
        ok(str(stage) in QUESTS[qid]["stages"], f"{qid}: есть текст стадии {stage}")
        conds = cond if isinstance(cond, list) else [cond]
        if not any(c.startswith("loc:") or c in set_flags or c in code for c in conds):
            missing.append(f"{qid}:{stage} {conds}")
ok(not missing, "все стадии журнала достижимы" + (f": {missing}" if missing else ""))

cities = ["zzyzx", "needles", "hub", "junktown", "necropolis", "aradesh", "boneyard", "vault15", "vault4", "primm",
          "goodsprings", "vault22", "nipton", "searchlight", "vegas", "poseidon", "catalina", "nova", "ares"]
have = {q for q, _ in STORY_STEPS}
for c in cities:
    ok(any(c in q for q in have), f"у города «{c}» есть квест в журнале")

# прокачка: мастером во всём не стать — шаг навыка падает на высоких значениях
v, raises = 20, 0
while v < 75:
    v += skills.step_for(v)
    raises += 1
ok(raises >= 7, f"Красноречие 20→75 — {raises} повышений (из ~12 за игру)")
b, s = speech_mult(20)
b2, s2 = speech_mult(100)
ok(b > 1 > b2 and s < 1 < s2, "Красноречие влияет на цены у торговцев")
ok(act_of("primm") == 3 and act_of("fifteen_school") == 1, "акты локаций определяются")
ok(scale_loot({"крышки": 100, "стимулятор": 3}, 1) == {"крышки": 70, "стимулятор": 1, "бинт": 2},
   "в первом акте меньше крышек и стимуляторов")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
