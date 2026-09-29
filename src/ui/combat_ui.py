"""Боевой интерфейс: маркеры клеток, шанс попадания, всплывающий урон,
трассеры выстрелов, нижняя панель с ОД и меню прицельной атаки."""
import pygame

from .. import settings as S
from ..combat import BODY_PARTS
from ..entities import sprite_of
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


def draw_health_bars(surf, game, cam):
    """Полоски HP над головами: в бою — у всех бойцов (герой зелёный, враги красные),
    вне боя — только у раненых врагов."""
    combat = game.combat
    if combat.active:
        fighters = [f for f in combat.order if f.alive]
    else:
        fighters = [e for e in game.enemies if e.alive and e.hp < e.max_hp]
    for f in fighters:
        _, r = sprite_of(f, cam)
        color = (90, 210, 90) if f is game.player or getattr(f, "ally", False) else (215, 60, 50)
        _bar(surf, r.centerx, health_bar_y(r), f.hp / f.max_hp if f.max_hp else 0, color)


def draw_combat_markers(surf, combat, cam):
    """Шанс попадания (или почему атаковать нельзя) над целью."""
    _, font_small = fonts()
    p, t = combat.game.player, combat.target
    if t is None or not t.alive:
        return
    _, r = sprite_of(t, cam)
    ok, reason = combat.can_attack(p, t)
    label, color = (f"{combat.hit_chance(p, t)}%", (240, 230, 200)) if ok else (reason, (170, 160, 140))
    txt = font_small.render(label, True, color)
    # справа от полоски HP цели: над головой места мало — там полоски соседей
    pos = txt.get_rect(midleft=(r.centerx + 21, health_bar_y(r) + 2))
    bg = pygame.Surface(pos.inflate(6, 2).size, pygame.SRCALPHA)
    bg.fill((15, 12, 10, 170))
    surf.blit(bg, pos.inflate(6, 2))
    surf.blit(txt, pos)


def draw_floaters(surf, floaters, cam):
    font, _ = fonts()
    for f in floaters:
        txt = font.render(f["text"], True, f["color"])
        txt.set_alpha(max(0, 255 - int(255 * f["t"] / 1100)))
        surf.blit(txt, txt.get_rect(center=(f["pos"].x - cam.x, f["pos"].y - cam.y)))


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
        pos = tr["from"] + u * min(length, tr["t"] / 1000 * Combat.BULLET_SPEED)
        head = (pos.x - cam.x, pos.y - cam.y)
        for ln, color, w in ((26, (120, 95, 60), 1), (14, (200, 160, 90), 2), (6, (255, 225, 140), 2)):
            tail = (head[0] - u.x * ln, head[1] - u.y * ln)  # хвост: дальний конец тусклее
            pygame.draw.line(surf, color, tail, head, w)
        pygame.draw.circle(surf, (255, 250, 220), head, 2)


def draw_speech(surf, speech, cam):
    """Реплика облачком над головой персонажа."""
    from .common import fonts
    _, font_small = fonts()
    ent = speech["ent"]
    _, r = sprite_of(ent, cam)
    txt = font_small.render(speech["text"], True, (30, 24, 18))
    box = txt.get_rect(midbottom=(r.centerx, r.top - 18)).inflate(20, 12)
    alpha = min(255, speech["t"] // 2)
    bubble = pygame.Surface((box.w, box.h + 10), pygame.SRCALPHA)
    pygame.draw.rect(bubble, (245, 235, 210, alpha), (0, 0, box.w, box.h), border_radius=10)
    pygame.draw.polygon(bubble, (245, 235, 210, alpha), [(box.w // 2 - 8, box.h - 1), (box.w // 2 + 8, box.h - 1),
                                                         (box.w // 2, box.h + 9)])
    pygame.draw.rect(bubble, (60, 45, 30, alpha), (0, 0, box.w, box.h), 2, border_radius=10)
    txt.set_alpha(alpha)
    bubble.blit(txt, txt.get_rect(center=(box.w // 2, box.h // 2)))
    surf.blit(bubble, box.topleft)
