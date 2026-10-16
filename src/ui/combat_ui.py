"""Боевой интерфейс: маркеры клеток, шанс попадания, всплывающий урон,
трассеры выстрелов, нижняя панель с ОД и меню прицельной атаки."""
import pygame

from .. import settings as S
from ..combat import BODY_PARTS
from ..entities import sprite_of, visible_rect
from .common import fonts, panel, hotspot, close_button, digit_key, COLOR_HOVER



OUTLINE_PLAYER = (110, 230, 110)
OUTLINE_TARGET = (235, 80, 60)
OUTLINE_ACTING = (235, 190, 80)   # враг, который сейчас ходит
_OUTLINE_CACHE = {}


def highlights(combat):
    """Кого обвести: {боец: цвет}."""
    if not combat.active:
        return {}
    p = combat.game.player
    hl = {}
    cur = combat.current
    if cur is p and not combat.tweens:
        hl[p] = OUTLINE_PLAYER
    elif cur is not None and cur is not p:
        hl[cur] = OUTLINE_ACTING
    t = combat.target
    if t is not None and t.alive:
        hl[t] = OUTLINE_TARGET
    # во время удара, выстрела, вздрагивания контур не рисуем — иначе он обводит вспышку и дым
    return {e: c for e, c in hl.items() if not e.anim.busy}


def draw_outline(surf, frame, rect, color):
    """Обводка по контуру спрайта: силуэт цвета color, сдвинутый на 2 px во все стороны."""
    key = (id(frame), color)
    sil = _OUTLINE_CACHE.get(key)
    if sil is None:
        if len(_OUTLINE_CACHE) > 400:
            _OUTLINE_CACHE.clear()
        sil = pygame.mask.from_surface(frame, 60).to_surface(setcolor=(*color, 255), unsetcolor=(0, 0, 0, 0))
        _OUTLINE_CACHE[key] = sil
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        surf.blit(sil, (rect.x + dx, rect.y + dy))


