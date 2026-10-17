"""
Собирает data/folks.json и data/folk_talks.json из tools/folks_*.py и приводит data/ambient.json в соответствие
(число людей в локации = число анкет, если анкеты есть).

Запуск из папки game_project:  .venv/bin/python tools/build_folks.py
"""
import glob
import importlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import folkkit  # noqa: E402

for path in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "folks_*.py"))):
    importlib.import_module(os.path.basename(path)[:-3])

json.dump(folkkit.FOLKS, open("data/folks.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(folkkit.TALKS, open("data/folk_talks.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
amb = json.load(open("data/ambient.json", encoding="utf-8"))
for loc, lst in folkkit.FOLKS.items():
    if loc in amb["locs"]:
        amb["locs"][loc]["people"] = len(lst)
    else:
        print("!! нет локации в ambient.json:", loc)
json.dump(amb, open("data/ambient.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
tot = sum(len(v) for v in folkkit.FOLKS.values())
talks = sum(len(v) for v in folkkit.TALKS.values())
chars = sum(len(json.dumps(p, ensure_ascii=False)) for v in folkkit.FOLKS.values() for p in v)
print(f"жителей с анкетами: {tot} в {len(folkkit.FOLKS)} локациях; личных разговоров: {talks}; {chars // 1000} КБ текста")
missing = [l for l, s in amb["locs"].items() if l not in folkkit.FOLKS]
print("локаций без анкет:", len(missing), missing[:12])
