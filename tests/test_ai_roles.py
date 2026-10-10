"""
Роли врагов (docs/combat_plan.md, src/ai_roles.py): медик лечит, снайпер целится и бьёт выцеленным, пулемётчик
держит сектор и стреляет по движению, командир даёт ауру и цель, без командира отряд бежит, засада
выскакивает (Выживание её замечает), гонец приводит подмогу, щитоносец закрывает ценного, стрелок бежит
за укрытие, фланговый заходит со спины, гренадёр выкуривает из укрытия, удар в спину точнее.

    .venv/bin/python tests/test_ai_roles.py
"""
import os
import random
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
from src.combat import tile_of, rect_pos_for_tile, chebyshev  # noqa: E402
from src.location import make_enemy  # noqa: E402
from src import ai_roles as R  # noqa: E402
from src import settings as S  # noqa: E402

T = S.TILE
saveload.SAVE_DIR = tempfile.mkdtemp()
failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


def arena():
    random.seed(3)
    g = Game(intro=False)
    g.enter_location("spot_saltlake")
    g.slides = None
    g.dialogue.active_node = None
    g.loc.enemies[:] = []
    g.loc.npcs[:] = [] if hasattr(g.loc, "npcs") else []
    p = g.player
    p.max_hp = p.hp = 400
    place(g, p, (20, 20))
    for _ in range(3):
        g.update(16)
    return g


def place(g, ent, tile):
    ent.rect.topleft = rect_pos_for_tile(ent, tile)


def add(g, kind, tile, role=None, **kw):
    e = make_enemy((tile[0] * T, tile[1] * T), kind)
    place(g, e, tile)
    e.role = role
    e.hidden = role == "ambush"
    e.medkits = 3 if role == "medic" else 0
    e.hostile = True
    e.aggro = 2000
    for k, v in kw.items():
        setattr(e, k, v)
    g.loc.enemies.append(e)
    return e


def free_lane(g, tiles):
    for t in tiles:
        g.level.blocked.discard(t)
        g.level.sight.discard(t)


def until_player(g, n=4000):
    """Пропустить ходы врагов до хода героя."""
    c = g.combat
    for _ in range(n):
        g.update(16)
        if not c.active or (c.is_player_turn() and c.player_can_act()):
            return


def pass_turn(g):
    g.combat.end_turn()
    until_player(g)


def logs(g):
    return " | ".join(str(m) for m in g.messages[-40:]) if hasattr(g, "messages") else ""


def log_has(g, part):
    msgs = getattr(g, "messages", None) or getattr(g, "log_lines", None) or []
    return any(part in (m if isinstance(m, str) else str(m)) for m in list(msgs)[-60:])


# ------------------------------------------------------------ медик
g = arena()
free_lane(g, [(x, y) for x in range(15, 35) for y in range(15, 26)])
hurt = add(g, "raider", (27, 20), coward=False)
hurt.hp = 6
med = add(g, "raider", (29, 22), "medic")
g.combat.start(player_first=True)
pass_turn(g)
pass_turn(g)
ok(hurt.hp > 6 and med.medkits < 3, f"медик перевязал раненого: HP 6 → {hurt.hp}, аптечек {med.medkits}")

# ------------------------------------------------------------ снайпер
g = arena()
free_lane(g, [(x, 20) for x in range(15, 35)] + [(x, y) for x in range(15, 35) for y in range(18, 23)])
sn = add(g, "sniper", (30, 20), "sniper")
g.combat.start(player_first=True)
hp0 = g.player.hp
pass_turn(g)
ok(sn.aiming is g.player and g.player.hp == hp0, "снайпер первый ход целится, не стреляет")
pass_turn(g)
ok(sn.aiming is None and getattr(sn, "fired", False), "второй ход — выцеленный выстрел")
g = arena()
free_lane(g, [(x, y) for x in range(15, 35) for y in range(15, 26)])
sn = add(g, "sniper", (30, 20), "sniper")
g.combat.start(player_first=True)
pass_turn(g)
g.level.blocked.add((29, 20))      # герой «ушёл в укрытие»: между ним и снайпером — мешки рядом со снайпером
g.level.blocked.add((21, 20))
hp0 = g.player.hp
c = g.combat
ok(c.cover_between(tile_of(sn), tile_of(g.player)), "герой за укрытием от снайпера")
pass_turn(g)
ok(g.player.hp == hp0 or sn.aiming is not None, "за укрытием выцеленного выстрела нет — прицел сбит")

