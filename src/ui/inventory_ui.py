"""
Рюкзак: три зоны в одном окне.

  слева  — снаряжение (слоты оружия и брони) и характеристики героя;
  центр  — вкладки-фильтры и сетка ячеек с иконками и количеством;
  справа — карточка предмета: большая иконка, описание, свойства, цена, действие.

Карточка показывает предмет под курсором, а если курсор не над сеткой — выбранный.
Клик по ячейке выбирает предмет, двойной клик (или E) — главное действие.
"""
import pygame

from .. import settings as S
from .. import items
from .. import loader
from ..perks import PERKS_BY_ID
from ..weapons import WEAPONS
from .common import (fonts, font_tiny, wrap_text, panel, button, close_button, hotspot,
                     COLOR_TITLE, COLOR_DIM, COLOR_OK, COLOR_HOVER, PANEL_H)

COLS, ROWS = 6, 4
CELL, GAP = 58, 6
CELL_BG = (36, 31, 25)
CELL_BORDER = (88, 76, 54)
SLOT_BG = (30, 27, 22)
CAT_COLORS = {"weapon": (225, 150, 90), "ammo": (220, 190, 100), "armor": (140, 170, 210),
              "meds": (130, 220, 130), "resource": (200, 185, 150), "misc": (180, 170, 200)}


def _cell(surf, rect, name, count, selected, hover, worn=False):
    pygame.draw.rect(surf, (70, 60, 40) if hover else CELL_BG, rect, border_radius=4)
    border = COLOR_HOVER if selected else CAT_COLORS.get(items.category(name), CELL_BORDER) if name else CELL_BORDER
    pygame.draw.rect(surf, border, rect, 2 if selected else 1, border_radius=4)
    if not name:
        return
    icon = loader.item_icon(name, (40, 40), halo=False)
    surf.blit(icon, icon.get_rect(center=(rect.centerx, rect.centery - 3)))
    if worn:  # надетое — зелёная галочка в углу
        pygame.draw.circle(surf, (40, 120, 50), (rect.x + 10, rect.y + 10), 7)
        mark = font_tiny().render("✓", True, (230, 255, 230))
        surf.blit(mark, mark.get_rect(center=(rect.x + 10, rect.y + 10)))
    if count > 1:
        txt = font_tiny().render(str(count), True, (245, 240, 220))
        pos = txt.get_rect(bottomright=(rect.right - 4, rect.bottom - 2))
        surf.blit(font_tiny().render(str(count), True, (0, 0, 0)), pos.move(1, 1))
        surf.blit(txt, pos)


def _slot(surf, rect, label, name, caption, on_click=None):
    font, font_small = fonts()
    if on_click and name:
        if hotspot(rect, on_click):
            pygame.draw.rect(surf, (70, 60, 40), rect.inflate(4, 4), border_radius=7)
    pygame.draw.rect(surf, SLOT_BG, rect, border_radius=6)
    pygame.draw.rect(surf, CELL_BORDER, rect, 1, border_radius=6)
    if name:
        icon = loader.item_icon(name, (48, 48), halo=False)
        surf.blit(icon, icon.get_rect(center=rect.center))
    else:
        dash = font.render("—", True, (90, 80, 65))
        surf.blit(dash, dash.get_rect(center=rect.center))
    lab = font_tiny().render(label, True, COLOR_DIM)
    surf.blit(lab, lab.get_rect(midbottom=(rect.centerx, rect.y - 2)))
    lines = wrap_text(font_tiny(), caption, rect.w + 8)
    if len(lines) > 2:
        lines = [lines[0], lines[1] + "…"]
    for i, line in enumerate(lines):
        cap = font_tiny().render(line, True, (220, 205, 160))
        surf.blit(cap, cap.get_rect(midtop=(rect.centerx, rect.bottom + 3 + i * 15)))


