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
  .venv/bin/python tools/playthrough.py lesson     — один шаг: последний урок мисс Лейн (смоук квеста)
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

# Мышь для бота: обычно курсор вне окна (−50, −50). В экшене за Дэкса бот целится и жмёт гашетку
# сам, поэтому позиция и кнопка лежат в изменяемом словаре (src/action.py читает их каждый кадр).
MOUSE = {"pos": (-50, -50), "fire": False}
pygame.mouse.get_pos = lambda: MOUSE["pos"]
pygame.mouse.get_pressed = lambda num_buttons=3: (MOUSE["fire"], False, False)
pygame.mouse.get_focused = lambda: True

from src.game import Game, saveload  # noqa: E402
from src.combat import tile_of, rect_pos_for_tile, chebyshev  # noqa: E402
from src.weapons import WEAPONS, shortfall, skill_of  # noqa: E402
from src import items as ITEMS  # noqa: E402
from src import settings as S  # noqa: E402
import bot_sides as SQ  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()


# ------------------------------------------------------------ воспроизводимость
# Игра и бот кое-где меряют время pygame.time.get_ticks(), а он идёт от реального
# времени: на быстрой машине прогон выходит другим. Для замеров баланса подменяем
# его счётчиком, который двигает каждый Game.update(dt) — «время» теперь часть
# симуляции, и одинаковый сид даёт одинаковый прогон.
class _VirtualClock:
    ms = 0


pygame.time.get_ticks = lambda: _VirtualClock.ms     # noqa: E731 — подмена модуля pygame
_update_real = Game.update


def _update_fixed(self, dt_ms):
    _VirtualClock.ms += int(dt_ms)
    return _update_real(self, dt_ms)


Game.update = _update_fixed

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


HP_EDGES = ((0, 10), (10, 25), (25, 50), (50, 75), (75, 101))


def hp_buckets(vals):
    """Сколько боёв закончилось с минимумом HP в каждом диапазоне (0-9, 10-24, ...)."""
    return [sum(1 for v in vals if a <= v < b) for a, b in HP_EDGES]


