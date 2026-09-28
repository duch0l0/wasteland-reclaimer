"""
Экран терминала RobCo: зелёный моноширинный текст на тёмном стекле,
строки развёртки, виньетка. Тем же экраном показываются записки (янтарная
бумага) и голозаписи (зелёный с помехами).
"""
import pygame

from .. import settings as S
from .common import hotspot, wrap_text, PANEL_H

GREEN = (110, 235, 130)
GREEN_DIM = (60, 150, 75)
BG = (8, 22, 12)
PAPER_BG = (46, 38, 26)
PAPER_INK = (235, 215, 170)

_FONTS = {}
_OVERLAY = {}


def _mono(size):
    if size not in _FONTS:
        path = pygame.font.match_font("dejavusansmono") or pygame.font.match_font("liberationmono")
        _FONTS[size] = pygame.font.Font(path, size) if path else pygame.font.Font(None, size + 4)
    return _FONTS[size]


def _crt_overlay(size):
    """Строки развёртки и затемнение к краям — один раз на размер экрана."""
    if size not in _OVERLAY:
        w, h = size
        o = pygame.Surface(size, pygame.SRCALPHA)
        for y in range(0, h, 3):
            pygame.draw.line(o, (0, 0, 0, 55), (0, y), (w, y))
        for i in range(24):  # виньетка — несколько рамок с нарастающей тенью
            a = int(6 + i * 3.5)
            pygame.draw.rect(o, (0, 0, 0, a), (i * 2, i * 2, w - i * 4, h - i * 4), 2, border_radius=18)
        _OVERLAY[size] = o
    return _OVERLAY[size]


def _screen_rect():
    return pygame.Rect(90, 20, S.SCREEN_W - 180, S.SCREEN_H - PANEL_H - 36)


def _frame(surf, rect, paper=False):
    """Корпус терминала (или лист бумаги) и стекло."""
    if paper:
        pygame.draw.rect(surf, (20, 16, 12), rect.inflate(18, 18), border_radius=6)
        pygame.draw.rect(surf, PAPER_BG, rect, border_radius=4)
        return
    pygame.draw.rect(surf, (70, 64, 52), rect.inflate(36, 36), border_radius=22)
    pygame.draw.rect(surf, (40, 36, 30), rect.inflate(36, 36), 3, border_radius=22)
    pygame.draw.rect(surf, (25, 22, 18), rect.inflate(12, 12), border_radius=16)
    pygame.draw.rect(surf, BG, rect, border_radius=14)


def _line(surf, font, text, pos, color, hover_key=None, width=None, selected=False):
    """Строка меню: под курсором или выбранная — инверсия, как в Fallout."""
    r = pygame.Rect(pos[0] - 6, pos[1] - 2, (width or font.size(text)[0]) + 12, font.get_linesize() + 2)
    hover = hotspot(r, hover_key) if hover_key is not None else False
    if hover or selected:
        pygame.draw.rect(surf, GREEN, r)
        surf.blit(font.render(text, True, BG), pos)
    else:
        surf.blit(font.render(text, True, color), pos)
    return hover


def draw_terminal(surf, game):
    t = game.term
    rect = _screen_rect()
    dim = pygame.Surface((S.SCREEN_W, S.SCREEN_H), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 170))
    surf.blit(dim, (0, 0))
    if t.get("doc"):
        _draw_doc(surf, game, rect)
        return
    _frame(surf, rect)
    from ..game.terminals import TERMINALS
    term = TERMINALS[t["id"]]
    f, fs = _mono(20), _mono(17)
    x, y = rect.x + 34, rect.y + 26
    for line in term["header"]:
        surf.blit(f.render(line, True, GREEN), (x, y))
        y += 26
    y += 6
    pygame.draw.line(surf, GREEN_DIM, (x, y), (rect.right - 34, y), 1)
    y += 16
    view = t["view"]
    if view == "menu":
        for i, (_, e) in enumerate(game.term_entries()):
            label = f"> {e['label']}"
            if "lock" in e and not game.is_unlocked(e):
                label += "  [ЗАБЛОКИРОВАНО]" if game.is_locked_out(e) else "  [ЗАКРЫТО]"
            if _line(surf, f, label, (x, y), GREEN, lambda i=i: game.term_open_entry(i), selected=i == t["sel"]):
                t["sel"] = i
            y += 32
        _footer(surf, fs, rect, "↑↓ — выбор · Enter/клик — открыть · Esc — выключить", game)
    elif view == "entry":
        e = term["entries"][t["entry"]]
        surf.blit(f.render(e["label"], True, GREEN), (x, y))
        y += 34
        _draw_text(surf, fs, game.term_entry_text(), x, y, rect, t, GREEN)
        _line(surf, f, "> Назад", (x, rect.bottom - 58), GREEN, game.term_back)
        _footer(surf, fs, rect, "↑↓ — прокрутка · Esc — назад", game)
    elif view == "locked":
        e = term["entries"][t["entry"]]
        surf.blit(f.render(f"{e['label']}: ДОСТУП ЗАКРЫТ", True, GREEN), (x, y))
        y += 30
        msg = ("Слишком много неверных попыток. Терминал заблокирован. Обратитесь к администратору."
               if game.is_locked_out(e) else "Введите пароль.")
        surf.blit(fs.render(msg, True, GREEN_DIM), (x, y))
        y += 44
        for i, (label, action) in enumerate(game.lock_options()):
            if _line(surf, f, f"> {label}", (x, y), GREEN, action, selected=i == t.get("lock_sel", 0)):
                t["lock_sel"] = i
            y += 34
        _footer(surf, fs, rect, "↑↓ — выбор · Enter/клик — выполнить · Esc — назад", game)
    elif view == "hack":
        _draw_hack(surf, game, rect, x, y)
    surf.blit(_crt_overlay(rect.size), rect)


