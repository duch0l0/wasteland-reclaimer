"""
Живое население: жители с профессиями и характерами, дети, старики, пьяницы, музыканты — и зверьё: собаки,
кошки, куры, двухголовые брамины. Они не запечены в карты: при создании локации (src/location.py) их ставит
populate(), всегда одинаково для одной локации (зерно — id локации). Данные — data/ambient.json
(собираются tools/build_ambient.py).

У каждого жителя своя профессия и свой характер: от них зависят его реплики (барки), разговор по клику
(«Что нового?» — свежие слухи города, «Расскажи о себе») и то, о чём он болтает с соседями
(src/game/chatter.py). Животные рычат, мяукают, кудахчут — и гладятся по клику.

Включено в живой игре; под headless-тестами (SDL_VIDEODRIVER=dummy) выключено, чтобы расстановка и случайные
реплики не сбивали сценарии. Принудительно: WASTELAND_AMBIENT=1 (включить) / 0 (выключить).
"""
import json
import os
import random
import zlib
from collections import deque

from . import settings as S

T = S.TILE
AMBIENT = {}      # npc_id -> персона {"name", "kind": human|critter, "job", "trait", "barks", ...}
_DATA = None


def enabled():
    env = os.environ.get("WASTELAND_AMBIENT")
    if env is not None:
        return env == "1"
    return os.environ.get("SDL_VIDEODRIVER") != "dummy"


def data():
    global _DATA
    if _DATA is None:
        with open(os.path.join("data", "ambient.json"), "r", encoding="utf-8") as f:
            _DATA = json.load(f)
    return _DATA


def is_ambient(npc_id):
    return npc_id in AMBIENT


def is_critter(npc_id):
    return npc_id.startswith("amb_critter_")


# ------------------------------------------------------------------ расстановка
def _walkable(level, t):
    return not level.is_wall(*t) and not level.is_exit(*t) and not (hasattr(level, "portal_at") and level.portal_at(*t))


def _reach(level, start, limit=6000):
    seen = {start}
    q = deque([start])
    while q and len(seen) < limit:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and 0 <= n[0] < level.width and 0 <= n[1] < level.height and _walkable(level, n):
                seen.add(n)
                q.append(n)
    return seen


def _roomy(level, t):
    """Клетка не в тупике и не у самого прохода: рядом есть хотя бы три свободных соседа."""
    x, y = t
    return sum(_walkable(level, (x + dx, y + dy)) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy) >= 6


def _persona(rnd, loc_id, i, spec):
    d = data()
    job_key = rnd.choice(spec["jobs"])
    job = d["jobs"][job_key]
    trait_key = rnd.choice(list(d["traits"]))
    trait = d["traits"][trait_key]
    gender = rnd.choice("mf")
    title = job["m"] if gender == "m" else job["f"]
    nm = rnd.choice(d["names"][gender])
    sheets = d["sheets"]["ghoulkid" if spec.get("ghoul") and job_key == "kid" else "ghoul" if spec.get("ghoul") else job["sheets"]]
    sheet = rnd.choice(sheets)
    nid = f"amb_{loc_id}_{i}"
    barks = list(job["barks"]) + list(trait["barks"])
    return nid, {"name": f"{title} {nm}", "kind": "human", "job": job_key, "trait": trait_key, "gender": gender,
                 "sheet": sheet, "barks": barks, "greet": rnd.choice(trait["greet"]) + " " + rnd.choice(job["greet"]),
                 "about": list(job["about"]), "stroll": 7 if job_key in ("courier", "kid", "musician", "scav") else rnd.choice((4, 5, 6))}


def _critter(rnd, loc_id, i, species):
    c = data()["critters"][species]
    sheet = rnd.choice(c["sheets"])
    nid = f"amb_critter_{loc_id}_{i}"
    return nid, {"name": c["title"], "kind": "critter", "species": species, "sheet": sheet, "barks": list(c["barks"]),
                 "talk": list(c["talk"]), "stroll": rnd.choice((6, 8, 9)) if species != "brahmin" else 5}


