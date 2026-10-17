"""
Собирает data/folks.json и data/folk_talks.json из tools/folks_*.py и приводит data/ambient.json в соответствие
(число людей в локации = число анкет, если анкеты есть).

Запуск из папки game_project:  .venv/bin/python tools/build_folks.py
"""
import glob
import re
import importlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import folkkit  # noqa: E402

for path in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "folks_*.py"))):
    importlib.import_module(os.path.basename(path)[:-3])

def _first_sentence(t, limit=120):
    t = t.strip()
    m = re.match(r"(.+?[.!?…])(\s|$)", t)
    out = m.group(1) if m else t
    if len(out) > limit:
        out = out[:limit].rsplit(" ", 1)[0].rstrip(",;:—- ") + "…"
    return out


def unique_barks():
    """Реплики над головой не должны повторяться между жителями: общие («Тише», «Сдачи нет») заменяем
    собственными фразами из биографии, мечты, новостей и взглядов самого персонажа."""
    seen = set()
    for lst in folkkit.FOLKS.values():
        for p in lst:
            keep = []
            for b in p["barks"]:
                if b not in seen:
                    seen.add(b)
                    keep.append(b)
            own = []
            for n in p["news"]:
                own.append(n if isinstance(n, str) else n[0])
            pool = [p["world"]] + own + list(p["bio"]) + [p["dream"]]
            for t in pool:
                if len(keep) >= 3:
                    break
                f = _first_sentence(t)
                if f not in seen and len(f) > 12:
                    seen.add(f)
                    keep.append(f)
            p["barks"] = keep


unique_barks()

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
