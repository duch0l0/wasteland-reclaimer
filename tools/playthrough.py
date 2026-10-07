"""
Бот-игрок: проходит сюжет по-честному — без бессмертия и без убийства врагов строчкой кода.
Сам дерётся (подходит, стреляет, лечится, меняет оружие на лучшее), обыскивает ящики на пути,
выбирает навыки и перки, покупает патроны и лекарства, разговаривает по сюжету. Единственные упрощения —
мгновенные переходы между локациями (без случайных встреч в пустоши) и «шаг к цели» телепортом, как
игрок, который кликнул и дошёл.

На каждом этапе пишет строку отчёта: уровень, HP, крышки, патроны, аптечки, сколько боёв и сколько
раз чуть не умер. В конце — сводка и список проблем (смерть, застрял, не открылось).

  .venv/bin/python tools/playthrough.py            — пройти всё, что умеет
  .venv/bin/python tools/playthrough.py act1       — только первый акт
  .venv/bin/python tools/playthrough.py --build energy --seed 3 --nosides   — другая сборка, бросок, без побочек
"""
import os
import random
import sys
import tempfile
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame  # noqa: E402

pygame.mouse.get_pos = lambda: (-50, -50)
pygame.mouse.get_focused = lambda: True

from src.game import Game, saveload  # noqa: E402
from src.combat import tile_of, rect_pos_for_tile, chebyshev  # noqa: E402
from src.weapons import WEAPONS, shortfall, skill_of  # noqa: E402
from src import items as ITEMS  # noqa: E402
from src import settings as S  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()

# сборки героя: какие навыки качать (по очереди, пока не выйдет следующий порог)
BUILDS = {
    "guns": [("guns", 70), ("speech", 60), ("guns", 80), ("science", 55), ("speech", 75), ("medicine", 45),
             ("guns", 100), ("science", 75), ("survival", 50), ("guns", 150)],
    "energy": [("guns", 60), ("energy", 50), ("speech", 60), ("energy", 75), ("science", 55), ("energy", 100),
               ("medicine", 45), ("energy", 130), ("science", 75), ("energy", 150)],
    "heavy": [("guns", 60), ("heavy", 50), ("speech", 50), ("heavy", 75), ("medicine", 45), ("heavy", 100),
              ("science", 55), ("heavy", 130), ("survival", 50), ("heavy", 150)],
    "melee": [("melee", 80), ("speech", 55), ("melee", 100), ("medicine", 50), ("throwing", 60), ("melee", 120),
              ("science", 55), ("survival", 50), ("melee", 150)],
    "talker": [("speech", 75), ("science", 60), ("guns", 70), ("speech", 100), ("science", 80), ("guns", 90),
               ("medicine", 45), ("speech", 150)],
}
PERK_PREF = ["steady_hand", "action_boy", "tough", "silver_tongue", "sharp_eye", "thick_skin", "burst_master",
             "hacker", "medic", "point_blank", "bonus_move", "scavenger"]
HEALS = ["стимулятор", "аптечка армейская", "тоник", "набор", "бинт", "консервы", "вяленое мясо",
         "энергетический батончик", "чистая вода", "самогон", "сушёные травы"]


class Stuck(Exception):
    pass


class Dead(Exception):
    pass


class Critic:
    """Придирчивый игрок: смотрит, что видит бот, и ворчит. Каждое замечание — с местом, где его словил."""

    def __init__(self, bot):
        self.bot = bot
        self.notes = []      # (место, текст)
        self.seen_locs = set()

    def say(self, text):
        g = self.bot.g
        where = g.loc.id if g.loc else "мир"
        if (where, text) not in self.notes:
            self.notes.append((where, text))
            print(f"   🗯 [{where}] {text}", flush=True)

    def on_enter(self):
        g = self.bot.g
        lid = g.loc.id
        if lid in self.seen_locs:
            return
        self.seen_locs.add(lid)
        npcs = g.npcs
        flavor = 0
        for n in npcs:
            tree = g.dialogue.trees.get(n.npc_id)
            if not tree:
                self.say(f"{n.name} молчит — у жителя вообще нет диалога. Манекен?")
                continue
            nodes = tree["nodes"]
            if len(nodes) == 1 and all(o["label"] in ("...", "…") for nd in nodes.values() for o in nd["options"]):
                flavor += 1
        if npcs and flavor >= max(4, len(npcs) * 0.6):
            self.say(f"Из {len(npcs)} жителей {flavor} только бросают фразу и «...». Город как декорация.")
        boxes = [b for b in g.level.containers if not b.get("owner")]
        if not npcs and not g.enemies and not boxes and not g.level.terminals:
            self.say("Пустая локация: ни людей, ни врагов, ни ящиков. Зачем я сюда шёл?")

    def on_fight(self, rounds, enemies, hp_lost, hp_cap, one_shots):
        if rounds >= 14:
            self.say(f"Бой тянулся {rounds} раундов. Скучно, враги — губки для пуль.")
        if enemies and one_shots == enemies and enemies >= 3 and hp_lost == 0:
            self.say(f"Все {enemies} врагов легли с одного выстрела и даже не поцарапали. Где вызов?")
        if hp_lost >= hp_cap * 0.75:
            self.say("Чуть не умер в обычной стычке. Многовато для рядового боя.")

    def on_level(self, level, act_name):
        pass

    def on_checkpoint(self, name):
        g = self.bot.g
        p = g.player
        caps = g.inventory.count("крышки")
        heal_hp = sum(g.inventory.count(h) * ITEMS.ITEMS.get(h, {}).get("use", {}).get("heal", 0) for h in HEALS)
        if heal_hp >= p.hp_cap * 7:
            self.say(f"В рюкзаке лечения на {heal_hp} HP — семь полных жизней. Умереть теперь невозможно даже нарочно.")
        if caps >= 2500:
            self.say(f"{caps} крышек и тратить некуда. Экономика сломалась.")
        if g.inventory.count("патроны") >= 400:
            self.say(f"{g.inventory.count('патроны')} патронов — склад, а не рюкзак.")
        guns = [k for k, w in WEAPONS.items() if w.get("item") and g.inventory.has(w["item"])]
        if p.level_sys.level >= 6 and len(guns) <= 1:
            self.say(f"Уровень {p.level_sys.level}, а всё ещё бегаю с одним стволом. Где лучше оружие?")

    def summary(self):
        return self.notes


