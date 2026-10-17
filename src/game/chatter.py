"""
Разговоры жителей друг с другом (data/chatter.json, собирается tools/build_chatter.py).

Раз в полминуты двое соседей неподалёку от героя сходятся, поворачиваются друг к другу и по очереди говорят —
репликами над головой в 2–3 строки: быт, байки, новости города, слухи. Кто стоит рядом, тот слышит.
Разговор с золотой каймой — «стоит подслушать»: если героя рядом хватило на большую часть реплик, в журнале событий
появляется то, что он узнал, а условные эффекты (флаги заданий, точки на карте мира) срабатывают — подсказка к
заданию или другая дорога. Каждую такую тайну слышат один раз.

Именные пары (pair) разговаривают на расстоянии, не сходясь, — например бармен и пьяница через стойку.
Выключено под headless-тестами (см. src/ambient.enabled).
"""
import json
import random
from collections import deque

import pygame

from .. import ambient, settings as S, wander
from ..combat import tile_of, rect_pos_for_tile
from ..ui.combat_ui import speech_ms

T = S.TILE
NEAR_TILES = 7           # так близко от героя слышно
SPOT_TILES = 10          # разговор затевают в такой близости от героя
_DATA = None


def data():
    global _DATA
    if _DATA is None:
        with open("data/chatter.json", "r", encoding="utf-8") as f:
            _DATA = json.load(f)
        import os
        if os.path.isfile("data/folk_talks.json"):       # личные разговоры конкретных жителей (tools/folks_*.py)
            with open("data/folk_talks.json", "r", encoding="utf-8") as f:
                for loc, convs in json.load(f).items():
                    _DATA.setdefault(f"loc:{loc}", []).extend(convs)
    return _DATA


def _keys(game):
    from .reputation import town_of
    town = town_of(game.loc.id) if game.loc else None
    return ([f"loc:{game.loc.id}"] if game.loc else []) + ([f"@{town}"] if town else []) + ["@all"]


def rumors_for(game):
    """Слухи из разговоров (поле rumor), подходящие этому городу и поступкам героя."""
    out = []
    for k in _keys(game):
        for c in data().get(k, []):
            if c.get("rumor") and game.check_condition(c.get("if", {})):
                out.append(c["rumor"])
    return out


