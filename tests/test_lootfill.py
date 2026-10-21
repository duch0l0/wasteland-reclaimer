"""
Пустые ящики (docs/review_plan.md, п. 2.6): при загрузке карты пустой контейнер получает
1-2 единицы хлама, пустых на карте — не больше 8%, вскрытый ящик после сохранения/загрузки
не наполняется заново.

  - план наполнения детерминированный (crc32 от карты и индекса), повторный вход — то же самое;
  - кладём только resource-хлам из data/items.json (ни крышек, ни патронов, ни лечения, ни оружия);
  - сюжетные пустышки (requires / on_put / owner) не трогаем;
  - обыскал → сохранил → загрузил → ящик пуст, лут нетронутых ящиков тот же;
  - у пустого ящика вскрытый проп, если пара есть в каталоге (crate → crate_open).

    .venv/bin/python tests/test_lootfill.py
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

from src import items, lootfill  # noqa: E402
from src.game import Game, saveload  # noqa: E402

failed = []
JUNK_OK = {n for n, d in items.ITEMS.items() if d.get("cat") == "resource"}


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


# ------------------------------------------------------------ данные карт: план и квота
maps = {os.path.basename(f)[:-5]: json.load(open(f, encoding="utf-8"))
        for f in sorted(glob.glob("data/maps/*.json"))}
total = empty_before = empty_after = 0
over = []
bad_item = []
for mid, d in maps.items():
    cs = d.get("containers", [])
    if not cs:
        continue
    plan = lootfill.plan(mid, cs, d.get("style"))
    again = lootfill.plan(mid, cs, d.get("style"))
    if plan != again:
        bad_item.append(f"{mid}: план не воспроизводится")
    after = [(c.get("loot") or plan.get(i, {})) for i, c in enumerate(cs)]
    e0, e1 = sum(1 for c in cs if not c.get("loot")), sum(1 for l in after if not l)
    total, empty_before, empty_after = total + len(cs), empty_before + e0, empty_after + e1
    if e1 > int(len(cs) * lootfill.EMPTY_SHARE):      # выше 8% — только за счёт «особых»
        if any(not l and not lootfill.is_special(c) for c, l in zip(cs, after)):
            over.append(mid)
    for i, loot in plan.items():
        if lootfill.is_special(cs[i]):
            bad_item.append(f"{mid}#{i}: наполнен сюжетный ({cs[i].get('name')})")
        for name, cnt in loot.items():
            if name not in JUNK_OK:
                bad_item.append(f"{mid}#{i}: {name} — не хлам")
            if not 1 <= cnt <= 2:
                bad_item.append(f"{mid}#{i}: {name} ×{cnt}")

print(f"контейнеров {total}: пусто было {empty_before} ({empty_before / total:.1%}), "
      f"стало {empty_after} ({empty_after / total:.1%})")
ok(empty_after <= total * lootfill.EMPTY_SHARE, "пустых по всем картам ≤ 8%")
ok(not over, f"на каждой карте пустых ≤ 8% ({over[:3]})")
ok(not bad_item, f"кладём только хлам 1-2 шт., сюжетные не тронуты ({bad_item[:3]})")

# вид: сколько пустых получит вскрытый проп, а сколько останется со старой картинкой
# (рисуется по имени пропа d["objs"][c["obj"]]["t"], не по русскому name контейнера)
open_props = []
for mid, d in maps.items():
    props = d.get("props", [])
    for c in d.get("containers", []):
        if not c.get("loot") and not lootfill.is_special(c) and c.get("prop") is not None:
            if c["prop"] < len(props):
                open_props.append(props[c["prop"]][0])
pair = [1 for n in open_props if lootfill.has_open_variant(n)]
print(f"пустых не-сюжетных {len(open_props)}: со вскрытым пропом {len(pair)}, "
      f"без пары {len(open_props) - len(pair)} (пропы: {sorted(set(open_props))[:6]})")

# ------------------------------------------------------------ вид пустого
ok(lootfill.open_variant("crate") == "crate_open", "вскрытый проп: crate → crate_open")
ok(lootfill.open_variant("locker_2") == "locker_open_a", "вскрытый проп: locker_2 → locker_open_a")
ok(lootfill.open_variant("crate_open") is None, "уже вскрытый проп не подменяется дважды")
ok(not lootfill.looks_empty({"loot": {}, "requires": {"flag": "never"}}), "запертый ящик не «пустой» с виду")

# ------------------------------------------------------------ обыскал → сохранил → загрузил
saveload.SAVE_DIR = tempfile.mkdtemp()
g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 5
g.enter_location("ruins")
while g.slides:
    g.update(5000)
    g.slides_next()
data = maps["town"]
base = [c for c in g.loc.level.containers if not c.get("corpse")]
refilled = [i for i, c in enumerate(base) if not data["containers"][i]["loot"] and c["loot"]]
ok(bool(refilled), f"пустые ящики Пятнадцатой наполнились хламом ({len(refilled)} шт.)")
i, refill_loot = (refilled[0], dict(base[refilled[0]]["loot"])) if refilled else (None, {})
if i is not None:
    g.open_container(base[i])
    g.loot_take_all()
    g.close_loot()
    ok(not base[i]["loot"], "ящик обыскан — пуст")
j = next((i for i, c in enumerate(base) if data["containers"][i]["loot"]), None)
keep = dict(base[j]["loot"]) if j is not None else {}
ok(g.save_game("q"), "сохранение")
g2 = Game(intro=False)
ok(g2.load_game("q"), "загрузка")
base2 = [c for c in g2.locations["ruins"].level.containers if not c.get("corpse")]
if i is not None:
    ok(not base2[i]["loot"] and base2[i]["opened"], "после загрузки обысканный ящик пуст — заново не наполнился")
ok(j is not None and base2[j]["loot"] == keep, "нетронутый ящик после загрузки с тем же лутом")

# новая игра (без сохранения) даёт тот же хлам: хэш, а не случайность
g3 = Game(intro=False)
g3.enter_location("ruins")
while g3.slides:
    g3.update(5000)
    g3.slides_next()
base3 = [c for c in g3.loc.level.containers if not c.get("corpse")]
ok(i is not None and base3[i]["loot"] == refill_loot, "новая игра наполняет ящики тем же хламом")

# отрисовка пустого ящика идёт через вскрытый проп, без падений
g2.enter_location("ruins")
for _ in range(2):
    g2.update(16)
    g2.draw()

# две загрузки одного сохранения дают один и тот же лут (детерминизм сохраняется и на load)
g4 = Game(intro=False)
g5 = Game(intro=False)
g4.load_game("q")
g5.load_game("q")
l4 = [dict(c["loot"]) for c in g4.locations["ruins"].level.containers if not c.get("corpse")]
l5 = [dict(c["loot"]) for c in g5.locations["ruins"].level.containers if not c.get("corpse")]
ok(l4 == l5 and len(l4) == len(base), f"две загрузки одной карты — одинаковый лут ({len(l4)} контейнеров)")

# сюжетные контейнеры Барстоу/города: on_put / requires / owner целы, lootfill ничего не подсыпал
SCALED = ("крышки", "стимулятор", "бинт")      # что законно меняет src/balance.py: scale_loot по акту
spec_json = [(i, c) for i, c in enumerate(data["containers"]) if lootfill.is_special(c)]
live = base  # контейнеры Пятнадцатой, как их видит игра
ok(len(spec_json) > 0, f"в карте есть сюжетные контейнеры ({len(spec_json)} шт.)")
bad_spec = []
for i, c in spec_json:
    lc, jl = live[i], c.get("loot", {})
    if (lc.get("on_put") != c.get("on_put") or lc.get("requires") != c.get("requires")
            or lc.get("owner") != c.get("owner")):
        bad_spec.append(f"{c['name']}#{i}: поля")
    elif set(lc["loot"]) != set(jl):                       # новый предмет = подсыпали
        bad_spec.append(f"{c['name']}#{i}: {set(lc['loot']) ^ set(jl)}")
    elif any(lc["loot"][k] != v for k, v in jl.items() if k not in SCALED):
        bad_spec.append(f"{c['name']}#{i}: количество")
ok(not bad_spec, f"on_put/requires/owner и лут сюжетных не тронуты ({bad_spec[:3]})")
locked = [(i, c) for i, c in enumerate(data["containers"]) if c.get("requires")]
junk_in_locked = [c["name"] for i, c in locked
                  if any(n not in items.ITEMS or items.ITEMS[n].get("cat") == "resource"
                         for n in live[i]["loot"] if n not in c.get("loot", {}))]
ok(not junk_in_locked, f"в запертые хлам не подсыпан ({len(locked)} запертых, {junk_in_locked[:3]})")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
