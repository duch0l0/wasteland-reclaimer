"""
Случайные встречи на карте мира (как в Fallout 2): небольшая арена,
сгенерированная на лету, с группой врагов или чем-нибудь странным.
Выход — по краям карты ('>').
"""
import random
from collections import deque

from .location import Location

W, H = 30, 14

# вес, id, описание для лога, что поставить на арену
ENCOUNTERS = [
    (30, "rats", "Стая крысюков. Похоже, они тоже рады встрече.", {"r": (3, 4)}),
    (25, "mutants", "Парочка мутантов-падальщиков что-то доедает. Возможно, предыдущего путника.", {"m": (2, 2)}),
    (20, "raiders", "Рейдеры устроили засаду. Засада, правда, так себе — вас видно издалека, и их тоже.", {"R": (2, 2)}),
    (10, "beetle", "Панцирный жук и его свита из крысюков.", {"B": (1, 1), "r": (1, 2)}),
    (8, "robot", "Посреди пустоши стоит почтовый робот и терпеливо ждёт. Уже лет сто.", {"N": (1, 1)}),
    (7, "cache", "Брошенная тележка каравана. Караванщиков не видно. Может, оно и к лучшему.", {"X": (1, 1)}),
]


def _connected(grid):
    start = (2, H // 2)
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and 0 <= n[0] < W and 0 <= n[1] < H and grid[n[1]][n[0]] not in "#X":
                seen.add(n)
                q.append(n)
    floor = sum(1 for y in range(H) for x in range(W) if grid[y][x] not in "#X")
    return len(seen) == floor


def _arena(rnd):
    while True:
        g = [["." for _ in range(W)] for _ in range(H)]
        for x in range(W):
            g[0][x] = g[H - 1][x] = "#"
        for y in range(H):
            g[y][0] = g[y][W - 1] = "#"
        for y in (H // 2 - 1, H // 2):
            g[y][0] = g[y][W - 1] = ">"
        for _ in range(rnd.randint(6, 10)):  # скалы и обломки — укрытия
            cx, cy = rnd.randint(5, W - 6), rnd.randint(2, H - 3)
            for _ in range(rnd.randint(2, 5)):
                x, y = cx + rnd.randint(-1, 1), cy + rnd.randint(-1, 1)
                if 1 <= x < W - 1 and 1 <= y < H - 1:
                    g[y][x] = "#"
        for x in range(1, 5):  # вход свободен
            for y in range(H // 2 - 2, H // 2 + 2):
                g[y][x] = "."
        if _connected(g):
            return g


def roll(flags, rnd=random):
    table = [e for e in ENCOUNTERS if not (e[1] == "robot" and flags.get("robot_done"))]
    weights = [e[0] for e in table]
    return rnd.choices(table, weights=weights)[0]


def make_encounter(flags, rnd=random):
    _, enc_id, text, content = roll(flags, rnd)
    g = _arena(rnd)
    g[H // 2][2] = "P"
    npcs, containers = [], []
    free = [(x, y) for y in range(2, H - 2) for x in range(16, W - 3) if g[y][x] == "."]
    rnd.shuffle(free)
    for ch, (lo, hi) in content.items():
        for _ in range(rnd.randint(lo, hi)):
            x, y = free.pop()
            g[y][x] = ch
            if ch == "N":
                npcs.append("robot")
            elif ch == "X":
                containers.append({"name": "тележка каравана",
                                   "loot": {"крышки": rnd.randint(15, 35), "патроны": rnd.randint(3, 8),
                                            "химикаты": 2, "бинт": 1}})
    if not _connected(g):  # контейнер/NPC мог перекрыть проход — перегенерируем
        return make_encounter(flags, rnd)
    loc = Location(f"encounter:{enc_id}", d={"name": "Пустошь", "npcs": npcs, "containers": containers,
                                            "encounter": True}, rows=["".join(r) for r in g])
    return loc, text
