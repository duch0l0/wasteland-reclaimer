"""
Город меняется на глазах (docs/city_plan.md, этап 1): решения героя видны на карте, а не только в слухах.

data/world_changes.json — для локации список изменений с условием (if, как в диалогах):
  add      — поставить объект рядом с якорем: {"prop", "near": "npc:<id>" | "prop:<имя>" | [x, y], "r": радиус,
             "doc": id записки — объект читается кликом, как доска объявлений}
  remove   — убрать объекты по имени: {"prop": имя} (все такие на карте) или {"prop", "near", "r"} (ближайший)
  hide_npc — житель больше не стоит на своём месте (ушёл, умер, переехал)

Изменения ставятся при каждом входе в локацию; место выбирается так, чтобы не встать в проход, на выход,
портал или дверь и не отрезать путь (проверка: все жители, порталы и выходы остаются досягаемы).
"""
import json
from collections import deque

import pygame

from .. import props as P
from .. import settings as S

T = S.TILE
with open("data/world_changes.json", encoding="utf-8") as _f:
    CHANGES = {k: v for k, v in json.load(_f).items() if not k.startswith("_")}


def _anchor(level, npcs, near):
    if isinstance(near, list):
        return tuple(near)
    kind, _, name = near.partition(":")
    if kind == "npc":
        n = next((n for n in npcs if n.npc_id == name), None)
        if n is not None:
            return (n.rect.centerx // T, n.rect.centery // T)
        spawn = next((p for p, nid in level.npc_spawns if nid == name), None)
        return (spawn[0] // T, spawn[1] // T) if spawn else None
    o = next((o for o in level.objects if o["name"] == name and not o.get("hidden")), None)
    return o["foot"][0] if o else None


def _reach(level, start):
    seen, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n not in seen and not level.is_wall(*n):
                seen.add(n)
                q.append(n)
    return seen


class WorldChangesMixin:
    def apply_world_changes(self):
        lvl = self.level
        if not hasattr(lvl, "objects") or not hasattr(lvl, "npc_spawns"):
            return
        done = getattr(lvl, "changes_done", None)
        if done is None:
            done = lvl.changes_done = set()
        for i, ch in enumerate(CHANGES.get(self.loc.id, [])):
            if i in done or not self.check_condition(ch.get("if", {})):
                continue
            done.add(i)
            for r in ch.get("remove", []):
                self._wc_remove(r)
            for a in ch.get("add", []):
                self._wc_add(a)
            for nid in ch.get("hide_npc", []):
                self.loc.npcs[:] = [n for n in self.npcs if n.npc_id != nid]

    def _wc_remove(self, r):
        lvl = self.level
        objs = [o for o in lvl.objects if o["name"] == r["prop"] and not o.get("hidden")]
        if "near" in r:
            a = _anchor(lvl, self.npcs, r["near"])
            objs = sorted(objs, key=lambda o: abs(o["foot"][0][0] - a[0]) + abs(o["foot"][0][1] - a[1]))[:1] if a else []
        for o in objs:
            lvl.remove_object(o)

    def _wc_add(self, a):
        lvl = self.level
        center = _anchor(lvl, self.npcs, a["near"])
        if center is None:
            return
        inf = P.info(a["prop"])
        fw, fh = inf["foot"]
        block = inf["block"]
        passages = set(lvl.doors) | set(lvl.exits) | {t for p in lvl.portals for t in p["tiles"]}
        busy = set(passages)
        busy |= {(n.rect.centerx // T, n.rect.centery // T) for n in self.npcs}
        busy.add((self.player.rect.centerx // T, self.player.rect.centery // T))
        for o in lvl.objects:
            if not o.get("hidden"):
                busy.update(o["foot"])
        targets = [t for p in lvl.portals for t in p["tiles"]] + list(lvl.exits)[:4] + \
                  [(n.rect.centerx // T, n.rect.centery // T) for n in self.npcs]
        start = (self.player.rect.centerx // T, self.player.rect.centery // T)
        r = a.get("r", 4)
        spots = sorted(((x, y) for x in range(center[0] - r, center[0] + r + 1)
                        for y in range(center[1] - r, center[1] + r + 1)),
                       key=lambda c: (abs(c[0] - center[0]) + abs(c[1] - center[1]), c))
        for x, y in spots:
            foot = [(x + i, y + j) for i in range(fw) for j in range(fh)]
            # не в стену, не на занятое; блокирующий объект — не вплотную к двери, выходу или порталу
            if any(lvl.is_wall(*t) or t in busy for t in foot):
                continue
            if block and any((t[0] + dx, t[1] + dy) in passages
                             for t in foot for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                continue
            if block:
                before = _reach(lvl, start)
                lvl.blocked.update(foot)
                after = _reach(lvl, start)
                if any(t in before and t not in after and t not in foot for t in targets) or \
                        len(before) - len(after) > len(foot) + 2:
                    lvl.blocked.difference_update(foot)
                    continue
                if inf["sight"]:
                    lvl.sight.update(foot)
            bottom = (y + fh) * T
            rect = pygame.Rect(0, 0, *inf["size"])
            rect.midbottom = ((x + fw / 2) * T, bottom)
            obj = {"name": a["prop"], "rect": rect, "sort_y": bottom, "foot": foot, "container": None,
                   "floor": inf["layer"] == "floor", "changed": True}
            lvl.objects.append(obj)
            if a.get("doc"):
                term = {"id": "doc:" + a["doc"], "tiles": foot, "obj": obj}
                obj["terminal"] = term
                lvl.terminals.append(term)
            return obj
        return None
