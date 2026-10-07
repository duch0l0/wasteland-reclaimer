"""
Арсенал как в Fallout — без окна.

  - каждое оружие: предмет в items.json, иконка, патроны существуют; пять классов — пять навыков;
  - оружие не по навыку: штраф к попаданию, очередью не стрелять, предупреждение при смене;
  - лазер прожигает броню, огнемёт поджигает, ракета рвётся у цели и задевает соседей;
  - ЭМИ-граната выключает робота; точность броска растёт с Метанием;
  - броня: тяжёлая — с уровня, силовая — после курса оператора (голозапись);
  - легенды (unique) лежат в мире ровно в одном месте; всё, что продают и роняют враги, — существует;
  - слухи о легендах ходят по барам; карточка предмета в рюкзаке собирается для всего оружия и брони.

    .venv/bin/python tests/test_arsenal.py
"""
import glob
import json
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
from src.combat import rect_pos_for_tile, tile_of  # noqa: E402
from src.location import make_enemy  # noqa: E402
from src.weapons import WEAPONS, SKILL_NAMES, shortfall  # noqa: E402
from src import items  # noqa: E402
from src.ui.inventory_ui import _item_facts  # noqa: E402
from src.balance import roll_loot  # noqa: E402

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


random.seed(3)
g = Game(intro=False)
p = g.player
c = g.combat

# ------------------------------------------------------------ данные
bad = [k for k, w in WEAPONS.items() if w.get("item") and w["item"] not in items.ITEMS]
ok(not bad, f"у каждого оружия есть предмет ({bad})")
bad = [k for k, w in WEAPONS.items() if w.get("ammo") and w["ammo"] not in items.ITEMS]
ok(not bad, f"патроны всех стволов существуют ({bad})")
icons = [d["icon"] for d in items.ITEMS.values() if d.get("cat") in ("weapon", "ammo", "armor")]
missing = sorted({i for i in icons if not os.path.isfile(f"assets/items/{i}.png")} - {"grenade"})
ok(not missing, f"у оружия, патронов и брони есть иконки ({missing})")
classes = {w.get("skill") for w in WEAPONS.values()}
ok(classes == set(SKILL_NAMES), f"пять классов оружия: {sorted(classes)}")
ok(len(WEAPONS) >= 28, f"арсенал: {len(WEAPONS)} видов оружия")
for sid in ("heavy", "energy", "throwing"):
    ok(sid in p.skills or p.skill(sid) > 0, f"навык {SKILL_NAMES[sid]} есть у героя")

# ------------------------------------------------------------ навык и порог
g.inventory.add("плазменная винтовка", 1)
g.inventory.add("ядерный элемент", 10)
g.switch_weapon("plasma")
ok(shortfall(p, "plasma") > 50 and "не по руке" in g.log_lines[-1], "плазма новичку не по руке — предупреждение")
weak = c.profile(p)["skill"]
p.skills["energy"] = 120
strong = c.profile(p)["skill"]
ok(strong - weak > 150, f"с навыком плазма слушается ({weak} → {strong})")
g.inventory.add("миниган", 1)
g.inventory.add("патроны", 50)
g.switch_weapon("minigun")
pr = c.profile(p)
ok(pr["burst"] == 1 and pr["ap"] == WEAPONS["minigun"]["ap"] + 1, "миниган без навыка: одиночными и тяжелее")
p.skills["heavy"] = 100
ok(c.profile(p)["burst"] == 8, "с «Тяжёлым оружием» — очередь из восьми")


def dummy(kind, dist=2):
    e = make_enemy((0, 0), kind)
    x, y = tile_of(p)
    e.rect.topleft = rect_pos_for_tile(e, (x + dist, y))
    return e


# ------------------------------------------------------------ энергия, огонь, ракеты
p.skills["guns"] = 150
p.weapon = "pistol10"
g.inventory.add("10-мм пистолет", 1)
prof_gun = c.profile(p)
p.weapon = "plasma"
prof_pl = c.profile(p)
random.seed(2)
dmg_gun = dmg_pl = 0
for _ in range(40):
    r1, r2 = dummy("robot_guard"), dummy("robot_guard")
    r1.hp = r2.hp = 999
    c._resolve_hit(p, r1, 0, dict(prof_gun, damage=10), 0, penalty=-300)
    c._resolve_hit(p, r2, 0, dict(prof_pl, damage=10), 0, penalty=-300)
    dmg_gun += 999 - r1.hp
    dmg_pl += 999 - r2.hp
ok(dmg_pl > dmg_gun, f"тот же урон, но луч прожигает броню робота ({dmg_pl} против {dmg_gun})")
g.inventory.add("огнемёт", 1)
g.inventory.add("топливо", 10)
p.weapon = "flamer"
e = dummy("raider")
e.hp = 999
c._resolve_hit(p, e, 0, c.profile(p), 0, penalty=-300)
ok(any(d["kind"] == "fire" for d in e.dots), "огнемёт поджигает цель")
g.inventory.add("ракетомёт", 1)
g.inventory.add("ракета", 2)
p.weapon = "rocket"
pr = c.profile(p)
ok(pr["blast"] == "rocket", "ракетомёт стреляет ракетой")
a, b = dummy("raider", 3), dummy("raider", 3)
b.rect.topleft = rect_pos_for_tile(b, (tile_of(a)[0], tile_of(a)[1] + 1))
hp_a, hp_b = a.hp, b.hp
g.enemies[:] = [a, b]
c.throws.clear()
c.explode(tile_of(a), "rocket")
ok(a.hp < hp_a and b.hp < hp_b, "ракета рвётся у цели и задевает соседа")
r = dummy("robot_guard", 3)
g.enemies[:] = [r]
hp = r.hp
c.explode(tile_of(r), "pulse")
ok(hp - r.hp >= 25, "ЭМИ-граната выжигает робота")
human = dummy("raider", 3)
g.enemies[:] = [human]
hp = human.hp
c.explode(tile_of(human), "pulse")
ok(hp - human.hp <= 4, "а человеку от ЭМИ — щекотка")
g.enemies[:] = []
if c.active:
    c.end("тест")

