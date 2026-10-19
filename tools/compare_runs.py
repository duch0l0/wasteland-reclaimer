"""
Сравнить два отчёта playthrough.py --stats: было / стало. Печатает разницу по боям.

  .venv/bin/python tools/compare_runs.py old.json new.json

Перед правками баланса снимите старый отчёт, после — новый, и смотрите, что изменилось:
«на волоске», урон за бой, доля боёв без урона, средняя длина боя, лечение к финалу.
"""
import json
import sys

HELP = ("Сравнить два отчёта playthrough.py --stats: было / стало.\n"
        "  .venv/bin/python tools/compare_runs.py old.json new.json")


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    st = dict(d.get("stats") or {})
    fights = max(1, st.get("fights", 0))
    st["rounds_per_fight"] = st.get("rounds", 0) / fights
    st["no_damage_pct"] = 100 * st.get("fights_no_damage", 0) / fights
    st["damage_taken_per_fight"] = st.get("damage_taken", 0) / fights
    st["quests_done"] = (d.get("quests") or {}).get("done", 0)
    st["quests_total"] = (d.get("quests") or {}).get("total", 0)
    return d, st


ROWS = [
    ("бои", "fights", 0),
    ("«на волоске»", "close_calls", 0),
    ("смертей", "deaths", 0),
    ("лечилок съедено", "heals_used", 0),
    ("урон получен", "damage_taken", 0),
    ("урон на бой", "damage_taken_per_fight", 1),
    ("урон нанесён", "damage_dealt", 0),
    ("раундов на бой", "rounds_per_fight", 2),
    ("боёв без урона, %", "no_damage_pct", 0),
    ("долгих боёв (14+)", "fights_long", 0),
    ("квестов пройдено", "quests_done", 0),
]


def main():
    if len(sys.argv) < 3:
        print(HELP)
        sys.exit(2)
    a_doc, a = load(sys.argv[1])
    b_doc, b = load(sys.argv[2])
    print(f"было:  {sys.argv[1]}  ({a_doc.get('build')}, сид {a_doc.get('seed')}, "
          f"{'с побочками' if a_doc.get('sides') else 'только сюжет'})")
    print(f"стало: {sys.argv[2]}  ({b_doc.get('build')}, сид {b_doc.get('seed')}, "
          f"{'с побочками' if b_doc.get('sides') else 'только сюжет'})")
    print()
    print(f"{'показатель':22s} {'было':>10s} {'стало':>10s} {'разница':>10s}")
    for label, key, digits in ROWS:
        av, bv = a.get(key, 0), b.get(key, 0)
        delta = bv - av
        sign = "+" if delta > 0 else ""
        print(f"{label:22s} {av:10.{digits}f} {bv:10.{digits}f} {sign + format(delta, f'.{digits}f'):>10s}")
    print()
    edges = ((0, 10), (10, 25), (25, 50), (50, 75), (75, 101))
    names = ("0-9%", "10-24%", "25-49%", "50-74%", "75-100%")
    print("минимум HP за бой (сколько боёв в диапазоне):")
    for doc, label in ((a_doc, "было"), (b_doc, "стало")):
        vals = (doc.get("stats") or {}).get("hp_min") or []
        cells = [sum(1 for v in vals if lo <= v < hi) for lo, hi in edges]
        print(f"  {label:6s} " + "  ".join(f"{n}: {c}" for n, c in zip(names, cells)))
    print()
    for doc, name in ((a_doc, "было"), (b_doc, "стало")):
        end = doc.get("ending") or "нет"
        probs = len(doc.get("problems") or [])
        print(f"{name}: концовка {end}, проблем {probs}, критик замечаний {len(doc.get('critic') or [])}")


if __name__ == "__main__":
    main()
