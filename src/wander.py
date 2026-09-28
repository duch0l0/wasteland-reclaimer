"""
Блуждание вне боя: NPC и враги бродят в 2–3 клетках от места, где стоят,
чтобы мир не казался застывшим. Постоят пару секунд — пройдут к соседней
клетке — снова постоят. В бою, в разговоре и в открытых окнах все замирают.
"""
import random
from collections import deque

import pygame

from . import settings as S
from .combat import tile_of, rect_pos_for_tile

WANDER_SPEED = 45           # px/сек — прогулочный шаг, заметно медленнее игрока
WAIT_MS = (1500, 4500)      # сколько стоять между прогулками
MAX_PATH = 6                # дальше этого за одну прогулку не уходят


def _init(ent):
    ent.home = tile_of(ent)
    ent.wander_radius = random.choice((2, 3))
    ent.wander_path = []
    ent.wander_wait = random.randint(*WAIT_MS)


NPC_KEEP_AWAY = 4  # враги и мирные NPC не забредают ближе стольких клеток друг к другу


def _pick_path(ent, level, blocked, avoid=()):
    """Случайная достижимая клетка в радиусе от дома (и не рядом с avoid); путь до неё по BFS."""
    start = tile_of(ent)
    prev = {start: None}
    q = deque([(start, 0)])
    while q:
        c, d = q.popleft()
        if d >= MAX_PATH:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + dx, c[1] + dy)
            if n in prev or level.is_wall(*n) or level.is_exit(*n) or n in blocked:
                continue
            prev[n] = c
            q.append((n, d + 1))
    home, r = ent.home, ent.wander_radius
    goals = [t for t in prev if t != start and max(abs(t[0] - home[0]), abs(t[1] - home[1])) <= r
             and all(max(abs(t[0] - a[0]), abs(t[1] - a[1])) > NPC_KEEP_AWAY for a in avoid)]
    if not goals:
        return []
    goal = random.choice(goals)
    path = []
    while goal != start:
        path.append(goal)
        goal = prev[goal]
    return path[::-1]


def _stop(ent):
    ent.wander_path = []
    ent.anim.set_action("idle")


def update(game, dt_ms, frozen):
    """frozen — бой/диалог/окно: все стоят (и заканчивают шаг на клетке позже)."""
    walkers = [e for e in game.enemies if e.alive] + list(game.npcs)
    if frozen:
        for e in walkers:
            if getattr(e, "wander_path", None):
                _stop(e)
        return
    player_rect = game.player.rect
    for e in walkers:
        if not hasattr(e, "home"):
            _init(e)
        if not e.wander_path:
            e.wander_wait -= dt_ms
            if e.wander_wait > 0:
                continue
            e.wander_wait = random.randint(*WAIT_MS)
            blocked = {tile_of(o) for o in walkers if o is not e} | {tile_of(game.player)}
            # враги и мирные гуляют порознь: не подходят к «дому» и месту друг друга
            others = [o for o in walkers if (o in game.npcs) != (e in game.npcs)]
            avoid = [getattr(o, "home", tile_of(o)) for o in others] + [tile_of(o) for o in others]
            e.wander_path = _pick_path(e, game.level, blocked, avoid)
            if not e.wander_path:
                continue
        target = pygame.Vector2(rect_pos_for_tile(e, e.wander_path[0]))
        pos = pygame.Vector2(e.rect.topleft)
        delta = target - pos
        step = WANDER_SPEED * dt_ms / 1000
        # не наступать на игрока: подождать, пока он отойдёт
        nxt = e.rect.move(round(delta.x and step * (1 if delta.x > 0 else -1)),
                          round(delta.y and step * (1 if delta.y > 0 else -1)))
        if nxt.colliderect(player_rect) and not e.rect.colliderect(player_rect):
            _stop(e)
            continue
        e.anim.set_action("walk")
        e.anim.face(delta.x, delta.y)
        if delta.x:
            e.facing_left = delta.x < 0
        if delta.length() <= step:
            e.rect.topleft = (int(target.x), int(target.y))
            e.wander_path.pop(0)
            if not e.wander_path:
                e.anim.set_action("idle")
        else:
            pos += delta.normalize() * step
            e.rect.topleft = (round(pos.x), round(pos.y))