def populate(loc, loc_id=None):
    """Поставить в Location жителей и зверей по data/ambient.json (если для локации они заданы)."""
    from .entities import NPC
    from .location import NPC_NAMES, NPC_SPRITES, npc_animations
    loc_id = loc_id or loc.id
    spec = data()["locs"].get(loc_id)
    lv = loc.level
    if not spec or getattr(lv, "iso", False) or not hasattr(lv, "is_wall") or loc.is_encounter:
        return 0
    rnd = random.Random(zlib.crc32(loc_id.encode()) & 0xFFFFFFFF)
    ex, ey = int(loc.entry[0]) // T, int(loc.entry[1]) // T
    reach = _reach(lv, (ex, ey))
    if len(reach) < 40:
        return 0
    taken = [(int(p[0]) // T, int(p[1]) // T) for p, _ in lv.npc_spawns] + \
            [(int(sp[0][0]) // T, int(sp[0][1]) // T) for sp in lv.enemy_spawns]
    foes = [(int(sp[0][0]) // T, int(sp[0][1]) // T) for sp in lv.enemy_spawns]
    cand = [t for t in reach if _roomy(lv, t) and max(abs(t[0] - ex), abs(t[1] - ey)) >= 5
            and all(max(abs(t[0] - f[0]), abs(t[1] - f[1])) > 8 for f in foes)]
    if not cand:
        return 0
    # где жизнь: рядом с жителями карты клетки «тяжелее»
    anchors = [t for t in taken if t not in foes]
    weights = [3.0 if any(abs(t[0] - a[0]) + abs(t[1] - a[1]) <= 14 for a in anchors) else 1.0 for t in cand]

    def pick(dist):
        for _ in range(60):
            t = rnd.choices(cand, weights)[0]
            if all(max(abs(t[0] - o[0]), abs(t[1] - o[1])) >= dist for o in taken):
                taken.append(t)
                return t
        return None

    made = []
    for i in range(spec["people"]):
        t = pick(4)
        if t is None:
            break
        nid, p = _persona(rnd, loc_id, i, spec)
        made.append((nid, p, t))
    n = 0
    for species, count in spec.get("critters", {}).items():
        anchor = None
        for k in range(count):
            t = None
            if species == "chicken" and anchor is not None:    # куры ходят кучкой
                near = [c for c in cand if 1 <= max(abs(c[0] - anchor[0]), abs(c[1] - anchor[1])) <= 3]
                if near:
                    t = rnd.choice(near)
                    taken.append(t)
            if t is None:
                t = pick(3)
            if t is None:
                break
            if species == "chicken":
                anchor = anchor or t
            nid, p = _critter(rnd, loc_id, n, species)
            n += 1
            made.append((nid, p, t))
    count = 0
    for nid, p, t in made:
        AMBIENT[nid] = p
        NPC_NAMES[nid] = p["name"]
        NPC_SPRITES[nid] = p["sheet"]
        npc = NPC((t[0] * T, t[1] * T), npc_animations(nid), npc_id=nid, name=p["name"])
        npc.stroll = p["stroll"]
        loc.npcs.append(npc)
        loc.npcs_all.append(npc)
        count += 1
    return count


# ------------------------------------------------------------------ реплики и разговор
def barks_for(npc_id):
    p = AMBIENT.get(npc_id)
    return list(p["barks"]) if p else []


def rumor_pool(game, npc):
    """Слухи, которые знает житель: слухи города и пустоши, подходящие к поступкам героя; свежие — первыми."""
    pool = []
    try:
        pool = [t for t in game.bark_lines(npc) if t not in AMBIENT.get(npc.npc_id, {}).get("barks", [])]
    except Exception:
        pass
    from .game import chatter
    pool += chatter.rumors_for(game)
    return pool


def tree_for(game, npc_id):
    """Диалоговое дерево жителя или зверя — собирается на лету (слухи зависят от того, что уже сделал герой)."""
    p = AMBIENT.get(npc_id)
    if not p:
        return None
    npc = next((n for n in game.npcs if n.npc_id == npc_id), None)
    if p["kind"] == "critter":
        text = random.choice(p["talk"])
        return {"start": "t", "nodes": {"t": {"text": text, "options": [{"label": "(погладить и уйти)", "next": None}]}}}
    name = p["name"]
    rumors = []
    if npc is not None:
        pool = rumor_pool(game, npc)
        random.shuffle(pool)
        rumors = pool[:3]
    if not rumors:
        rumors = ["Да ничего особенного. Ветер, пыль, всё как всегда."]
    nodes = {"greet": {"text": f"{name}: {p['greet']}",
                       "options": [{"label": "Что нового в городе?", "next": "r0"},
                                   {"label": "Расскажи о себе.", "next": "about"},
                                   {"label": "Бывай.", "next": None}]}}
    for i, r in enumerate(rumors):
        last = i == len(rumors) - 1
        nodes[f"r{i}"] = {"text": f"{name}: {r}",
                          "options": ([] if last else [{"label": "А ещё что слышно?", "next": f"r{i + 1}"}]) +
                                     [{"label": "Спасибо за новости.", "next": None}]}
    about = random.choice(p["about"])
    nodes["about"] = {"text": f"{name}: {about}", "options": [{"label": "Интересно. Что ещё слышно?", "next": "r0"},
                                                           {"label": "Бывай.", "next": None}]}
    return {"start": "greet", "nodes": nodes}