def hp_buckets_text(vals):
    names = ("0-9%", "10-24%", "25-49%", "50-74%", "75-100%")
    return ", ".join(f"{n}: {c}" for n, c in zip(names, hp_buckets(vals)) if c) or "нет данных"



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
    Stuck = Stuck

    def __init__(self, seed=7, sides=True, build="guns", noheal=False):
        random.seed(seed)
        self.sides = sides
        # noheal — контрольный прогон: герой не ест лечилки ни в бою, ни после. Нужно, чтобы
        # понять, бой опасен сам по себе или бота спасает запас лечения. Отдых вне боя остаётся.
        self.noheal = noheal
        self.build_name = build
        self.build = BUILDS[build]
        self.g = Game(intro=False)
        self.stats = {"fights": 0, "close_calls": 0, "heals_used": 0, "deaths": 0, "kills": 0,
                      "damage_taken": 0, "damage_dealt": 0, "rounds": 0,
                      "fights_no_damage": 0, "fights_long": 0, "hp_min": []}
        self.rows = []
        self.problems = []
        self.t0 = time.time()
        self.critic = Critic(self)
        self.read_docs = set()
        self.side_fails = []

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
        if g.perk_choices:      # окно повышения уровня так и не закрылось — молча стоять на портале нельзя
            raise Stuck("окно выбора не закрывается: "
                        + ", ".join(str(o.get("name")) for o in g.perk_choices)
                        + f"; непринятых навыков {g.player.pending_skills}, перков {g.player.pending_perks}")
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
        pick_idx = pick if pick is not None else 0
        g.handle_key(pygame.K_1 + pick_idx if pick_idx < 9 else pygame.K_0)   # десятый пункт — клавиша «0»

    # ------------------------------------------------------------ перемещение
    def go(self, loc_id):
        g = self.g
        if g.combat.active:
            self.fight()
        g.dialogue.close()
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
                    return True
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
            if g.term:                 # забытый терминал или ящик держат окно — порог не сработает
                g.close_terminal()
            g.loot = None
            g.dialogue.close()
            g.player.rect.topleft = rect_pos_for_tile(g.player, tuple(sorted(p["tiles"])[0]))
            self.fr(4)
            if g.loc.id == to:
                break
        if g.loc.id != to:
            busy = [k for k in ("dialogue", "perk_choices", "combat", "slides", "term", "loot", "trade", "inv_open",
                                "journal_open", "craft_open", "ctx_menu", "fishing", "menu", "game_over")
                    if (g.dialogue.is_active() if k == "dialogue" else g.combat.active if k == "combat"
                        else getattr(g, k, None))]
            raise Stuck(f"переход {g.loc.id} → {to} не сработал ({(p.get('requires') or {}).get('msg', '')}) "
                        f"[на месте: {tile_of(g.player)}, портал {sorted(p['tiles'])[0]}, открыто: {busy}, "
                        f"диалог: {g.dialogue.active_id}/{g.dialogue.active_node}; режим {g.mode}, автоход {bool(g.autowalk)}, "
                        f"экшен {g.action.active}, жив {g.player.alive}, стоп-кадр {g.combat.hitstop_ms}, "
                        f"портал под ногами {bool(g.level.portal_at(*tile_of(g.player)))}]")
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
            stem_lid = {os.path.basename(d.get("map", ""))[:-5]: lid           # id локации не всегда совпадает с именем карты
                        for lid, d in json.load(open("data/locations.json", encoding="utf-8")).items() if d.get("map")}
            for f in glob.glob("data/maps/*.json"):
                stem = os.path.basename(f)[:-5]
                mid = stem_lid.get(stem, stem)
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
                stem = os.path.basename(f)[:-5]
                for lid, d in json.load(open("data/locations.json", encoding="utf-8")).items():
                    if os.path.basename(d.get("map", "")) == stem + ".json":     # id локации не всегда совпадает с именем карты
                        return lid
                return stem
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
        for n in list(g.npcs):            # сначала ствол своего навыка, патроны и лечение — потом роскошь
            if n.npc_id in g.traders:
                try:
                    self.stand_near([tile_of(n)])
                    self.shop(n.npc_id)
                except Stuck:
                    pass
        if self.own_weapon_ok():
            self.buy_implants()
            self.lessons()

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
        g.dialogue.close()
        npc = self.find_npc(npc_id)
        if npc is None:
            raise Stuck(f"{g.loc.id}: нет жителя {npc_id}")
        for attempt in range(4):
            if g.combat.active:
                self.fight()
                # бой может увести героя за порог (шаг на клетку перехода — и он уже в соседней локации):
                # собеседник остался на прежней карте, и координаты его клетки в новой ничего не значат
                npc = self.find_npc(npc_id)
                if npc is None:
                    raise Stuck(f"{g.loc.id}: нет жителя {npc_id}")
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
            g.dialogue.close()
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
        self.g.dialogue.close()

    def chat(self, npc_id, *parts):
        """Разговор по готовой цепочке реплик (как в тестах квестов). Часть — строка или кортеж вариантов:
        берётся первый, что виден (реплика с проверкой навыка — если навык есть)."""
        g = self.g
        self.talk(npc_id)
        for part in parts:
            if not g.dialogue.is_active():
                break
            alts = part if isinstance(part, tuple) else (part,)
            if not any(self.say(a, required=False) for a in alts):
                opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
                self.end_talk()
                raise Stuck(f"{npc_id}: нет реплики {alts} среди {opts}")
        self.end_talk()
        self.fr(2)

    def side(self, name, fn):
        """Побочный квест: не вышел — записать и идти дальше (сюжет важнее)."""
        g = self.g
        try:
            fn()
        except Stuck as ex:
            self.side_fails.append(f"{name}: {ex}")
            print(f"   ~ побочка «{name}» не вышла: {ex}", flush=True)
            g.dialogue.close()
            if g.term:
                g.close_terminal()
            g.loot = None
            g.trade = None
            if not g.player.alive or g.game_over:
                raise
            return False
        self.stats["sides_done"] = self.stats.get("sides_done", []) + [name]
        return True

    def buy_from(self, trader_id, item, n=1):
        """Купить у торговца нужное квесту (если он рядом и денег хватает)."""
        g = self.g
        self.talk(trader_id)
        self.end_talk()
        g.open_trade(trader_id)
        if not g.trade:
            return False
        g.trade["tab"] = "buy"
        while g.inventory.count(item) < n:
            row = next((r for r in g.trade_rows() if r[0] == item), None)
            if row is None or g.inventory.count("крышки") < row[2]:
                break
            g._buy(*row[:3])
        g.trade = None
        return g.inventory.count(item) >= n

    TEACHERS = {"guns": "arms_seller", "melee": "neal", "heavy": "sl_trader", "energy": "strip_trader",
                "throwing": "rose", "steal": "decker", "medicine": "ghoul_healer", "science": "jt_tinker",
                "speech": "mother_snake", "survival": "chet"}

    def lessons(self):
        """Платные уроки у мастера своего навыка — когда деньги есть с запасом (как сделал бы игрок)."""
        g = self.g
        for sid, _ in self.build:
            npc = self.TEACHERS.get(sid)
            if not npc or not any(n.npc_id == npc for n in g.npcs) or g.flags.get(f"lesson_{npc}_done"):
                continue
            try:
                self.talk(npc)
                ask = next((o["label"] for o in g.dialogue.visible_options() if o.get("next") == "lessons"), None)
                if ask and self.say(ask, required=False):
                    while g.inventory.count("крышки") >= 700 and any(
                            self.say(w, required=False) for w in ("Первый урок", "Второй урок", "Третий урок")):
                        self.stats["lessons"] = self.stats.get("lessons", 0) + 1
                        if not self.say("Ещё урок", required=False):
                            break
                self.end_talk()
            except Stuck:
                self.end_talk()

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
        if not g.term or g.term.get("id") != tid:   # E открыл соседний ящик — терминал открыть напрямую, как кликом
            g.loot = None
            g.open_terminal(tid)
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
        if g.term and not g.loot:          # рядом терминал, и E открыл его — закрыть и открыть ящик напрямую
            g.close_terminal()
            g.open_container(box)
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
        base = p.base_damage + max(0, (p.melee_skill - 60) // 10) + 3 * p.perk_rank("heavy_hand")
        sharp = 3 if wid == "melee" and g.inventory.has("заточенный лом") else 0
        dmg = (base + w.get("damage", 0) + sharp) if not w["ranged"] else (w.get("damage", 0) or 23)
        dmg = max(1, dmg - int(armor * (1 - w.get("pierce", 0))))
        hit = max(0.05, min(0.95, (skill_of(p, wid) - 2 * short - 25) / 100))
        return dmg * burst * hit * (1.6 if w["ranged"] else 1) * (0.3 if w.get("thrown") else 1) / w["ap"] * 4

    def own_weapon_ok(self):
        """Есть ли ствол (или клинок) своего главного навыка, к которому есть заряды."""
        g = self.g
        main = self.build[0][0] if self.build_name != "heavy" else "heavy"
        main = {"guns": "guns", "energy": "energy", "heavy": "heavy", "melee": "melee"}.get(self.build_name, main)
        if self.build_name == "talker":
            return True
        for wid, w in WEAPONS.items():
            if w.get("skill") == main and (not w.get("item") or g.inventory.has(w["item"])) and wid != "melee":
                if not w.get("ammo") or g.inventory.count(w["ammo"]) >= 20:
                    return True
        return main == "melee" and False

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



    def flank(self, target, need=12):
        """Обойти укрытие: шаг на клетку, откуда цель не в укрытии и шанс попасть выше.

        Против стрелков в укрытии стоять и стрелять в лоб — 10-15% на выстрел. Игрок
        обходит сбоку; бот теперь тоже.
        """
        g, c, p = self.g, self.g.combat, self.g.player
        if p.ap < S.AP_MOVE or not c.los(p, target):
            return False
        px, py = tile_of(p)
        here = p.rect.copy()
        base = c.hit_chance(p, target)
        best = None
        for r in (1, 2, 3):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    tile = (px + dx, py + dy)
                    if not c._walkable(tile) or tile in c._occupied(except_ent=p):
                        continue
                    p.rect.topleft = rect_pos_for_tile(p, tile)
                    if c.los(p, target):
                        val = c.hit_chance(p, target)
                        if best is None or val > best[2]:
                            best = (dx, dy, val)
                    p.rect = here.copy()
            if best and best[2] >= base + need:
                break
        if best and best[2] >= base + need:
            before = tile_of(p)
            c.player_step(best[0], best[1])
            for _ in range(30):
                if not c.tweens:
                    break
                self.fr(1)
            return tile_of(p) != before
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
        dmg0 = self.stats["damage_taken"]
        foes = list(c.enemies_in_combat())
        hp_foes = {id(e): e.hp for e in foes}
        rounds0 = c.round
        n = 0
        last_hp = g.player.hp
        while c.active and g.player.alive:
            if g.player.hp < last_hp:                      # урон, полученный с прошлого кадра (лечение его не маскирует)
                self.stats["damage_taken"] += last_hp - g.player.hp
            last_hp = g.player.hp
            n += 1
            if n > 30000:
                from src.companion import party
                me = tile_of(g.player)
                foes = [f"{e.type_id}@{tile_of(e)} hp{e.hp} {'бежит ' if getattr(e, 'retreated', False) else ''}"
                        f"d{chebyshev(me, tile_of(e))} {'видит' if c.los(e, g.player) else 'не видит'}"
                        for e in c.enemies_in_combat()]
                pals = [f"{a.name} {'выбит' if a.down else 'в строю'}" for a in party(g)]
                raise Stuck(f"бой не кончается [герой {me}, раунд {c.round}, {g.loc.id}; враги: {foes}; спутники: {pals}]")
            if c.player_can_act():
                p = g.player
                if p.ap >= p.max_ap:
                    p._flank_tried = False
                urgent = p.hp < max(8, p.max_hp * 0.2)      # совсем плохо — лечиться в любом случае
                spare = p.ap - S.AP_CRAFT >= c.attack_cost(p)  # после бинта ещё хватит на выстрел
                if (not self.noheal and p.hp < p.hp_cap * 0.45 and p.ap >= S.AP_CRAFT
                        and (urgent or spare) and self.heal_if_needed(0.45)):
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
                first = {"medic": 0, "sniper": 1, "commander": 2, "gunner": 3, "grenadier": 4}   # как игрок: сначала «мозги» отряда
                t = min(left, key=lambda e: (not c.can_attack(p, e)[0], first.get(getattr(e, "role", None), 9),
                                             chebyshev(here, tile_of(e)), e.hp))
                c.target = t
                if (getattr(t, "robot", False) and g.inventory.has("импульсная граната") and p.ap >= c.THROW_AP
                        and 2 <= chebyshev(here, tile_of(t)) <= c.THROW_RANGE and c.los(p, t)):
                    c.player_throw()                  # ЭМИ в робота — как сделал бы игрок
                    self.fr(1)
                    continue
                if (c.hit_chance(p, t) < 38 and p.ap >= S.AP_MOVE + c.attack_cost(p)
                        and not getattr(p, "_flank_tried", False)):
                    p._flank_tried = True
                    if self.flank(t):
                        continue
                close_in = (c.can_attack(p, t)[0] and c.hit_chance(p, t) < 45 and chebyshev(here, tile_of(t)) > 2
                            and p.ap >= c.attack_cost(p) + 1)
                if close_in:                      # мажу издалека — подойду ближе, как сделал бы игрок
                    step = c._path_next_step(p, t)
                    if step:
                        before = tile_of(p)
                        c.player_step(*step)
                        for _ in range(30):
                            if not c.tweens:
                                break
                            self.fr(1)
                        if tile_of(p) != before:
                            self.fr(1)
                            continue
                if c.can_attack(p, t)[0] and p.ap >= c.attack_cost(p):
                    part = 0                      # в оптику — если броня и шанс приличный
                    if ("eyes" in t.weak_parts and t.armor and c.hit_chance(p, t, 2) >= 30
                            and p.ap >= c.attack_cost(p, 2)):        # прицельный дороже — хватит ли ОД
                        part = 2
                    c.player_attack(part)
                elif p.ap >= 1 and not c.can_attack(p, t)[0]:
                    step = c._path_next_step(p, t)
                    if step:
                        before = tile_of(p)
                        c.player_step(*step)
                        for _ in range(30):       # шаг — анимация: клетка сменится, когда она доиграет
                            if not c.tweens:
                                break
                            self.fr(1)
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
        rounds = c.round - rounds0 + 1
        taken = self.stats["damage_taken"] - dmg0
        self.stats["rounds"] += rounds
        self.stats["damage_dealt"] += sum(max(0, hp_foes[id(e)] - e.hp) for e in foes)
        if taken == 0:
            self.stats["fights_no_damage"] += 1
        if rounds >= 14:
            self.stats["fights_long"] += 1
        one = sum(1 for e in foes if not e.alive and hp_foes[id(e)] == e.max_hp and getattr(e, "_hits_taken", 1) <= 1)
        self.stats["kills"] += sum(1 for e in foes if not e.alive)
        self.critic.on_fight(rounds, len(foes), max(0, hp0 - low), g.player.hp_cap, one)
        self.check_alive("бой")
        self.stats["hp_min"].append(round(100 * low / max(1, g.player.hp_cap)))
        if not self.noheal:
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
        """Перебить всех враждебных в локации: подойти туда, откуда врага можно достать (вплотную —
        для ближнего боя, на дистанции по линии огня — для стрельбы), начать бой, добить.
        Кого не вышло — записать в problems с местом и причиной, а не пропускать молча.
        max_rounds — сколько заходов без продвижения терпеть."""
        g = self.g
        p = g.player
        skip = {}
        stall = 0
        burnt = {}                            # id(враг) -> клетки, с которых уже не вышло нанести урон
        for _ in range(400):
            if g.combat.active:
                self.fight()
            left = [e for e in g.enemies if e.alive and e.hostile and id(e) not in skip]
            if not left:
                return
            e = min(left, key=lambda e: chebyshev(tile_of(p), tile_of(e)))
            hp0 = sum(x.hp for x in left)
            tx, ty = tile_of(e)
            prof = g.combat.profile(p)
            reach = prof["range"] if prof["ranged"] else 1     # ближний бой — только вплотную
            taken = {tile_of(o) for o in [p] + [x for x in g.enemies if x.alive] + list(g.npcs)}
            ring = [(tx + dx, ty + dy) for r in (1, 2, 3, 4, 5, 6, 7, 8) for dx in range(-r, r + 1) for dy in range(-r, r + 1)
                    if max(abs(dx), abs(dy)) == r]
            free = [c for c in ring if not g.level.is_wall(*c) and not g.level.is_exit(*c)
                    and c not in getattr(g.level, "blocked", ()) and c not in taken]
            # откуда реально можно ударить: вплотную — всегда, дальше — по линии огня (как can_attack);
            # затаившийся в засаде не выдаёт себя, пока герой не подойдёт на две клетки, — иначе бой не начнётся
            spots = []
            for c in free:
                d = chebyshev(c, (tx, ty))
                if d > reach or (getattr(e, "hidden", False) and d > 2):
                    continue
                p.rect.topleft = rect_pos_for_tile(p, c)
                if d > 1 and not g.combat.los(p, e):
                    continue
                spots.append(c)
            bad = burnt.setdefault(id(e), set())
            spots.sort(key=lambda c: (c in bad, chebyshev(c, tile_of(p))))
            if not spots:
                self._clear_skip(e, "некуда подойти" if free else "нет свободной клетки рядом", skip)
                continue
            spot = next((c for c in spots if c not in bad), None)
            if spot is None:
                self._clear_skip(e, f"с {len(bad)} позиций урон не прошёл", skip)
                continue
            p.rect.topleft = rect_pos_for_tile(p, spot)
            g.snap_camera()
            self.fr(2)
            if not g.combat.active:
                g.combat.start(player_first=True)
            if not g.combat.active:          # враг не втянулся в бой (засада, далеко) — пробуем другую клетку
                bad.add(spot)
                stall += 1
                if stall > max(8, max_rounds):
                    self._clear_skip(e, "бой не начинается", skip)
                    stall = 0
                continue
            self.fight()
            now = sum(x.hp for x in left if x.alive)
            if e.alive and now >= hp0:
                bad.add(spot)
                stall += 1
                if stall >= 6:
                    self._clear_skip(e, "6 заходов без урона", skip)
                    stall = 0
            else:
                stall = 0

    def _clear_skip(self, e, why, skip):
        """Враг, которого зачистка не взяла: не молчать, а записать место и причину в problems."""
        g = self.g
        tx, ty = tile_of(e)
        skip[id(e)] = why
        msg = f"не смог зачистить: {e.type_id} ({tx},{ty}) на {g.loc.id} ({why})"
        if msg not in self.problems:
            self.problems.append(msg)
            print(f"!! {msg}", flush=True)

    # ------------------------------------------------------------ встреча в пустоши
    def encounter(self, enc_id):
        """Найти в пустоши нужную встречу (src/encounters.ENCOUNTERS): бот не бросает кости —
        шаг между городами у него телепорт, поэтому встречу он «высматривает» сам, как игрок,
        который прошёл по трассе и остановился. Нужен почтовый робот, и только он."""
        from src import encounters
        g = self.g
        entry = next((e for e in encounters.ENCOUNTERS if e[1] == enc_id), None)
        if entry is None:
            raise Stuck(f"встречи «{enc_id}» нет в таблице пустоши")
        if g.mode != "world":
            g.go_world_map()
            self.fr(2)
        real = encounters.roll
        encounters.roll = lambda *a, **k: entry
        try:
            g.start_encounter()
        finally:
            encounters.roll = real
        self.fr(2)
        if not g.loc.id.endswith(":" + enc_id):
            raise Stuck(f"встреча «{enc_id}» не началась ({g.loc.id})")
        self.check_alive(f"встреча {enc_id}")

    # ------------------------------------------------------------ экшен за Дэкса (Барстоу)
    def action_aim(self, ent):
        g = self.g
        cx, cy = g.cam.p(ent.rect.centerx, ent.rect.centery)
        MOUSE["pos"] = (int(round(cx * g.zoom)), int(round(cy * g.zoom)))

    def action_fire(self, on=True):
        MOUSE["fire"] = bool(on)

    def action_stop(self):
        MOUSE["fire"] = False
        MOUSE["pos"] = (-50, -50)

    def action_on_screen(self, ent):
        """Гуль не под панелью и в кадре: по нему можно целиться, не задевая интерфейс."""
        g = self.g
        cx, cy = g.cam.p(ent.rect.centerx, ent.rect.centery)
        return 0 <= cx * g.zoom <= S.SCREEN_W and 0 <= cy * g.zoom <= S.SCREEN_H - 130

    def action_stand(self, tile):
        """Встать в клетку (или рядом) — бот ходит телепортом, как игрок, который кликнул."""
        g = self.g
        p = g.player
        for dx, dy in ((0, 0), (0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
            t = (tile[0] + dx, tile[1] + dy)
            if g.level.is_wall(*t) or g.level.is_exit(*t) or t in getattr(g.level, "blocked", ()):
                continue
            p.rect.topleft = rect_pos_for_tile(p, t)
            g.snap_camera()
            self.fr(1)
            return True
        return False

    def action_spot(self, foe, lo=4, hi=8):
        """Клетка в 4–8 шагах от гуля, откуда он по линии огня и выше центра экрана
        (в изометрии «выше» — меньшая сумма x+y, иначе прицел уходит под панель)."""
        g = self.g
        p = g.player
        fx, fy = tile_of(foe)
        iso = bool(getattr(g.cam, "iso", False))
        best = None
        for r in range(lo, hi + 1):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    t = (fx + dx, fy + dy)
                    if g.level.is_wall(*t) or g.level.is_exit(*t) or t in getattr(g.level, "blocked", ()):
                        continue
                    if any(chebyshev(t, tile_of(x)) <= 1 for x in g.enemies if x.alive and x.hostile and x is not foe):
                        continue
                    above = (t[0] + t[1] > fx + fy + 2) if iso else (t[1] > fy + 2)
                    if not above:
                        continue
                    here = p.rect.copy()
                    p.rect.topleft = rect_pos_for_tile(p, t)
                    seen = g.combat.los(p, foe)
                    p.rect = here
                    if not seen:
                        continue
                    score = (abs(r - 6), chebyshev(t, tile_of(p)))
                    if best is None or score < best[0]:
                        best = (score, t)
        return best[1] if best else None

    def action_clear(self, where="", max_ticks=6000, dt=100):
        """Зачистить район Барстоу в экшене за Дэкса: целится в ближайшего гуля, держит гашетку,
        перезаряжается (движок сам), отходит, когда гуль подошёл вплотную, и ждёт толпы из домов.
        Не вышло — честная причина с тем, кто остался жив."""
        g, a = self.g, self.g.action
        if not a.active:
            raise Stuck(f"{g.loc.id}: экшен-режим не включился (играем не за Дэкса?)")
        kills0 = a.kills
        ticks = 0
        quiet = 0
        while ticks < max_ticks:
            ticks += 1
            foes = [e for e in g.enemies if e.alive and e.hostile]
            if not foes and not a.hordes_left():
                break
            if not foes:                                   # толпы ещё сидят в домах — подойти к триггеру
                h = next((h for h in getattr(g.level, "hordes", []) if not h["done"]), None)
                if h is not None:
                    x0, y0, x1, y1 = h["trigger"]
                    self.action_stop()
                    self.action_stand(((x0 + x1) // 2, (y0 + y1) // 2))
                elif a.hordes_left():
                    self.action_stop()                     # толпа уже валит из двери — дать ей выйти
                else:
                    break
                g.update(dt)
                continue
            me = tile_of(g.player)
            near = min(foes, key=lambda e: chebyshev(me, tile_of(e)))
            gap = chebyshev(me, tile_of(near))
            if gap <= 2 or not self.action_on_screen(near):
                self.action_stop()                         # вплотную бьют больно, под панелью не выстрелить
                spot = self.action_spot(near)
                if spot:
                    self.action_stand(spot)
                else:
                    quiet += 5
            self.action_aim(near)
            self.action_fire(True)
            if g.player.hp < g.player.hp_cap * 0.45:
                self.heal_if_needed(0.45)
            before = sum(e.hp for e in foes)
            g.update(dt)
            if ticks % 4 == 0:
                g.draw()
                self.handle_popups()
            quiet = quiet + 1 if sum(e.hp for e in foes if e.alive) >= before else 0
            if quiet >= 40:                                # гули стоят, а урона нет: сменить позицию
                self.action_stop()
                spot = self.action_spot(near, lo=3, hi=10)
                if spot:
                    self.action_stand(spot)
                quiet = 0
            self.check_alive(where or g.loc.id)
        self.action_stop()
        left = [f"{e.type_id}@{tile_of(e)}" for e in g.enemies if e.alive and e.hostile]
        if left or a.hordes_left():
            raise Stuck(f"{where or g.loc.id}: не зачищено за {ticks} кадров — живы {left[:6]}, "
                        f"толпы {'ещё выходят' if a.hordes_left() else 'вышли'}, HP {g.player.hp}")
        return a.kills - kills0


    def check_alive(self, where):
        g = self.g
        if not g.player.alive or g.game_over:
            self.stats["deaths"] += 1
            raise Stuck(f"герой погиб ({where})")

    # ------------------------------------------------------------ торговля
    KEEP_MISC = ("отмычка", "лопата")

    _quest_items = None

    @classmethod
    def quest_items(cls):
        """Вещи, о которых спрашивают в разговорах (условие item / items_all / items_any) — их не продают."""
        if cls._quest_items is None:
            import json
            found = set()

            def walk(x):
                if isinstance(x, dict):
                    if isinstance(x.get("item"), str) and x.get("type") is None:
                        found.add(x["item"])
                    for k in ("items_all", "items_any"):
                        found.update(x.get(k) or [])
                    for v in x.values():
                        walk(v)
                elif isinstance(x, list):
                    for v in x:
                        walk(v)
            with open("data/dialogues.json", encoding="utf-8") as fh:
                walk(json.load(fh))
            found.discard("крышки")
            cls._quest_items = found
        return cls._quest_items

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
            if price <= 0 or name == "крышки" or name in self.quest_items():
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
                if name.startswith("письмо: "):     # чужую почту 2077 года не вскрываем: её доставляют
                    continue
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
            if g.inventory.count("крышки") < price + 100 or not any(n.npc_id == npc for n in g.npcs):
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
def lane_lesson(b):
    """Школа: учебник из библиотеки — и последний урок мисс Лейн (sq_lane).

    Отдельный шаг и отдельный акт (`playthrough.py lesson`): его можно прогнать, не гоняя весь
    сюжет, — так проверяют квест после правок школы, детей и награды за урок.
    """
    g = b.g
    if not b.sides or g.stage("sq_lane") >= 100:
        return
    b.fetch("fifteen_school_in", "библиотечный шкаф")     # дойти, зачистить радтаканов, взять учебник
    if not g.inventory.has("Наша Америка, 5 класс"):
        raise Stuck("учебник в библиотечном шкафу не нашёлся")
    b.pursue("miss_lane", "lane_task")                        # взять просьбу у доски
    b.pursue("miss_lane", "quest:sq_lane")                    # отдать учебник — последний урок
    if g.stage("sq_lane") < 100:
        raise Stuck(f"«Последний урок» не закрылся: стадия {g.stage('sq_lane')}, "
                    f"учебник в рюкзаке {g.inventory.has('Наша Америка, 5 класс')}")
    print(f"   sq_lane: стадия {g.stage('sq_lane')}, «Наука» {g.player.skill('science')}, "
          f"крышек {g.inventory.count('крышки')}, флаг урока {bool(g.flags.get('lane_lesson'))}", flush=True)
    b.walk_to_map("ruins")


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
        g.dialogue.close()
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

    b.step("Пятнадцатая: последний урок мисс Лейн", lambda: lane_lesson(b))

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
        g.player.rect.topleft = rect_pos_for_tile(g.player, (88, 20))
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

    def baker_sides():
        if b.sides:
            SQ.baker(b)
    b.step("Бейкер: побочки", baker_sides)


def act1b(b):
    """Зайзикс и Нидлс — хвост первого акта, дорога к Хабу."""
    g = b.g

    def postman():
        """На трассе — почтовый робот: мешок писем 2077 года (квест «Письма почтальона»).
        Письма бот разносит по адресатам дальше по маршруту — в каждом городе своё."""
        if not b.sides:
            return
        b.side("Письма почтальона: мешок", lambda: SQ.mail_sack(b))
    b.step("Пустошь: Почтальон-3000", postman)

    def zzyzx():
        g.go_world_map()
        if b.sides:
            b.go("ruins")                              # Дэкс ждёт у въезда в Пятнадцатую
            b.side("Контракт на Барстоу", lambda: SQ.merc_contract(b))
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
            SQ.mail(b, "springer", "письмо: Спрингеру, Зайзикс", "mail_done_springer", "Зайзикс")
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
        if b.sides:
            SQ.needles(b)
        b.walk_to_map("needles")
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
            SQ.hub_start(b)
            SQ.caravans_take(b)                       # Маргарет: неделя на правду, а не Ханы
            SQ.mail(b, "harold", "письмо: Р. Грею, Хаб", "mail_done_grey", "Хаб")
            SQ.harold_story(b)                        # Гарольд: Грей и грузовой въезд Марипозы
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
            SQ.junktown(b)
            SQ.mail(b, "mayor_darkwater", "письмо: Дарквотеру, Джанктаун", "mail_done_darkwater", "Джанктаун")
            SQ.mail(b, "anna_shaw", "письмо: доктору Шоу, Бейкерсфилд", "mail_done_shaw", "Джанктаун")
            b.side("Цена воды", lambda: SQ.water_war(b))    # Сэл → артель Веги → сейф Декера → мэр
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
            SQ.necropolis(b)
        b.walk_to_map("necropolis")
        b.shop_here()
    b.step("Некрополь: Водораздел, Сет, Коббс", necropolis)

    def aradesh():
        g.go_world_map()
        b.go("aradesh")
        b.shop_here()
        b.pursue("aradesh", "aradesh_job", required=False)
        if b.sides:
            # пещера (бой) или насос Вика из каньона; провал — в side_fails с причиной, а не тишиной
            b.side("Вода для Арадеша", lambda: SQ.aradesh(b))
        else:
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
        if b.sides:
            SQ.boneyard_before(b)
        if b.steal("boneyard_cathedral", "сундук на складе"):
            b.pursue("adytum_mayor", "adytum_truce", required=False)
        if b.sides:
            b.pursue("cooper", "tag_done", required=False)
            SQ.boneyard(b)
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
        if b.sides:
            SQ.mail(b, "beatrice", "письмо: смотрителю Убежища 15", "mail_done_vault15", "Убежище 15")
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

    def rounds():
        if not b.sides:
            return
        SQ.hub_finish(b)
        SQ.ferals_finish(b)
        SQ.needles_finish(b)
    b.step("Обход: Хаб, Некрополь, Нидлс", rounds)

    def rounds_tour():
        """Хвост акта: улики караванов разбросаны по трассе (застава I-15, мост в Нидлсе) — это
        обход, а не отдельный круг: бот всё равно возвращается в Хаб сдать дела. Там же письмо
        Убежища 15 отыгрывается в Арадеше — Лейла мирится с Беатрис."""
        if not b.sides:
            return
        SQ.caravans_rounds(b)
        b.side("Письма: сёстры Арадеша", lambda: SQ.mail_sisters(b))
    b.step("Обход: караваны и сёстры", rounds_tour)


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
        if b.sides:
            SQ.mail(b, "mae_reeves", "письмо: Ривзам, Примм", "mail_done_reeves", "Примм")
        b.terminal("reeves_archive", "Марипоза, «Ноль»", "Письмо 2077 года")
        if b.sides and g.inventory.has("карта клада"):
            b.read_books()
            b.walk_to_map("primm")
            b.take_from("камень с крестом")
            b.gear_up()
        SQ.primm_case(b)             # улики → вдова → фишка → брат Иов: Тоби дома
        if b.sides:
            SQ.primm(b)
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
            SQ.goodsprings(b)
            b.visit("goodsprings_cave")
            b.take_from("тайник старателей")
            SQ.goodsprings_after_cave(b)
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
        if b.sides:
            b.side("Кровь Убежища 11", lambda: SQ.vault11(b))    # устав → протокол → мэр Кэрролл
            b.side("Беглый субъект", lambda: SQ.subject(b))      # Тед → клетка № 12 → Ниптон
            SQ.nipton(b)
            SQ.luis_home(b)
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
            b.side("Письма: Лаки 38", lambda: SQ.mail_house(b))     # письмо Хаусу — в щель терминала
            b.pursue("boots_rider", "bike_job", required=False)
            b.pursue("snake_trader", "bike_done", required=False)
        b.terminal("agatha_salon", "[Зашифрованное]")      # тайна Ладоней: Агата — из Ордена
        b.pursue("mother_agatha", "palms_codes", required=False)
        if not g.flags.get("palms_codes") and b.steal("vegas_boots", "ящик с книгами"):   # книги Ладоней — Агате
            b.pursue("mother_agatha", "palms_codes", required=False)
        b.terminal("snakes_ledger", "[Отдельный список]")   # тайна Змей: продают «лишних» белым
        b.pursue("mother_snake", "snakes_passage", required=False)
        if not g.flags.get("snakes_passage"):          # книгу не взломал — путь родни: гость, чертёж, пропуск
            b.pursue("mother_snake", "snakes_job1_taken", required=False)
            b.visit("vegas_strip", clear=False)
            b.pursue("grey_buyer", "snakes_job1", required=False)
            if not g.inventory.has("чертёж электростанции"):
                if not g.inventory.has("отмычка"):
                    b.visit("vegas_strip", clear=False)
                    for t in ("strip_trader", "snake_trader"):
                        try:
                            b.buy_from(t, "отмычка")
                        except Stuck:
                            pass
                b.steal("vegas_boots", "сейф электростанции")
                print("   чертёж:", g.inventory.has("чертёж электростанции"), "отмычка:", g.inventory.has("отмычка"), flush=True)
            b.visit("vegas_snakes", clear=False)
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

    def vegas_sides():                 # побочки Вегаса — после «Ноля»: разговоры с Матерью-Змеёй не мешают пропуску в ходы
        if b.sides:
            b.side("Последний банк Вегаса", lambda: SQ.heist(b))   # крупье → команда → пульт → хранилище
            SQ.vegas(b)
    b.step("Вегас: побочки", vegas_sides)



def secrets(b):
    """Тайные места: ложа Ордена, «Посейдон-7», Каталина, «Нова», REPCONN и «Арес» — и легенды в них."""
    g = b.g

    def city(cid):
        g.go_world_map()
        b.go(cid)
        b.shop_here()

    def errands():
        if not b.sides:
            return
        if g.inventory.has("динамит") and not g.flags.get("truck_done"):
            g.go_world_map()
            b.go("junktown")
            b.pursue("scrapper", "truck_done", required=False)
        SQ.bell_finish(b)
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
        b.side("«Нова»: лавка Шрапнели", lambda: (b.visit("nova_under", clear=False), b.shop_here()))
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
        if b.sides:
            b.side("Экспедиция Гарольда: журнал «Купели»", lambda: SQ.harold_finish(b))
        b.terminal("mariposa_core", "[Код от Тобиаса", "[Ввести код взвода охраны]",
                   "[«Пепел»", "[«Сталь»", "[«Чужие руки»")
        b.fr(5)
        if not g.flags.get("game_ending"):
            need = ("mariposa_unlocked", "mariposa_code", "order_contact", "zero_fate_destroy", "v4_vre_destroyed",
                    "ending_ash_way")
            alive = [f"{e.type_id}/{getattr(e, 'role', None)}" for e in g.enemies if e.alive]
            raise Stuck("концовка не наступила: " + ", ".join(f"{k}={bool(g.flags.get(k))}" for k in need)
                        + f"; бой {g.combat.active}; живы {alive}; терминал {bool(g.term)}; "
                        + f"лог: {g.log_lines[-4:]}")
    b.step("Марипоза: финал", mariposa)


ACTS = {"act1": act1, "act1b": act1b, "act2": act2, "act3": act3, "secrets": secrets, "final": final,
        # один шаг, без всего сюжета: смоук квеста мисс Лейн после правок школы
        "lesson": lambda b: b.step("Пятнадцатая: последний урок мисс Лейн", lambda: lane_lesson(b))}


def main():
    args = sys.argv[1:]
    opts = {"--seed": "7", "--build": "guns"}
    for k in list(opts):
        if k in args:
            i = args.index(k)
            opts[k] = args[i + 1]
            del args[i:i + 2]
    stats_path = None
    if "--stats" in args:
        i = args.index("--stats")
        stats_path = args[i + 1]
        del args[i:i + 2]
    noheal = "--noheal" in args
    args = [a for a in args if a != "--noheal"]
    sides = "--nosides" not in args
    args = [a for a in args if a != "--nosides"]
    which = args or list(ACTS)
    b = Bot(seed=int(opts["--seed"]), sides=sides, build=opts["--build"], noheal=noheal)
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
    st = b.stats
    if st["fights"]:
        print(f"раундов {st['rounds']} (в среднем {st['rounds'] / st['fights']:.1f} на бой), "
              f"урона получено {st['damage_taken']}, нанесено {st['damage_dealt']}, "
              f"боёв без урона игроку {st['fights_no_damage']}/{st['fights']} "
              f"({100 * st['fights_no_damage'] / st['fights']:.0f}%), долгих (14+ раундов) {st['fights_long']}")
        print("минимум HP за бой: " + hp_buckets_text(st.get("hp_min") or []))
    print(f"продал на {b.stats.get('sold', 0)} крышек")
    print("купил:", ", ".join(b.stats.get("bought", [])) or "ничего")
    print("прочитал:", ", ".join(b.stats.get("books", [])) or "ничего")
    print("импланты:", ", ".join(b.stats.get("implants", [])) or "нет")
    print("уроков у мастеров:", b.stats.get("lessons", 0))
    print("побочки по сценарию:", len(b.stats.get("sides_done", [])), "вышли;", len(b.side_fails), "нет")
    for f in b.side_fails:
        print("   ~", f)
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
    if stats_path:
        payload = {
            "build": opts["--build"], "seed": int(opts["--seed"]), "sides": sides, "acts": which,
            "noheal": noheal,
            "elapsed_s": round(time.time() - b.t0, 1),
            "stats": b.stats,
            "quests": {"done": len(done), "total": len(Q), "started": started, "untouched": untouched},
            "ending": ending[0] if ending else None,
            "problems": b.problems,
            "critic": [{"where": w, "text": t} for w, t in b.critic.summary()],
            "steps": b.rows,
            "side_fails": b.side_fails,
        }
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=1)
        print(f"\nотчёт: {stats_path}")


if __name__ == "__main__":
    main()
