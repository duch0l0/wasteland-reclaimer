"""Боевой интерфейс: маркеры клеток, шанс попадания, всплывающий урон,
трассеры выстрелов, нижняя панель с ОД и меню прицельной атаки."""
import pygame

from .. import settings as S
from ..combat import BODY_PARTS, tile_of
from .common import fonts, font_tiny, wrap_text, panel
from .hud import weapon_label

COMBAT_PANEL_H = 104


def draw_combat_markers(surf, combat, cam):
    """Клетка игрока, клетка цели и шанс попадания над целью."""
    _, font_small = fonts()
    T = S.TILE
    p = combat.game.player

    def tile_rect(ent):
        tx, ty = tile_of(ent)
        return pygame.Rect(tx * T - int(cam.x), ty * T - int(cam.y), T, T)

    if not combat.tweens:
        pygame.draw.rect(surf, (90, 200, 90), tile_rect(p), 2)
    t = combat.target
    if t is not None and t.alive:
        r = tile_rect(t)
        pygame.draw.rect(surf, (220, 70, 50), r, 2)
        ok, reason = combat.can_attack(p, t)
        if ok:
            label = f"{combat.hit_chance(p, t)}%"
            color = (240, 230, 200)
        else:
            label = reason
            color = (170, 160, 140)
        txt = font_small.render(label, True, color)
        surf.blit(txt, txt.get_rect(midbottom=(r.centerx, r.top - 30)))


def draw_floaters(surf, floaters, cam):
    font, _ = fonts()
    for f in floaters:
        txt = font.render(f["text"], True, f["color"])
        txt.set_alpha(max(0, 255 - int(255 * f["t"] / 1100)))
        surf.blit(txt, txt.get_rect(center=(f["pos"].x - cam.x, f["pos"].y - cam.y)))


def draw_combat_panel(surf, combat, log_lines):
    """Нижняя панель в стиле интерфейса Fallout: лог, ОД-лампочки, чей ход, клавиши."""
    font, font_small = fonts()
    h = COMBAT_PANEL_H
    box = pygame.Rect(0, S.SCREEN_H - h, S.SCREEN_W, h)
    bg = pygame.Surface(box.size, pygame.SRCALPHA)
    bg.fill((*S.COLOR_PANEL, 240))
    pygame.draw.line(bg, S.COLOR_PANEL_BORDER, (0, 0), (box.w, 0), 2)
    surf.blit(bg, box.topleft)

    # лог — слева, как зелёный «монитор» Пип-боя
    log_w = 560
    lines = []
    for line in log_lines[-6:]:
        lines.extend(wrap_text(font_small, line, log_w - 20))
    y = box.y + 8
    for line in lines[-4:]:
        surf.blit(font_small.render(line, True, (140, 220, 120)), (box.x + 12, y))
        y += 19
    pygame.draw.line(surf, S.COLOR_PANEL_BORDER, (log_w, box.y + 6), (log_w, box.bottom - 6), 1)

    x0 = log_w + 14
    p = combat.game.player
    cur = combat.current
    whose = "ВАШ ХОД" if cur is p else f"Ход: {cur.name}" if cur else ""
    surf.blit(font.render(whose, True, (230, 200, 110) if cur is p else (220, 120, 90)), (x0, box.y + 6))
    surf.blit(font_small.render(f"Раунд {combat.round}", True, (160, 150, 130)), (box.right - 90, box.y + 10))

    # ОД — ряд лампочек
    surf.blit(font_small.render("ОД", True, S.COLOR_TEXT), (x0, box.y + 36))
    for i in range(p.max_ap):
        lit = cur is p and i < p.ap
        center = (x0 + 38 + i * 20, box.y + 46)
        pygame.draw.circle(surf, (90, 230, 90) if lit else (40, 60, 40), center, 7)
        pygame.draw.circle(surf, (20, 30, 20), center, 7, 1)

    if p.free_steps > 0 and cur is p:
        surf.blit(font_small.render(f"+{p.free_steps} беспл. шага", True, (140, 220, 140)),
                  (x0 + 42 + p.max_ap * 20, box.y + 38))

    surf.blit(font_small.render(f"{weapon_label(combat.game)} · F", True, (210, 200, 170)),
              (x0, box.y + 62))
    # полная строка клавиш — мелко под логом, на всю ширину
    cost = combat.attack_cost(p)
    keys = (f"WASD шаг 1 · Space атака {cost} · Q прицельно {cost + 1} · Tab цель · "
            f"C крафт {S.AP_CRAFT} · R конец хода")
    surf.blit(font_tiny().render(keys, True, (170, 160, 140)), (12, box.bottom - 18))


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
    y = box.y + 62
    for i, part in enumerate(BODY_PARTS):
        chance = combat.hit_chance(p, t, i) if t else 0
        crit = combat.crit_chance(p, i)
        weak = t is not None and t.armor and part["id"] in t.weak_parts
        color = (140, 220, 140) if weak else (220, 210, 190)
        # шрифт пропорциональный — колонки выравниваем координатами, а не пробелами
        cols = [(f"[{i + 1}] {part['name']}", 0), (f"попасть {chance}%", 130), (f"крит {crit}%", 250)]
        if weak:
            cols.append(("без брони", 350))
        for text, dx in cols:
            surf.blit(font_small.render(text, True, color), (box.x + 16 + dx, y))
        y += 26


def draw_tracers(surf, tracers, cam):
    for tr in tracers:
        alpha = max(0.0, 1 - tr["t"] / 180)
        color = (255, int(200 * alpha + 40), 80)
        a = (tr["from"].x - cam.x, tr["from"].y - cam.y - 10)
        b = (tr["to"].x - cam.x, tr["to"].y - cam.y - 10)
        pygame.draw.line(surf, color, a, b, 2)
