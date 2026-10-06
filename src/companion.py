"""
Спутник вне боя: идёт следом за героем, держится в 1–2 клетках позади.
Если отстал больше чем на 10 клеток или не может пройти — догоняет рывком
(появляется рядом). Вне боя понемногу залечивает раны, как и герой.
"""
from collections import deque

import pygame

from . import settings as S
from .combat import tile_of, rect_pos_for_tile, chebyshev

T = S.TILE

# спутники-люди: кого можно взять с собой (второй слот — к псу). npc — житель, который «уходит» с героем;
# sprite_npc — чьи кадры; флаг <id>_with_hero — сейчас в отряде.
ALLIES = {
    "lira": {"id": "lira", "name": "Лира", "npc": "lira_baker", "sprite_npc": "blondie", "hp": 60, "damage": 9, "skill": 75,
             "ai": "ranged", "range": 8, "ap": 9, "ac": 18, "sequence": 9, "hitbox": (28, 32),
             "hit_verb": "стреляет из лазерного пистолета Братства"},
    "punk": {"id": "punk", "name": "Панк", "npc": "loner_baker", "sprite_npc": "loner", "hp": 55, "damage": 11, "skill": 70,
             "ai": "melee", "range": 1, "ap": 10, "ac": 14, "sequence": 10, "hitbox": (28, 32),
             "hit_verb": "бьёт трубой с размаху"},
    "hugo": {"id": "hugo", "name": "Хьюго Ли", "npc": "hugo_lee", "sprite_npc": "hugo_lee", "hp": 50, "damage": 8, "skill": 72,
             "ai": "ranged", "range": 7, "ap": 8, "ac": 14, "sequence": 7, "hitbox": (28, 32),
             "hit_verb": "стреляет из армейского пистолета"},
    "cobbs": {"id": "cobbs", "name": "Капрал Коббс", "npc": "cobbs", "sprite_npc": "cobbs", "hp": 70, "damage": 10, "skill": 85,
              "ai": "ranged", "range": 9, "ap": 8, "ac": 16, "sequence": 8, "hitbox": (28, 32),
              "hit_verb": "бьёт из винтовки без промаха — как учили в семьдесят седьмом"},
    "cooper": {"id": "cooper", "name": "Купер Говард", "npc": "cooper", "sprite_npc": "cooper", "hp": 80, "damage": 14, "skill": 90,
               "ai": "ranged", "range": 9, "ap": 10, "ac": 18, "sequence": 11, "hitbox": (28, 32),
               "hit_verb": "стреляет из револьвера, не вынимая сигарету изо рта"},
}


def make_ally(ally_id):
    from .entities import Companion
    from .location import npc_animations
    prof = ALLIES[ally_id]
    return Companion((0, 0), npc_animations(prof["sprite_npc"]), profile=prof)


def party(game):
    """Все спутники героя: пёс и спутник-человек."""
    return [c for c in (game.companion, getattr(game, "ally", None)) if c is not None]
SPEED = S.PLAYER_SPEED * 1.15   # чуть быстрее героя — чтобы не отставал
REGEN_MS = 1200


def place_near_player(game):
    """Поставить спутников на свободные клетки рядом с героем (вход в локацию, загрузка)."""
    taken = {tile_of(game.player)}
    for c in party(game):
        _place_one(game, c, taken)


def _place_one(game, c, taken=None):
    taken = taken if taken is not None else {tile_of(game.player)} | {tile_of(o) for o in party(game) if o is not c}
    px, py = tile_of(game.player)
    for d in ((-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (1, 1), (-1, -1), (1, -1), (-2, 0), (2, 0)):
        t = (px + d[0], py + d[1])
        if t not in taken and not game.level.is_wall(*t) and not game.level.is_exit(*t):
            c.rect.topleft = rect_pos_for_tile(c, t)
            c.path = []
            taken.add(t)
            return
    c.rect.topleft = game.player.rect.topleft


def _path(level, start, goal, limit=400):
    prev = {start: None}
    q = deque([start])
    while q and len(prev) < limit:
        cur = q.popleft()
        if cur == goal:
            out = []
            while cur != start:
                out.append(cur)
                cur = prev[cur]
            return out[::-1]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (cur[0] + dx, cur[1] + dy)
            if n not in prev and not level.is_wall(*n):
                prev[n] = cur
                q.append(n)
    return None


def update(game, dt_ms):
    if game.mode != "local":
        return
    for c in party(game):
        _update_one(game, c, dt_ms)


def _update_one(game, c, dt_ms):
    c.update(dt_ms)
    if game.combat.active:
        return
    if c.down:  # после боя поднимается
        c.down, c.alive, c.hp = False, True, max(1, c.hp)
        c.anim.set_action("idle")
        game.log(f"{c.name} поднимается, отряхивается и снова рядом.")
    if c.hp < c.max_hp:
        c.regen_ms += dt_ms
        if c.regen_ms >= REGEN_MS:
            c.regen_ms, c.hp = 0, c.hp + 1
    me, hero = tile_of(c), tile_of(game.player)
    dist = chebyshev(me, hero)
    if dist > 10:
        _place_one(game, c)
        return
    path = getattr(c, "path", [])
    if dist <= 1 and not path:
        c.anim.set_action("idle")
        return
    if dist >= 2 and (not path or chebyshev(path[-1], hero) > 1):
        full = _path(game.level, me, hero)
        if full is None:
            _place_one(game, c)
            return
        c.path = full[:-1] or []  # до соседней с героем клетки
        path = c.path
    if not path:
        c.anim.set_action("idle")
        return
    target = pygame.Vector2(rect_pos_for_tile(c, path[0]))
    pos = pygame.Vector2(c.rect.topleft)
    delta = target - pos
    step = SPEED * dt_ms / 1000
    c.anim.face(delta.x, delta.y)
    c.anim.set_action("walk")
    if delta.length() <= step:
        c.rect.topleft = (int(target.x), int(target.y))
        path.pop(0)
    else:
        pos += delta.normalize() * step
        c.rect.topleft = (round(pos.x), round(pos.y))
