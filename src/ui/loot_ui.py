"""
Окно обыска: слева рюкзак, справа контейнер (ящик, шкаф, тело).
ЛКМ по ячейке — перенести всю стопку, ПКМ — одну штуку. Внизу — описание
предмета под курсором.
"""
import pygame

from .. import settings as S
from .. import items
from .common import (fonts, font_tiny, wrap_text, panel, button, close_button, hotspot,
                     COLOR_TITLE, COLOR_DIM, PANEL_H)
from .inventory_ui import _cell, CELL, GAP

COLS, ROWS = 6, 5


def _grid(surf, game, side, x, y, title, subtitle):
    font, font_small = fonts()
    surf.blit(font.render(title, True, COLOR_TITLE), (x, y))
    surf.blit(font_tiny().render(subtitle, True, COLOR_DIM), (x, y + 26))
    y += 48
    names = game.loot_list(side)
    L = game.loot
    hovered = None
    for i in range(COLS * ROWS):
        r = pygame.Rect(x + (i % COLS) * (CELL + GAP), y + (i // COLS) * (CELL + GAP), CELL, CELL)
        name = names[i] if i < len(names) else None
        hover = hotspot(r, lambda n=name, s=side: game.loot_click(s, n)) if name else False
        if hover:
            hovered = name
            L["side"], L["sel"] = side, i
        selected = name is not None and L["side"] == side and L["sel"] == i
        _cell(surf, r, name, game.loot_count(side, name) if name else 0, selected, hover)
    if len(names) > COLS * ROWS:
        more = font_tiny().render(f"ещё {len(names) - COLS * ROWS}…", True, COLOR_DIM)
        surf.blit(more, (x, y + ROWS * (CELL + GAP)))
    return hovered


def draw_loot(surf, game):
    font, font_small = fonts()
    box = game.loot["box"]
    grid_w = COLS * (CELL + GAP) - GAP
    w = grid_w * 2 + 190
    h = 48 + ROWS * (CELL + GAP) + 140
    frame = pygame.Rect((S.SCREEN_W - w) // 2, max(8, (S.SCREEN_H - PANEL_H - h) // 2), w, h)
    panel(surf, frame, 248)
    close_button(surf, frame)

    lx, rx, y = frame.x + 20, frame.right - 20 - grid_w, frame.y + 16
    caps = game.inventory.count("крышки")
    hov_me = _grid(surf, game, "me", lx, y, "Рюкзак", f"крышки: {caps} · клик — положить")
    title = box["name"][:1].upper() + box["name"][1:]
    hov_box = _grid(surf, game, "box", rx, y, title,
                    "клик — взять · ПКМ — одну штуку" if game.loot_list("box") else "пусто")

    # середина: кнопки
    mx = lx + grid_w + 15
    bw = rx - mx - 15
    by = y + 80
    button(surf, (mx, by, bw, 30), "← Взять всё", game.loot_take_all, bool(game.loot_list("box")))
    button(surf, (mx, by + 40, bw, 30), "Закрыть", game.close_loot)
    arrow = font.render("⇄", True, COLOR_DIM)
    surf.blit(arrow, arrow.get_rect(center=(mx + bw // 2, by + 120)))

    # низ: описание предмета под курсором (или выбранного)
    name = hov_box or hov_me
    if name is None:
        names = game.loot_list(game.loot["side"])
        if names:
            name = names[min(game.loot["sel"], len(names) - 1)]
    iy = frame.bottom - 86
    pygame.draw.line(surf, (70, 62, 45), (frame.x + 20, iy - 10), (frame.right - 20, iy - 10))
    if name:
        d = items.ITEMS.get(name, {})
        line = name[:1].upper() + name[1:]
        if d.get("price"):
            line += f"   ·   цена {d['price']} кр."
        surf.blit(font_small.render(line, True, COLOR_TITLE), (frame.x + 24, iy))
        for i, t in enumerate(wrap_text(font_small, d.get("desc", ""), w - 48)[:2]):
            surf.blit(font_small.render(t, True, (215, 205, 185)), (frame.x + 24, iy + 24 + i * 20))
    hint = "Tab — сторона · стрелки — выбор · E — перенести · R — взять всё · Esc — закрыть"
    surf.blit(font_tiny().render(hint, True, COLOR_DIM), (frame.x + 24, frame.bottom - 20))