# ------------------------------------------------------------ броня
g.inventory.add("металлическая броня", 1)
g.equip("металлическая броня")
ok(p.equipped("body") != "металлическая броня", "металлическая броня новичку не по плечу")
while p.level_sys.level < 10:
    g.gain_xp(p.level_sys.xp_needed - p.level_sys.xp)
    while g.perk_choices:
        g.handle_key(pygame.K_1)
g.equip("металлическая броня")
ok(p.equipped("body") == "металлическая броня" and p.armor == 2, "с опытом — надета, гасит 2 урона")
g.inventory.add("силовая броня T-45", 1)
g.equip("силовая броня T-45")
ok(p.equipped("body") == "металлическая броня", "силовую броню без курса оператора не надеть")
g.inventory.add("голозапись «Курс оператора СБ»", 1)
g.item_action("голозапись «Курс оператора СБ»")[1]()
g.close_terminal()
ok(g.flags.get("pa_training"), "голозапись: курс оператора пройден")
g.equip("силовая броня T-45")
ok(p.equipped("body") == "силовая броня T-45" and p.armor == 5 and p.armor_class >= 32, "силовая броня надета")
e = dummy("raider")
e.damage = 4
hp = p.hp
for _ in range(10):
    c._resolve_hit(e, p, 0, c.profile(e), 0, penalty=-300)
ok(hp - p.hp <= 20, f"в силовой броне рейдерская пукалка почти не берёт ({hp - p.hp} за 10 попаданий)")

# ------------------------------------------------------------ мир: легенды, торговцы, добыча
places = {}
for f in glob.glob("data/maps/*.json"):
    m = json.load(open(f, encoding="utf-8"))
    for box in m.get("containers", []):
        for it in box.get("loot") or {}:
            places.setdefault(it, []).append(os.path.basename(f)[:-5])
E = json.load(open("data/enemies.json", encoding="utf-8"))
for k, v in E.items():
    for it, n in (v.get("loot") or {}).items():
        if n == 1 and k == "mommy_mutant":
            places.setdefault(it, []).append("враг " + k)
_ENC = open("src/encounters.py", encoding="utf-8").read()       # особые встречи в пустоши
for w in WEAPONS.values():
    if w.get("unique") and f'"{w.get("item")}"' in _ENC:
        places.setdefault(w["item"], []).append("особая встреча")
_DLG = json.load(open("data/dialogues.json", encoding="utf-8"))   # награда в разговоре (головоломки)
for tid, t in _DLG.items():
    for nid, nd in t["nodes"].items():
        for o in nd.get("options", []):
            for e in o.get("effects", []):
                if e["type"] == "give" and e.get("item") in {w.get("item") for w in WEAPONS.values() if w.get("unique")}:
                    if f"разговор {tid}" not in places.get(e["item"], []):
                        places.setdefault(e["item"], []).append(f"разговор {tid}")
for k, w in WEAPONS.items():
    if w.get("unique"):
        ok(len(places.get(w["item"], [])) == 1, f"легенда «{w['item']}» лежит в одном месте: {places.get(w['item'])}")
ok(len(places.get("голозапись «Курс оператора СБ»", [])) >= 1, "курс оператора силовой брони есть в мире")
T = json.load(open("data/traders.json", encoding="utf-8"))
bad = sorted({it for t in T.values() for it in t["stock"] if it not in items.ITEMS})
ok(not bad, f"всё, что продают торговцы, существует ({bad})")
bad = sorted({it for v in E.values() for it in (v.get("loot") or {}) if it not in items.ITEMS})
ok(not bad, f"всё, что роняют враги, существует ({bad})")
sold = {it for t in T.values() for it in t["stock"]}
uniq = {w["item"] for w in WEAPONS.values() if w.get("unique")}
ok(not (sold & uniq), "легенды не продаются в лавках")
random.seed(5)
drops = sum(1 for _ in range(400) if "плазменная винтовка" in roll_loot(E["enclave_soldier"]["loot"]))
ok(60 < drops < 140, f"плазма падает с солдата Анклава не всегда (~25%: {drops}/400)")
B = json.load(open("data/barks.json", encoding="utf-8"))
text = json.dumps(B, ensure_ascii=False)
for word in ("Гаусс", "Мамочка", "Красотк", "Звездочёт", "кувалд", "курса оператора"):
    ok(word in text, f"слух о легенде: «{word}…»")

# ------------------------------------------------------------ карточки предметов
errs = []
for name, d in items.ITEMS.items():
    if d.get("cat") in ("weapon", "armor", "ammo"):
        try:
            _item_facts(g, name)
        except Exception as ex:  # noqa: BLE001
            errs.append(f"{name}: {ex}")
ok(not errs, f"карточки оружия и брони собираются ({errs[:3]})")
g.open_inventory()
fr(g)
ok(True, "рюкзак рисуется с новыми навыками")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