class Bot:
    def __init__(self, seed=7, sides=True, build="guns"):
        random.seed(seed)
        self.sides = sides
        self.build_name = build
        self.build = BUILDS[build]
        self.g = Game(intro=False)
        self.stats = {"fights": 0, "close_calls": 0, "heals_used": 0, "deaths": 0, "kills": 0}
        self.rows = []
        self.problems = []
        self.t0 = time.time()
        self.critic = Critic(self)
        self.read_docs = set()

    # ------------------------------------------------------------ кадры и окна
    def fr(self, n=2):
        g = self.g
        for _ in range(n):
            g.update(16)
            g.draw()
            self.handle_popups()

    def handle_popups(self):
        g = self.g
        guard = 0
        while (g.perk_choices or getattr(g, "slides", None)) and guard < 50:
            guard += 1
            if g.slides:
                g.update(5000)
                g.slides_next()
                continue
            self.choose_levelup()
        if g.loot:
            g.handle_key(pygame.K_r)
            if g.loot:
                g.handle_key(pygame.K_ESCAPE)

    def choose_levelup(self):
        g = self.g
        opts = g.perk_choices
        pick = None
        if opts and opts[0].get("kind") == "skill":
            for sid, target in self.build:
                if g.player.skill(sid) < target:
                    pick = next((i for i, o in enumerate(opts) if o["id"] == sid), None)
                    if pick is not None:
                        break
        else:
            for pid in PERK_PREF:
                pick = next((i for i, o in enumerate(opts) if o.get("id") == pid), None)
                if pick is not None:
                    break
        g.handle_key(pygame.K_1 + (pick or 0))

    # ------------------------------------------------------------ перемещение
    def go(self, loc_id):
        g = self.g
        if g.combat.active:
            self.fight()
        g.dialogue.active_node = None
        g.enter_location(loc_id)
        self.fr(3)
        self.check_alive(f"вход в {loc_id}")
        self.critic.on_enter()

    def stand_near(self, tiles):
        g = self.g
        tiles = [tuple(t) for t in tiles]
        for t in tiles:
            for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
                c = (t[0] + dx, t[1] + dy)
                if not g.level.is_wall(*c) and c not in tiles and not g.level.is_exit(*c):
                    g.player.rect.topleft = rect_pos_for_tile(g.player, c)
                    g.snap_camera()
                    self.fr(2)
                    if g.combat.active:
                        self.fight()
                    return
        raise Stuck(f"негде встать рядом с {tiles[:2]}")

    def goto_portal(self, to):
        g = self.g
        p = next((p for p in g.level.portals if p["to"] == to), None)
        if p is None:
            if to in self.portal_graph():
                return self.walk_to_map(to)
            raise Stuck(f"{g.loc.id}: нет перехода в {to}")
        for _ in range(4):
            if g.combat.active:
                self.fight()
            g.dialogue.active_node = None
            g.player.rect.topleft = rect_pos_for_tile(g.player, tuple(sorted(p["tiles"])[0]))
            self.fr(4)
            if g.loc.id == to:
                break
        if g.loc.id != to:
            raise Stuck(f"переход {g.loc.id} → {to} не сработал ({(p.get('requires') or {}).get('msg', '')})")
        self.critic.on_enter()

    def walk_to_map(self, target):
        """Дойти до карты target по переходам (BFS по порталам, как игрок по дверям)."""
        g = self.g
        if g.loc.id == target:
            return
        graph = self.portal_graph()
        prev = {g.loc.id: None}
        queue = [g.loc.id]
        while queue:
            cur = queue.pop(0)
            if cur == target:
                break
            for nxt, req in graph.get(cur, ()):
                if nxt not in prev and self.can_pass(req):
                    prev[nxt] = cur
                    queue.append(nxt)
        if target not in prev:
            raise Stuck(f"не знаю дороги {g.loc.id} → {target}")
        path = []
        cur = target
        while cur != g.loc.id:
            path.append(cur)
            cur = prev[cur]
        for step in reversed(path):
            self.goto_portal(step)

    def can_pass(self, req):
        """Открыта ли дверь сейчас (ключ, флаг) — запертые бот обходит, как игрок."""
        if not req:
            return True
        g = self.g
        if req.get("item") and not g.inventory.has(req["item"]):
            return False
        cond = {k: v for k, v in req.items() if k not in ("item", "msg")}
        return g.check_condition(cond)

    _graph = None
    _npc_home = None

    def portal_graph(self):
        if Bot._graph is None:
            import glob
            import json
            Bot._graph, Bot._npc_home = {}, {}
            for f in glob.glob("data/maps/*.json"):
                mid = os.path.basename(f)[:-5]
                with open(f, encoding="utf-8") as fh:
                    m = json.load(fh)
                Bot._graph[mid] = [(p["to"], p.get("requires")) for p in m.get("portals", [])]
                for n in m.get("npcs", []):
                    Bot._npc_home.setdefault(n[0] if isinstance(n, list) else n.get("id"), mid)
        return Bot._graph

    def terminal_home(self, tid):
        import glob
        import json
        for f in glob.glob("data/maps/*.json"):
            with open(f, encoding="utf-8") as fh:
                m = json.load(fh)
            if any(t.get("id") == tid for t in m.get("terminals", [])):
                return os.path.basename(f)[:-5]
        return None

    def visit(self, map_id, clear=True):
        """Дойти до карты (через мир, если это другой город) и при нужде зачистить."""
        g = self.g
        self.portal_graph()
        if map_id not in self.reachable():
            root = next(k for k, v in g.locations.items()) if False else None
            g.go_world_map()
            city = self.city_of(map_id)
            self.go(city)
        self.walk_to_map(map_id)
        if clear and any(e.alive and e.hostile for e in g.enemies):
            self.clear(max_rounds=25)
            self.loot_area()

    def reachable(self):
        graph = self.portal_graph()
        seen = {self.g.loc.id}
        queue = [self.g.loc.id]
        while queue:
            for n, req in graph.get(queue.pop(0), ()):
                if n not in seen and self.can_pass(req):
                    seen.add(n)
                    queue.append(n)
        return seen

    def city_of(self, map_id):
        """Корень города: карта, из которой по порталам доступна map_id и которая есть на карте мира."""
        graph = self.portal_graph()
        known = self.g.worldmap.known
        for root in known:
            seen = {root}
            queue = [root]
            while queue:
                cur = queue.pop(0)
                if cur == map_id:
                    return root
                for n, req in graph.get(cur, ()):
                    if n not in seen and self.can_pass(req):
                        seen.add(n)
                        queue.append(n)
        raise Stuck(f"{map_id}: не открыт город, откуда туда дойти")

    def fetch(self, map_id, box, clear=True):
        """Сходить за ящиком: дойти, зачистить, обыскать."""
        self.visit(map_id, clear)
        self.search(box)
        self.fr(2)
        if self.g.combat.active:
            self.fight()

    def shop_here(self):
        g = self.g
        self.buy_implants()
        for n in list(g.npcs):
            if n.npc_id in g.traders:
                try:
                    self.stand_near([tile_of(n)])
                    self.shop(n.npc_id)
                except Stuck:
                    pass

    def find_npc(self, npc_id):
        g = self.g
        npc = next((n for n in g.npcs if n.npc_id == npc_id), None)
        if npc is None:
            self.portal_graph()
            home = Bot._npc_home.get(npc_id)
            if home and home != g.loc.id:
                self.walk_to_map(home)
                npc = next((n for n in g.npcs if n.npc_id == npc_id), None)
        return npc

    # ------------------------------------------------------------ разговоры и терминалы
    def talk(self, npc_id):
        g = self.g
        g.dialogue.active_node = None
        npc = self.find_npc(npc_id)
        if npc is None:
            raise Stuck(f"{g.loc.id}: нет жителя {npc_id}")
        for attempt in range(4):
            if g.combat.active:
                self.fight()
            tx, ty = tile_of(npc)
            order = [(0, 1), (1, 0), (-1, 0), (0, -1)]
            dx, dy = order[attempt]
            c = (tx + dx, ty + dy)
            if attempt and not g.level.is_wall(*c) and not g.level.is_exit(*c):
                g.player.rect.topleft = rect_pos_for_tile(g.player, c)
                g.snap_camera()
                self.fr(2)
            else:
                self.stand_near([tile_of(npc)])
            g.dialogue.active_node = None
            g.handle_key(pygame.K_e)
            if g.dialogue.is_active():
                return
        raise Stuck(f"разговор с {npc_id} не начался")

    def say(self, part, required=True):
        g = self.g
        opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
        idx = next((i for i, lbl in enumerate(opts) if part in lbl), None)
        if idx is None:
            if required:
                raise Stuck(f"нет реплики «{part}» среди {opts}")
            return False
        g.handle_key(pygame.K_1 + idx)
        self.fr(1)
        return True

    BAD_EFFECTS = ("town_fight", "fight", "leave_ally", "baker_assault")

    def plan_talk(self, goal, avoid=()):
        """Путь по текущему разговору до реплики, которая ставит флаг/даёт предмет goal (BFS по веткам,
        видимым прямо сейчас). Так прощупывает разговор игрок: «а если спросить вот это?»."""
        d = self.g.dialogue
        if not d.is_active():
            return None
        nodes = d.trees[d.active_id]["nodes"]
        check = d.check
        start = d.active_node
        seen = {start}
        queue = [(start, [])]
        while queue:
            nid, path = queue.pop(0)
            for o in nodes[nid].get("options", []):
                if not check(o.get("if", {})):
                    continue
                eff = o.get("effects", [])
                if any(e["type"] in self.BAD_EFFECTS + tuple(avoid) for e in eff):
                    continue
                if any(e.get("flag") == goal or (e["type"] == "give" and e.get("item") == goal)
                       or (goal.startswith("quest:") and e["type"] == "quest" and e.get("id") == goal[6:]
                           and e.get("stage", 0) > self.g.stage(goal[6:])) for e in eff):
                    return path + [o]
                nxt = o.get("next")
                if nxt and nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, path + [o]))
        return None

    def pursue(self, npc_id, goal, required=True, avoid=()):
        """Поговорить с жителем и довести разговор до goal; True — если вышло."""
        g = self.g
        if g.flags.get(goal):
            return True
        stage0 = g.stage(goal[6:]) if goal.startswith("quest:") else 0
        self.talk(npc_id)
        for _ in range(20):
            path = self.plan_talk(goal, avoid)
            if not path:
                break
            o = path[0]
            vis = g.dialogue.visible_options()
            idx = next(i for i, x in enumerate(vis) if x is o)
            g.handle_key(pygame.K_1 + idx)
            self.fr(1)
            if len(path) == 1:
                break
        self.end_talk()
        done = bool(g.flags.get(goal) or g.inventory.has(goal)
                    or (goal.startswith("quest:") and g.stage(goal[6:]) > stage0))
        if required and not done:
            raise Stuck(f"{npc_id}: не вышло добиться «{goal}»")
        return done

    def parley(self, type_id, goal):
        """Поговорить с мирным врагом (у него свой диалог) и довести разговор до goal."""
        g = self.g
        e = next((e for e in g.enemies if e.alive and e.type_id == type_id and getattr(e, "talk", None)), None)
        if e is None or e.hostile:
            return False
        self.stand_near([tile_of(e)])
        e.talked = True
        g.talk_to(e, e.talk)
        if not g.dialogue.is_active():
            return False
        for _ in range(20):
            path = self.plan_talk(goal)
            if not path:
                break
            vis = g.dialogue.visible_options()
            g.handle_key(pygame.K_1 + next(i for i, x in enumerate(vis) if x is path[0]))
            self.fr(1)
            if len(path) == 1:
                break
        self.end_talk()
        return bool(g.flags.get(goal))

    def end_talk(self):
        self.g.dialogue.active_node = None

    def terminal(self, tid, *parts):
        g = self.g
        t = next((t for t in g.level.terminals if t["id"] == tid), None)
        if t is None:
            home = self.terminal_home(tid)
            if home:
                self.walk_to_map(home)
                t = next((t for t in g.level.terminals if t["id"] == tid), None)
        if t is None:
            raise Stuck(f"{g.loc.id}: нет терминала {tid}")
        self.stand_near(t["tiles"])
        g.handle_key(pygame.K_e)
        for part in parts:
            entries = g.term_entries()
            idx = next((i for i, (_, e) in enumerate(entries) if part in e["label"]), None)
            if idx is None:
                continue
            g.term_open_entry(idx)
            if g.term and g.term.get("view") == "locked":   # взлом: честно, по подсказкам
                self.hack()
            if g.term:
                g.term_back()
        g.close_terminal()

    def hack(self):
        g = self.g
        opts = g.lock_options()
        known = next((fn for lbl, fn in opts if lbl.startswith("Ввести пароль")), None)
        if known:
            known()
            return
        hack = next((fn for lbl, fn in opts if "Взлом" in lbl or "взлом" in lbl), None)
        if hack is None:
            return
        hack()
        h = g.term.get("hack") if g.term else None
        if not h:
            return
        # как игрок в Fallout: после каждой попытки отсеять слова, не совпадающие по числу букв на местах
        cand = list(h["words"])
        while g.term and g.term.get("view") == "hack" and cand and g.term["hack"]["tries"] > 0:
            word = cand.pop(0)
            g.hack_guess(word)
            if not g.term or g.term.get("view") != "hack":
                break
            log = g.term["hack"]["log"]
            if log and log[-1].startswith(">Совпадение="):
                n = int(log[-1].split("=")[1])
                cand = [w for w in cand if sum(a == b for a, b in zip(w, word)) == n]
        self.stats["hacks"] = self.stats.get("hacks", 0) + 1

    def pickup(self, kind):
        g = self.g
        it = next((p for p in g.level.pickups if p["kind"] == kind), None)
        if it is None:
            raise Stuck(f"{g.loc.id}: на земле нет «{kind}»")
        g.player.rect.topleft = rect_pos_for_tile(g.player, (it["rect"].x // 48, it["rect"].y // 48))
        self.fr(1)
        g.handle_key(pygame.K_e)
        self.fr(1)

    def take_from(self, title):
        """Открыть ящик (свой — без кражи) и забрать всё."""
        self.search(title)

    def open_gate(self, flag):
        g = self.g
        gate = next((x for x in getattr(g.level, "gates", []) if x["flag"] == flag), None)
        if gate is None:
            raise Stuck(f"{g.loc.id}: нет двери {flag}")
        self.stand_near(gate["tiles"])
        g.handle_key(pygame.K_e)
        self.fr(2)
        if not g.flags.get(flag):
            raise Stuck(f"дверь {flag} не открылась")

    def search(self, title):
        g = self.g
        box = next((c for c in g.level.containers if c["name"].startswith(title)), None)
        if box is None:
            raise Stuck(f"{g.loc.id}: нет ящика «{title}»")
        self.stand_near(box["tiles"])
        g.handle_key(pygame.K_e)
        self.fr(1)

    def take_item(self, map_id, item):
        """Сходить туда, где лежит вещь (по описанию квеста), и забрать её из ящика."""
        g = self.g
        self.visit(map_id)
        box = next((c for c in g.level.containers if item in (c.get("loot") or {})), None)
        if box is None:
            return False
        self.stand_near(box["tiles"])
        g.handle_key(pygame.K_e)
        self.fr(1)
        return g.inventory.has(item)

    def steal(self, map_id, title):
        """Вскрыть чужое так, чтобы хозяин не видел (встать с той стороны, где он не смотрит). True — взято."""
        g = self.g
        if not g.inventory.has("отмычка"):
            return False
        self.visit(map_id, clear=False)
        box = next((c for c in g.level.containers if c["name"].startswith(title)), None)
        if box is None or box["opened"]:
            return False
        owner = next((n for n in g.npcs if n.npc_id == box.get("owner")), None)
        spots = [(t[0] + dx, t[1] + dy) for t in box["tiles"] for dx, dy in
                 ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1))]
        spots = [c for c in spots if not g.level.is_wall(*c) and c not in box["tiles"]]
        for c in spots:
            g.player.rect.topleft = rect_pos_for_tile(g.player, c)
            if owner is None or not (pygame.Vector2(owner.rect.center).distance_to(g.player.rect.center) <= 6 * 48
                                     and g.combat.los(owner, g.player)):
                break
        g.snap_camera()
        self.fr(1)
        g.handle_key(pygame.K_e)
        self.fr(1)
        self.stats["thefts"] = self.stats.get("thefts", 0) + 1
        return box["opened"]

    def loot_area(self, owned_too=False):
        """Обыскать все ящики локации, к которым можно подойти (чужие — нет, это кража)."""
        g = self.g
        for box in list(g.level.containers):
            if box["opened"] or (box.get("owner") and not owned_too) or box.get("requires"):
                continue
            if box["name"].startswith("тело"):
                continue
            try:
                self.stand_near(box["tiles"])
            except Stuck:
                continue
            g.handle_key(pygame.K_e)
            self.fr(1)

    # ------------------------------------------------------------ бой
    def weapon_score(self, wid, armor=3, check_ammo=True):
        """Сколько урона за выстрел по цели с бронёй armor — с моими навыками (как прикидывает игрок)."""
        g = self.g
        p = g.player
        w = WEAPONS[wid]
        ammo = w.get("ammo")
        short = shortfall(p, wid)
        burst = 1 if short else w.get("burst", 1)
        if check_ammo and ammo and g.inventory.count(ammo) < 15 * burst:   # мало патронов — очередями не сорить
            burst = 1
        dmg = (p.damage + w.get("damage", 0)) if not w["ranged"] else (w.get("damage", 0) or 23)
        dmg = max(1, dmg - int(armor * (1 - w.get("pierce", 0))))
        hit = max(0.05, min(0.95, (skill_of(p, wid) - 2 * short - 25) / 100))
        return dmg * burst * hit * (1.6 if w["ranged"] else 1) * (0.3 if w.get("thrown") else 1) / w["ap"] * 4

    def best_weapon(self):
        """Лучшее, что слушается и чем есть стрелять."""
        g = self.g
        best, score = "melee", -1
        for wid, w in WEAPONS.items():
            item = w.get("item")
            if item and not g.inventory.has(item):
                continue
            ammo = w.get("ammo")
            if ammo and not g.inventory.has(ammo):
                continue
            s = self.weapon_score(wid)
            if s > score:
                best, score = wid, s
        if best != g.player.weapon:
            g.switch_weapon(best)

    def heal_if_needed(self, threshold=0.45):
        g = self.g
        p = g.player
        if p.hp >= p.hp_cap * threshold:
            return False
        for name in HEALS:
            if g.inventory.has(name):
                before = g.inventory.count(name)
                g.use_item(name)
                if g.inventory.count(name) < before:     # в бою может не хватить ОД — тогда не съедено
                    self.stats["heals_used"] += 1
                    return True
                return False
        return False

    def fight(self):
        g = self.g
        c = g.combat
        if not c.active:
            return
        self.stats["fights"] += 1
        self.best_weapon()
        low = g.player.hp
        hp0 = g.player.hp
        foes = list(c.enemies_in_combat())
        hp_foes = {id(e): e.hp for e in foes}
        rounds0 = c.round
        n = 0
        while c.active and g.player.alive:
            n += 1
            if n > 30000:
                raise Stuck("бой не кончается")
            if c.player_can_act():
                p = g.player
                urgent = p.hp < max(8, p.max_hp * 0.2)      # совсем плохо — лечиться в любом случае
                spare = p.ap - S.AP_CRAFT >= c.attack_cost(p)  # после бинта ещё хватит на выстрел
                if p.hp < p.hp_cap * 0.45 and p.ap >= S.AP_CRAFT and (urgent or spare) and self.heal_if_needed(0.45):
                    self.fr(1)
                    continue
                left = c.enemies_in_combat()
                if not left:
                    c.end_turn()
                    self.fr(1)
                    continue
                if not c.can_attack(p, left[0])[0] and c.can_attack(p, left[0])[1] == "нет патронов":
                    self.best_weapon()            # кончились патроны — за лом
                here = tile_of(p)
                t = min(left, key=lambda e: (not c.can_attack(p, e)[0], chebyshev(here, tile_of(e)), e.hp))
                c.target = t
                if (getattr(t, "robot", False) and g.inventory.has("импульсная граната") and p.ap >= c.THROW_AP
                        and 2 <= chebyshev(here, tile_of(t)) <= c.THROW_RANGE and c.los(p, t)):
                    c.player_throw()                  # ЭМИ в робота — как сделал бы игрок
                    self.fr(1)
                    continue
                close_in = (c.can_attack(p, t)[0] and c.hit_chance(p, t) < 45 and chebyshev(here, tile_of(t)) > 2
                            and p.ap >= c.attack_cost(p) + 1)
                if close_in:                      # мажу издалека — подойду ближе, как сделал бы игрок
                    step = c._path_next_step(p, t)
                    if step:
                        before = tile_of(p)
                        c.player_step(*step)
                        if tile_of(p) != before:
                            self.fr(1)
                            continue
                if c.can_attack(p, t)[0] and p.ap >= c.attack_cost(p):
                    part = 0                      # в оптику — если броня и шанс приличный
                    if "eyes" in t.weak_parts and t.armor and c.hit_chance(p, t, 2) >= 30:
                        part = 2
                    c.player_attack(part)
                elif p.ap >= 1 and not c.can_attack(p, t)[0]:
                    step = c._path_next_step(p, t)
                    if step:
                        before = tile_of(p)
                        c.player_step(*step)
                        if tile_of(p) == before:
                            c.end_turn()
                    else:
                        c.end_turn()
                else:
                    c.end_turn()
            low = min(low, g.player.hp)
            self.fr(1)
        if low < g.player.hp_cap * 0.25:
            self.stats["close_calls"] += 1
        one = sum(1 for e in foes if not e.alive and hp_foes[id(e)] == e.max_hp and getattr(e, "_hits_taken", 1) <= 1)
        self.stats["kills"] += sum(1 for e in foes if not e.alive)
        self.critic.on_fight(c.round - rounds0 + 1, len(foes), max(0, hp0 - low), g.player.hp_cap, one)
        self.check_alive("бой")
        self.heal_if_needed(0.5)
        self.cure_rads()
        self.rest()
        self.loot_bodies()
        self.gear_up()

    def rest(self, target=0.9, max_s=240):
        """Отдохнуть вне боя: раны затягиваются сами (как игрок, который постоял в укрытии)."""
        g = self.g
        p = g.player
        t = 0
        while p.alive and p.hp < p.hp_cap * target and t < max_s * 1000 and not g.combat.active:
            g.update(250)
            t += 250
            if g.combat.active:
                self.fight()
                return
        self.stats["rest_s"] = self.stats.get("rest_s", 0) + t // 1000

    def loot_bodies(self):
        g = self.g
        for box in list(g.level.containers):
            if box["name"].startswith("тело") and not box["opened"]:
                try:
                    self.stand_near(box["tiles"])
                except Stuck:
                    continue
                g.handle_key(pygame.K_e)
                self.fr(1)

    def clear(self, max_rounds=12, radius=None):
        """Перебить всех враждебных в локации: подойти к ближнему (свободная клетка кольцом вокруг него),
        начать бой, добить. Недосягаемых (за стеной, в воде) — пропустить. max_rounds — сколько заходов без
        продвижения терпеть."""
        g = self.g
        skip = set()
        stall = 0
        for _ in range(400):
            if g.combat.active:
                self.fight()
            left = [e for e in g.enemies if e.alive and e.hostile and id(e) not in skip]
            if not left:
                return
            e = min(left, key=lambda e: chebyshev(tile_of(g.player), tile_of(e)))
            hp0 = sum(x.hp for x in left)
            tx, ty = tile_of(e)
            ring = [(tx + dx, ty + dy) for r in (3, 2, 1, 4, 5, 6, 7, 8) for dx in range(-r, r + 1) for dy in range(-r, r + 1)
                    if max(abs(dx), abs(dy)) == r]
            free = [c for c in ring if not g.level.is_wall(*c) and not g.level.is_exit(*c)
                    and c not in getattr(g.level, "blocked", ())]
            spot = None
            for c in free:                       # встать туда, откуда цель видна
                g.player.rect.topleft = rect_pos_for_tile(g.player, c)
                if g.combat.los(g.player, e):
                    spot = c
                    break
            if spot is None and free:            # не видно ниоткуда — подойти вплотную (в дверь)
                spot = min(free, key=lambda c: chebyshev(c, (tx, ty)))
                g.player.rect.topleft = rect_pos_for_tile(g.player, spot)
            if spot is None:
                skip.add(id(e))
                continue
            g.snap_camera()
            self.fr(2)
            if not g.combat.active:
                g.combat.start(player_first=True)
            self.fight()
            now = sum(x.hp for x in left if x.alive)
            if e.alive and now >= hp0:
                stall += 1
                if stall >= 6:
                    skip.add(id(e))
                    stall = 0
            else:
                stall = 0

    def check_alive(self, where):
        g = self.g
        if not g.player.alive or g.game_over:
            self.stats["deaths"] += 1
            raise Stuck(f"герой погиб ({where})")

    # ------------------------------------------------------------ торговля
    KEEP_MISC = ("отмычка", "лопата")

    def junk(self):
        """Что продать: ценный хлам, лишние стволы, броня хуже надетой. Сюжетное (цена 0) не трогаем."""
        g = self.g
        inv = g.inventory
        best = WEAPONS.get(g.player.weapon, {}).get("item")
        guns = sorted((k for k, w in WEAPONS.items() if w.get("item") and inv.has(w["item"])),
                      key=lambda k: -self.weapon_score(k, check_ammo=False))
        keep_guns = {WEAPONS[k]["item"] for k in guns[:2]} | {best}       # то, чем владею лучше всего
        keep_guns |= {w["item"] for w in WEAPONS.values() if w.get("unique") and w.get("item")}   # легенды — на потом
        out = []
        for name, have in inv.nonzero().items():
            cat = ITEMS.category(name)
            price = ITEMS.price(name)
            if price <= 0 or name == "крышки":
                continue
            if cat == "misc" and name not in self.KEEP_MISC and "use" not in ITEMS.ITEMS[name]:
                out.append((name, have))
            elif cat == "weapon" and ITEMS.ITEMS[name].get("ap") is None and name not in keep_guns \
                    and name not in ("граната", "коктейль Молотова"):
                out.append((name, have))
            elif cat == "armor" and name not in g.player.equipment.values():
                out.append((name, have))
            elif cat == "resource" and have > 4:
                out.append((name, have - 4))
        return out

    def buy_upgrades(self):
        """Ствол лучше нынешнего (и патроны к нему продаются) или броня, которую можно надеть, — если по карману."""
        g = self.g
        tr = g.traders[g.trade["id"]]
        mine = max((self.weapon_score(k, check_ammo=False) for k, w in WEAPONS.items()
                    if not w.get("item") or g.inventory.has(w["item"])), default=0)
        for name, qty, price, have in g.trade_rows():
            wid = next((k for k, w in WEAPONS.items() if w.get("item") == name), None)
            if wid and not WEAPONS[wid].get("thrown"):
                ammo = WEAPONS[wid].get("ammo")
                ammo_ok = not ammo or g.inventory.count(ammo) >= 20 or tr["stock"].get(ammo, 0) >= 20
                if ammo_ok and self.weapon_score(wid, check_ammo=False) > mine * 1.25 \
                        and g.inventory.count("крышки") - price >= 60:
                    g._buy(name, qty, price)
                    self.stats["bought"] = self.stats.get("bought", []) + [name]
                    mine = self.weapon_score(wid, check_ammo=False)
            slot = ITEMS.slot(name)
            if slot and not g.wear_block(name):
                worn = g.player.equipped(slot)
                cur = ITEMS.ITEMS[worn].get("armor_ac", 0) if worn else 0
                if ITEMS.ITEMS[name].get("armor_ac", 0) > cur + 4 and g.inventory.count("крышки") - price >= 60:
                    g._buy(name, qty, price)
                    self.stats["bought"] = self.stats.get("bought", []) + [name]
        self.gear_up()
        self.best_weapon()

    def read_books(self):
        g = self.g
        for name in list(g.inventory.nonzero()):    # письма, жетоны, голозаписи — игрок их читает
            doc = ITEMS.ITEMS.get(name, {}).get("read")
            if doc and name not in self.read_docs and not g.combat.active:
                self.read_docs.add(name)
                g.open_document(doc)
                g.close_terminal()
        for name in list(g.inventory.nonzero()):
            if "skill" in ITEMS.ITEMS.get(name, {}).get("use", {}) and not g.combat.active:
                g.use_item(name)
                self.stats["books"] = self.stats.get("books", []) + [name]

    IMPLANTS = (("anna_shaw", "сердце", 1200), ("anna_shaw", "Миомеры", 1000), ("ghoul_healer", "сетка", 1500),
                ("nv_doctor", "ускоритель", 2500))

    def buy_implants(self):
        """Лишние деньги — хирургу (как игрок, у которого к концу игры копятся крышки)."""
        g = self.g
        for npc, part, price in self.IMPLANTS:
            if g.inventory.count("крышки") < price + 300 or not any(n.npc_id == npc for n in g.npcs):
                continue
            try:
                self.talk(npc)
                for p_ in ("операции", part):
                    if not self.say(p_, required=False):
                        break
                self.end_talk()
                self.stats["implants"] = self.stats.get("implants", []) + [part]
            except Stuck:
                pass

    def gear_up(self):
        g = self.g
        self.read_books()
        best = {}
        for name in g.inventory.nonzero():
            slot = ITEMS.slot(name)
            if slot and not g.wear_block(name):
                ac = ITEMS.ITEMS[name].get("armor_ac", 0)
                if ac > best.get(slot, ("", -1))[1]:
                    best[slot] = (name, ac)
        for slot, (name, _) in best.items():
            if g.player.equipped(slot) != name:
                g.equip(name)

    def cure_rads(self):
        g = self.g
        p = g.player
        while p.rads >= 100 and (g.inventory.has("антирадин") or g.inventory.has("вода Зайзикса")):
            g.use_item("вода Зайзикса" if g.inventory.has("вода Зайзикса") else "антирадин")
            self.fr(1)

    def shop(self, trader_id):
        """Продать хлам, купить патроны под свои стволы, лечение и антирадин (оставив запас крышек)."""
        g = self.g
        self.gear_up()
        g.open_trade(trader_id)
        if not g.trade:
            return
        g.trade["tab"] = "sell"
        sold = 0
        for name, n in self.junk():
            for _ in range(n):
                rows = {r[0]: r for r in g.trade_rows()}
                if name not in rows:
                    break
                cash = g.inventory.count("крышки")
                g._sell(*rows[name][:3])
                if g.inventory.count("крышки") == cash:
                    break
                sold += g.inventory.count("крышки") - cash
        self.stats["sold"] = self.stats.get("sold", 0) + sold
        g.trade["tab"] = "buy"
        self.buy_upgrades()
        want = sorted({w["ammo"] for w in WEAPONS.values()
                       if w.get("ammo") and w.get("item") and g.inventory.has(w["item"])})
        heals = sum(g.inventory.count(h) for h in HEALS)
        if heals < 12:                                # запас как у разумного игрока, не аптечный склад
            want += ["стимулятор", "бинт", "аптечка армейская"]
        if g.inventory.count("импульсная граната") < 2:
            want.append("импульсная граната")
        want += ["изолента", "пружина", "отмычка"]   # на ремонт: антенна REPCONN, самоделки; отмычки — путь Тени
        mine = {sid for sid, _ in self.build}
        want += [n for n, d in ITEMS.ITEMS.items() if d.get("use", {}).get("skill") in mine]
        want.insert(0, "антирадин")           # пара антирадинов всегда с собой
        def enough(name):
            if name in HEALS:
                return sum(g.inventory.count(h) for h in HEALS) >= 12
            if ITEMS.category(name) == "ammo":
                return g.inventory.count(name) >= 150
            if name in ("изолента", "пружина"):
                return g.inventory.count(name) >= 3
            if name == "отмычка":
                return g.inventory.count(name) >= 2
            if "skill" in ITEMS.ITEMS.get(name, {}).get("use", {}):
                return g.inventory.count("крышки") < 900      # книга — когда деньги есть с запасом
            return g.inventory.count(name) >= 2
        for _ in range(60):
            rows = g.trade_rows()
            bought = False
            for i, (name, qty, price, have) in enumerate(rows):
                if name in want and not enough(name) and g.inventory.count("крышки") - price >= 40:
                    g._buy(name, qty, price)
                    bought = True
                    break
            if not bought:
                break
        g.trade = None

    # ------------------------------------------------------------ отчёт
    def checkpoint(self, name):
        g = self.g
        p = g.player
        inv = g.inventory
        heals = sum(inv.count(h) for h in HEALS)
        row = (f"{name:<38} ур.{p.level_sys.level:>2} ({p.level_sys.total_xp if hasattr(p.level_sys, 'total_xp') else p.level_sys.xp:>5})  HP {p.hp:>3}/{p.hp_cap:<3} крышки {inv.count('крышки'):>4}  "
               f"патроны {inv.count('патроны'):>3}  лечение {heals:>2}  оружие {p.weapon:<10} боёв {self.stats['fights']:>3}  "
               f"на волоске {self.stats['close_calls']}  рад {p.rads}")
        self.rows.append(row)
        print(row, flush=True)
        self.critic.on_checkpoint(name)

    def step(self, name, fn):
        try:
            fn()
        except Stuck as ex:
            self.problems.append(f"{name}: {ex}")
            print(f"!! {name}: {ex}", flush=True)
            if not self.g.player.alive or self.g.game_over:
                self.checkpoint(name + " — СМЕРТЬ")
                raise Dead()
        self.checkpoint(name)
        return True