# ------------------------------------------------------------ пулемётчик
g = arena()
free_lane(g, [(x, y) for x in range(10, 40) for y in range(10, 30)])
gun = add(g, "raider", (28, 20), "gunner")
gun.base_ap = gun.ap = 12
g.combat.start(player_first=True)
pass_turn(g)
ok(gun.overwatch is not None, "пулемётчик после очереди держит сектор")
ok(R.in_sector(g.combat, gun, (21, 20)), "клетка перед героем — в секторе")
g.combat.player_step(1, 0)
for _ in range(60):
    g.update(16)
ok(getattr(gun, "ow_fired", False), "шаг в секторе — очередь по движению")

# ------------------------------------------------------------ командир и мораль
g = arena()
free_lane(g, [(x, y) for x in range(10, 40) for y in range(10, 30)])
cmd = add(g, "raider", (30, 20), "commander")
mates = [add(g, "raider", (30, y)) for y in (17, 23, 25)]
g.combat.start(player_first=True)
pass_turn(g)
ok(g.combat.focus is g.player, "командир указал цель")
ok(any(getattr(m, "inspired", False) for m in mates), "свои рядом с командиром воодушевлены (+10 к попаданию, +1 ОД)")
random.seed(1)
g.combat.hurt(cmd, 999)
ok(any(getattr(m, "broken", False) for m in mates), "командир убит — кто-то из отряда дрогнул")

# ------------------------------------------------------------ засада
g = arena()
free_lane(g, [(x, y) for x in range(10, 40) for y in range(10, 30)])
g.player.skills["survival"] = 20
amb = add(g, "raider", (25, 20), "ambush")
for _ in range(5):
    g.update(16)
ok(amb.hidden and not g.combat.active, "засада не видна издалека")
place(g, g.player, (23, 20))
for _ in range(5):
    g.update(16)
ok(not amb.hidden and g.combat.active and g.combat.order[0] is amb, "подошёл вплотную — выскочил и бьёт первым")
g = arena()
free_lane(g, [(x, y) for x in range(10, 40) for y in range(10, 30)])
g.player.skills["survival"] = 60
amb = add(g, "raider", (25, 20), "ambush")
for _ in range(5):
    g.update(16)
ok(not amb.hidden and getattr(amb, "spotted", False), "Выживание 60 замечает засаду заранее")

# ------------------------------------------------------------ гонец
g = arena()
free_lane(g, [(x, y) for x in range(5, 45) for y in range(5, 35)])
run = add(g, "raider", (26, 20), "runner")
mate = add(g, "raider", (27, 22))
n0 = len(g.enemies)
g.combat.start(player_first=True)
for _ in range(6):
    pass_turn(g)
    if getattr(run, "help_called", False):
        break
ok(getattr(run, "help_called", False) and len(g.enemies) > n0, f"гонец добежал — подмога: {n0} → {len(g.enemies)}")

# ------------------------------------------------------------ щитоносец
g = arena()
free_lane(g, [(x, y) for x in range(10, 40) for y in range(10, 30)])
med = add(g, "raider", (30, 20), "medic")
sh = add(g, "raider", (33, 23), "shield")
g.combat.start(player_first=True)
for _ in range(3):
    pass_turn(g)
ok(chebyshev(tile_of(sh), tile_of(med)) == 1 and chebyshev(tile_of(sh), tile_of(g.player)) < chebyshev(tile_of(med), tile_of(g.player)),
   "щитоносец встал между героем и медиком")

