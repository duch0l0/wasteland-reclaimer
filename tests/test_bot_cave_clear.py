"""
Страж бота: пещера Гудспрингса зачищается до конца, а не «почти».

Раньше clear() молча пропускал врага, к которому не смог подойти (засада выдаёт себя только
с двух клеток, а бот вставал на третьей), и флаг gs_cave_cleared не выставлялся.

    .venv/bin/python tests/test_bot_cave_clear.py
"""
import os
import sys
import importlib.util

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))     # playthrough импортирует bot_sides как соседний модуль
os.chdir(ROOT)

_spec = importlib.util.spec_from_file_location("playthrough", os.path.join(ROOT, "tools", "playthrough.py"))
PT = importlib.util.module_from_spec(_spec)
sys.modules["playthrough"] = PT
_spec.loader.exec_module(PT)

failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


def hero(weapon, weapon_item, skill):
    """Герой уровня 14 в боевой броне — как в отчёте бота на подходе к Гудспрингсу."""
    b = PT.Bot(seed=7, sides=True)
    g = b.g
    b.go("goodsprings_cave")
    p = g.player
    p.level_sys.level = 14
    p.max_hp = 81
    p.hp = 81
    p.skills[skill] = 100
    g.inventory.add(weapon_item, 1)
    p.weapon = weapon
    g.inventory.add("патроны", 120)
    for name in ("боевая броня", "шлем боевой брони"):
        g.inventory.add(name, 1)
    p.equipment["body"] = "боевая броня"
    p.equipment["head"] = "шлем боевой брони"
    g.inventory.add("стимулятор", 6)
    g.inventory.add("бинт", 4)
    return b, g


for tag, args in (("винтовка", ("voice", "винтовка «Голос пустоши»", "guns")),
                  ("ближний бой", ("power_fist", "силовой кулак", "melee"))):
    b, g = hero(*args)
    print(f"--- {tag}")
    ok(len(g.enemies) == 3, "в пещере трое ящеров")
    b.clear(max_rounds=25)
    alive = [e for e in g.enemies if e.alive]
    ok(not alive, f"все убиты (живы: {[e.type_id for e in alive]})")
    ok(bool(g.flags.get("gs_cave_cleared")), "флаг gs_cave_cleared выставлен")
    ok(g.stage("sq_spring") == 50, "«Двор Санни» на этапе 50")
    ok(not [x for x in b.problems if "не смог зачистить" in x], "в problems нет пропущенных врагов")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
