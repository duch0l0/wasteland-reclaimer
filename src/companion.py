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
SPEED = S.PLAYER_SPEED * 1.15   # чуть быстрее героя — чтобы не отставал
REGEN_MS = 1200


def place_near_player(game):
    """Поставить спутника на свободную клетку рядом с героем (вход в локацию, загрузка)."""
    c = game.companion
    if c is None:
        return
    px, py = tile_of(game.player)
    for d in ((-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (1, 1), (-1, -1), (1, -1), (-2, 0), (2, 0)):
        t = (px + d[0], py + d[1])
        if not game.level.is_wall(*t) and not game.level.is_exit(*t):
            c.rect.topleft = rect_pos_for_tile(c, t)
            c.path = []
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
    c = game.companion
    if c is None or game.mode != "local":
        return
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
        place_near_player(game)
        return
    path = getattr(c, "path", [])
    if dist <= 1 and not path:
        c.anim.set_action("idle")
        return
    if dist >= 2 and (not path or chebyshev(path[-1], hero) > 1):
        full = _path(game.level, me, hero)
        if full is None:
            place_near_player(game)
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