# ------------------------------------------------------------ стрелок из укрытия
g = arena()
free_lane(g, [(x, y) for x in range(10, 40) for y in range(10, 30)])
cv = add(g, "raider", (27, 20), "cover")
g.level.blocked.add((26, 22))       # мешки: клетка (27, 22) прикрыта со стороны героя
c = g.combat
ok(c.cover_between((20, 20), (27, 22)), "клетка за мешками — укрытие")
c.start(player_first=True)
pass_turn(g)
ok(c.cover_between(tile_of(g.player), tile_of(cv)), f"стрелок перебежал за укрытие: {tile_of(cv)}")

# ------------------------------------------------------------ фланговый и удар в спину
g = arena()
free_lane(g, [(x, y) for x in range(10, 40) for y in range(10, 30)])
g.player.facing_left = True          # герой смотрит налево
fl = add(g, "feral", (14, 20), "flanker")
fl.base_ap = fl.ap = 14
g.combat.start(player_first=True)
pass_turn(g)
ok(tile_of(fl)[0] > tile_of(g.player)[0],
   f"фланговый обошёл со спины: {tile_of(fl)} (герой {tile_of(g.player)})")
g.player.facing_left = True          # пока герой не обернулся на удар
ok(R.hit_bonus(g.combat, fl, g.player) >= 15, "удар в спину +15 (получив удар, герой оборачивается)")

# ------------------------------------------------------------ гренадёр
g = arena()
free_lane(g, [(x, y) for x in range(10, 40) for y in range(10, 30)])
gr = add(g, "raider", (24, 20), "grenadier", grenades=2)
g.level.blocked.add((21, 20))        # герой за мешками
g.combat.start(player_first=True)
pass_turn(g)
ok(gr.grenades < 2, "гренадёр выкуривает героя из укрытия гранатой")

# ------------------------------------------------------------ ощущение удара: отлёт, тряска, стоп-кадр
g = arena()
free_lane(g, [(x, y) for x in range(10, 40) for y in range(10, 30)])
e = add(g, "raider", (22, 20))
c = g.combat
c.start(player_first=True)
c.knockback(e, (21, 20))
for _ in range(40):
    g.update(16)
ok(tile_of(e) == (23, 20), f"сильный удар отбрасывает на клетку: {tile_of(e)}")
g.level.blocked.add((24, 20))
hp0 = e.hp
c.knockback(e, (22, 20))
ok(e.hp < hp0 and tile_of(e) == (23, 20), "в стену — лишний урон, с места не сдвинуть")
c.explode((25, 21), "grenade")
ok(c.shake_ms > 0 and c.hitstop_ms > 0, "взрыв трясёт экран и даёт стоп-кадр")
t0 = c.hitstop_ms
g.update(16)
ok(c.hitstop_ms < t0, "стоп-кадр тает")

# ------------------------------------------------------------ роли на картах (data/squads.json)
g = Game(intro=False)
g.enter_location("needles_bridge")
roles = sorted(getattr(e, "role", None) or "-" for e in g.enemies)
ok({"commander", "sniper", "grenadier", "cover"} <= set(roles), f"мост Нидлса: отряд с ролями {roles}")
ok(any(e.name.endswith("-главарь") for e in g.enemies), "главарь подписан в имени")
g.enter_location("drain")
ok(any(getattr(e, "hidden", False) for e in g.enemies), "ливнёвка: крысолюд в засаде")
from src.encounters import Scene, _raiders  # noqa: E402
sc = Scene(random.Random(1), road=True)
_raiders(sc, 12)
ok({"cover", "grenadier", "commander", "medic"} <= {e[3] for e in sc.enemies if len(e) > 3},
   "засада рейдеров на 12 уровне — с укрытием, гранатами, главарём и медиком")
sc = Scene(random.Random(1), road=True)
_raiders(sc, 2)
ok(not any(len(e) > 3 for e in sc.enemies), "на 2 уровне рейдеры — без ролей")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
