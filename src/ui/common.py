"""Общее для всего интерфейса: шрифты, перенос строк, подложка окон,
кликабельные зоны для мыши."""
import pygame

from .. import settings as S
from .. import fonts as fontlib

pygame.font.init()
_FONTS = {}

COLOR_TITLE = (210, 190, 120)
COLOR_DIM = (170, 160, 145)
COLOR_OK = (140, 220, 140)
COLOR_BAD = (150, 130, 110)
COLOR_HOVER = (255, 240, 170)

PANEL_H = 104  # нижняя панель интерфейса (лог, HP, ОД, кнопки) — всегда на экране

# ------------------------------------------------------------ мышь
# Окна при отрисовке отмечают кликабельные зоны и клавишу, которой равен клик
# (строка ответа [2] = клавиша 2, кнопка «Конец хода» = R и т.д.), —
# поэтому мышь идёт через ту же логику, что и клавиатура.
_hotspots = []


def begin_frame():
    _hotspots.clear()


def mouse_pos():
    return pygame.mouse.get_pos()


def hotspot(rect, key):
    """Отметить зону; key — клавиша, которой равен клик, или функция, которую вызвать.
    Возвращает True, если мышь сейчас над зоной (для подсветки)."""
    rect = pygame.Rect(rect)
    _hotspots.append((rect, key))
    return rect.collidepoint(mouse_pos())


def hotspot_at(pos):
    """Клавиша под курсором (верхняя из отмеченных) или None."""
    for rect, key in reversed(_hotspots):
        if rect.collidepoint(pos):
            return key
    return None


def over_ui(pos):
    """Курсор над интерфейсом (панель или отмеченная зона), а не над миром."""
    return pos[1] >= S.SCREEN_H - PANEL_H or hotspot_at(pos) is not None


def button(surf, rect, label, key, enabled=True):
    """Кнопка в стиле панели Fallout. Кликабельна, подсвечивается под курсором."""
    rect = pygame.Rect(rect)
    hover = hotspot(rect, key) if enabled else False
    fill = (70, 60, 40) if hover else (45, 38, 30)
    pygame.draw.rect(surf, fill, rect, border_radius=3)
    pygame.draw.rect(surf, S.COLOR_PANEL_BORDER if enabled else (70, 62, 45), rect, 1, border_radius=3)
    color = COLOR_HOVER if hover else ((220, 205, 160) if enabled else (110, 100, 85))
    while font_tiny().size(label)[0] > rect.w - 6 and len(label) > 4:
        label = label[:-2].rstrip() + "…"  # длинная подпись — обрезаем с многоточием
    txt = font_tiny().render(label, True, color)
    surf.blit(txt, txt.get_rect(center=rect.center))


def close_button(surf, box):
    """[×] в правом верхнем углу окна — то же, что Esc."""
    button(surf, (box.right - 30, box.y + 8, 22, 22), "×", pygame.K_ESCAPE)


def option_row(surf, font, text, pos, key, color, width):
    """Строка-вариант (ответ в диалоге, рецепт, товар): кликабельна, подсвечивается."""
    rect = pygame.Rect(pos[0] - 4, pos[1] - 1, width + 8, font.get_linesize())
    hover = hotspot(rect, key)
    if hover:
        pygame.draw.rect(surf, (70, 60, 40), rect, border_radius=3)
    surf.blit(font.render(text, True, COLOR_HOVER if hover else color), pos)
    return hover


def digit_key(i):
    """Номер пункта 0..9 -> клавиша 1..9, 0 (как в controls.number_key)."""
    return pygame.K_1 + i if i < 9 else pygame.K_0


def _font(size):
    if size not in _FONTS:
        try:
            _FONTS[size] = fontlib.get("dejavusans", size)
        except Exception:
            _FONTS[size] = pygame.font.Font(None, size + 2)
    return _FONTS[size]


def fonts():
    """(обычный, мелкий) — используются почти везде."""
    return _font(20), _font(16)


def font_tiny():
    return _font(13)


def wrap_text(font, text, max_w):
    """Разбивает текст на строки по словам так, чтобы каждая влезала в max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}" if cur else word
        if cur and font.size(trial)[0] > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def panel(surf, rect, alpha=240):
    """Полупрозрачная тёмная подложка окна с рамкой."""
    p = pygame.Surface(rect.size, pygame.SRCALPHA)
    p.fill((*S.COLOR_PANEL, alpha))
    pygame.draw.rect(p, S.COLOR_PANEL_BORDER, p.get_rect(), 2)
    surf.blit(p, rect.topleft)


def centered_box(w, h):
    """Окно по центру области над нижней панелью (если влезает)."""
    area_h = S.SCREEN_H - PANEL_H
    y = max(8, (area_h - h) // 2)
    return pygame.Rect(S.SCREEN_W // 2 - w // 2, y, w, h)


def draw_rows(surf, rows, x, y, font, line_h=20, gap=8):
    """rows: (текст, цвет, отступ) или None (пустой промежуток). Возвращает y после последней строки."""
    for r in rows:
        if r is None:
            y += gap
            continue
        text, color, dx = r
        surf.blit(font.render(text, True, color), (x + dx, y))
        y += line_h
    return y


def rows_height(rows, line_h=20, gap=8):
    return sum(line_h if r else gap for r in rows)
