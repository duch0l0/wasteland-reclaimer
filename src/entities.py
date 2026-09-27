"""Игровые сущности: игрок, враг-мутант, NPC."""
import pygame

from . import settings as S
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
        self.level_sys = LevelSystem(S.XP_TO_LEVEL)
        self.attack_cd = 0
        self.attacking = False
        self.alive = True
        self.init_combat_stats(S.PLAYER_AP, S.PLAYER_AC, S.PLAYER_SEQUENCE)
        self.weapon = "melee"   # ключ из src/weapons.py
        self.perks = {}         # id перка -> ранг
        self.free_steps = 0     # перк «Бонус движения»: бесплатные шаги в этом ходу
        self.pending_perks = 0  # сколько перков ждут выбора

    def perk_rank(self, perk_id):
        return self.perks.get(perk_id, 0)

    @property
    def melee_skill(self):
        return S.PLAYER_MELEE_SKILL + (self.level_sys.level - 1) * S.PLAYER_SKILL_PER_LEVEL

    @property
    def guns_skill(self):
        return (S.PLAYER_GUNS_SKILL + (self.level_sys.level - 1) * S.PLAYER_SKILL_PER_LEVEL
                + 15 * self.perk_rank("steady_hand"))

    @property
    def crit_bonus(self):
        return 10 * self.perk_rank("sharp_eye")

    @property
    def damage(self):
        """Урон в ближнем бою (у самопала свой — см. src/weapons.py)."""
        return self.base_damage + (self.level_sys.level - 1) * 2 + 3 * self.perk_rank("heavy_hand")

    def handle_input(self, keys, dt_ms, solid_rects):
        if not self.alive:
            return
        dx = dy = 0
        speed = S.PLAYER_SPEED * dt_ms / 1000
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= speed
            self.facing_left = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += speed
            self.facing_left = False
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += speed

        moving = dx != 0 or dy != 0

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

    def play_attack(self):
        """Анимация удара без кулдауна — в пошаговом бою темп задаёт ОД."""
        self.attacking = True
        self.anim.set_action("attack")

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
        if self.attacking and self.anim.action == "attack" and self.anim.is_finished_once():
            self.attacking = False

    def gain_xp(self, amount):
        msgs = self.level_sys.add_xp(amount)
        self.pending_perks += len(msgs)
        if msgs:
            self.max_hp += 5 * len(msgs)
            self.hp = self.max_hp
        return msgs

    def draw(self, surf, cam):
        frame = self.anim.current_frame(flip=self.facing_left)
        r = frame.get_rect(midbottom=(self.rect.centerx - cam.x, self.rect.bottom - cam.y))
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
        self.loot = dict(d.get("loot", {}))
        self.ai = d.get("ai", "melee")
        self.range = d.get("range", 1)
        self.hit_verb = d.get("hit_verb", "бьёт вас")
        self.armor = d.get("armor", 0)                 # сколько урона гасит панцирь
        self.weak_parts = set(d.get("weak_parts", []))  # куда броня не прикрывает
        self.faction = d.get("faction")   # у фракции (банды) враги нейтральны, пока их не разозлить
        self.hostile = self.faction is None
        self.talk = d.get("talk")         # id диалога: такой враг сначала заговаривает
        self.talked = False
        self.facing_left = False
        self.alive = True
        self.init_combat_stats(d["ap"], d["ac"], d["sequence"])

    def update(self, dt_ms):
        """Только анимация: ходит и бьёт враг лишь в пошаговом бою (src/combat.py)."""
        if self.alive:
            self.anim.update(dt_ms)

    def draw(self, surf, cam):
        frame = self.anim.current_frame(flip=self.facing_left)
        r = frame.get_rect(midbottom=(self.rect.centerx - cam.x, self.rect.bottom - cam.y))
        surf.blit(frame, r)
        if self.alive and self.hp < self.max_hp:
            bar_w = 30
            x = r.centerx - bar_w // 2
            y = r.top - 8
            pygame.draw.rect(surf, S.COLOR_HP_BG, (x, y, bar_w, 4))
            pygame.draw.rect(surf, S.COLOR_HP, (x, y, int(bar_w * self.hp / self.max_hp), 4))


class NPC:
    def __init__(self, pos, animations, npc_id, name):
        self.rect = _hitbox_in_tile(pos, HUMANOID_HITBOX)
        self.anim = Animator(animations, frame_ms=S.ANIM_FRAME_MS)
        self.npc_id = npc_id
        self.name = name

    def update(self, dt_ms):
        self.anim.update(dt_ms)

    def draw(self, surf, cam):
        frame = self.anim.current_frame()
        r = frame.get_rect(midbottom=(self.rect.centerx - cam.x, self.rect.bottom - cam.y))
        surf.blit(frame, r)