def _item_facts(game, name):
    """Строки свойств для карточки: (текст, цвет)."""
    d = items.ITEMS.get(name, {})
    facts = []
    use = d.get("use", {})
    if use.get("heal_full"):
        facts.append(("Лечит полностью", COLOR_OK))
    elif use.get("heal"):
        facts.append((f"Лечит {use['heal']} HP", COLOR_OK))
    if use:
        facts.append((f"В бою: {S.AP_CRAFT} ОД", COLOR_DIM))
    slot = d.get("slot")
    if slot:
        worn = game.player.equipped(slot) == name
        facts.append((f"Слот: {items.SLOT_NAMES[slot]}" + (" · НАДЕТО" if worn else ""),
                      COLOR_HOVER if worn else (140, 170, 210)))
        facts.append((f"+{d.get('armor_ac', 0)} к классу брони", (140, 170, 210)))
        if d.get("ap"):
            facts.append((f"{d['ap']:+d} ОД в бою", (230, 110, 90) if d["ap"] < 0 else COLOR_OK))
        if d.get("guns"):
            facts.append((f"{d['guns']:+d}% к стрельбе", (230, 110, 90) if d["guns"] < 0 else COLOR_OK))
    for w in WEAPONS.values():
        if w.get("item") == name:
            facts.append((f"Урон {w['damage']}±2 · дальность {w['range']} кл.", (225, 150, 90)))
            facts.append((f"Выстрел: {w['ap']} ОД · патроны: {game.inventory.count(w['ammo'])}", COLOR_DIM))
            if game.player.weapon == "pistol":
                facts.append(("В руках", COLOR_HOVER))
        if w.get("ammo") == name:
            facts.append((f"Для оружия: {w['name']}", (220, 190, 100)))
    if name == "заточенный лом":
        facts.append(("+3 к урону в ближнем бою (уже учтено)", (225, 150, 90)))
    used_in = [r["name"] for r in game.inventory.recipes.values() if name in r["ingredients"]]
    if used_in:
        facts.append(("Нужен для: " + ", ".join(used_in), (200, 185, 150)))
    if d.get("price"):
        facts.append((f"Цена: {d['price']} кр.", (230, 210, 110)))
    return facts


def _card(surf, rect, game, name):
    font, font_small = fonts()
    pygame.draw.rect(surf, (26, 22, 18), rect, border_radius=6)
    pygame.draw.rect(surf, CELL_BORDER, rect, 1, border_radius=6)
    x, y, w = rect.x + 14, rect.y + 14, rect.w - 28
    if not name:
        msg = font_small.render("Выберите предмет", True, COLOR_DIM)
        surf.blit(msg, msg.get_rect(center=rect.center))
        return
    cat = items.category(name)
    icon_box = pygame.Rect(x, y, 72, 72)
    pygame.draw.rect(surf, CELL_BG, icon_box, border_radius=6)
    pygame.draw.rect(surf, CAT_COLORS.get(cat, CELL_BORDER), icon_box, 1, border_radius=6)
    icon = loader.item_icon(name, (64, 64), halo=False)
    surf.blit(icon, icon.get_rect(center=icon_box.center))
    tx = x + 84
    title = name[:1].upper() + name[1:]
    tfont, th = font, 22
    title_lines = wrap_text(tfont, title, w - 84)
    if len(title_lines) > 2:  # длинное название — мельче, но целиком
        tfont, th = font_small, 18
        title_lines = wrap_text(tfont, title, w - 84)[:3]
    for i, line in enumerate(title_lines):
        surf.blit(tfont.render(line, True, COLOR_TITLE), (tx, y + i * th))
    ty = y + len(title_lines) * th + 2
    surf.blit(font_tiny().render(items.CATEGORY_NAMES.get(cat, ""), True, CAT_COLORS.get(cat, COLOR_DIM)), (tx, ty))
    surf.blit(font_small.render(f"× {game.inventory.count(name)}", True, S.COLOR_TEXT), (tx, ty + 18))

    y += 84
    for line in wrap_text(font_small, items.ITEMS.get(name, {}).get("desc", ""), w)[:5]:
        surf.blit(font_small.render(line, True, (215, 205, 185)), (x, y))
        y += 19
    y += 6
    pygame.draw.line(surf, (70, 62, 45), (x, y), (x + w, y), 1)
    y += 8
    for text, color in _item_facts(game, name):
        for line in wrap_text(font_small, text, w):
            if y > rect.bottom - 58:
                break
            surf.blit(font_small.render(line, True, color), (x, y))
            y += 19

    action = game.item_action(name)
    brect = pygame.Rect(x, rect.bottom - 44, w, 30)
    if action:
        button(surf, brect, f"{action[0]}  [E]", action[1])
    else:
        note = font_tiny().render("Нельзя использовать напрямую", True, (110, 100, 85))
        surf.blit(note, note.get_rect(center=brect.center))


