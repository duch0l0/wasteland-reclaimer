"""Игровые сущности: игрок, враг-мутант, NPC."""
import pygame

from . import settings as S
from . import items
from . import skills
from .animator import Animator
from .leveling import LevelSystem


# Коллизионный прямоугольник — «ноги» персонажа, а не весь спрайт: спрайт
# рисуется от midbottom, так что он может быть выше хитбокса. Хитбокс должен
# быть меньше тайла, иначе персонаж не пролезет в коридор шириной в 1 тайл.
HUMANOID_HITBOX = (28, 32)


def _hitbox_in_tile(pos, size):
    """Хитбокс по центру тайла по горизонтали, прижатый к его низу."""
    w, h = size
    return pygame.Rect(pos[0] + (S.TILE - w) // 2, pos[1] + S.TILE - h - 2, w, h)


def sprite_of(ent, cam):
    """Текущий кадр персонажа и где он на экране: спрайт стоит «ногами» на хитбоксе
    (изометрический персонаж — точкой ног из его кадров)."""
    frame = ent.anim.current_frame(flip=getattr(ent, "facing_left", False))
    fx, fy = cam.foot(ent) if hasattr(cam, "foot") else (ent.rect.centerx - cam.x, ent.rect.bottom - cam.y)
    foot = getattr(ent.anim, "foot", None)
    if foot:
        return frame, frame.get_rect(topleft=(round(fx - foot[0]), round(fy - foot[1])))
    return frame, frame.get_rect(midbottom=(round(fx), round(fy)))


_VISIBLE = {}


def visible_rect(ent, cam):
    """Где на экране видимая фигура (без прозрачных полей кадра) — для полосок здоровья и
    облачков речи: у героя кадр с запасом сверху под поднятый лом."""
    frame, r = sprite_of(ent, cam)
    key = id(frame)
    box = _VISIBLE.get(key)
    if box is None or box[0] is not frame:
        box = _VISIBLE[key] = (frame, frame.get_bounding_rect(min_alpha=10))
    b = box[1]
    return pygame.Rect(r.x + b.x, r.y + b.y, b.w, b.h) if b.w and b.h else r


class CombatStats:
    """Общие для игрока и врагов поля пошагового боя: ОД и травмы от критов."""
    armor = 0                  # панцирь: сколько урона гасит (у жука)
    weak_parts = frozenset()   # части тела, где панциря нет
    retreated = False          # стрелок уже отступал в этом ходу
    def init_combat_stats(self, max_ap, ac, sequence):
        self.base_ap = max_ap
        self.ap = max_ap
        self.ac = ac
        self.sequence = sequence
        self.blinded = False          # крит в глаза: -25% к попаданию
        self.crippled_legs = False    # крит в ноги: -3 ОД каждый ход
        self.crippled_arms = False    # крит в руки: урон вдвое меньше
        self.skip_turns = 0           # крит в пах: пропуск хода
        self.dots = []                # урон со временем: [{"kind": "poison"/"fire", "dmg", "turns"}]

    @property
    def max_ap(self):
        return max(2, self.base_ap - (3 if self.crippled_legs else 0))

    def apply_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.alive = False


class Player(CombatStats):
    name = "Вы"

    def __init__(self, pos, animations):
        self.rect = _hitbox_in_tile(pos, HUMANOID_HITBOX)
        self.anim = Animator(animations, frame_ms=S.ANIM_FRAME_MS)
        self.facing_left = False
        self.hp = S.PLAYER_BASE_HP
        self.max_hp = S.PLAYER_BASE_HP
        self.base_damage = S.PLAYER_BASE_DMG
        self.inventory = None  # рюкзак (ставит Game) — от него зависят бонусы предметов
        self.equipment = {slot: None for slot in items.SLOTS}  # надетая броня по слотам
        self.level_sys = LevelSystem(S.XP_TO_LEVEL)
        self.attack_cd = 0
        self.attacking = False
        self.alive = True
        self.init_combat_stats(S.PLAYER_AP, S.PLAYER_AC, S.PLAYER_SEQUENCE)
        self.weapon = "melee"   # ключ из src/weapons.py
        self.perks = {}         # id перка -> ранг
        self.free_steps = 0     # перк «Бонус движения»: бесплатные шаги в этом ходу
        self.pending_perks = 0  # сколько перков ждут выбора (перк — на чётных уровнях)
        self.skills = skills.defaults()   # навыки (src/skills.py): растут по выбору при повышении уровня
        self.pending_skills = 0 # сколько повышений навыка ждут выбора
        self.rads = 0           # радиация: каждые 10 рад отъедают 1 HP от максимума (как в Fallout 4)

    @property
    def hp_cap(self):
        """Сколько HP можно иметь при текущей радиации."""
        return max(5, self.max_hp - self.rads // 10)

    def add_rads(self, n):
        self.rads = max(0, min(self.max_hp * 10 - 50, self.rads + n))
        self.hp = min(self.hp, self.hp_cap)

    def perk_rank(self, perk_id):
        return self.perks.get(perk_id, 0)

    def equipped(self, slot):
        """Что надето в слот. Если предмета больше нет в рюкзаке (продан, отдан) — слот пуст."""
        name = self.equipment.get(slot)
        if name and (self.inventory is None or not self.inventory.has(name)):
            self.equipment[slot] = name = None
        return name

    def equip_mod(self, stat):
        """Сумма бонусов надетого к характеристике (armor_ac, ap, guns)."""
        return sum(items.mod(self.equipped(s), stat) for s in items.SLOTS if self.equipped(s))

    @property
    def armor_class(self):
        return self.ac + self.equip_mod("armor_ac")

    @property
    def max_ap(self):
        return max(2, self.base_ap + self.equip_mod("ap") - (3 if self.crippled_legs else 0))

    def skill(self, skill_id):
        return self.skills.get(skill_id, skills.SKILL_BY_ID[skill_id]["base"])

    @property
    def melee_skill(self):
        return self.skill("melee")

    @property
    def guns_skill(self):
        return self.skill("guns") + 15 * self.perk_rank("steady_hand") + self.equip_mod("guns")

    @property
    def crit_bonus(self):
        return 10 * self.perk_rank("sharp_eye")

    @property
    def damage(self):
        """Урон в ближнем бою (у самопала свой — см. src/weapons.py).
        Заточенный лом даёт +3, пока лежит в рюкзаке."""
        sharp = 3 if self.inventory is not None and self.inventory.has("заточенный лом") else 0
        return (self.base_damage + max(0, (self.melee_skill - 60) // 10) + 3 * self.perk_rank("heavy_hand")
                + sharp)

    iso = False   # на изометрической карте клавиши двигают по экрану, а не по сетке

    def handle_input(self, keys, dt_ms, solid_rects):
        if not self.alive:
            return
        dx = dy = 0
        speed = S.PLAYER_SPEED * dt_ms / 1000
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += speed
        if self.iso and (dx or dy):
            from .iso import input_to_world
            ux, uy = input_to_world(dx, dy)
            dx, dy = ux * speed, uy * speed
        self.walk(dx, dy, solid_rects)

    def walk(self, dx, dy, solid_rects):
        """Сдвиг на (dx, dy) пикселей со стенами; анимация и поворот — по движению."""
        moving = dx != 0 or dy != 0
        if dx:
            self.facing_left = dx < 0
        self.anim.face(dx, dy)

        self._move_axis(dx, 0, solid_rects)
        self._move_axis(0, dy, solid_rects)

        if self.attacking:
            self.anim.set_action("attack")
        elif moving:
            self.anim.set_action("walk")
        else:
            self.anim.set_action("idle")

    def _move_axis(self, dx, dy, solid_rects):
        self.rect.x += int(dx)
        self.rect.y += int(dy)
        for r in solid_rects:
            if self.rect.colliderect(r):
                if dx > 0:
                    self.rect.right = r.left
                elif dx < 0:
                    self.rect.left = r.right
                if dy > 0:
                    self.rect.bottom = r.top
                elif dy < 0:
                    self.rect.top = r.bottom

    def try_attack(self):
        if self.attack_cd <= 0 and not self.attacking:
            self.attacking = True
            self.anim.set_action("attack")
            self.attack_cd = S.PLAYER_ATTACK_COOLDOWN_MS
            return True
        return False

    def play_attack(self, kind="melee"):
        """Анимация удара (melee) или выстрела (shoot) — в пошаговом бою темп задаёт ОД."""
        self.attacking = True
        if not self.anim.play_once(kind):
            self.anim.play_once("attack")

    def attack_hitbox(self):
        w = S.PLAYER_ATTACK_RANGE
        # по вертикали шире хитбокса ног — бьём на уровне всего тела
        top, h = self.rect.top - 12, self.rect.height + 24
        if self.facing_left:
            return pygame.Rect(self.rect.left - w, top, w, h)
        return pygame.Rect(self.rect.right, top, w, h)

    def update(self, dt_ms):
        self.anim.update(dt_ms)
        if self.attack_cd > 0:
            self.attack_cd -= dt_ms
        if self.attacking and not self.anim.busy and (self.anim.action != "attack" or self.anim.is_finished_once()):
            self.attacking = False

    def gain_xp(self, amount):
        before = self.level_sys.level
        msgs = self.level_sys.add_xp(amount)
        if msgs:
            new = range(before + 1, self.level_sys.level + 1)
            self.pending_skills += len(new)                          # навык — каждый уровень
            self.pending_perks += sum(1 for lv in new if lv % 2 == 0)  # перк — на чётных
            self.max_hp += S.HP_PER_LEVEL * len(new) + 2 * self.perk_rank("lifegiver") * len(new)
            self.hp = self.hp_cap
        return msgs

    def draw(self, surf, cam):
        frame, r = sprite_of(self, cam)
        surf.blit(frame, r)


class Enemy(CombatStats):
    """Враг, собранный по описанию типа из data/enemies.json."""
    crit_bonus = 0

    def __init__(self, pos, animations, type_id, d):
        self.type_id = type_id
        self.rect = _hitbox_in_tile(pos, tuple(d.get("hitbox", (30, 32))))
        self.anim = Animator(animations, frame_ms=S.ANIM_FRAME_MS)
        self.name = d["name"]
        self.hp = self.max_hp = d["hp"]
        self.damage = d["damage"]
        self.skill = d["skill"]
        self.aggro = d.get("aggro", 220)
        self.xp_reward = d.get("xp", 10)
        self.level = d.get("level", 1)                 # насколько опасен: опыт за убийство зависит от разницы
        self.burst = d.get("burst", 1)                 # выстрелов в очереди
        self.loot = dict(d.get("loot", {}))
        self.ai = d.get("ai", "melee")
        self.range = d.get("range", 1)
        self.hit_verb = d.get("hit_verb", "бьёт вас")
        self.armor = d.get("armor", 0)                 # сколько урона гасит панцирь
        self.weak_parts = set(d.get("weak_parts", []))  # куда броня не прикрывает
        # особенности для разнообразия боя (см. src/combat.py)
        self.poison = d.get("poison", 0)       # ядовитые когти: урон за ход, 3 хода
        self.rads = d.get("rads", 0)           # облучает при попадании
        self.coward = d.get("coward", False)   # при малом HP убегает
        self.grenades = d.get("grenades", 0)   # сколько гранат бросит
        self.stims = d.get("stims", 0)         # сколько раз уколется стимулятором
        self.robot = d.get("robot", False)     # не кровоточит, яд не берёт
        self.faction = d.get("faction")   # у фракции (банды) враги нейтральны, пока их не разозлить
        self.hostile = self.faction is None
        self.talk = d.get("talk")         # id диалога: такой враг сначала заговаривает
        self.pack = d.get("pack")         # стая: вся стая рядом вступает в бой разом
        self.talked = False
        self.facing_left = False
        self.alive = True
        self.init_combat_stats(d["ap"], d["ac"], d["sequence"])

    def update(self, dt_ms):
        """Только анимация: ходит и бьёт враг лишь в пошаговом бою (src/combat.py)."""
        if self.alive:
            self.anim.update(dt_ms)

    def draw(self, surf, cam):
        frame, r = sprite_of(self, cam)
        surf.blit(frame, r)


class NPC:
    def __init__(self, pos, animations, npc_id, name):
        self.rect = _hitbox_in_tile(pos, HUMANOID_HITBOX)
        self.anim = Animator(animations, frame_ms=S.ANIM_FRAME_MS)
        self.npc_id = npc_id
        self.name = name

    def update(self, dt_ms):
        self.anim.update(dt_ms)

    def draw(self, surf, cam):
        frame, r = sprite_of(self, cam)
        surf.blit(frame, r)


class Companion(CombatStats):
    """Спутник героя (пёс). В бою ходит сам: бежит к ближайшему врагу и кусает.
    Выбитый из боя (down) лежит до конца боя, потом поднимается с 1 HP."""
    ally = True
    crit_bonus = 0
    talk = None
    hostile = False
    faction = "ally"
    pack = None
    loot = {}
    ai = "melee"
    range = 1
    aggro = 0

    def __init__(self, pos, animations, name="Псина"):
        self.type_id = "dog"
        self.rect = _hitbox_in_tile(pos, (24, 20))
        self.anim = Animator(animations, frame_ms=S.ANIM_FRAME_MS)
        self.name = name
        self.hp = self.max_hp = 30
        self.damage = 5
        self.skill = 60
        self.hit_verb = "вцепляется в противника"
        self.facing_left = False
        self.alive = True
        self.down = False
        self.regen_ms = 0
        self.init_combat_stats(8, 15, 7)

    def update(self, dt_ms):
        self.anim.update(dt_ms)