def _dist(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def _bfs_to_neighbor(level, start, goal, blocked, maxd=14):
    """Путь от start до клетки, соседней с goal (или пустой, если уже рядом); None — не дойти."""
    if _dist(start, goal) <= 1:
        return []
    want = {(goal[0] + dx, goal[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
    prev = {start: None}
    q = deque([(start, 0)])
    while q:
        c, d = q.popleft()
        if c in want:
            path = []
            while c != start:
                path.append(c)
                c = prev[c]
            return path[::-1]
        if d >= maxd:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + dx, c[1] + dy)
            if n in prev or level.is_wall(*n) or level.is_exit(*n) or n in blocked:
                continue
            prev[n] = c
            q.append((n, d + 1))
    return None


class ChatterMixin:
    chat = None
    chat_cd = 12000
    chat_recent = ()

    # ------------------------------------------------------------ кто может говорить
    def _chat_ok(self, n):
        from .core import NO_RUMORS
        if n.npc_id in NO_RUMORS or ambient.is_critter(n.npc_id) or getattr(n, "chatting", False):
            return False
        if n is getattr(self, "dialogue_speaker", None) or self.hidden_by_roof(n):
            return False
        return not self.level.is_wall(*tile_of(n))

    def _chat_pool(self):
        recent = set(self.chat_recent)
        out = []
        for k in _keys(self):
            for c in data().get(k, []):
                if c["id"] in recent:
                    continue
                if c.get("once") and self.flags.get(f"chat_heard_{c['id']}"):
                    continue
                if c.get("reveal") and all(r in self.worldmap.known for r in c["reveal"]):
                    continue
                if not self.check_condition(c.get("if", {})):
                    continue
                out.append(c)
        return out

    def _chat_gossip(self):
        """Сплетня между двумя жителями с анкетами: один пересказывает свой слух, другой отвечает своей репликой.
        Каждый говорит только своё — повторяться нечему."""
        folk = [n for n in self.npcs if self._chat_ok(n) and ambient.AMBIENT.get(n.npc_id, {}).get("folk")]
        hero = tile_of(self.player)
        near = [n for n in folk if 2 <= _dist(hero, tile_of(n)) <= SPOT_TILES]
        random.shuffle(near)
        busy = {tile_of(o) for o in self.npcs} | {tile_of(e) for e in self.enemies if e.alive} | {hero}
        recent = set(self.chat_recent)
        for a in near[:5]:
            others = [n for n in folk if n is not a and _dist(tile_of(a), tile_of(n)) <= 9]
            others.sort(key=lambda n: _dist(tile_of(a), tile_of(n)))
            for b in others[:3]:
                pa, pb = ambient.AMBIENT[a.npc_id], ambient.AMBIENT[b.npc_id]
                tid = f"g_{a.npc_id}_{b.npc_id}"
                if tid in recent:
                    continue
                news = [t for t in (ambient._cond_text(self, n) for n in pa["news"]) if t]
                if not news:
                    continue
                path = _bfs_to_neighbor(self.level, tile_of(a), tile_of(b), busy - {tile_of(a)} - {tile_of(b)})
                if path is None:
                    continue
                lines = [[ "A", random.choice(news)], ["B", random.choice(pb["barks"] + pb["news"][:1] if all(isinstance(x, str) for x in pb["news"][:1]) else pb["barks"])]]
                if random.random() < 0.5:
                    lines.append(["A", random.choice(pa["barks"])])
                self._chat_start({"id": tid, "lines": lines}, a, b, path)
                return True
        return False

    def _chat_pick(self, conv):
        """Двое для разговора: (A, B, путь для A | None — говорят на расстоянии)."""
        lv = self.level
        hero = tile_of(self.player)
        by_id = {n.npc_id: n for n in self.npcs}
        if conv.get("pair"):
            a, b = (by_id.get(ambient.KEY2ID.get(i, i)) for i in conv["pair"])
            if a and b and self._chat_ok(a) and self._chat_ok(b) and _dist(tile_of(a), tile_of(b)) <= 9 \
                    and min(_dist(hero, tile_of(a)), _dist(hero, tile_of(b))) <= SPOT_TILES:
                return a, b, None
            return None
        near = [n for n in self.npcs if self._chat_ok(n) and 2 <= _dist(hero, tile_of(n)) <= SPOT_TILES]
        random.shuffle(near)
        busy = {tile_of(o) for o in self.npcs} | {tile_of(e) for e in self.enemies if e.alive} | {hero}
        for a in near[:5]:
            others = [n for n in self.npcs if n is not a and self._chat_ok(n) and _dist(tile_of(a), tile_of(n)) <= 9]
            others.sort(key=lambda n: _dist(tile_of(a), tile_of(n)))
            for b in others[:3]:
                path = _bfs_to_neighbor(lv, tile_of(a), tile_of(b), busy - {tile_of(a)} - {tile_of(b)})
                if path is not None:
                    return a, b, path
        return None

    # ------------------------------------------------------------ ход разговора
    def _chatter(self, dt_ms):
        if not ambient.enabled() or self.mode != "local" or getattr(self.level, "iso", False) or self.merc_mode:
            return
        if self.modal_open() or self.combat.active or self.action.active or self.dialogue.is_active():
            self._chat_end(abort=True)
            return
        c = self.chat
        if c is None:
            self.chat_cd -= dt_ms
            if self.chat_cd > 0 or self.speech:
                return
            self.chat_cd = 5000
            pool = self._chat_pool()
            if not pool or random.random() < 0.38:
                g = self._chat_gossip()
                if g:
                    return
            if not pool:
                return
            weights = [4 if p.get("hint") and not self.flags.get(f"chat_heard_{p['id']}") else 1 for p in pool]
            for _ in range(4):
                conv = random.choices(pool, weights)[0]
                pick = self._chat_pick(conv)
                if pick:
                    self._chat_start(conv, *pick)
                    return
            return
        c["t"] -= dt_ms
        a, b = c["A"], c["B"]
        if c["phase"] == "approach":
            c["deadline"] -= dt_ms
            ta, tb = tile_of(a), tile_of(b)
            if not a.wander_path and _dist(ta, tb) <= 1:
                self._chat_face(a, b)
                c["phase"], c["t"] = "talk", 200
            elif c["deadline"] <= 0 or (not a.wander_path and _dist(ta, tb) > 1):
                self._chat_end(abort=True)
            return
        if c["t"] > 0:
            return
        if c["i"] >= len(c["conv"]["lines"]):
            self._chat_end()
            return
        role, text = c["conv"]["lines"][c["i"]]
        who = a if role == "A" else b
        near = self._chat_near(who) or self._chat_near(b if who is a else a)
        interesting = bool(c["conv"].get("hint")) and not self.flags.get(f"chat_heard_{c['conv']['id']}")
        self.speech = {"ent": who, "text": text, "t": speech_ms(text), "chat": True, "hint": interesting and near}
        c["t"] = speech_ms(text) + 450
        c["heard"] += 1 if near else 0
        c["i"] += 1
        self._chat_face(a, b)

    def _chat_near(self, n):
        return _dist(tile_of(self.player), tile_of(n)) <= NEAR_TILES and not self.hidden_by_roof(n)

    def _chat_face(self, a, b):
        a.anim.face(b.rect.centerx - a.rect.centerx, b.rect.centery - a.rect.centery)
        b.anim.face(a.rect.centerx - b.rect.centerx, a.rect.centery - b.rect.centery)
        a.anim.set_action("idle")
        b.anim.set_action("idle")

    def _chat_start(self, conv, a, b, path):
        for n in (a, b):
            n.chatting = True
            if not hasattr(n, "home"):
                wander._init(n)
            n.wander_path = []
        c = {"conv": conv, "A": a, "B": b, "i": 0, "heard": 0, "t": 0, "phase": "talk", "deadline": 14000}
        if path:
            a.wander_path = path
            c["phase"] = "approach"
        else:
            self._chat_face(a, b)
        self.chat = c

    def _chat_end(self, abort=False):
        c = self.chat
        if c is None:
            return
        self.chat = None
        for n in (c["A"], c["B"]):
            n.chatting = False
            n.home = tile_of(n)
            n.wander_path = []
            n.wander_wait = random.randint(2500, 7000)
            n.anim.set_action("idle")
        conv = c["conv"]
        self.chat_recent = (list(self.chat_recent) + [conv["id"]])[-14:]
        self.chat_cd = random.randint(22000, 48000)
        if abort:
            if self.speech and self.speech.get("chat"):
                self.speech = None
            return
        need = max(1, int(len(conv["lines"]) * 0.6 + 0.5))
        if c["heard"] >= need and (conv.get("hint") or conv.get("reveal")):
            self._chat_eavesdropped(conv)

    def _chat_eavesdropped(self, conv):
        self.flags[f"chat_heard_{conv['id']}"] = True
        self.log(f"Вы подслушали разговор: {conv['hint']}" if conv.get("hint") else "Вы подслушали разговор.")
        self.apply_effect({"type": "xp", "amount": 12})          # внимательность вознаграждается
        for eff in conv.get("effects", []):
            self.apply_effect(eff)
        for loc in conv.get("reveal", []):
            if loc not in self.worldmap.known:
                self.reveal_location(loc)
