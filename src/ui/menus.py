"""Всплывающие окна: диалог, крафт, рюкзак, торговля, выбор перка."""
import pygame

from .. import settings as S
from .. import items
from ..perks import PERKS_BY_ID
from .common import (fonts, wrap_text, panel, centered_box, draw_rows, rows_height,
                     COLOR_TITLE, COLOR_DIM, COLOR_OK, COLOR_BAD)


def draw_dialogue(surf, node, option_labels, speaker_name):
    font, font_small = fonts()
    line_h = 20
    box_w = S.SCREEN_W - 80
    text_lines = wrap_text(font_small, node.get("text", ""), box_w - 32)
    opt_lines = [wrap_text(font_small, f"[{i + 1}] {label}", box_w - 32) for i, label in enumerate(option_labels)]
    n_opt_lines = sum(len(l) for l in opt_lines) if option_labels else 1
    box_h = 44 + len(text_lines) * line_h + 8 + n_opt_lines * line_h + 12

    box = pygame.Rect(40, S.SCREEN_H - box_h - 20, box_w, box_h)
    panel(surf, box, 235)
    surf.blit(font.render(speaker_name, True, COLOR_TITLE), (box.x + 16, box.y + 10))

    y = box.y + 40
    for line in text_lines:
        surf.blit(font_small.render(line, True, S.COLOR_TEXT), (box.x + 16, y))
        y += line_h
    y += 8
    for lines in opt_lines:
        for j, line in enumerate(lines):
            surf.blit(font_small.render(line, True, (220, 210, 190)), (box.x + 16 + (0 if j == 0 else 24), y))
            y += line_h
    if not option_labels:
        surf.blit(font_small.render("[любая клавиша — закрыть]", True, (160, 150, 130)), (box.x + 16, y))


def draw_craft_menu(surf, inventory):
    font, font_small = fonts()
    box_w = 640
    inner_w = box_w - 32
    rows = []
    for i, (rid, recipe) in enumerate(inventory.recipes.items()):
        color = COLOR_OK if inventory.can_craft(rid) else COLOR_BAD
        need = ", ".join(f"{k} ×{v}" for k, v in recipe["ingredients"].items())
        for line in wrap_text(font_small, f"[{i + 1}] {recipe['name']}  —  нужно: {need}", inner_w):
            rows.append((line, color, 0))
        for line in wrap_text(font_small, recipe.get("desc", ""), inner_w - 14):
            rows.append((line, COLOR_DIM, 14))
        rows.append(None)

    box = centered_box(box_w, 80 + rows_height(rows) + 8)
    panel(surf, box)
    surf.blit(font.render("Крафт (Esc/C — закрыть)", True, COLOR_TITLE), (box.x + 16, box.y + 12))
    res = ", ".join(f"{k}: {inventory.count(k)}" for k in ("лом", "химикаты", "ткань")) 
    surf.blit(font_small.render("Ресурсы: " + res, True, S.COLOR_TEXT), (box.x + 16, box.y + 44))
    draw_rows(surf, rows, box.x + 16, box.y + 80, font_small)


