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
        self.throws = []    # летящие гранаты/бутылки: взрываются по прилёте
        self.blasts = []    # вспышки взрывов (для картинки)

    # ------------------------------------------------------------ состояние
    @property
    def current(self):
        return self.order[self.turn_idx] if self.active else None

    def is_player_turn(self):
        return self.active and self.current is self.game.player

    def player_can_act(self):
        return self.is_player_turn() and self.busy_ms <= 0 and not self.tweens

    @staticmethod
    def is_ally(e):
        return getattr(e, "ally", False)

    def enemies_in_combat(self):
        return [e for e in self.order if e is not self.game.player and not self.is_ally(e) and e.alive]

    def allies_in_combat(self):
        return [e for e in self.order if self.is_ally(e) and e.alive]

    def _companion_here(self):
        c = self.game.companion
        return c if c is not None and c.alive and not c.down else None

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
        allies = [c for c in (self._companion_here(),) if c]
        if player_first:  # напал сам — ходишь первым, спутник сразу за тобой
            self.order = [p] + allies + enemies
        else:             # заметили тебя — очередь по Реакции
            self.order = sorted([p] + allies + enemies, key=lambda f: -f.sequence)
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
        if self._tick_dots(ent):   # яд или огонь добили — ход следующему
            self.busy_ms = S.COMBAT_ATTACK_MS
            if self.active and self.game.player.alive:
                self._advance()
            return
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
        self._advance()

    def _advance(self):
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
        return ([g.player] + [e for e in g.enemies if e.alive] + list(g.npcs)
                + [c for c in (g.companion,) if c is not None and c.alive])

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
        ranged = ent.ai in ("ranged", "turret")
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
            if self.in_cover(attacker, defender):
                chance -= self.COVER_PENALTY
        return max(S.HIT_CHANCE_MIN, min(S.HIT_CHANCE_MAX, chance))

    COVER_PENALTY = 25

    def in_cover(self, attacker, defender):
        """Цель за низким укрытием (мешки, ящики, бочки) со стороны стрелка: клетка рядом
        с целью в сторону стрелка непроходима, но обзор не закрывает."""
        (ax, ay), (dx, dy) = tile_of(attacker), tile_of(defender)
        if chebyshev((ax, ay), (dx, dy)) <= 1:
            return False
        sx = (ax > dx) - (ax < dx)
        sy = (ay > dy) - (ay < dy)
        lv = self.game.level
        for t in {(dx + sx, dy + sy), (dx + sx, dy), (dx, dy + sy)} - {(dx, dy)}:
            if lv.is_wall(*t) and not lv.blocks_sight(*t) and not lv.is_exit(*t):
                return True
        return False

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
        ally_attacks = self.is_ally(attacker)
        name = _cap(attacker.name)
        if random.randint(1, 100) > self.hit_chance(attacker, defender, part_idx):
            if ally_attacks:
                self.game.log(f"{name} щёлкает зубами — мимо.")
                self._float(defender, "мимо", (200, 200, 190))
                self._react(defender, attacker, "dodge", impact_ms)
                return True
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
        if dmg > 0 and not getattr(defender, "robot", False):  # кровь; от выстрела — ещё и ошмётки
            self.game.gore.hit(self.game.level, defender.rect, attacker.rect.center,
                               "ranged" if prof["ranged"] else "melee", crit=crit, kill=not defender.alive,
                               delay_ms=impact_ms)
        if dmg > 0 and defender.alive and not getattr(defender, "robot", False):
            if getattr(attacker, "poison", 0):
                self._add_dot(defender, "poison", attacker.poison, 3)
            if getattr(attacker, "rads", 0) and defender is self.game.player:
                defender.add_rads(attacker.rads)
                self._float(defender, f"+{attacker.rads} рад", (140, 230, 90))
        if dmg == 0:
            self._float(defender, "броня", (150, 170, 200))
        else:
            self._float(defender, f"-{dmg}" + ("!" if crit else ""),
                        (255, 220, 90) if crit else (230, 80, 60))

        if ally_attacks:
            self.game.log(f"{name} {attacker.hit_verb} ({defender.name}): {dmg} урона" + (" — КРИТ!" if crit else "."))
            if not defender.alive:
                self.game.on_enemy_killed(defender)
                if self.target is defender:
                    self.target = self._nearest_enemy()
        elif self.is_ally(defender):
            crit_note = " — КРИТ!" if crit else ""
            self.game.log(f"{name} бьёт: {defender.name} получает {dmg} урона{crit_note}.")
            if not defender.alive:
                defender.down = True
                defender.anim.set_action("idle")
                self.game.log(f"{defender.name} скулит и отползает — выбыл из боя.")
        elif is_player:
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
        for b in self.blasts:
            b["t"] += dt_ms
        self.blasts = [b for b in self.blasts if b["t"] < 700]
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

        self._update_throws(dt_ms)
        if self.busy_ms > 0:
            self.busy_ms -= dt_ms
            return
        if self.tweens or self.throws:
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
        elif self.is_ally(ent):
            self._ally_turn(ent)
        elif self._enemy_special(ent):
            return
        elif ent.ai == "turret":
            self._enemy_turret(ent)
        elif ent.ai == "ranged":
            self._enemy_ranged(ent)
        else:
            self._enemy_melee(ent)

    def _enemy_target(self, enemy):
        """Кого бить: ближайшего из героя и спутника (при равенстве — героя)."""
        here = tile_of(enemy)
        cands = [self.game.player] + self.allies_in_combat()
        return min(cands, key=lambda c: (chebyshev(here, tile_of(c)), c is not self.game.player))

    def _ally_turn(self, ally):
        """Спутник: к ближайшему врагу и кусать, пока хватает ОД."""
        enemies = self.enemies_in_combat()
        if not enemies:
            self.end_turn()
            return
        here = tile_of(ally)
        t = min(enemies, key=lambda e: chebyshev(here, tile_of(e)))
        if chebyshev(here, tile_of(t)) == 1:
            if ally.ap >= self.attack_cost(ally) and self.attack(ally, t):
                return
        elif ally.ap >= S.AP_MOVE:
            step = self._path_next_step(ally, t)
            if step and self.try_step(ally, *step):
                return
        self.end_turn()

    def _enemy_melee(self, enemy):
        p = self._enemy_target(enemy)
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
        p = self._enemy_target(enemy)
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

    # ------------------------------------------------------ урон вне атаки
    def _add_dot(self, ent, kind, dmg, turns):
        for d in ent.dots:
            if d["kind"] == kind:
                d["turns"] = max(d["turns"], turns)
                d["dmg"] = max(d["dmg"], dmg)
                return
        ent.dots.append({"kind": kind, "dmg": dmg, "turns": turns})
        who = "Вы" if ent is self.game.player else _cap(ent.name)
        self.game.log(f"{who}: {'яд в крови' if kind == 'poison' else 'горит'}!")

    def _tick_dots(self, ent):
        """Яд и огонь в начале хода. True — боец от этого погиб."""
        if not ent.dots or not ent.alive:
            return False
        total = 0
        for d in ent.dots:
            total += d["dmg"]
            d["turns"] -= 1
        kinds = {d["kind"] for d in ent.dots}
        ent.dots = [d for d in ent.dots if d["turns"] > 0]
        what = " и ".join(k for k in (("яд" if "poison" in kinds else ""), ("огонь" if "fire" in kinds else "")) if k)
        who = "Вас" if ent is self.game.player else _cap(ent.name)
        self.game.log(f"{what.capitalize()} жжёт: {who.lower() if ent is self.game.player else who} −{total} HP.")
        self.hurt(ent, total, (150, 220, 90) if "poison" in kinds else (255, 150, 60))
        return not ent.alive

    def hurt(self, ent, dmg, color=(230, 120, 60), source=None):
        """Урон не от удара (взрыв, яд, огонь): число над головой, вздрагивание, смерть."""
        if dmg <= 0 or not ent.alive:
            return
        ent.apply_damage(dmg)
        self._float(ent, f"-{dmg}", color)
        if ent.alive:
            ent.anim.play_once("hit")
            return
        g = self.game
        if ent is g.player:
            return
        if self.is_ally(ent):
            ent.down = True
            ent.anim.set_action("idle")
            g.log(f"{ent.name} скулит и отползает — выбыл из боя.")
            return
        if ent in g.enemies:
            g.on_enemy_killed(ent)
            if self.target is ent:
                self.target = self._nearest_enemy()

    # ------------------------------------------------------ броски и взрывы
    THROW_AP = 4
    THROW_RANGE = 6
    THROW_MS = 520

    def throw(self, thrower, tile, kind):
        """Бросок гранаты/бутылки в клетку: летит дугой, по прилёте взрывается."""
        thrower.ap -= self.THROW_AP
        thrower.anim.face(tile[0] * T - thrower.rect.centerx, tile[1] * T - thrower.rect.centery)
        thrower.anim.play_once("attack_ranged") or thrower.anim.play_once("attack")
        a = pygame.Vector2(thrower.rect.centerx, thrower.rect.top + 10)
        b = pygame.Vector2(tile_center(tile))
        self.throws.append({"from": a, "to": b, "tile": tile, "t": 0, "kind": kind, "by": thrower,
                            "dur": self.THROW_MS + int(a.distance_to(b) * 0.4)})
        self.busy_ms = S.COMBAT_ATTACK_MS

    def _update_throws(self, dt_ms):
        for th in self.throws:
            th["t"] += dt_ms
        landed = [th for th in self.throws if th["t"] >= th["dur"]]
        self.throws = [th for th in self.throws if th["t"] < th["dur"]]
        for th in landed:
            self.explode(th["tile"], th["kind"], th["by"])

    def explode(self, tile, kind, by=None):
        """Взрыв гранаты/бочки (урон всем в радиусе 1) или вспышка коктейля (поджигает)."""
        g = self.game
        cx, cy = tile_center(tile)
        self.blasts.append({"pos": pygame.Vector2(cx, cy), "t": 0, "kind": kind})
        g.audio.play("shot", cx - g.cam.x, volume=1.0)
        g.audio.play("hit", cx - g.cam.x, delay_ms=60)
        fighters = [g.player] + [e for e in g.enemies if e.alive] + \
            [c for c in (g.companion,) if c is not None and c.alive and not c.down]
        hit = [e for e in fighters if e.alive and chebyshev(tile_of(e), tile) <= 1]
        if kind == "molotov":
            g.log("Бутылка разбивается — пламя разливается по земле!")
            for e in hit:
                self.hurt(e, random.randint(3, 5), (255, 150, 60))
                if e.alive:
                    self._add_dot(e, "fire", 3, 3)
        else:
            g.log("БУМ! " + ("Бочка взрывается!" if kind == "barrel" else "Граната рвётся!"))
            lo, hi = (12, 18) if kind == "barrel" else (7, 12)
            for e in hit:
                dmg = random.randint(lo, hi) if tile_of(e) == tile else random.randint(lo // 2, hi // 2)
                if e is not g.player and e.alive:
                    g.gore.hit(g.level, e.rect, (cx, cy), "ranged", crit=True, kill=dmg >= e.hp, delay_ms=0)
                self.hurt(e, dmg, (255, 200, 80))
        # рядом с бочкой — цепная реакция
        for b in self.barrels_near(tile, 1):
            self.blow_barrel(b)
        # бой мог начаться со взрыва — например, герой подорвал бочку рядом с врагами
        if not self.active and any(e.alive for e in hit if e in g.enemies):
            for e in hit:
                if e in g.enemies and e.alive and not e.hostile:
                    g.make_hostile(e.faction)
            self.start(player_first=True)

    def barrels_near(self, tile, r):
        objs = getattr(self.game.level, "objects", [])
        from . import props as P
        return [o for o in objs if not o.get("hidden") and P.info(o["name"]).get("explosive")
                and any(chebyshev(t, tile) <= r for t in o["foot"])]

    def blow_barrel(self, obj):
        if obj.get("hidden"):
            return
        self.game.level.remove_object(obj)
        self.explode(obj["foot"][0], "barrel")

    def player_throw(self):
        """G: бросить гранату (или коктейль Молотова) в текущую цель."""
        if not self.player_can_act():
            return
        g, p, t = self.game, self.game.player, self.target
        kind = "grenade" if g.inventory.has("граната") else "molotov" if g.inventory.has("коктейль Молотова") else None
        if kind is None:
            g.log("Бросать нечего. Гранаты бывают у бандитов, коктейль Молотова — в крафте (C).")
            return
        if t is None or not t.alive:
            g.log("Некуда бросать — нет цели (Tab).")
            return
        dist = chebyshev(tile_of(p), tile_of(t))
        if dist > self.THROW_RANGE or not self.los(p, t):
            g.log("Не докинуть: цель далеко или за стеной.")
            return
        if dist <= 1:
            g.log("Слишком близко — заденет и вас. Отойдите хотя бы на клетку.")
            return
        if p.ap < self.THROW_AP:
            g.log(f"Бросок стоит {self.THROW_AP} ОД — не хватает.")
            return
        g.inventory.remove("граната" if kind == "grenade" else "коктейль Молотова")
        tile = tile_of(t)
        if random.randint(1, 100) > 75:  # недолёт/перелёт на клетку
            tile = (tile[0] + random.choice((-1, 0, 1)), tile[1] + random.choice((-1, 0, 1)))
        g.log("Вы бросаете " + ("гранату." if kind == "grenade" else "коктейль Молотова."))
        self.throw(p, tile, kind)

    def player_shoot_barrel(self, obj):
        """Выстрел по красной бочке: попал — взрыв."""
        if not self.player_can_act():
            return
        g, p = self.game, self.game.player
        prof = self.profile(p)
        tile = obj["foot"][0]
        dist = chebyshev(tile_of(p), tile)
        if not prof["ranged"] and dist > 1:
            g.log("Бочку ломом? Только вплотную. И лучше не надо.")
            return
        if prof["ranged"] and (dist > prof["range"] or
                               not has_los(g.level, p.rect.center, tile_center(tile))):
            g.log("Не достать: далеко или нет линии огня.")
            return
        if prof["ammo"] and not g.inventory.has(prof["ammo"]):
            g.log("Нет патронов.")
            return
        if p.ap < prof["ap"]:
            g.log(f"Не хватает ОД: выстрел стоит {prof['ap']}.")
            return
        p.ap -= prof["ap"]
        p.play_attack("shoot" if prof["ranged"] else "melee")
        self.busy_ms = S.COMBAT_ATTACK_MS
        if prof["ammo"]:
            g.inventory.remove(prof["ammo"], 1)
        chance = max(S.HIT_CHANCE_MIN, 95 - RANGE_PENALTY_PER_TILE * max(0, dist - 1))
        if prof["ranged"]:
            g.audio.play("shot", p.rect.centerx - g.cam.x)
            a = pygame.Vector2(p.rect.centerx, p.rect.bottom - 40)
            self.tracers.append({"from": a, "to": pygame.Vector2(tile_center(tile)), "t": -self.BULLET_DELAY})
        if random.randint(1, 100) <= chance:
            self.blow_barrel(obj)
        else:
            g.log("Мимо бочки. Она облегчённо булькает.")

    # ------------------------------------------------------ особые приёмы врагов
    def _enemy_special(self, enemy):
        """Трус бежит, главарь колется стимулятором, бандит бросает гранату.
        True — действие сделано (или ход закончен)."""
        g = self.game
        low = enemy.hp <= enemy.max_hp * 0.3
        if enemy.stims and enemy.hp <= enemy.max_hp * 0.4 and enemy.ap >= 2:
            enemy.stims -= 1
            enemy.ap -= 2
            heal = min(enemy.max_hp - enemy.hp, 15)
            enemy.hp += heal
            self._float(enemy, f"+{heal}", (120, 230, 120))
            g.log(f"{_cap(enemy.name)} всаживает себе стимулятор в бедро. +{heal} HP.")
            self.busy_ms = S.COMBAT_ATTACK_MS
            return True
        if enemy.coward and low:
            p = self._enemy_target(enemy)
            if chebyshev(tile_of(enemy), tile_of(p)) >= 7 and not self.los(enemy, p):
                g.log(f"{_cap(enemy.name)} удирает, поджав хвост.")
                g.loc.enemies[:] = [e for e in g.enemies if e is not enemy]
                self.order.remove(enemy)
                self.turn_idx = (self.turn_idx - 1) % max(1, len(self.order))
                self.end_turn()
                return True
            if enemy.ap >= S.AP_MOVE and self._flee_step(enemy, p):
                if not getattr(enemy, "fleeing", False):
                    enemy.fleeing = True
                    g.log(f"{_cap(enemy.name)} в панике бросается бежать!")
                return True
        if enemy.grenades and enemy.ap >= self.THROW_AP:
            p = self._enemy_target(enemy)
            dist = chebyshev(tile_of(enemy), tile_of(p))
            near_allies = [e for e in self.enemies_in_combat() if e is not enemy
                           and chebyshev(tile_of(e), tile_of(p)) <= 1]
            if 2 <= dist <= 5 and self.los(enemy, p) and not near_allies and random.random() < 0.6:
                enemy.grenades -= 1
                g.log(f"{_cap(enemy.name)} выдёргивает чеку и бросает гранату!")
                self.throw(enemy, tile_of(p), "grenade")
                return True
        return False

    def _flee_step(self, enemy, p):
        here, goal = tile_of(enemy), tile_of(p)
        options = []
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (here[0] + d[0], here[1] + d[1])
            if self._walkable(n) and n not in self._occupied(except_ent=enemy):
                options.append((chebyshev(n, goal), d))
        options = [o for o in options if o[0] > chebyshev(here, goal) or o[0] >= 7]
        if not options:
            return False
        return self.try_step(enemy, *max(options)[1])

    def _enemy_turret(self, enemy):
        """Турель: не двигается, стреляет, пока хватает ОД (очередь)."""
        p = self._enemy_target(enemy)
        if self.can_attack(enemy, p)[0] and enemy.ap >= self.attack_cost(enemy):
            self.attack(enemy, p)
            return
        self.end_turn()
