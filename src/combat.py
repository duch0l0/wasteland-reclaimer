"""
Пошаговый бой в духе Fallout 2.

Мир исследуется в реальном времени, но как только враг замечает игрока
(или игрок бьёт первым), игра переходит в пошаговый режим:
  - все участники встают на клетки сетки;
  - ходят по очереди, порядок — по Реакции (кто начал бой — ходит первым);
  - в свой ход тратят очки действия (ОД): шаг, удар/выстрел, прицельная атака, крафт;
  - шанс попасть = навык − КБ цели ± модификатор части тела − штраф за дальность;
  - стрелять можно только по линии огня (стены — укрытия);
  - критическое попадание умножает урон и калечит (глаза, ноги, руки, пах);
  - панцирь (armor) гасит урон везде, кроме уязвимых частей тела.
Бой заканчивается, когда враги в бою мертвы или игрок от них ушёл.
"""
import random
from collections import deque

import pygame

from . import settings as S
from .weapons import WEAPONS, RANGE_PENALTY_PER_TILE

T = S.TILE

# hit — модификатор шанса попасть, crit — прибавка к шансу крита,
# mult — множитель урона при крите, effect — чем крит калечит цель.
BODY_PARTS = [
    {"id": "torso", "name": "торс",   "hit": 0,   "crit": 0,  "mult": 2.0, "effect": None},
    {"id": "head",  "name": "голова", "hit": -40, "crit": 20, "mult": 3.0, "effect": None},
    {"id": "eyes",  "name": "глаза",  "hit": -60, "crit": 35, "mult": 2.0, "effect": "blinded"},
    {"id": "arms",  "name": "руки",   "hit": -30, "crit": 10, "mult": 2.0, "effect": "crippled_arms"},
    {"id": "legs",  "name": "ноги",   "hit": -20, "crit": 10, "mult": 2.0, "effect": "crippled_legs"},
    {"id": "groin", "name": "пах",    "hit": -30, "crit": 15, "mult": 1.5, "effect": "skip_turn"},
]

# Сообщения о критах игрока. {name} — имя врага с заглавной буквы.
CRIT_TEXT = {
    "torso": ["{name} складывается пополам, как шезлонг с дефектом.",
              "Прямо в корпус! {name} на секунду вспоминает всю свою мутацию."],
    "head":  ["Звонко по голове! {name} слышит колокола, которых тут не было с войны.",
              "{name} получает по макушке так, что мысли вылетают. Обе."],
    "eyes":  ["Прямо в глаз! {name} теперь видит мир мутнее, чем обычно. Ослеплён.",
              "В глаза! {name} машет конечностями наугад. Ослеплён."],
    "arms":  ["Хруст! {name} больше не может толком замахнуться. Урон вдвое меньше.",
              "По конечности! {name} теперь дерётся без огонька. Урон вдвое меньше."],
    "legs":  ["Колено хрустит! {name} хромает и теряет 3 ОД в ход.",
              "По ногам! {name} ковыляет, как Гена после праздника. −3 ОД."],
    "groin": ["Ниже пояса. {name} замирает с выражением глубокой обиды и пропускает ход.",
              "{name} получает туда, куда не принято. Пропускает ход, думает о жизни."],
}
PLAYER_MISS_MELEE = ["Вы промахиваетесь. Воздух повержен.",
                     "Вы машете ломом. Цель не впечатлена.",
                     "Мимо. Цель делает вид, что так и было задумано."]
PLAYER_MISS_RANGED = ["Выстрел уходит в молоко.",
                      "Пуля свистит мимо. Где-то вдали вздрагивает консервная банка.",
                      "Мимо. Самопал обиженно щёлкает."]
ENEMY_MISS_MELEE = ["{name} кусает воздух с большим энтузиазмом.",
                    "{name} промахивается и выглядит смущённым.",
                    "{name} бросается — и промахивается."]
ENEMY_MISS_RANGED = ["{name} стреляет — пуля уходит в молоко.",
                     "{name} палит мимо. Пустошь вздрагивает.",
                     "{name} стреляет, но попадает только в чью-то старую кастрюлю."]