def draw_inventory(surf, game):
    """Рюкзак и характеристики — местный «Пип-бой»."""
    font, font_small = fonts()
    p, inv = game.player, game.inventory
    box = centered_box(760, 440)
    panel(surf, box, 245)
    surf.blit(font.render("Рюкзак (I/Esc — закрыть)", True, COLOR_TITLE), (box.x + 16, box.y + 12))

    # слева — предметы; используемые пронумерованы
    usable = game.usable_items()
    rows = []
    for name, cnt in sorted(inv.nonzero().items()):
        if name in usable:
            text, color = f"[{usable.index(name) + 1}] {name} ×{cnt} — {items.ITEMS[name]['desc']}", COLOR_OK
        else:
            text, color = f"{name} ×{cnt}", S.COLOR_TEXT
        for j, line in enumerate(wrap_text(font_small, text, 400)):
            rows.append((line, color, 0 if j == 0 else 20))
    if not rows:
        rows.append(("пусто", COLOR_DIM, 0))
    draw_rows(surf, rows, box.x + 16, box.y + 50, font_small)
    if usable:
        cost = f" ({S.AP_CRAFT} ОД в бою)" if game.combat.active else ""
        surf.blit(font_small.render(f"Цифра — использовать{cost}", True, COLOR_DIM), (box.x + 16, box.bottom - 28))

    # справа — характеристики и перки
    x = box.x + 450
    armor = items.armor_ac(inv)
    stats = [
        (f"Уровень {p.level_sys.level}   HP {p.hp}/{p.max_hp}", S.COLOR_TEXT, 0),
        (f"ОД {p.max_ap}   КБ {p.ac + armor}" + (f" (броня +{armor})" if armor else ""), S.COLOR_TEXT, 0),
        (f"Ближний бой {p.melee_skill}%   Стрельба {p.guns_skill}%", S.COLOR_TEXT, 0),
        (f"Урон: {game.weapon_name()} {p.damage}±2", S.COLOR_TEXT, 0),
        None,
        ("Перки:", COLOR_TITLE, 0),
    ]
    for pid, rank in p.perks.items():
        name = PERKS_BY_ID[pid]["name"]
        stats.append((f"{name}" + (f" ×{rank}" if rank > 1 else ""), (200, 190, 170), 10))
    if not p.perks:
        stats.append(("пока нет", COLOR_DIM, 10))
    draw_rows(surf, stats, x, box.y + 50, font_small, line_h=22)


def draw_trade(surf, game):
    font, font_small = fonts()
    tr = game.traders[game.trade["id"]]
    buying = game.trade["tab"] == "buy"
    box = centered_box(640, 400)
    panel(surf, box, 245)
    title = f"Торговля: {tr['name']}  —  {'КУПИТЬ' if buying else 'ПРОДАТЬ'}"
    surf.blit(font.render(title, True, COLOR_TITLE), (box.x + 16, box.y + 12))
    money = f"Ваши крышки: {game.inventory.count('крышки')}   ·   у торговца: {tr['cash']}"
    if game.player.perk_rank("silver_tongue"):
        money += "   ·   [Красноречие] −20%"
    surf.blit(font_small.render(money, True, S.COLOR_TEXT), (box.x + 16, box.y + 44))

    rows = []
    for i, (name, qty, price, have) in enumerate(game.trade_rows()):
        afford = game.inventory.has("крышки", price) if buying else tr["cash"] >= price
        verb = "за" if buying else "получите"
        lot = f" ×{qty}" if qty > 1 else ""
        rows.append((f"[{(i + 1) % 10}] {name}{lot} — {verb} {price} кр.   (есть: {have})",
                     COLOR_OK if afford else COLOR_BAD, 0))
    if not rows:
        rows.append(("Нечего " + ("купить." if buying else "продать."), COLOR_DIM, 0))
    draw_rows(surf, rows[:10], box.x + 16, box.y + 80, font_small, line_h=24)
    surf.blit(font_small.render("Tab — купить/продать · цифра — сделка · Esc — выход", True, COLOR_DIM),
              (box.x + 16, box.bottom - 28))


def draw_perk_menu(surf, choices, player):
    font, font_small = fonts()
    box_w = 620
    rows = []
    for i, perk in enumerate(choices):
        rank = player.perk_rank(perk["id"])
        title = f"[{i + 1}] {perk['name']}" + (f" (ранг {rank + 1})" if perk["max_rank"] > 1 else "")
        rows.append((title, (230, 200, 110), 0))
        for line in wrap_text(font_small, perk["desc"], box_w - 50):
            rows.append((line, (200, 190, 170), 18))
        rows.append(None)
    box = centered_box(box_w, 70 + rows_height(rows, line_h=22))
    panel(surf, box, 245)
    surf.blit(font.render(f"Уровень {player.level_sys.level}! Выберите перк (1–{len(choices)})", True,
                          (140, 220, 120)), (box.x + 16, box.y + 14))
    draw_rows(surf, rows, box.x + 16, box.y + 52, font_small, line_h=22)
