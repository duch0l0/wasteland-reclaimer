"""
Полигон: замер одного и того же боя с дальнобойным врагом и без него.

Ставит готового героя (112 HP, навык 110, «Голос пустоши», металлическая броня) на
открытую соляную равнину против отряда Анклава и считает, что вышло: сколько урона
получил герой, за сколько раундов, скольких убил, сколько раз погиб. Бой ведёт бот
из tools/playthrough.py — тот же, что проходит игру.

Так проверяется правка дальности: если враг с range 7 на 12 клетках не достаёт героя,
бой кончается ничем; с range 11-14 — герой получает урон и должен подходить.

  .venv/bin/python tools/balance_arena.py                      — сравнить роль «снайпер» и без
  .venv/bin/python tools/balance_arena.py --foes 3 --dist 11   — отряд из трёх на 11 клетках
  .venv/bin/python tools/balance_arena.py --runs 8             — больше повторов

Печатает строку на конфигурацию: раунды, урон герою, убито врагов, смерти, дальность.
"""
import os
import sys
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

import pygame  # noqa: E402

from src.game import saveload  # noqa: E402
from src.location import make_enemy, apply_role  # noqa: E402
from src.balance import scale_enemy  # noqa: E402
from src.weapons import WEAPONS  # noqa: E402
from src.combat import rect_pos_for_tile, tile_of  # noqa: E402
from playthrough import Bot, Stuck  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()

ARENA = "spot_saltlake"          # открытая карта без стен: чистая проверка дальности
P_LEVEL, P_HP, P_GUNS = 14, 112, 110
P_WEAPON, P_ARMOR = "voice", "металлическая броня"


def level_up(g, p, level):
    """Поднять героя до уровня: иначе броню с req_level не надеть и замер врёт."""
    while p.level_sys.level < level:
        g.gain_xp(p.level_sys.xp_needed - p.level_sys.xp)
        while g.perk_choices:
            g.handle_key(pygame.K_1)


def once(role, foes, dist, seed, act=3):
    b = Bot(seed=seed, sides=False, build="guns")
    g = b.g
    p = g.player
    p.max_hp = p.hp = P_HP
    p.skills["guns"] = P_GUNS
    p.weapon = P_WEAPON
    g.inventory.add(WEAPONS[P_WEAPON]["item"], 1)
    g.inventory.add("патроны", 200)
    g.inventory.add(P_ARMOR, 1)
    level_up(g, p, P_LEVEL)
    p.max_hp = p.hp = P_HP
    g.equip(P_ARMOR)
    if p.weapon != P_WEAPON or not g.inventory.has(WEAPONS[P_WEAPON]["item"]) or p.armor_class <= p.ac:
        raise SystemExit(f"сборка не собралась: оружие {p.weapon!r}, броня {p.equipped('body')!r}, КБ {p.armor_class}")
    g.enter_location(ARENA)
    g.slides = None
    g.dialogue.active_node = None
    g.loc.enemies[:] = []
    x, y = tile_of(p)
    made = []
    for i in range(foes):
        e = make_enemy(rect_pos_for_tile(p, (x + dist + i, y)), "enclave_soldier")
        g.loc.enemies.append(e)
        made.append(e)
    if role:
        apply_role(made[0], role)
    for e in made:
        scale_enemy(e, act)          # в акте III враги крепче: замер без этого врёт
    for e in made:
        e.hostile = True
    g.update(16)
    g.combat.start(player_first=True)
    if not g.combat.active:
        raise SystemExit("бой не начался — проверьте клетки и линию огня")
    hp0 = p.hp
    try:
        b.fight()
        dead = False
    except Stuck:
        dead = True
    return dead, max(0, int(hp0 - max(0, p.hp))), int(g.combat.round), \
        sum(1 for e in made if not e.alive), int(getattr(made[0], "range", 0)), int(made[0].skill)


def main():
    args = sys.argv[1:]
    opts = {"--foes": "1", "--dist": "12", "--runs": "5", "--act": "3"}
    for k in opts:
        if k in args:
            i = args.index(k)
            opts[k] = args[i + 1]
            del args[i:i + 2]
    foes, dist, runs, act = int(opts["--foes"]), int(opts["--dist"]), int(opts["--runs"]), int(opts["--act"])
    print(f"полигон: {ARENA}, врагов {foes}, дистанция {dist}, повторов {runs}, герой {P_LEVEL} ур., акт {act}")
    print(f"{'конфигурация':18s} {'раундов':>8s} {'урон герою':>11s} {'убито':>7s} {'смертей':>8s} {'дальность':>10s}")
    for label, role in (("без роли", None), ("снайпер", "sniper")):
        rows = [once(role, foes, dist, seed, act) for seed in range(1, runs + 1)]
        n = len(rows)
        dead, dmg, rounds, killed = (sum(r[i] for r in rows) for i in range(4))
        print(f"{label:18s} {rounds / n:8.1f} {dmg / n:11.1f} {killed / n:5.1f}/{foes} "
              f"{int(dead):4d}/{n} {rows[0][4]:5d} навык {rows[0][5]}")


if __name__ == "__main__":
    main()
