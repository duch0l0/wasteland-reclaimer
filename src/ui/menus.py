"""Всплывающие окна: диалог, крафт, рюкзак, торговля, выбор перка."""
import pygame

from .. import settings as S
from .. import items
from ..perks import PERKS_BY_ID
from .common import (fonts, wrap_text, panel, centered_box, draw_rows, hotspot,
                     close_button, button, digit_key, PANEL_H,
                     COLOR_TITLE, COLOR_DIM, COLOR_OK, COLOR_BAD, COLOR_HOVER)


def _clickable_block(surf, rect, key):
    """Кликабельный блок из нескольких строк (рецепт, перк): подсветка под курсором."""
    hover = hotspot(rect, key)
    if hover:
        pygame.draw.rect(surf, (70, 60, 40), rect, border_radius=3)
    return hover


def draw_dialogue(surf, node, option_labels, speaker_name):
    font, font_small = fonts()
    line_h = 20
    box_w = S.SCREEN_W - 80
    text_lines = wrap_text(font_small, node.get("text", ""), box_w - 32)
    opt_lines = [wrap_text(font_small, f"[{i + 1}] {label}", box_w - 32) for i, label in enumerate(option_labels)]
    n_opt_lines = sum(len(l) for l in opt_lines) if option_labels else 1
    box_h = 44 + len(text_lines) * line_h + 8 + n_opt_lines * line_h + 12

    box = pygame.Rect(40, S.SCREEN_H - PANEL_H - box_h - 8, box_w, box_h)
    panel(surf, box, 235)
    surf.blit(font.render(speaker_name, True, COLOR_TITLE), (box.x + 16, box.y + 10))

    y = box.y + 40
    for line in text_lines:
        surf.blit(font_small.render(line, True, S.COLOR_TEXT), (box.x + 16, y))
        y += line_h
    y += 8
    for i, lines in enumerate(opt_lines):
        hover = _clickable_block(surf, pygame.Rect(box.x + 10, y - 1, box.w - 20, len(lines) * line_h), digit_key(i))
        for j, line in enumerate(lines):
            color = COLOR_HOVER if hover else (220, 210, 190)
            surf.blit(font_small.render(line, True, color), (box.x + 16 + (0 if j == 0 else 24), y))
            y += line_h
    if not option_labels:
        hover = _clickable_block(surf, pygame.Rect(box.x + 10, y - 1, 260, line_h), pygame.K_SPACE)
        surf.blit(font_small.render("[любая клавиша или клик — закрыть]", True,
                                    COLOR_HOVER if hover else (160, 150, 130)), (box.x + 16, y))


def draw_craft_menu(surf, inventory):
    font, font_small = fonts()
    box_w = 640
    inner_w = box_w - 32
    blocks = []  # строки каждого рецепта отдельно — рецепт кликается целиком
    for i, (rid, recipe) in enumerate(inventory.recipes.items()):
        color = COLOR_OK if inventory.can_craft(rid) else COLOR_BAD
        need = ", ".join(f"{k} ×{v}" for k, v in recipe["ingredients"].items())
        rows = [(line, color, 0) for line in
                wrap_text(font_small, f"[{i + 1}] {recipe['name']}  —  нужно: {need}", inner_w)]
        rows += [(line, COLOR_DIM, 14) for line in wrap_text(font_small, recipe.get("desc", ""), inner_w - 14)]
        blocks.append(rows)

    line_h = 19
    box = centered_box(box_w, 74 + sum(len(b) * line_h + 6 for b in blocks) + 6)
    panel(surf, box)
    surf.blit(font.render("Крафт — клик по рецепту (Esc/C — закрыть)", True, COLOR_TITLE), (box.x + 16, box.y + 12))
    close_button(surf, box)
    res = ", ".join(f"{k}: {inventory.count(k)}" for k in ("лом", "химикаты", "ткань"))
    surf.blit(font_small.render("Ресурсы: " + res, True, S.COLOR_TEXT), (box.x + 16, box.y + 42))
    y = box.y + 72
    for i, rows in enumerate(blocks):
        h = len(rows) * line_h
        hover = _clickable_block(surf, pygame.Rect(box.x + 10, y - 2, box.w - 20, h + 2), digit_key(i))
        for text, color, dx in rows:
            surf.blit(font_small.render(text, True, COLOR_HOVER if hover and dx == 0 else color), (box.x + 16 + dx, y))
            y += line_h
        y += 6