def _cap(text):
    return text[:1].upper() + text[1:]


def tile_of(ent):
    return ent.rect.centerx // T, ent.rect.centery // T


def rect_pos_for_tile(ent, tile):
    """Позиция rect.topleft, при которой хитбокс стоит в клетке (как при спавне)."""
    return (tile[0] * T + (T - ent.rect.w) // 2, tile[1] * T + T - ent.rect.h - 2)


def tile_center(tile):
    return (tile[0] * T + T // 2, tile[1] * T + T // 2)


def has_los(level, a, b):
    """Прямая видимость между двумя точками: вдоль отрезка (шаг 6 px) нет клеток,
    закрывающих обзор. Клетки самих концов не считаются — стоящий у стены видит."""
    ax, ay = a
    bx, by = b
    ends = {(int(ax) // T, int(ay) // T), (int(bx) // T, int(by) // T)}
    steps = int(max(abs(bx - ax), abs(by - ay)) / 6) + 1
    checked = set()
    for i in range(1, steps):
        t = (int(ax + (bx - ax) * i / steps) // T, int(ay + (by - ay) * i / steps) // T)
        if t in ends or t in checked:
            continue
        checked.add(t)
        if level.blocks_sight(*t):
            return False
    return True


def chebyshev(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


class Combat:
    def __init__(self, game):
        self.game = game
        self.active = False
        self.order = []
        self.turn_idx = 0
        self.round = 0
        self.busy_ms = 0
        self.tweens = []
        self.floaters = []  # всплывающий текст над головами: урон, «мимо», «броня»
        self.tracers = []   # вспышки выстрелов
        self.target = None
        self.aim_menu = False

    # ------------------------------------------------------------ состояние
    @property
    def current(self):
        return self.order[self.turn_idx] if self.active else None

    def is_player_turn(self):
        return self.active and self.current is self.game.player

    def player_can_act(self):
        return self.is_player_turn() and self.busy_ms <= 0 and not self.tweens

    def enemies_in_combat(self):
        return [e for e in self.order if e is not self.game.player and e.alive]

    def _dist(self, a, b):
        return pygame.Vector2(a.rect.center).distance_to(b.rect.center)

    def los(self, a, b):
        return has_los(self.game.level, a.rect.center, b.rect.center)

    def enemy_notices_player(self, enemy):
        p = self.game.player
        return enemy.hostile and self._dist(enemy, p) <= enemy.aggro and self.los(enemy, p)

    # ------------------------------------------------------ начало и конец
    def start(self, player_first):
        g = self.game
        p = g.player
        enemies = [e for e in g.enemies if e.alive and self.enemy_notices_player(e)]
        if player_first:
            # напасть первым можно на любого, кого видишь в пределах досягаемости оружия
            reach = max(WEAPONS[p.weapon]["range"] * T, 4 * T)
            enemies += [e for e in g.enemies if e.alive and e not in enemies
                        and self._dist(e, p) <= reach and self.los(e, p)]
        if not enemies:
            return False
        for e in list(enemies):
            if not e.hostile:  # напали на нейтрального — вся его фракция теперь враждебна
                g.make_hostile(e.faction)
            enemies += [m for m in self._pack_of(e) if m not in enemies]
        self.active = True
        self.round = 1
        self.tweens.clear()
        self.busy_ms = 0
        self.aim_menu = False
        g.craft_open = False
        if player_first:  # напал сам — ходишь первым
            self.order = [p] + enemies
        else:             # заметили тебя — очередь по Реакции
            self.order = sorted([p] + enemies, key=lambda f: -f.sequence)
        for f in self.order:
            self._snap_to_grid(f)
            if f is not p:
                f.anim.set_action("idle")
        g.log("— БОЙ! —" if player_first else f"{_cap(enemies[0].name)} замечает вас. — БОЙ! —")
        self.target = None
        self.turn_idx = 0
        self._begin_turn()
        return True

    def _pack_of(self, enemy):
        """Сородичи рядом (стая, рейдеры одного лагеря) поднимаются вместе."""
        return [e for e in self.game.enemies
                if e.alive and e is not enemy and e.hostile
                and (e.type_id == enemy.type_id or (e.faction and e.faction == enemy.faction)
                     or (e.pack and e.pack == enemy.pack))
                and chebyshev(tile_of(e), tile_of(enemy)) <= 5]

    def end(self, reason):
        self.active = False
        self.order = []
        self.target = None
        self.aim_menu = False
        self.tweens.clear()
        self.game.player.ap = self.game.player.max_ap
        self.game.log(reason)

    def _snap_to_grid(self, ent):
        """Ставит бойца в ближайшую свободную проходимую клетку."""
        taken = {tile_of(o) for o in self._obstacles() if o is not ent}
        start = tile_of(ent)
        q, seen = deque([start]), {start}
        while q:
            c = q.popleft()
            if self._walkable(c) and c not in taken:
                ent.rect.topleft = rect_pos_for_tile(ent, c)
                return
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (c[0] + d[0], c[1] + d[1])
                if n not in seen and 0 <= n[0] < self.game.level.width and 0 <= n[1] < self.game.level.height:
                    seen.add(n)
                    q.append(n)

    # --------------------------------------------------------------- ходы
    def _begin_turn(self):
        ent = self.current
        ent.ap = ent.max_ap
        if ent is self.game.player:
            ent.free_steps = 2 if ent.perk_rank("bonus_move") else 0
            self._check_new_enemies()
            if not self._still_threatened():
                self.end("Враги потеряли вас из виду. Бой окончен.")
                return
            if self.target not in self.enemies_in_combat():
                self.target = self._nearest_enemy()
        else:
            ent.retreated = False
        if ent.skip_turns > 0:
            ent.skip_turns -= 1
            self.game.log(f"{_cap(ent.name)} всё ещё приходит в себя и пропускает ход."
                          if ent is not self.game.player else "Вы приходите в себя и пропускаете ход.")
            self.busy_ms = S.COMBAT_ATTACK_MS
            ent.ap = 0
            if ent is self.game.player:
                ent.free_steps = 0

    def end_turn(self):
        self.aim_menu = False
        if not self.active:
            return
        if not self.enemies_in_combat():
            self.end("Бой окончен. Пустошь снова тиха.")
            return
        for _ in range(len(self.order)):
            self.turn_idx = (self.turn_idx + 1) % len(self.order)
            if self.turn_idx == 0:
                self.round += 1
            if self.current.alive:
                break
        self._begin_turn()

    def _check_new_enemies(self):
        for e in self.game.enemies:
            if e.alive and e not in self.order and self.enemy_notices_player(e):
                for m in [e] + self._pack_of(e):
                    if m not in self.order:
                        self._snap_to_grid(m)
                        self.order.append(m)
                        m.ap = m.max_ap
                self.game.log(f"{_cap(e.name)} присоединяется к драке.")

    def _still_threatened(self):
        """Враг, уже вступивший в бой, не теряет игрока за углом — только если
        тот ушёл далеко (дальше, чем радиус, на котором враг замечает, — иначе
        бой бы начинался и заканчивался каждый кадр)."""
        p = self.game.player
        return any(self._dist(e, p) <= e.aggro * 1.5 for e in self.enemies_in_combat())

    def _nearest_enemy(self):
        enemies = self.enemies_in_combat()
        if not enemies:
            return None
        p = tile_of(self.game.player)
        return min(enemies, key=lambda e: chebyshev(p, tile_of(e)))

    # ------------------------------------------------------------ движение
    def _walkable(self, tile):
        return not self.game.level.is_wall(*tile)

    def _obstacles(self):
        g = self.game
        return [g.player] + [e for e in g.enemies if e.alive] + list(g.npcs)

    def _occupied(self, except_ent=None):
        return {tile_of(o) for o in self._obstacles() if o is not except_ent}

    def _can_pay_step(self, ent):
        return ent.ap >= S.AP_MOVE or (ent is self.game.player and ent.free_steps > 0)

    def try_step(self, ent, dx, dy):
        if not self._can_pay_step(ent):
            return False
        if dx:
            ent.facing_left = dx < 0
        ent.anim.face(dx, dy)
        cur = tile_of(ent)
        nxt = (cur[0] + dx, cur[1] + dy)
        if not self._walkable(nxt) or nxt in self._occupied(except_ent=ent):
            return False
        if ent is self.game.player and ent.free_steps > 0:
            ent.free_steps -= 1
        else:
            ent.ap -= S.AP_MOVE
        self.tweens.append({"ent": ent, "from": pygame.Vector2(ent.rect.topleft),
                            "to": pygame.Vector2(rect_pos_for_tile(ent, nxt)), "t": 0})
        ent.anim.set_action("walk")
        return True

    def find_path(self, ent, done):
        """BFS по свободным клеткам до первой, где done(tile) истинно.
        Список клеток пути без стартовой ([] — уже на месте, None — не дойти)."""
        start = tile_of(ent)
        blocked = self._occupied(except_ent=ent)
        q, prev = deque([start]), {start: None}
        while q:
            c = q.popleft()
            if done(c):
                path = []
                while c != start:
                    path.append(c)
                    c = prev[c]
                return path[::-1]
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (c[0] + d[0], c[1] + d[1])
                if n not in prev and self._walkable(n) and n not in blocked:
                    prev[n] = c
                    q.append(n)
        return None

    def _path_next_step(self, ent, goal_ent, done=None):
        """Первый шаг (dx, dy) к цели; done(tile) — «сюда достаточно дойти»
        (по умолчанию — вплотную к цели). None — идти некуда."""
        goal = tile_of(goal_ent)
        path = self.find_path(ent, done or (lambda c: chebyshev(c, goal) == 1))
        if not path:
            return None
        start = tile_of(ent)
        return (path[0][0] - start[0], path[0][1] - start[1])

    # --------------------------------------------------------------- атака
    def profile(self, ent):
        """Чем атакует боец: дальний ли бой, дальность, цена в ОД, навык, урон."""
        p = self.game.player
        if ent is p:
            w = WEAPONS[p.weapon]
            if w["ranged"]:
                return {"ranged": True, "range": w["range"], "ap": w["ap"],
                        "skill": p.guns_skill, "damage": w["damage"], "ammo": w["ammo"]}
            return {"ranged": False, "range": 1, "ap": w["ap"], "skill": p.melee_skill,
                    "damage": p.damage, "ammo": None}
        ranged = ent.ai == "ranged"
        return {"ranged": ranged, "range": ent.range if ranged else 1,
                "ap": S.AP_ATTACK + (1 if ranged else 0), "skill": ent.skill,
                "damage": ent.damage, "ammo": None}

    def attack_cost(self, ent, part_idx=0):
        return self.profile(ent)["ap"] + (1 if part_idx else 0)

    def can_attack(self, attacker, defender):
        """(можно ли, причина — если нельзя)."""
        prof = self.profile(attacker)
        dist = chebyshev(tile_of(attacker), tile_of(defender))
        if not prof["ranged"]:
            return (dist == 1, "подойдите вплотную")
        if prof["ammo"] and not self.game.inventory.has(prof["ammo"]):
            return (False, "нет патронов")
        if dist > prof["range"]:
            return (False, "далеко")
        if not self.los(attacker, defender):
            return (False, "нет линии огня")
        return (True, "")

    def hit_chance(self, attacker, defender, part_idx=0):
        prof = self.profile(attacker)
        part = BODY_PARTS[part_idx]
        chance = prof["skill"] - self.defense(defender) + part["hit"] - (25 if attacker.blinded else 0)
        if prof["ranged"]:
            dist = chebyshev(tile_of(attacker), tile_of(defender))
            chance -= RANGE_PENALTY_PER_TILE * max(0, dist - 1)
        return max(S.HIT_CHANCE_MIN, min(S.HIT_CHANCE_MAX, chance))

    def defense(self, ent):
        """КБ бойца; у игрока — с надетой бронёй."""
        if ent is self.game.player:
            return ent.armor_class
        return ent.ac

    def crit_chance(self, attacker, part_idx=0):
        return S.BASE_CRIT_CHANCE + BODY_PARTS[part_idx]["crit"] + attacker.crit_bonus

    def armor_blocks(self, defender, part_idx):
        return defender.armor if BODY_PARTS[part_idx]["id"] not in defender.weak_parts else 0

    def attack(self, attacker, defender, part_idx=0):
        prof = self.profile(attacker)
        cost = self.attack_cost(attacker, part_idx)
        ok, _ = self.can_attack(attacker, defender)
        if attacker.ap < cost or not ok:
            return False
        attacker.ap -= cost
        attacker.facing_left = defender.rect.centerx < attacker.rect.centerx
        attacker.anim.face(defender.rect.centerx - attacker.rect.centerx,
                           defender.rect.centery - attacker.rect.centery)
        if attacker is self.game.player:
            attacker.play_attack("shoot" if prof["ranged"] else "melee")
        else:
            attacker.anim.play_once("attack_ranged" if prof["ranged"] else "attack_melee") \
                or attacker.anim.play_once("attack")
        self.busy_ms = S.COMBAT_ATTACK_MS
        sx = attacker.rect.centerx - self.game.cam.x
        if prof["ranged"]:
            self.game.audio.play("shot", sx)
        else:  # удар звучит в момент удара, а не замаха
            self.game.audio.play("melee", sx, delay_ms=100, volume=1.0 if attacker is self.game.player else 0.7)
        if prof["ammo"]:
            self.game.inventory.remove(prof["ammo"], 1)
        impact_ms = 140  # когда удар «доходит» до цели: вздрагивание, кровь, звук попадания
        if prof["ranged"]:
            impact_ms = self._fire_bullet(attacker, defender)

        part = BODY_PARTS[part_idx]
        is_player = attacker is self.game.player
        name = _cap(attacker.name)
        if random.randint(1, 100) > self.hit_chance(attacker, defender, part_idx):
            if is_player:
                text = random.choice(PLAYER_MISS_RANGED if prof["ranged"] else PLAYER_MISS_MELEE)
            else:
                text = random.choice(ENEMY_MISS_RANGED if prof["ranged"] else ENEMY_MISS_MELEE)
            self.game.log(text.format(name=name))
            self._float(defender, "мимо", (200, 200, 190))
            if prof["ranged"]:  # промах — пуля пролетает мимо цели
                b = self.tracers[-1]
                d = (b["to"] - b["from"])
                perp = pygame.Vector2(-d.y, d.x).normalize() * random.choice((-18, 18))
                b["to"] = b["to"] + d.normalize() * 170 + perp
            self._react(defender, attacker, "dodge", impact_ms)
            return True

        dmg = random.randint(max(1, prof["damage"] - 2), prof["damage"] + 2)
        if attacker.crippled_arms:
            dmg = max(1, dmg // 2)
        crit = random.randint(1, 100) <= self.crit_chance(attacker, part_idx)
        if crit:
            dmg = int(dmg * part["mult"])
        armor = 0 if crit else self.armor_blocks(defender, part_idx)  # крит находит щель в панцире
        absorbed = min(dmg, armor)
        dmg -= absorbed
        defender.apply_damage(dmg)
        if dmg > 0 and defender.alive:
            self._react(defender, attacker, "hit", impact_ms)
        if dmg > 0:  # звук попадания — вместе с вздрагиванием цели
            self.game.audio.play("hit", defender.rect.centerx - self.game.cam.x, delay_ms=impact_ms)
        if dmg > 0:  # кровь; от выстрела — ещё и ошмётки
            self.game.gore.hit(self.game.level, defender.rect, attacker.rect.center,
                               "ranged" if prof["ranged"] else "melee", crit=crit, kill=not defender.alive,
                               delay_ms=impact_ms)
        if dmg == 0:
            self._float(defender, "броня", (150, 170, 200))
        else:
            self._float(defender, f"-{dmg}" + ("!" if crit else ""),
                        (255, 220, 90) if crit else (230, 80, 60))

        if is_player:
            where = "" if part_idx == 0 else f" ({part['name']})"
            dname = _cap(defender.name)
            if crit:
                msg = random.choice(CRIT_TEXT[part["id"]]).format(name=dname)
                self.game.log(f"КРИТ{where}: {msg} {dmg} урона.")
                self._apply_crit_effect(defender, part["effect"])
            elif dmg == 0:
                self.game.log(f"{dname}: панцирь выдержал удар{where}. Цельтесь в глаза или ноги (Q)!")
            else:
                note = " Панцирь погасил часть." if absorbed else ""
                self.game.log(f"{dname} получает {dmg} урона{where}.{note}")
            if not defender.alive:
                self.game.on_enemy_killed(defender)
                if self.target is defender:
                    self.target = self._nearest_enemy()
        else:
            crit_note = " — КРИТ!" if crit else ""
            self.game.log(f"{name} {attacker.hit_verb}{crit_note}: {dmg} урона.")
        return True

    BULLET_SPEED = 2600   # px/с — пуля видна, но пролетает за доли секунды
    BULLET_DELAY = 90     # мс — вылет в момент вспышки в анимации выстрела

    def _fire_bullet(self, attacker, defender):
        """Пуля от дула (уровень груди, чуть впереди) к груди цели. Возвращает, через сколько мс она долетит."""
        side = 1 if defender.rect.centerx >= attacker.rect.centerx else -1
        a = pygame.Vector2(attacker.rect.centerx + side * 26, attacker.rect.bottom - 40)
        b = pygame.Vector2(defender.rect.centerx, defender.rect.bottom - 36)
        self.tracers.append({"from": a, "to": b, "t": -self.BULLET_DELAY})
        return self.BULLET_DELAY + int(a.distance_to(b) / self.BULLET_SPEED * 1000)

    def _react(self, defender, attacker, kind, delay_ms=140):
        """Цель поворачивается к нападающему и вздрагивает (hit) или уворачивается (dodge) —
        чуть позже замаха, чтобы реакция шла за ударом."""
        defender.anim.face(attacker.rect.centerx - defender.rect.centerx,
                           attacker.rect.centery - defender.rect.centery)
        defender.facing_left = attacker.rect.centerx < defender.rect.centerx
        defender.anim.play_once(kind, delay_ms=delay_ms)

    def _apply_crit_effect(self, ent, effect):
        if effect == "blinded":
            ent.blinded = True
        elif effect == "crippled_arms":
            ent.crippled_arms = True
        elif effect == "crippled_legs":
            ent.crippled_legs = True
            ent.ap = min(ent.ap, ent.max_ap)
        elif effect == "skip_turn":
            ent.skip_turns = 1

    def _float(self, ent, text, color):
        # надписи над одним бойцом не должны слипаться — новая встаёт выше самой верхней
        y = ent.rect.top - 58
        recent = [f["pos"].y for f in self.floaters if f["ent"] is ent and f["t"] < 900]
        if recent:
            y = min(y, min(recent) - 22)
        self.floaters.append({"text": text, "color": color, "t": 0, "ent": ent,
                              "pos": pygame.Vector2(ent.rect.centerx, y)})

    # ------------------------------------------------- действия игрока
    def player_step(self, dx, dy):
        if self.player_can_act() and not self.aim_menu:
            p = self.game.player
            if not self.try_step(p, dx, dy) and not self._can_pay_step(p):
                self.game.log("Не хватает ОД. R — конец хода.")

    def player_attack(self, part_idx=0):
        if not self.player_can_act():
            return
        self.aim_menu = False
        p, t = self.game.player, self.target
        if t is None:
            self.game.log("Некого бить.")
            return
        cost = self.attack_cost(p, part_idx)
        ok, reason = self.can_attack(p, t)
        if not ok:
            self.game.log(f"Атаковать нельзя: {reason}.")
        elif p.ap < cost:
            self.game.log(f"Не хватает ОД: атака стоит {cost}. R — конец хода.")
        else:
            self.attack(p, t, part_idx)

    def cycle_target(self):
        enemies = self.enemies_in_combat()
        if not enemies:
            return
        p = tile_of(self.game.player)
        enemies.sort(key=lambda e: chebyshev(p, tile_of(e)))
        i = enemies.index(self.target) if self.target in enemies else -1
        self.target = enemies[(i + 1) % len(enemies)]

    def spend_player_ap(self, cost):
        """Для действий вне боевого модуля (крафт, предметы). True — ОД списаны."""
        if not self.active:
            return True
        if not self.player_can_act() or self.game.player.ap < cost:
            self.game.log(f"В бою это стоит {cost} ОД — не хватает.")
            return False
        self.game.player.ap -= cost
        self.busy_ms = S.COMBAT_ATTACK_MS
        return True

    # -------------------------------------------------------------- кадр
    def update(self, dt_ms):
        for f in self.floaters:
            f["t"] += dt_ms
            f["pos"].y -= dt_ms * 0.03
        self.floaters = [f for f in self.floaters if f["t"] < 1100]
        for tr in self.tracers:  # пули: летят, пока не пройдут весь путь
            tr["t"] += dt_ms
        self.tracers = [tr for tr in self.tracers
                        if tr["t"] < tr["from"].distance_to(tr["to"]) / self.BULLET_SPEED * 1000]
        if not self.active:
            return

        for tw in self.tweens:
            tw["t"] = min(1.0, tw["t"] + dt_ms / S.COMBAT_STEP_MS)
            pos = tw["from"].lerp(tw["to"], tw["t"])
            tw["ent"].rect.topleft = (round(pos.x), round(pos.y))
        for tw in self.tweens:
            if tw["t"] >= 1.0:
                tw["ent"].rect.topleft = (int(tw["to"].x), int(tw["to"].y))
                tw["ent"].anim.set_action("idle")
        self.tweens = [tw for tw in self.tweens if tw["t"] < 1.0]

        if self.busy_ms > 0:
            self.busy_ms -= dt_ms
            return
        if self.tweens:
            return
        for e in self.order:
            if e is not self.game.player and e.alive and e.anim.action == "attack" and not e.anim.busy:
                e.anim.set_action("idle")

        if not self.game.player.alive:
            self.active = False
            return
        if not self.enemies_in_combat():
            self.end("Бой окончен. Пустошь снова тиха.")
            return

        ent = self.current
        if ent is self.game.player:
            if ent.ap <= 0 and ent.free_steps <= 0:
                self.end_turn()  # как в Fallout с автозавершением: ОД кончились — ход врага
        elif ent.ai == "ranged":
            self._enemy_ranged(ent)
        else:
            self._enemy_melee(ent)

    def _enemy_melee(self, enemy):
        p = self.game.player
        if chebyshev(tile_of(enemy), tile_of(p)) == 1:
            if enemy.ap >= self.attack_cost(enemy):
                self.attack(enemy, p)
                return
        elif enemy.ap >= S.AP_MOVE:
            step = self._path_next_step(enemy, p)
            if step and self.try_step(enemy, *step):
                return
        self.end_turn()

    def _enemy_ranged(self, enemy):
        """Стрелок: держит дистанцию, стреляет по линии огня, ищет позицию, если её нет."""
        p = self.game.player
        cost = self.attack_cost(enemy)
        here = tile_of(enemy)
        # игрок вплотную — один раз за ход отступает, если после этого хватит ОД на выстрел
        if chebyshev(here, tile_of(p)) == 1 and not enemy.retreated and enemy.ap >= S.AP_MOVE + cost:
            enemy.retreated = True
            if self._step_away(enemy, p):
                return
        ok, _ = self.can_attack(enemy, p)
        if ok and enemy.ap >= cost:
            self.attack(enemy, p)
            return
        if not ok and enemy.ap >= S.AP_MOVE:
            goal = tile_of(p)
            good = lambda c: (chebyshev(c, goal) <= enemy.range
                              and has_los(self.game.level, tile_center(c), tile_center(goal)))
            step = self._path_next_step(enemy, p, done=good)
            if step and self.try_step(enemy, *step):
                return
        self.end_turn()

    def _step_away(self, enemy, p):
        here, goal = tile_of(enemy), tile_of(p)
        best = None
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (here[0] + d[0], here[1] + d[1])
            if (self._walkable(n) and n not in self._occupied(except_ent=enemy)
                    and chebyshev(n, goal) > 1
                    and has_los(self.game.level, tile_center(n), tile_center(goal))):
                best = d
                break
        return bool(best) and self.try_step(enemy, *best)