def _draw_text(surf, font, text, x, y, rect, t, color):
    lines = []
    for para in text.split("\n"):
        lines += wrap_text(font, para, rect.w - 70) or [""]
    per_page = (rect.bottom - 80 - y) // font.get_linesize()
    t["scroll"] = max(0, min(t["scroll"], len(lines) - per_page))
    for line in lines[t["scroll"]: t["scroll"] + per_page]:
        surf.blit(font.render(line, True, color), (x, y))
        y += font.get_linesize()
    if len(lines) > per_page:
        more = font.render(f"[{t['scroll'] + per_page}/{len(lines)}] ↓", True, color)
        surf.blit(more, (rect.right - 40 - more.get_width(), rect.bottom - 90))


def _footer(surf, font, rect, text, game):
    surf.blit(font.render(text, True, GREEN_DIM), (rect.x + 34, rect.bottom - 30))


def _draw_hack(surf, game, rect, x, y):
    h = game.term["hack"]
    f, fs = _mono(18), _mono(17)
    surf.blit(f.render("ВЗЛОМ: введите пароль", True, GREEN), (x, y))
    y += 26
    blocks = "■ " * h["tries"]
    surf.blit(f.render(f"Попыток осталось: {h['tries']}  {blocks}", True, GREEN), (x, y))
    y += 36
    left = game.hack_words_left()
    cur = left[h["cursor"] % len(left)] if left and h["tries"] > 0 else None
    cw = f.size("W")[0]
    col_w = cw * (7 + DUMP_W) + 40
    for r, line in enumerate(h["dump"]):
        col, row = divmod(r, _rows(h))
        lx, ly = x + col * col_w, y + row * 22
        surf.blit(f.render(f"0x{h['base'] + r * 12:04X}", True, GREEN_DIM), (lx, ly))
        tx = lx + cw * 7
        word = next((w for w, (wr, _) in h["placed"].items() if wr == r), None)
        if word is None:
            surf.blit(f.render(line, True, GREEN), (tx, ly))
            continue
        start = h["placed"][word][1]
        before, after = line[:start], line[start + len(word):]
        surf.blit(f.render(before, True, GREEN), (tx, ly))
        wx = tx + cw * start
        tried = word in h["tried"]
        wrect = pygame.Rect(wx - 2, ly - 1, cw * len(word) + 4, 21)
        hover = h["tries"] > 0 and not tried and hotspot(wrect, lambda w=word: game.hack_guess(w))
        if hover:
            h["cursor"] = left.index(word)
        if (hover or word == cur) and not tried:
            pygame.draw.rect(surf, GREEN, wrect)
            surf.blit(f.render(word, True, BG), (wx, ly))
        else:
            surf.blit(f.render("." * len(word) if tried else word, True, GREEN_DIM if tried else GREEN), (wx, ly))
        surf.blit(f.render(after, True, GREEN), (wx + cw * len(word), ly))
    # журнал попыток — справа, снизу вверх
    lx = x + 2 * col_w + 10
    ly = y + _rows(h) * 22 - 22
    for line in reversed(h["log"][-14:]):
        surf.blit(fs.render(line, True, GREEN), (lx, ly))
        ly -= 22
    hint = ("Терминал заблокирован. Enter/Esc — назад." if h["tries"] <= 0 else
            "Клик по слову или ←→ и Enter. Число совпадений — буквы на своих местах. Esc — отмена")
    _footer(surf, fs, rect, hint, game)


DUMP_W = 12


def _rows(h):
    return len(h["dump"]) // 2


def _draw_doc(surf, game, rect):
    from ..game.terminals import DOCS
    d = DOCS[game.term["doc"]]
    paper = d.get("kind") == "note"
    r = rect.inflate(-180, 0) if paper else rect
    _frame(surf, r, paper=paper)
    color = PAPER_INK if paper else GREEN
    title_font = pygame.font.SysFont("dejavuserif", 24) if paper else _mono(20)
    body = pygame.font.SysFont("dejavuserif", 19) if paper else _mono(17)
    x, y = r.x + 34, r.y + 26
    prefix = "" if paper else "ГОЛОЗАПИСЬ ▶ "
    surf.blit(title_font.render(prefix + d["title"], True, color), (x, y))
    y += 44
    _draw_text(surf, body, d["text"], x, y, r, game.term, color)
    hint_font = _mono(15)
    hint = hint_font.render("↑↓ — прокрутка · Esc/Enter/клик — закрыть", True, (150, 130, 100) if paper else GREEN_DIM)
    surf.blit(hint, (x, r.bottom - 30))
    hotspot(r, game.close_terminal)
    if not paper:
        surf.blit(_crt_overlay(r.size), r)