def _bar(surf, centerx, y, ratio, color, w=34, h=4):
    pygame.draw.rect(surf, (15, 12, 10), (centerx - w // 2 - 1, y - 1, w + 2, h + 2))
    pygame.draw.rect(surf, (60, 30, 28), (centerx - w // 2, y, w, h))
    pygame.draw.rect(surf, color, (centerx - w // 2, y, max(0, int(w * ratio)), h))


def health_bar_y(sprite_rect):
    return sprite_rect.top - 8


def _z(r, zoom):
    """Прямоугольник с холста мира -> на экран."""
    if zoom == 1:
        return r
    return pygame.Rect(round(r.x * zoom), round(r.y * zoom), round(r.w * zoom), round(r.h * zoom))


def draw_health_bars(surf, game, cam, zoom=1):
    """Полоски HP над головами: в бою — у всех бойцов (герой зелёный, враги красные),
    вне боя — только у раненых врагов."""
    combat = game.combat
    if combat.active:
        fighters = [f for f in combat.order if f.alive]
    else:
        fighters = [e for e in game.enemies if e.alive and e.hp < e.max_hp and not getattr(e, "hidden", False)]
    for f in fighters:
        if game.hidden_by_roof(f):
            continue
        r = _z(visible_rect(f, cam), zoom)
        color = (90, 210, 90) if f is game.player or getattr(f, "ally", False) else (215, 60, 50)
        _bar(surf, r.centerx, health_bar_y(r), f.hp / f.max_hp if f.max_hp else 0, color)


def draw_combat_markers(surf, combat, cam, zoom=1):
    """Шанс попадания (или почему атаковать нельзя) над целью."""
    _, font_small = fonts()
    p, t = combat.game.player, combat.target
    if t is None or not t.alive:
        return
    r = _z(visible_rect(t, cam), zoom)
    ok, reason = combat.can_attack(p, t)
    label, color = (f"{combat.hit_chance(p, t)}%", (240, 230, 200)) if ok else (reason, (170, 160, 140))
    txt = font_small.render(label, True, color)
    # справа от полоски HP цели: над головой места мало — там полоски соседей
    pos = txt.get_rect(midleft=(r.centerx + 21, health_bar_y(r) + 2))
    bg = pygame.Surface(pos.inflate(6, 2).size, pygame.SRCALPHA)
    bg.fill((15, 12, 10, 170))
    surf.blit(bg, pos.inflate(6, 2))
    surf.blit(txt, pos)


def draw_floaters(surf, floaters, cam, zoom=1):
    font, _ = fonts()
    for f in floaters:
        txt = font.render(f["text"], True, f["color"])
        txt.set_alpha(max(0, 255 - int(255 * f["t"] / 1100)))
        surf.blit(txt, txt.get_rect(center=tuple(c * zoom for c in (lambda x, y: (x, y - f.get("rise", 0)))(*cam.p(f["pos"].x, f["pos"].y)))))


def draw_aim_menu(surf, combat):
    font, font_small = fonts()
    p, t = combat.game.player, combat.target
    box = pygame.Rect(S.SCREEN_W // 2 - 250, 70, 500, 60 + len(BODY_PARTS) * 26 + 14)
    panel(surf, box, 245)
    surf.blit(font.render(f"Прицельная атака ({combat.attack_cost(p, 1)} ОД)", True, (210, 190, 120)),
              (box.x + 16, box.y + 10))
    ok, reason = combat.can_attack(p, t) if t else (False, "нет цели")
    note = t.name if ok else f"{t.name if t else ''}: {reason}"
    if t is not None and t.armor:
        note += f" · панцирь гасит {t.armor} урона"
    surf.blit(font_small.render(note, True, (170, 160, 145)), (box.x + 16, box.y + 36))
    close_button(surf, box)
    y = box.y + 62
    for i, part in enumerate(BODY_PARTS):
        chance = combat.hit_chance(p, t, i) if t else 0
        crit = combat.crit_chance(p, i)
        weak = t is not None and t.armor and part["id"] in t.weak_parts
        row = pygame.Rect(box.x + 10, y - 3, box.w - 20, 24)
        hover = hotspot(row, digit_key(i))
        if hover:
            pygame.draw.rect(surf, (70, 60, 40), row, border_radius=3)
        color = COLOR_HOVER if hover else (140, 220, 140) if weak else (220, 210, 190)
        # шрифт пропорциональный — колонки выравниваем координатами, а не пробелами
        cols = [(f"[{i + 1}] {part['name']}", 0), (f"попасть {chance}%", 130), (f"крит {crit}%", 250)]
        if weak:
            cols.append(("без брони", 350))
        for text, dx in cols:
            surf.blit(font_small.render(text, True, color), (box.x + 16 + dx, y))
        y += 26


def draw_tracers(surf, tracers, cam):
    """Летящие пули: яркая головка и короткий гаснущий хвост."""
    from ..combat import Combat
    for tr in tracers:
        if tr["t"] < 0:
            continue
        d = tr["to"] - tr["from"]
        length = d.length()
        if not length:
            continue
        u = d / length
        k = min(1.0, tr["t"] / 1000 * Combat.BULLET_SPEED / length)
        pos = tr["from"] + d * k
        head = cam.p(pos.x, pos.y)
        if cam.iso:   # хвост пули — по направлению полёта на экране
            a, b = cam.p(*tr["from"]), cam.p(*tr["to"])
            if tr.get("muzzle"):   # экшен: пуля вылетает из дула и летит на высоте груди
                a = (a[0] + tr["muzzle"][0], a[1] + tr["muzzle"][1])
                b = (b[0], b[1] - tr["lift"])
                head = (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
            d2 = pygame.Vector2(b[0] - a[0], b[1] - a[1])
            u = d2.normalize() if d2.length() else u
        for ln, color, w in ((26, (120, 95, 60), 1), (14, (200, 160, 90), 2), (6, (255, 225, 140), 2)):
            tail = (head[0] - u.x * ln, head[1] - u.y * ln)  # хвост: дальний конец тусклее
            pygame.draw.line(surf, color, tail, head, w)
        pygame.draw.circle(surf, (255, 250, 220), head, 2)


def wrap_text(font, text, max_w, max_lines=4):
    """Перенос по словам в строки не шире max_w; больше max_lines — хвост уходит в многоточие."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if font.size(trial)[0] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" ,.;:") + "…"
    return lines


def speech_ms(text):
    """Сколько держать облачко: чтение — около 14 знаков в секунду, не меньше двух секунд."""
    return max(2400, min(7500, 1500 + 70 * len(text)))


def draw_speech(surf, speech, cam, zoom=1, hint=False):
    """Реплика облачком над головой персонажа: 2–3 строки, крупно, с тёмной каймой; hint — золотая кайма
    (разговор, который стоит подслушать)."""
    from .common import _font
    font_small = _font(18)
    ent = speech["ent"]
    r = _z(visible_rect(ent, cam), zoom)
    lines = wrap_text(font_small, speech["text"], 260)
    rendered = [font_small.render(ln, True, (34, 26, 18)) for ln in lines]
    lh = rendered[0].get_height() + 2
    tw = max(t.get_width() for t in rendered)
    box = pygame.Rect(0, 0, tw + 26, lh * len(rendered) + 14)
    box.midbottom = (r.centerx, r.top - 16)
    sw, sh = surf.get_size()
    box.left = max(4, min(box.left, sw - box.w - 4))
    box.top = max(4, box.top)        # не уходит за верх экрана
    alpha = min(255, speech["t"] // 2)
    bubble = pygame.Surface((box.w, box.h + 11), pygame.SRCALPHA)
    fill = (248, 240, 218, alpha)
    border = (176, 128, 40, alpha) if hint or speech.get("hint") else (60, 45, 30, alpha)
    pygame.draw.rect(bubble, fill, (0, 0, box.w, box.h), border_radius=10)
    pygame.draw.polygon(bubble, fill, [(box.w // 2 - 8, box.h - 1), (box.w // 2 + 8, box.h - 1), (box.w // 2, box.h + 10)])
    pygame.draw.rect(bubble, border, (0, 0, box.w, box.h), 2, border_radius=10)
    pygame.draw.lines(bubble, border, False, [(box.w // 2 - 8, box.h - 1), (box.w // 2, box.h + 10),
                                              (box.w // 2 + 8, box.h - 1)], 2)
    for i, t in enumerate(rendered):
        t.set_alpha(alpha)
        bubble.blit(t, t.get_rect(midtop=(box.w // 2, 7 + i * lh)))
    surf.blit(bubble, box.topleft)


def draw_throws(surf, combat, cam):
    """Летящая граната/бутылка — дугой, с тенью на земле."""
    for th in combat.throws:
        k = min(1.0, th["t"] / th["dur"])
        pos = th["from"].lerp(th["to"], k)
        if th["kind"] == "rocket":   # ракета — прямо, с огненным хвостом
            x, y = (int(c) for c in cam.p(pos.x, pos.y))
            tail = th["from"].lerp(th["to"], max(0.0, k - 0.08))
            tx, ty = (int(c) for c in cam.p(tail.x, tail.y))
            pygame.draw.line(surf, (255, 160, 50), (tx, ty), (x, y), 4)
            pygame.draw.circle(surf, (90, 95, 80), (x, y), 5)
            continue
        lift = 4 * 60 * k * (1 - k)
        x, y = (int(c) for c in cam.p(pos.x, pos.y))
        pygame.draw.ellipse(surf, (0, 0, 0), (x - 5, y - 2, 10, 5))
        color = {"grenade": (80, 100, 60), "plasma": (90, 230, 120), "pulse": (110, 170, 255)}.get(
            th["kind"], (150, 190, 110))
        pygame.draw.circle(surf, (20, 18, 14), (x, int(y - lift)), 6)
        pygame.draw.circle(surf, color, (x, int(y - lift)), 4)
        if th["kind"] == "molotov":
            pygame.draw.circle(surf, (255, 170, 60), (x + 3, int(y - lift) - 5), 3)


def draw_blasts(surf, combat, cam):
    """Взрыв: вспышка, огненный шар, кольцо дыма."""
    for b in combat.blasts:
        k = b["t"] / 700
        x, y = (int(c) for c in cam.p(b["pos"].x, b["pos"].y))
        r = int(20 + 70 * k)
        layer = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        c = (r + 2, r + 2)
        a = max(0, int(255 * (1 - k)))
        fire = {"molotov": (255, 110, 30), "plasma": (110, 255, 120), "pulse": (120, 180, 255)}.get(
            b["kind"], (255, 140, 40))
        pygame.draw.circle(layer, (70, 60, 50, a // 2), c, r)
        pygame.draw.circle(layer, (*fire, a), c, max(4, int(r * (0.8 - 0.5 * k))))
        if k < 0.35:
            pygame.draw.circle(layer, (255, 245, 200, a), c, max(3, int(r * 0.35)))
        surf.blit(layer, (x - c[0], y - c[1] - 10))


_DARK = {}


def draw_darkness(surf, center, dark=200, radius=420):
    """Под землёй светло только рядом с героем — фонарик, как в Fallout 3.
    dark — насколько темно вдали (0..255, у каждой карты своё)."""
    dark = 200 if dark is True else int(dark)
    size = surf.get_size()
    key = (size, radius, dark)
    if key not in _DARK:
        w, h = size
        mask = pygame.Surface((w * 2, h * 2), pygame.SRCALPHA)
        mask.fill((6, 5, 8, dark))
        for i in range(radius, 0, -6):
            a = int(dark * (i / radius) ** 1.6)
            pygame.draw.circle(mask, (6, 5, 8, a), (w, h), i)
        _DARK[key] = mask
    mask = _DARK[key]
    surf.blit(mask, (center[0] - mask.get_width() // 2, center[1] - mask.get_height() // 2))


# ------------------------------------------------------------ роли врагов (src/ai_roles.py)
ROLE_BADGE = {"medic": ("+", (70, 170, 90)), "commander": ("К", (200, 160, 40)), "sniper": ("С", (180, 50, 50)),
              "gunner": ("П", (170, 90, 40)), "grenadier": ("Г", (150, 110, 60)), "shield": ("Щ", (90, 110, 150)),
              "runner": ("!", (200, 120, 40)), "flanker": ("Ф", (120, 80, 150)), "cover": ("У", (110, 120, 110)),
              "ambush": ("З", (90, 90, 90))}


def draw_role_badges(surf, game, cam, zoom=1):
    """Значок роли слева от полоски HP и щит, если враг сейчас за укрытием от героя."""
    combat = game.combat
    if not combat.active:
        return
    _, font_small = fonts()
    me = game.player
    shooters = [e for e in combat.enemies_in_combat() if e.ai in ("ranged", "turret") and not getattr(e, "hidden", False)]
    covered = sum(1 for e in shooters if combat.in_cover(e, me))
    if covered and me.alive:                   # герой за укрытием: щит и от скольких стрелков прикрыт
        r = _z(visible_rect(me, cam), zoom)
        x, y = r.centerx - 26, health_bar_y(r) + 2
        pts = [(x - 6, y - 7), (x + 6, y - 7), (x + 6, y), (x, y + 7), (x - 6, y)]
        pygame.draw.polygon(surf, (20, 16, 12), [(px + 1, py + 1) for px, py in pts])
        pygame.draw.polygon(surf, (120, 200, 130), pts)
        if len(shooters) > 1:
            t = font_small.render(f"{covered}/{len(shooters)}", True, (200, 235, 200))
            surf.blit(t, t.get_rect(midright=(x - 9, y)))
    for f in combat.enemies_in_combat():
        if getattr(f, "hidden", False) or game.hidden_by_roof(f):
            continue
        r = _z(visible_rect(f, cam), zoom)
        y = health_bar_y(r) + 2
        x = r.centerx - 26
        role = getattr(f, "role", None)
        if role in ROLE_BADGE:
            glyph, col = ROLE_BADGE[role]
            pygame.draw.circle(surf, (20, 16, 12), (x, y), 8)
            pygame.draw.circle(surf, col, (x, y), 7)
            t = font_small.render(glyph, True, (250, 245, 230))
            surf.blit(t, t.get_rect(center=(x, y)))
            x -= 18
        if combat.in_cover(game.player, f):
            pts = [(x - 6, y - 7), (x + 6, y - 7), (x + 6, y), (x, y + 7), (x - 6, y)]
            pygame.draw.polygon(surf, (20, 16, 12), [(px + 1, py + 1) for px, py in pts])
            pygame.draw.polygon(surf, (170, 180, 190), pts)
        if getattr(f, "broken", False):
            t = font_small.render("бежит", True, (230, 200, 120))
            surf.blit(t, t.get_rect(midleft=(r.centerx + 22, y + 12)))


def draw_role_warnings(surf, combat, cam):
    """Предупреждения, на которые можно ответить: луч снайпера и сектор пулемётчика."""
    if not combat.active:
        return
    from .. import ai_roles
    from ..combat import tile_of
    T = S.TILE
    pulse = 0.6 + 0.4 * abs(((pygame.time.get_ticks() // 8) % 200) - 100) / 100
    for e in combat.enemies_in_combat():
        if getattr(e, "role", None) == "sniper" and getattr(e, "aiming", None) is not None and e.aiming.alive:
            a, b = cam.p(*e.rect.center), cam.p(*e.aiming.rect.center)
            pygame.draw.line(surf, (int(255 * pulse), 30, 30), a, b, 2)
            pygame.draw.circle(surf, (255, 40, 40), (int(b[0]), int(b[1])), 5, 1)
        if getattr(e, "role", None) == "gunner" and getattr(e, "overwatch", None):
            gx, gy = tile_of(e)
            rng = e.overwatch["range"]
            shade = pygame.Surface((T, T), pygame.SRCALPHA)
            shade.fill((230, 60, 40, int(55 * pulse)))
            for ty in range(gy - rng, gy + rng + 1):
                for tx in range(gx - rng, gx + rng + 1):
                    if ai_roles.in_sector(combat, e, (tx, ty)):
                        sx, sy = cam.p(tx * T, ty * T)
                        surf.blit(shade, (int(sx), int(sy)))


def draw_sparks(surf, combat, cam):
    for sp in combat.sparks:
        k = 1 - sp["t"] / sp["life"]
        x, y = cam.p(sp["pos"].x, sp["pos"].y)
        col = (255, int(200 + 55 * k), int(120 * k))
        tail = sp["vel"] * 18
        pygame.draw.line(surf, col, (x, y), (x - tail.x, y - tail.y), 2 if k > 0.5 else 1)