def draw_trade(surf, game):
    font, font_small = fonts()
    tr = game.traders[game.trade["id"]]
    buying = game.trade["tab"] == "buy"
    box = centered_box(640, 400)
    panel(surf, box, 245)
    surf.blit(font.render(f"Торговля: {tr['name']}", True, COLOR_TITLE), (box.x + 16, box.y + 12))
    close_button(surf, box)
    # вкладки: активная не кликается, соседняя — переключает (Tab)
    for i, (label, tab) in enumerate((("Купить", "buy"), ("Продать", "sell"))):
        button(surf, (box.right - 230 + i * 96, box.y + 10, 90, 24), label.upper() if tab == game.trade["tab"] else label,
               pygame.K_TAB, enabled=tab != game.trade["tab"])
    money = f"Ваши крышки: {game.inventory.count('крышки')}   ·   у торговца: {tr['cash']}"
    if game.player.perk_rank("silver_tongue"):
        money += "   ·   [Красноречие] −20%"
    surf.blit(font_small.render(money, True, S.COLOR_TEXT), (box.x + 16, box.y + 44))

    y = box.y + 80
    rows = game.trade_rows()[:10]
    for i, (name, qty, price, have) in enumerate(rows):
        afford = game.inventory.has("крышки", price) if buying else tr["cash"] >= price
        verb = "за" if buying else "получите"
        lot = f" ×{qty}" if qty > 1 else ""
        hover = _clickable_block(surf, pygame.Rect(box.x + 10, y - 2, box.w - 20, 22), digit_key(i))
        text = f"[{(i + 1) % 10}] {name}{lot} — {verb} {price} кр.   (есть: {have})"
        color = COLOR_HOVER if hover else COLOR_OK if afford else COLOR_BAD
        surf.blit(font_small.render(text, True, color), (box.x + 16, y))
        y += 24
    if not rows:
        surf.blit(font_small.render("Нечего " + ("купить." if buying else "продать."), True, COLOR_DIM), (box.x + 16, y))
    surf.blit(font_small.render("Клик или цифра — сделка · Tab — купить/продать · Esc — выход", True, COLOR_DIM),
              (box.x + 16, box.bottom - 28))


def draw_perk_menu(surf, choices, player):
    font, font_small = fonts()
    box_w = 620
    blocks = []
    for i, perk in enumerate(choices):
        rank = player.perk_rank(perk["id"])
        title = f"[{i + 1}] {perk['name']}" + (f" (ранг {rank + 1})" if perk["max_rank"] > 1 else "")
        if perk.get("kind") == "skill":
            title = f"[{i + 1}] {perk['name']}"
        blocks.append([(title, (230, 200, 110), 0)] +
                      [(line, (200, 190, 170), 18) for line in wrap_text(font_small, perk["desc"], box_w - 50)])
    line_h = 22
    box = centered_box(box_w, 64 + sum(len(b) * line_h + 8 for b in blocks))
    panel(surf, box, 245)
    what = "навык (+10)" if choices and choices[0].get("kind") == "skill" else "перк"
    surf.blit(font.render(f"Уровень {player.level_sys.level}! Выберите {what} (клик или 1–{len(choices)})", True,
                          (140, 220, 120)), (box.x + 16, box.y + 14))
    y = box.y + 52
    for i, rows in enumerate(blocks):
        hover = _clickable_block(surf, pygame.Rect(box.x + 10, y - 2, box.w - 20, len(rows) * line_h + 2), digit_key(i))
        for text, color, dx in rows:
            surf.blit(font_small.render(text, True, COLOR_HOVER if hover and dx == 0 else color), (box.x + 16 + dx, y))
            y += line_h
        y += 8
