"""
Нижняя панель интерфейса — как в Fallout, всегда на экране:
слева зелёный лог событий, справа HP/XP, ход и ОД (в бою), кнопки.
"""
import pygame

from .. import settings as S
from ..weapons import WEAPONS
from .common import fonts, font_tiny, wrap_text, button, PANEL_H

LOG_W = S.SCREEN_W - 400  # слева лог, справа 400 px под состояние и кнопки
LOG_GREEN = (140, 220, 120)
DIM = (160, 150, 130)


def weapon_label(game, short=False):
    w = WEAPONS[game.player.weapon]
    name = game.weapon_name()
    if w.get("ammo"):
        n = game.inventory.count(w["ammo"])
        return f"{name} ({n})" if short else f"{name} (патроны: {n})"
    return name


def _bar(surf, rect, ratio, fg, bg, text):
    _, font_small = fonts()
    pygame.draw.rect(surf, bg, rect)
    pygame.draw.rect(surf, fg, (rect.x, rect.y, int(rect.w * max(0.0, min(1.0, ratio))), rect.h))
    pygame.draw.rect(surf, (20, 16, 12), rect, 1)
    surf.blit(font_small.render(text, True, S.COLOR_TEXT), (rect.x + 5, rect.y - 2))


def draw_panel(surf, game):
    font, font_small = fonts()
    combat, p = game.combat, game.player
    box = pygame.Rect(0, S.SCREEN_H - PANEL_H, S.SCREEN_W, PANEL_H)
    bg = pygame.Surface(box.size, pygame.SRCALPHA)
    bg.fill((*S.COLOR_PANEL, 250))
    pygame.draw.line(bg, S.COLOR_PANEL_BORDER, (0, 0), (box.w, 0), 2)
    surf.blit(bg, box.topleft)

    # ---- слева: лог, как зелёный экран Пип-боя
    lines = []
    for line in game.log_lines[-6:]:
        lines.extend(wrap_text(font_small, line, LOG_W - 20))
    y = box.y + 6
    for line in lines[-4:]:
        surf.blit(font_small.render(line, True, LOG_GREEN), (box.x + 12, y))
        y += 19
    if combat.active:
        cost = combat.attack_cost(p)
        hint = f"ЛКМ — идти/атака ({cost} ОД) · ПКМ — прицельно ({cost + 1}) · Tab — цель · G — бросок · бочка — выстрел"
    else:
        hint = "ЛКМ — идти, говорить, обыскать, напасть · E — действие · Esc — выход"
    parts = hint.split(" · ")
    while len(parts) > 1 and font_tiny().size(" · ".join(parts))[0] > LOG_W - 24:
        parts.pop()  # не влезает в колонку лога — отбрасываем последние подсказки
    surf.blit(font_tiny().render(" · ".join(parts), True, DIM), (12, box.bottom - 17))
    pygame.draw.line(surf, S.COLOR_PANEL_BORDER, (LOG_W, box.y + 6), (LOG_W, box.bottom - 6), 1)

    # ---- справа: состояние
    x0, right = LOG_W + 14, box.right - 10
    lv = p.level_sys
    if combat.active:
        cur = combat.current
        title = "ВАШ ХОД" if cur is p else f"Ход: {cur.name}" if cur else ""
        tcolor = (230, 200, 110) if cur is p else (220, 120, 90)
        corner = f"Раунд {combat.round}"
    else:
        title, tcolor, corner = game.loc.name, (210, 190, 120), f"Ур. {lv.level}"
    c = font_small.render(corner, True, DIM)
    surf.blit(c, (right - c.get_width(), box.y + 8))
    t = font.render(title, True, tcolor)
    if t.get_width() > right - x0 - c.get_width() - 10:  # длинное название локации — мельче
        t = font_small.render(title, True, tcolor)
    surf.blit(t, (x0, box.y + 5))

    hp_rect = pygame.Rect(x0, box.y + 32, 180, 15)
    rad_note = f" · РАД {p.rads}" if p.rads else ""
    _bar(surf, hp_rect, p.hp / p.max_hp if p.max_hp else 0,
         S.COLOR_HP, S.COLOR_HP_BG, f"HP {p.hp}/{p.hp_cap}{rad_note}")
    if p.rads:   # радиация съедает правый край полоски
        eaten = int(hp_rect.w * (p.max_hp - p.hp_cap) / p.max_hp)
        rad = pygame.Surface((eaten, hp_rect.h), pygame.SRCALPHA)
        rad.fill((110, 200, 60, 150))
        surf.blit(rad, (hp_rect.right - eaten, hp_rect.y))
    _bar(surf, pygame.Rect(x0 + 190, box.y + 32, right - x0 - 190, 15), lv.xp / lv.xp_needed,
         S.COLOR_XP, S.COLOR_XP_BG, f"XP {lv.xp}/{lv.xp_needed}")

    if combat.active:
        surf.blit(font_small.render("ОД", True, S.COLOR_TEXT), (x0, box.y + 52))
        mine = combat.current is p
        for i in range(p.max_ap):
            center = (x0 + 34 + i * 18, box.y + 61)
            pygame.draw.circle(surf, (90, 230, 90) if mine and i < p.ap else (40, 60, 40), center, 6)
            pygame.draw.circle(surf, (20, 30, 20), center, 6, 1)
        if p.free_steps > 0 and mine:
            surf.blit(font_small.render(f"+{p.free_steps} шага", True, (140, 220, 140)),
                      (x0 + 34 + p.max_ap * 18, box.y + 52))
    else:
        surf.blit(font_small.render(f"Крышки: {game.inventory.count('крышки')}", True, (210, 200, 170)),
                  (x0, box.y + 52))

    # ---- кнопки: ширина по подписи; если с клавишами не влезают — без клавиш
    enabled = not game.modal_open()
    weapon = weapon_label(game, short=True).replace("Заточенный лом", "Заточка")
    specs = [("Рюкзак", "I", pygame.K_i, enabled), ("Крафт", "C", pygame.K_c, enabled),
             (weapon, "F", pygame.K_f, enabled), ("Журнал", "J", pygame.K_j, enabled),
             ("Карта", "M", pygame.K_m, enabled)]
    if combat.active:
        specs.append(("Конец хода", "R", pygame.K_r, enabled and combat.player_can_act()))
    avail, gap = right - x0, 4
    labels = [f"{text} [{k}]" for text, k, _, _ in specs]
    if sum(font_tiny().size(t)[0] + 14 for t in labels) + gap * (len(specs) - 1) > avail:
        labels = [text for text, _, _, _ in specs]
    widths = [font_tiny().size(t)[0] + 14 for t in labels]
    extra = (avail - sum(widths) - gap * (len(specs) - 1)) // len(specs)
    x = x0
    for label, w, (_, _, key, on) in zip(labels, widths, specs):
        button(surf, (x, box.y + 76, w + extra, 22), label, key, on)
        x += w + extra + gap


def draw_log_overlay(surf, log_lines, n=4):
    """Лог поверх карты мира."""
    _, font_small = fonts()
    y = 10
    for line in log_lines[-n:]:
        for part in wrap_text(font_small, line, S.SCREEN_W - 20):
            surf.blit(font_small.render(part, True, (245, 235, 210)), (10, y))
            y += 18