# ================================================================ маршруты
def act1(b):
    g = b.g
    b.go("ruins")

    def house():
        eye = next(p for p in g.level.pickups if p["kind"] == "чей-то глаз")
        g.player.rect.topleft = rect_pos_for_tile(g.player, (eye["rect"].x // 48, eye["rect"].y // 48))
        b.fr(2)
        g.handle_key(pygame.K_e)
        b.terminal("grandpa", "ПОСЛЕДНЯЯ ЗАПИСЬ")
        b.talk("gena")
        b.say("Анкоридж")
        b.end_talk()
        b.loot_area()
    b.step("Пятнадцатая: дом деда, Гена", house)

    def sides_take():
        if not b.sides:
            return
        b.pursue("gena", "know_pw_grandpa", required=False)        # пароль деда — у Гены
        b.terminal("grandpa", "ЛИЧНОЕ")
        if g.flags.get("safe_code"):
            b.take_from("сейф деда")
        for npc, q in (("gena", "sq_scrap"), ("turtle", "sq_turtle"), ("gena", "sq_gang"), ("blondie", "sq_lira")):
            b.pursue(npc, "quest:" + q, required=False)
        b.pursue("blondie", "quest:sq_lira", required=False)
    b.step("Пятнадцатая: взять побочки", sides_take)

    def punk():
        b.talk("loner")
        b.say("Ты был в Бензо-банде")
        b.say("Куда его увезли")
        b.say("Договорились")
        b.end_talk()
    b.step("Пятнадцатая: Панк-одиночка", punk)

    def rats():
        b.talk("sheriff")
        b.say("Мне нужно оружие")
        b.say("Берусь")
        b.end_talk()
        b.talk("doc")                      # умный игрок сначала спросит Дока — отравленная приманка
        b.say("Крысолюды в ливнёвке", required=False)
        b.end_talk()
        b.goto_portal("drain")
        if g.inventory.has("отравленная приманка"):
            box = next((c for c in g.level.containers if c["name"].startswith("кормушка")), None)
            if box:
                b.stand_near(box["tiles"])
                g.open_container(box)
                g.loot_put("отравленная приманка")
                g.loot = None
                b.fr(2)
        b.clear(max_rounds=20)
        b.loot_area()
        b.goto_portal("ruins")
        b.talk("sheriff")
        b.say("Спасибо, шериф")
        b.end_talk()
        b.best_weapon()
    b.step("Пятнадцатая: крысолюды в ливнёвке", rats)

    def kolbasa():
        grave = next(c for c in g.level.containers if c["name"] == "могила «Колбаса»")
        b.stand_near(grave["tiles"])
        g.open_container(grave)
        g.loot = None
        b.pickup("лопата")
        b.take_from("могила «Колбаса»")
    b.step("Пятнадцатая: могила Колбасы", kolbasa)

    def vault():
        b.talk("ada")
        for part in ("Расскажите про Убежище 57", "Что на нижнем ярусе", "Ясно", "Мне нужна ключ-карта", "На жетоне деда"):
            b.say(part, required=False)
        b.end_talk()
        b.goto_portal("vault57")
        gate = g.level.gates[0]
        b.stand_near(gate["tiles"])
        g.handle_key(pygame.K_e)
        b.fr(2)
        b.clear(max_rounds=20)
        b.terminal("vault_lab", "Результаты")
        b.terminal("vault_overseer", "Последняя запись")
        b.take_from("шкаф с журналами")
        b.take_from("холодильник с сывороткой")
        b.loot_area()
        b.goto_portal("ruins")
        b.talk("turtle")
        b.say("Вот сыворотка", required=False)
        b.end_talk()
        b.talk("gena")
        b.say("Вот журналы", required=False)
        b.end_talk()
        b.talk("ada")
        b.say("Я был в ярусе Б", required=False)
        b.say("Он не бросил вас", required=False)
        b.end_talk()
    b.step("Убежище 57: нижний ярус", vault)

    def water():
        b.talk("doc")
        b.say("Проповедник раздаёт воду", required=False)
        b.say("Принесу", required=False)
        b.end_talk()
        b.talk("silas")
        b.say("Дай пробу", required=False)
        b.end_talk()
        b.talk("doc")
        b.say("Вот проба", required=False)
        b.end_talk()
        b.talk("mo")
        b.say("Лен тебе должен", required=False)
        b.say("Выбью", required=False)
        b.end_talk()
        b.talk("lenny")
        b.say("Мо говорит", required=False)
        b.say("заплачу", required=False)
        b.end_talk()
    b.step("Пятнадцатая: святая вода, долг Лена", water)

    def station():
        b.go("station")
        g.dialogue.active_node = None
        for e in g.enemies:
            e.talked = True
        b.search("тайник Панка")
        b.clear()
        b.loot_bodies()
        b.loot_area()
    b.step("Заправка: тайник Панка и Шрам", station)

    def back():
        b.go("ruins")
        b.talk("loner")
        b.say("Вот твоя доля")
        b.say("Скоро")
        b.talk("loner")
        b.say("Веди в Бейкер")
        b.end_talk()
        for t in ("gena", "doc", "mo"):
            if any(n.npc_id == t for n in g.npcs) and t in g.traders:
                b.shop(t)
    b.step("Пятнадцатая: доля Панка, закупка", back)

    def sides_done():
        if not b.sides:
            return
        b.go("ruins")
        b.terminal("pump", "Состояние контуров", "[Перекрыть контур Б]")     # мёртвая вода
        b.clear(max_rounds=12)                                               # рейдеры у пса
        for npc, q in (("dog", "sq_dog"), ("gena", "sq_scrap"), ("turtle", "sq_turtle"), ("gena", "sq_water"),
                       ("gena", "sq_gang"), ("silas", "sq_holywater"), ("blondie", "sq_lira")):
            b.pursue(npc, "quest:" + q, required=False)    # банду Гена даёт после лома
            g.sync_story()
        if g.flags.get("q_gang_taken") and not any(g.flags.get(k) for k in ("gang_dead", "gang_left", "gang_paid")):
            b.go("station")                                 # к Шраму: уговорить уйти, откупиться — драка последней
            if not (b.parley("boss", "gang_left") or b.parley("boss", "gang_paid")):
                g.make_hostile("gang")
                b.clear()
            b.go("ruins")
            b.pursue("gena", "quest:sq_gang", required=False)
    b.step("Пятнадцатая: сдать побочки", sides_done)

    def baker():
        g.go_world_map()
        b.go("baker")
        b.go("baker_mission")
        if b.sides:
            b.walk_to_map("baker")
            b.pursue("roy", "записка Роя", required=False)
            b.walk_to_map("baker_mission")
        b.talk("loner_baker")
        b.say("Скажу")
        b.end_talk()
        g.player.rect.topleft = rect_pos_for_tile(g.player, (57, 14))
        b.fr(2)
        if g.combat.active:
            b.fight()
        b.talk("iskra")
        b.say("Мне нужен ключ")
        b.say("Спасибо")
        b.say("Он ждёт тебя")
        b.end_talk()
        b.fr(2)
        b.open_gate("cells_open")
        b.talk("amos")
        b.say("Иди")
        b.end_talk()
        b.fr(2)
        if b.sides:
            if g.inventory.has("записка Роя"):
                b.talk("marla")
                b.say("записка", required=False)
                b.say("Иди к нему", required=False)
                b.end_talk()
                b.fr(2)
            b.walk_to_map("baker")
            b.pursue("roy", "quest:sq_roy", required=False)
    b.step("Бейкер: Тень — Искра, ключ, дед", baker)

    def b7():
        b.go("baker")
        b.go("baker_outskirts")
        b.talk("amos_b7")
        b.say("Открывай")
        b.say("Идём вниз")
        b.end_talk()
        b.fr(4)
        b.goto_portal("baker7")
        b.clear()
        b.loot_area()
        b.terminal("baker7_log", "Журнал", "Подняться")
        b.fr(3)
    b.step("«Бейкер-7»: склад и роботы", b7)


def act1b(b):
    """Зайзикс и Нидлс — хвост первого акта, дорога к Хабу."""
    g = b.g

    def zzyzx():
        g.go_world_map()
        b.go("barstow")                    # по дороге — Барстоу: Роза, караванщица
        b.shop_here()
        if b.sides:
            b.pursue("rose", "quest:sq_barstow", required=False)
            for m in ("barstow_depot", "barstow_center", "barstow_depot"):
                if not g.flags.get(m + "_cleared"):
                    b.visit(m)
            b.walk_to_map("barstow")
            b.pursue("rose", "quest:sq_barstow", required=False)
        b.go("zzyzx")
        b.goto_portal("zzyzx_bath")
        b.pursue("nurse_ava", "ava_asked")
        b.goto_portal("zzyzx")
        b.pursue("gus", "ключ от насосной")
        b.goto_portal("zzyzx_bath")
        b.goto_portal("zzyzx_cistern")
        b.clear()
        b.loot_area()
        b.terminal("zz_cistern", "Описание узла", "[Отключить ступень 2]")
        b.goto_portal("zzyzx_bath")
        b.goto_portal("zzyzx")
        b.pursue("springer", "springer_confessed", required=False)
        if b.sides:
            b.take_item("zzyzx_hotel", "обрывок карты (север)")
            b.walk_to_map("zzyzx")
        for t in ("abdul",):
            if any(n.npc_id == t for n in g.npcs) and t in g.traders:
                b.shop(t)
    b.step("Зайзикс: «Чистый лист»", zzyzx)

    def needles():
        g.go_world_map()
        b.go("needles")
        b.pursue("barkeep_ned", "know_barge", required=False)
        b.pursue("kate", "know_barge", required=False)
        if b.sides:
            b.pursue("drunk_vic", "обрывок карты (центр)", required=False)
            b.pursue("kate", "багор Мамаши Кейт", required=False)       # переправа: пёс, курица, кукуруза
            b.gear_up()
        b.goto_portal("needles_bridge")
        b.terminal("needles_toll", "Особые грузы")
        if not g.flags.get("know_cult_convoys"):
            raise Stuck("журнал пошлин не прочитан")
    b.step("Нидлс: журнал пошлин", needles)

    def radio():
        if not b.sides:
            return
        g.reveal_location("spot_radio")       # вышку видно с трассы
        g.go_world_map()
        b.go("spot_radio")
        b.clear()
        b.take_from("ящик радиста")
        b.read_books()
        b.pursue("radio_bot", "radio_done", required=False)
    b.step("Радиовышка: позывной в эфире", radio)


def act2(b):
    """Акт II «Караванные пути»: гонка за ветеранами Списка."""
    g = b.g

    def hub():
        g.go_world_map()
        b.go("hub")
        b.shop_here()
        b.pursue("dolores", "dolores_trust", required=False)
        b.pursue("dolores", "dolores_tunnels", required=False)
        b.pursue("crimson_boss", "know_cult_water", required=False)
        b.visit("hub_tunnels")
        b.terminal("hub_sluice", "Положение затворов", "[Открыть затвор 1 полностью]")
        b.terminal("hub_water_ledger", "[Личное]")
        b.walk_to_map("hub")
        b.shop_here()
        if b.sides:
            b.pursue("hub_kid", "runaway_job", required=False)
            b.pursue("crimson_boss", "runaway_done", required=False)
    b.step("Хаб: шлюз и Долорес Вега", hub)

    def junktown():
        g.go_world_map()
        b.go("junktown")
        b.shop_here()
        b.pursue("anna_shaw", "anna_trust", required=False)
        b.pursue("anna_shaw", "know_rourke", required=False)
        b.terminal("anna_archive", "Список Марипозы")
        b.pursue("gizmo", "know_gizmo_cult", required=False)
        b.pursue("hunter_rourke", "know_rourke_cult", required=False)
        if not b.pursue("hunter_rourke", "rourke_paid", required=False):
            if b.steal("junktown_casino", "сейф Гизмо"):      # книга долгов Гизмо — мэру
                b.pursue("mayor_darkwater", "rourke_paid", required=False)
        if g.inventory.has("расписка Анны Шоу"):
            b.pursue("anna_shaw", "anna_debt_cleared", required=False)
        b.fetch("junktown_cellar", "холодильный шкаф")
        b.walk_to_map("junktown")
        b.shop_here()
        if b.sides:
            b.pursue("scrapper", "truck_job", required=False)
            b.take_item("junktown_dump", "обрывок карты (юг)")
    b.step("Джанктаун: Анна Шоу и Рурк", junktown)

    def necropolis():
        g.go_world_map()
        b.go("necropolis")
        b.shop_here()
        b.pursue("lorraine", "know_set_deal", required=False)
        b.pursue("harry_mech", "v12_way", required=False)
        b.fetch("vault12", "ящик запчастей водоочистки")
        if b.sides:
            b.take_from("шкафчик жильца")
            b.read_books()                                   # стишок Хадсона: 2 → 4 → 1 → 3
            b.terminal("v12_valves", "Схема", "вентиль 2", "вентиль 4", "вентиль 1", "вентиль 3")
            b.take_from("шкаф Хадсона")
            b.gear_up()
        b.pursue("harry_mech", "watershed_fixed", required=False)
        b.pursue("set", "set_refuses", required=False)
        b.pursue("cobbs", "cobbs_clear")
        if b.sides:
            b.pursue("gravedigger", "tag_job", required=False)
            b.walk_to_map("necropolis")
            b.take_from("разрытая могила")
        b.walk_to_map("necropolis")
        b.shop_here()
    b.step("Некрополь: Водораздел, Сет, Коббс", necropolis)

    def aradesh():
        g.go_world_map()
        b.go("aradesh")
        b.shop_here()
        b.pursue("aradesh", "aradesh_job", required=False)
        b.visit("aradesh_cave")
        b.pursue("aradesh", "aradesh_free_water", required=False)
        b.pursue("aradesh", "know_vault15", required=False)
        b.visit("aradesh_canyon")
        b.terminal("convoy_wreck", "Груз", "Последняя запись")
        b.walk_to_map("aradesh")
        b.shop_here()
    b.step("Лагерь Арадеша: пещера и фургон", aradesh)

    def boneyard():
        g.go_world_map()
        b.go("boneyard")
        b.shop_here()
        b.pursue("adytum_mayor", "adytum_job", required=False)
        if b.sides:
            b.pursue("sphinx", "sphinx_done", required=False)
            b.take_from("витрина музея")
            b.gear_up()
        b.pursue("blade_nika", "blades_job", required=False)
        b.pursue("morpheus", "know_morpheus_deal", required=False)
        b.visit("boneyard_vt")
        b.terminal("vt_server", "[Поставки «ВРЭ / разв.»]")
        b.pursue("cooper", "cooper_card", required=False)
        if b.steal("boneyard_cathedral", "сундук на складе"):
            b.pursue("adytum_mayor", "adytum_truce", required=False)
        if b.sides:
            b.pursue("cooper", "tag_done", required=False)
        b.walk_to_map("boneyard")
        b.shop_here()
    b.step("Боунъярд: серверная Vault-Tec", boneyard)

    def vault15():
        g.go_world_map()
        b.go("vault15")
        b.pursue("captive_mira", "know_mira", required=False)
        b.pursue("jackal_boss", "mira_free", required=False)
        b.pursue("beatrice", "beatrice_trust", required=False)
        b.pursue("beatrice", "v15_lower_ok", required=False)
        b.visit("vault15_lower")
        b.terminal("v15_generator", "Состояние", "[Заменить предохранитель F-3 и запустить]")
        b.terminal("v15_mainframe", "Сеть убежищ округа")
    b.step("Убежище 15: Мира и генератор", vault15)

    def vault4():
        g.go_world_map()
        b.go("vault4")
        b.terminal("v4_intercom", "[Приложить ключ-карту директора]", "[Представиться курьером брата Т.]",
                   "[Рассказать про погоду]")
        try:
            b.take_from("ящик с печатью круга")
        except Stuck:
            pass
        b.pursue("overseer_sim", "know_v4_science", required=False)
        b.pursue("overseer_sim", "v4_deal_off", required=False)
    b.step("Убежище 4: Сим и сделка", vault4)


def act3(b):
    """Акт III «Мохаве»: шесть городов, «Ноль» под Вегасом, финал в Марипозе."""
    g = b.g

    def city(cid):
        g.go_world_map()
        b.go(cid)
        b.shop_here()

    def primm():
        city("primm")
        b.pursue("deputy_baxter", "primm_job", required=False)
        b.pursue("mae_reeves", "know_tobi_missing", required=False)
        b.terminal("reeves_archive", "Марипоза, «Ноль»", "Письмо 2077 года")
        if b.sides and g.inventory.has("карта клада"):
            b.read_books()
            b.walk_to_map("primm")
            b.take_from("камень с крестом")
            b.gear_up()
        b.visit("primm_camp")
        b.pursue("tobi", "tobi_home", required=False)
        b.walk_to_map("primm")
    b.step("Примм: пропавший Тоби", primm)

    def goodsprings():
        city("goodsprings")
        b.pursue("trudy", "know_ezekiel", required=False)
        if b.sides:
            b.pursue("deputy_abby", "quest:sq_murder", required=False)
            b.take_from("тело Гаррисона")
            for npc, goal in (("luis_cards", "clue_luis"), ("beth_waitress", "clue_contra"), ("beth_waitress", "clue_beth"),
                              ("hank_miner", "clue_hank")):
                b.pursue(npc, goal, required=False)
            b.walk_to_map("goodsprings")
            b.take_from("мусорный бак за салуном")
            b.read_books()
            b.pursue("deputy_abby", "револьвер «Справедливость»", required=False)
            b.walk_to_map("goodsprings")
        b.pursue("ezekiel", "know_zero", required=False)
        b.pursue("cult_hunter", "gs_decided", required=False)
        if b.sides:
            b.visit("goodsprings_cave")
            b.take_from("тайник старателей")
    b.step("Гудспрингс: Иезекииль", goodsprings)

    def vault22():
        city("vault22")
        b.pursue("hugo_lee", "hugo_known", required=False)
        b.pursue("overseer_keene", "v22_lab_ok", required=False)
        b.visit("vault22_lab")
        b.terminal("v22_lab", "Журнал Б-12")
        b.pursue("hugo_lee", "hugo_joins", required=False)
        b.pursue("overseer_keene", "v22_decided", required=False)
    b.step("Убежище 22: споры и Хьюго", vault22)

    def nipton():
        city("nipton")
        b.pursue("mayor_carroll", "know_grace", required=False)
        b.terminal("nipton_ledger", "Проигравшие")
        b.visit("nipton_mine")
        b.pursue("brother_t", "know_cult_race", required=False)
        b.pursue("brother_t", "brother_t_flees", required=False)
        b.steal("nipton_hall", "сейф мэра")               # список жребия: имена вписаны заранее
        b.walk_to_map("nipton")
        b.pursue("mayor_carroll", "nipton_decided", required=False, avoid=("take",))
    b.step("Ниптон: жребий и брат Т.", nipton)

    def searchlight():
        city("searchlight")
        b.pursue("fire_chief_hope", "fort_job", required=False)
        b.pursue("foreman_gus", "ключ от штрека", required=False)
        b.visit("searchlight_mine")
        b.visit("fort_bunker")
        b.terminal("fort_comm", "Журнал канала")
        b.terminal("general_core", "[Приказ: распустить призыв]")
        if g.flags.get("recruits_free"):
            b.take_from("армейский ящик")
            if g.inventory.has("голозапись «Курс оператора СБ»"):
                g.item_action("голозапись «Курс оператора СБ»")[1]()
                g.close_terminal()
            b.gear_up()
        b.loot_area()
    b.step("Сёрчлайт: Форт и Генерал", searchlight)

    def vegas():
        city("vegas_strip")
        b.pursue("judge_sol", "know_crowns", required=False)
        if b.sides:
            b.pursue("boots_rider", "bike_job", required=False)
            b.pursue("snake_trader", "bike_done", required=False)
        b.terminal("agatha_salon", "[Зашифрованное]")      # тайна Ладоней: Агата — из Ордена
        b.pursue("mother_agatha", "palms_codes", required=False)
        if not g.flags.get("palms_codes") and b.steal("vegas_boots", "ящик с книгами"):   # книги Ладоней — Агате
            b.pursue("mother_agatha", "palms_codes", required=False)
        b.terminal("snakes_ledger", "[Отдельный список]")   # тайна Змей: продают «лишних» белым
        b.pursue("mother_snake", "snakes_passage", required=False)
        b.terminal("boots_power", "[Дать ток в башню Vault-Tec]", "[Перебросить линию самому]")
        b.visit("vegas_tunnels")                    # «Мамочка» поёт колыбельные
        b.visit("vegas_tower")
        b.terminal("tower_archive", "Хранилище «Ноль»")
        b.visit("vegas_zero")
        b.terminal("zero_door", "[Ввести коды совета]", "[Сетчатка ветерана]", "[Голос ветерана]", "[Код шерифа Ривза]")
        b.fr(3)
        if not g.flags.get("zero_open"):
            raise Stuck("дверь «Ноля» не открылась: " + ", ".join(
                k for k in ("zero_power", "zero_codes", "zero_retina", "zero_voice", "zero_code") if not g.flags.get(k)) + " — нет")
        b.visit("vegas_vault")
        b.pursue("cooper_zero", "zero_fate", required=False)
        b.terminal("zero_vault", "[Уничтожить — стерилизация]", "[Опечатать для Братства Стали]", "[Передать Анклаву]")
    b.step("Вегас: «Ноль»", vegas)



def secrets(b):
    """Тайные места: ложа Ордена, «Посейдон-7», Каталина, «Нова», REPCONN и «Арес» — и легенды в них."""
    g = b.g

    def city(cid):
        g.go_world_map()
        b.go(cid)
        b.shop_here()

    def errands():
        if not b.sides or not g.inventory.has("динамит") or g.flags.get("truck_done"):
            return
        g.go_world_map()
        b.go("junktown")
        b.pursue("scrapper", "truck_done", required=False)
    b.step("Джанктаун: динамит для грузовика", errands)

    def order():
        g.go_world_map()
        b.go("ruins")                                # Мо из Пятнадцатой — связной Ордена
        b.pursue("mo", "знак Ордена Тайн", required=False)
        g.go_world_map()
        b.go("barstow")
        b.visit("barstow_order")
        b.terminal("order", "Приветствие", "Три испытания", "[Испытание I", "[Испытание II", "[Испытание III",
                   "[Принять знак ложи]", "Хозяйка ложи")
    b.step("Ложа Ордена Тайн", order)

    def poseidon():
        city("poseidon7")
        b.pursue("enclave_gate", "p7_invited", required=False)
        b.visit("poseidon7_base", clear=False)
        b.terminal("p7_comm", "Сводка разведки", "Директива с платформы", "[Отправить ложный отчёт на платформу]")
        if b.steal("poseidon7_base", "сейф коменданта"):     # код винтокрыла открывает и стойку силовой брони
            b.visit("poseidon7_hangar", clear=False)
            b.take_from("стойка силовой брони")
            b.read_books()
            b.gear_up()
        b.pursue("darnell", "darnell_home", required=False)
    b.step("«Посейдон-7»: станция Анклава", poseidon)

    def catalina():
        city("catalina")
        b.pursue("quarantine_nurse", "know_ct_lie", required=False)
        b.terminal("catalina_radio", "Последняя передача 2077", "Эфир Анклава")
        b.pursue("elder_mora", "ct_tribute_stop_ask", required=False)
        b.pursue("keeper_silas", "ct_signal_ready", required=False)
        b.terminal("catalina_radio", "[Сигнал: «вспышка чумы")
        b.visit("catalina_cove")
        b.take_from("затопленный ящик ВМФ")
    b.step("Каталина: дань «флоту» и грот", catalina)

    def nova():
        city("nova")
        b.pursue("raven_hacker", "nova_rebels_ally", required=False)
        b.visit("nova_core")
        b.take_from("ящик инженера Оками")
        b.terminal("nova_core", "[Червь Рэйвен")
    b.step("«Нова»: ядро и «Звездочёт»", nova)

    def ares():
        city("repconn")
        b.pursue("repconn_ghoul", "antenna_up", required=False)
        b.terminal("repconn_launch", "Заправить", "сигнал", "Подготовить")
        b.visit("ares_hab")
        b.pursue("cmdr_hale", "know_ares_vre", required=False)
        b.visit("ares_lab")
        b.take_from("стенд прототипа «Арес»")
        b.terminal("ares_project", "Стерилизовать")
        b.pursue("cmdr_hale", "ares_decided", required=False)
    b.step("REPCONN и «Арес»: винтовка Гаусса", ares)


def final(b):
    g = b.g

    def mariposa():
        g.go_world_map()
        b.go("mariposa")
        b.shop_here()
        b.clear(max_rounds=25)
        b.visit("mariposa_lab")
        b.pursue("tobi_mp", "tobi_home", required=False)
        b.pursue("brother_t_mp", "mariposa_code", required=False)
        b.visit("mariposa_vats")
        b.terminal("mariposa_core", "[Код от Тобиаса", "[Ввести код взвода охраны]",
                   "[«Пепел»", "[«Сталь»", "[«Чужие руки»")
        b.fr(5)
        if not g.flags.get("game_ending"):
            raise Stuck("концовка не наступила")
    b.step("Марипоза: финал", mariposa)


ACTS = {"act1": act1, "act1b": act1b, "act2": act2, "act3": act3, "secrets": secrets, "final": final}


def main():
    args = sys.argv[1:]
    opts = {"--seed": "7", "--build": "guns"}
    for k in list(opts):
        if k in args:
            i = args.index(k)
            opts[k] = args[i + 1]
            del args[i:i + 2]
    sides = "--nosides" not in args
    args = [a for a in args if a != "--nosides"]
    which = args or list(ACTS)
    b = Bot(seed=int(opts["--seed"]), sides=sides, build=opts["--build"])
    print(f"бот: сборка {opts['--build']}, бросок {opts['--seed']}, {'с побочками' if sides else 'только сюжет'}")
    for name in which:
        print(f"\n===== {name} =====", flush=True)
        try:
            ACTS[name](b)
        except Dead:
            pass
        if not b.g.player.alive:
            break
    print("\n===== СВОДКА =====")
    for r in b.rows:
        print(r)
    print(f"\nбоёв {b.stats['fights']}, убито {b.stats['kills']}, на волоске {b.stats['close_calls']}, "
          f"лечилок съедено {b.stats['heals_used']}, смертей {b.stats['deaths']}, {time.time() - b.t0:.0f} с")
    print(f"продал на {b.stats.get('sold', 0)} крышек")
    print("купил:", ", ".join(b.stats.get("bought", [])) or "ничего")
    print("прочитал:", ", ".join(b.stats.get("books", [])) or "ничего")
    print("импланты:", ", ".join(b.stats.get("implants", [])) or "нет")
    import json
    Q = {k: v for k, v in json.load(open("data/quests.json", encoding="utf-8")).items() if not k.startswith("_")}
    g = b.g
    done = [k for k, v in Q.items() if g.stage(k) >= v.get("done", 100)]
    started = [k for k in Q if 0 < g.stage(k) < Q[k].get("done", 100)]
    untouched = [k for k in Q if g.stage(k) == 0]
    print(f"\nквесты: выполнено {len(done)} из {len(Q)}")
    if started:
        print("  начаты, не закончены:", ", ".join(f"{Q[k]['title']} ({g.stage(k)})" for k in started))
    if untouched:
        print("  не тронуты:", ", ".join(Q[k]["title"] for k in untouched))
    ending = [k for k in ("ending_ash", "ending_steel", "ending_hands") if g.flags.get(k)]
    print("концовка:", ending[0] if ending else "нет")
    print("\n===== ПРОБЛЕМЫ =====")
    for p in b.problems or ["нет"]:
        print(" -", p)
    print("\n===== ОТЗЫВ ПРИДИРЧИВОГО ИГРОКА =====")
    for where, text in b.critic.summary() or [("-", "Придраться не к чему. Подозрительно.")]:
        print(f" [{where}] {text}")


if __name__ == "__main__":
    main()