def draw_inventory(surf, game):
    font, font_small = fonts()
    p, inv = game.player, game.inventory
    box = pygame.Rect(16, 6, S.SCREEN_W - 32, S.SCREEN_H - PANEL_H - 12)
    panel(surf, box, 248)
    surf.blit(font.render("РЮКЗАК", True, COLOR_TITLE), (box.x + 16, box.y + 12))
    close_button(surf, box)

    # ---- слева: снаряжение и персонаж
    lx = box.x + 16
    surf.blit(font_small.render("Снаряжение", True, COLOR_TITLE), (lx, box.y + 44))
    if p.weapon == "pistol":
        w_item = WEAPONS["pistol"]["item"]
    else:
        w_item = "заточенный лом" if inv.has("заточенный лом") else "лом"
    def select(n):
        return lambda: setattr(game, "inv_sel", n)
    slots = [("Голова", p.equipped("head")), ("Тело", p.equipped("body")), ("Оружие", w_item)]
    for i, (label, name) in enumerate(slots):
        cap = (game.weapon_name() if label == "Оружие" else name[:1].upper() + name[1:] if name else "пусто")
        _slot(surf, pygame.Rect(lx + 2 + i * 76, box.y + 84, 60, 60), label, name, cap, select(name))
    lv = p.level_sys
    stats = [
        f"Уровень {lv.level} · XP {lv.xp}/{lv.xp_needed}",
        f"HP {p.hp}/{p.max_hp}",
        f"ОД {p.max_ap} · КБ {p.armor_class}",
        f"Ближний бой {p.melee_skill}%",
        f"Стрельба {p.guns_skill}%",
        f"Урон в ближнем {p.damage}±2",
    ]
    y = box.y + 204
    for line in stats:
        surf.blit(font_small.render(line, True, S.COLOR_TEXT), (lx, y))
        y += 19
    y += 6
    surf.blit(font_small.render("Перки", True, COLOR_TITLE), (lx, y))
    y += 20
    perk_names = [PERKS_BY_ID[pid]["name"] + (f" ×{r}" if r > 1 else "") for pid, r in p.perks.items()]
    if len(perk_names) > 3:
        perk_names = perk_names[:2] + [f"…и ещё {len(perk_names) - 2}"]
    for line in perk_names or ["пока нет"]:
        surf.blit(font_tiny().render(line, True, (200, 190, 170) if perk_names else COLOR_DIM), (lx + 6, y))
        y += 16
    caps = loader.item_icon("крышки", (24, 24), halo=False)
    surf.blit(caps, (lx, box.bottom - 34))
    surf.blit(font_small.render(f"{inv.count('крышки')} крышек", True, (230, 210, 110)), (lx + 30, box.bottom - 32))

    # ---- центр: вкладки и сетка
    gx = box.x + 236
    # ширина вкладок — по подписи, остаток ширины сетки делится поровну
    grid_w = COLS * (CELL + GAP) - GAP
    tabs = items.CATEGORY_TABS
    widths = [font_tiny().size(label)[0] + 12 for _, label, _ in tabs]
    extra = (grid_w - sum(widths) - 4 * (len(tabs) - 1)) // len(tabs)
    tx = gx
    for i, (tid, label, _) in enumerate(tabs):
        r = pygame.Rect(tx, box.y + 42, widths[i] + extra, 24)
        tx += r.w + 4
        active = tid == game.inv_tab
        if active:
            pygame.draw.rect(surf, (80, 68, 44), r, border_radius=3)
            pygame.draw.rect(surf, COLOR_HOVER, r, 1, border_radius=3)
            t = font_tiny().render(label, True, COLOR_HOVER)
            surf.blit(t, t.get_rect(center=r.center))
        else:
            button(surf, r, label, lambda tid=tid: game.inv_set_tab(tid))

    visible = game.inventory_items()
    hovered = None
    gy = box.y + 76
    for i in range(COLS * ROWS):
        r = pygame.Rect(gx + (i % COLS) * (CELL + GAP), gy + (i // COLS) * (CELL + GAP), CELL, CELL)
        name = visible[i] if i < len(visible) else None
        hover = hotspot(r, lambda n=name: game.inv_click(n)) if name else False
        if hover:
            hovered = name
        worn = bool(name) and items.slot(name) is not None and p.equipped(items.slot(name)) == name
        _cell(surf, r, name, inv.count(name) if name else 0, name == game.inv_sel, hover, worn)
    grid_bottom = gy + ROWS * (CELL + GAP)
    info = f"Предметов: {len(visible)}" + (" (показаны первые 24)" if len(visible) > COLS * ROWS else "")
    surf.blit(font_tiny().render(info, True, COLOR_DIM), (gx, grid_bottom + 2))
    for i, hint in enumerate(("Клик — выбрать · двойной клик или E — использовать",
                              "Стрелки — выбор · Tab — вкладки · I или Esc — закрыть")):
        surf.blit(font_tiny().render(hint, True, COLOR_DIM), (gx, box.bottom - 38 + i * 16))

    # ---- справа: карточка предмета (под курсором или выбранного)
    cx = gx + COLS * (CELL + GAP) + 10
    _card(surf, pygame.Rect(cx, box.y + 42, box.right - cx - 14, box.h - 56), game, hovered or game.inv_sel)
