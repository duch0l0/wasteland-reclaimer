"""
Прокачка, баланс, новое оружие и случайные встречи — без окна.

  - опыт: 100 / 300 / 600… на уровень; за слабых врагов опыта мало;
  - уровень: каждый раз +10 к навыку на выбор, перк — только на чётных;
  - навыки работают: Красноречие открывает [Красноречие], Медицина лечит сильнее, Наука — попытки взлома;
  - дробовик: вплотную точнее и больнее, вдали урон падает; автомат — очередь из трёх, три патрона;
  - песчаный голем на 1-м уровне почти неуязвим (броня), подсказка предупреждает;
  - все сцены встреч собираются; следопыт обходит опасную встречу.

    .venv/bin/python tests/test_progression.py
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
from src.game.mouse import threat_name  # noqa: E402
from src.combat import rect_pos_for_tile, tile_of  # noqa: E402
from src.location import make_enemy  # noqa: E402
from src import skills, encounters, settings as S  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()
failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


def fr(g, n=2):
    for _ in range(n):
        g.update(16)
        g.draw()


random.seed(7)
g = Game(intro=False)
p = g.player

# ------------------------------------------------------------ опыт и уровни
ok([S.XP_TO_LEVEL(n) for n in (1, 2, 3, 4)] == [100, 225, 350, 475], "кривая опыта 100/225/350/475")
ok(skills.xp_for_kill(25, 1, 5) == 5 and skills.xp_for_kill(25, 5, 5) == 25 and skills.xp_for_kill(100, 8, 2) > 100,
   "за слабого — мало опыта, за сильного — с надбавкой")
g.gain_xp(100)
ok(p.level_sys.level == 2 and p.pending_skills == 1 and p.pending_perks == 1, "2-й уровень: навык и перк")
fr(g)
ok(g.perk_choices and g.perk_choices[0].get("kind") == "skill" and len(g.perk_choices) == 9, "сначала — выбор навыка (9)")
guns = p.skill("guns")
idx = next(i for i, c in enumerate(g.perk_choices) if c["id"] == "guns")
g.handle_key(pygame.K_1 + idx)
fr(g)
ok(p.skill("guns") == guns + 10, "Стрельба +10")
ok(g.perk_choices and g.perk_choices[0].get("kind") != "skill", "потом — перк")
ok(not any(c["id"] in ("armor_piercer", "sniper", "lifegiver") for c in g.perk_choices),
   "сильные перки на 2-м уровне не предлагаются")
g.handle_key(pygame.K_1)
fr(g)
p.perks.clear()   # перк выпадает случайно — дальше проверяем навыки без его влияния
g.gain_xp(300)
fr(g)
ok(p.level_sys.level == 3 and p.pending_perks == 0 and g.perk_choices and g.perk_choices[0]["kind"] == "skill",
   "3-й уровень: только навык, перка нет")
g.handle_key(pygame.K_1)
fr(g)

# ------------------------------------------------------------ навыки в деле
ok(not g.check_condition({"perk": "silver_tongue"}), "без Красноречия реплики [Красноречие] скрыты")
p.skills["speech"] = 60
ok(g.check_condition({"perk": "silver_tongue"}), "Красноречие 60 открывает их")
p.skills["science"] = 55
ok(g.hack_tries() == 6, "Наука 55 — 6 попыток взлома")
p.hp = 5
p.skills["medicine"] = 65
g.inventory.add("бинт", 1)
g.use_item("бинт")
ok(p.hp == 5 + 18, f"Медицина 65: бинт лечит 18 вместо 12 (стало {p.hp})")

# ------------------------------------------------------------ оружие
g.inventory.add("дробовик", 1)
g.inventory.add("дробь", 5)
g.inventory.add("автомат", 1)
g.inventory.add("патроны", 9)
p.weapon = "shotgun"
c = g.combat
prof = c.profile(p)
ok(prof["range"] == 5 and prof["close_bonus"] and prof["falloff"], "дробовик: короткая дальность, разлёт")


def dummy(dist):
    e = make_enemy((0, 0), "raider")
    x, y = tile_of(p)
    e.rect.topleft = rect_pos_for_tile(e, (x + dist, y))
    return e


near, far = dummy(1), dummy(5)
ok(c.hit_chance(p, near) - c.hit_chance(p, far) > 30, "вплотную попасть легче, чем издали")
random.seed(1)
dmg_near = dmg_far = 0
for _ in range(60):
    e1, e2 = dummy(1), dummy(4)
    e1.hp = e2.hp = 999
    c._resolve_hit(p, e1, 0, prof, 0, penalty=-200)
    c._resolve_hit(p, e2, 0, prof, 0, penalty=-200)
    dmg_near += 999 - e1.hp
    dmg_far += 999 - e2.hp
ok(dmg_near > dmg_far * 1.6, f"вдали дробь слабее ({dmg_near} против {dmg_far})")
p.weapon = "assault"
p.skills["guns"] = 40
prof = c.profile(p)
ok(prof["burst"] == 1 and prof["skill"] < 40, "автомат не по навыку: одиночными и с штрафом к попаданию")
p.skills["guns"] = 90
prof = c.profile(p)
ok(prof["burst"] == 3 and not prof["aim"], "автомат: очередь из трёх, без прицела")
e = dummy(3)
e.hp = 999
c.active = True
p.ap = 10
before = g.inventory.count("патроны")
c.attack(p, e, part_idx=1)
ok(before - g.inventory.count("патроны") == 3, "очередь съела три патрона")
c.active = False

# ------------------------------------------------------------ баланс: голем
golem = make_enemy((0, 0), "sand_golem")
ok(golem.level == 8 and golem.armor >= 8, "голем: 8-й уровень, броня 8")
p.weapon = "melee"
ok(p.damage + 2 <= golem.armor, f"лом 1-го уровня ({p.damage}±2) голема не пробивает без крита")
ok("смертельно опасен" in threat_name(golem, p), "подсказка: смертельно опасен")

# ------------------------------------------------------------ встречи
for enc in encounters.ENCOUNTERS:
    for seed in range(3):
        s = encounters.Scene(random.Random(seed), road=enc[1] in encounters.ROADS)
        enc[4](s, 5, False) if enc[1] == "cult" else enc[4](s, 5)
        reach = s._reach()
        assert all((x, y) in reach for _, x, y in s.enemies + s.npcs), enc[1]
ok(True, f"все {len(encounters.ENCOUNTERS)} сцен встреч собираются, все до кого-то можно дойти")
hits = sum(1 for i in range(200) if encounters.make_encounter({}, 1, 150, rnd=random.Random(i))[0] is None)
ok(hits > 0, f"следопыт обходит опасные встречи ({hits} из 200)")
loc, text = encounters.make_encounter({}, 3, 20, rnd=random.Random(5))
g.loc = loc
g.apply_view()
g.place_player(g.level.player_spawn)
g.mode = "local"
fr(g, 3)
ok(g.loc.is_encounter and g.level.exits, f"встреча: {text[:40]}…")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
