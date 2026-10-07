"""Журнал заданий (J) — в стиле Пип-боя: слева список, справа записи по стадиям."""
import pygame

from .. import settings as S
from .common import hotspot, wrap_text, close_button, PANEL_H
from .terminal_ui import _mono, _crt_overlay, GREEN, GREEN_DIM, BG

AMBER = (235, 200, 110)


def journal_list(game):
    """Задания в порядке показа: сначала главное и активные, потом выполненные."""
    from ..game.quests import QUESTS
    ids = [q for q in game.quests if q in QUESTS]

    def order(q):
        d = QUESTS[q]
        done = game.stage(q) >= d.get("done", 10 ** 9)
        return (done, not d.get("main"), q)
    return sorted(ids, key=order)


def draw_journal(surf, game):
    from ..game.quests import QUESTS
    dim = pygame.Surface((S.SCREEN_W, S.SCREEN_H), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 160))
    surf.blit(dim, (0, 0))
    box = pygame.Rect(60, 16, S.SCREEN_W - 120, S.SCREEN_H - PANEL_H - 28)
    pygame.draw.rect(surf, (70, 64, 52), box.inflate(24, 24), border_radius=16)
    pygame.draw.rect(surf, BG, box, border_radius=10)
    f, fs, ft = _mono(22), _mono(17), _mono(15)
    surf.blit(f.render("ПИП-БОЙ 2000", True, GREEN), (box.x + 24, box.y + 16))
    tx = box.x + 220
    for tab, label in (("quests", "ЗАДАНИЯ"), ("rep", "РЕПУТАЦИЯ")):   # вкладки: клик или Tab
        img = fs.render(label, True, BG if game.journal_tab == tab else GREEN)
        r = pygame.Rect(tx, box.y + 14, img.get_width() + 20, 28)
        hover = hotspot(r, lambda tab=tab: (setattr(game, "journal_tab", tab), setattr(game, "journal_scroll", 0)))
        if game.journal_tab == tab or hover:
            pygame.draw.rect(surf, GREEN if game.journal_tab == tab else GREEN_DIM, r)
            img = fs.render(label, True, BG)
        surf.blit(img, (r.x + 10, r.y + 4))
        tx = r.right + 12
    close_button(surf, box)
    pygame.draw.line(surf, GREEN_DIM, (box.x + 20, box.y + 52), (box.right - 20, box.y + 52))
    if game.journal_tab == "rep":
        draw_reputation(surf, game, box)
        surf.blit(ft.render("J или Esc — закрыть · Tab — задания", True, GREEN_DIM), (box.x + 24, box.bottom - 30))
        surf.blit(_crt_overlay(box.size), box)
        return

    quests = journal_list(game)
    if not quests:
        surf.blit(fs.render("Заданий пока нет.", True, GREEN_DIM), (box.x + 24, box.y + 70))
        surf.blit(_crt_overlay(box.size), box)
        return
    if game.journal_sel not in quests:
        game.journal_sel = quests[0]
    list_w = 340
    y = box.y + 66
    rows = max(1, (box.bottom - 50 - y) // 32)                 # сколько строк влезает — остальное листается
    game.journal_scroll = max(0, min(game.journal_scroll, len(quests) - rows))
    if game.journal_scroll:
        surf.blit(ft.render("▲", True, GREEN_DIM), (box.x + list_w + 8, y))
    if game.journal_scroll + rows < len(quests):
        surf.blit(ft.render("▼", True, GREEN_DIM), (box.x + list_w + 8, box.bottom - 70))
    for q in quests[game.journal_scroll:game.journal_scroll + rows]:
        d = QUESTS[q]
        done = game.stage(q) >= d.get("done", 10 ** 9)
        mark = "✓" if done else ("★" if d.get("main") else "•")
        text = f"{mark} {d['title']}"
        r = pygame.Rect(box.x + 18, y - 3, list_w, 28)
        hover = hotspot(r, lambda q=q: setattr(game, "journal_sel", q))
        if q == game.journal_sel or hover:
            pygame.draw.rect(surf, GREEN, r)
            surf.blit(fs.render(text, True, BG), (r.x + 8, y))
        else:
            surf.blit(fs.render(text, True, GREEN_DIM if done else (AMBER if d.get("main") else GREEN)), (r.x + 8, y))
        y += 32
    pygame.draw.line(surf, GREEN_DIM, (box.x + list_w + 34, box.y + 62), (box.x + list_w + 34, box.bottom - 40))

    # записи выбранного задания: прошлые стадии тусклые, текущая — яркая
    q = game.journal_sel
    d = QUESTS[q]
    x, y = box.x + list_w + 54, box.y + 66
    w = box.right - x - 26
    surf.blit(f.render(d["title"].upper(), True, AMBER if d.get("main") else GREEN), (x, y))
    y += 40
    cur = game.stage(q)
    stages = sorted((int(k), v) for k, v in d["stages"].items() if int(k) <= cur)
    for i, (num, text) in enumerate(reversed(stages)):
        latest = i == 0
        color = GREEN if latest else GREEN_DIM
        for j, line in enumerate(wrap_text(fs, text, w - 20)):
            if y > box.bottom - 60:
                break
            prefix = ("▶ " if latest else "✓ ") if j == 0 else "  "
            surf.blit(fs.render(prefix + line, True, color), (x, y))
            y += 22
        y += 12
    surf.blit(ft.render("J или Esc — закрыть · клик — выбрать задание · колесо/↑↓ — листать · Tab — репутация",
                        True, GREEN_DIM), (box.x + 24, box.bottom - 30))
    surf.blit(_crt_overlay(box.size), box)


def draw_reputation(surf, game, box):
    """Карма и звание, отношение городов (только где герой бывал), особые звания."""
    from ..game.reputation import TOWNS, REP_RANKS, rank, town_of
    f, fs, ft = _mono(22), _mono(17), _mono(15)
    x, y = box.x + 30, box.y + 70
    surf.blit(f.render(f"КАРМА: {game.karma}  ·  {game.karma_title().upper()}", True, AMBER), (x, y))
    y += 44
    surf.blit(fs.render("ГОРОДА", True, GREEN), (x, y))
    y += 28
    seen = {town_of(lid) for lid in game.locations} - {None}
    col_w = (box.w - 80) // 2
    rows = [t for t in TOWNS if t in seen]
    for i, t in enumerate(rows):
        cx = x + (i % 2) * col_w
        cy = y + (i // 2) * 24
        v = game.rep(t)
        color = AMBER if v >= 50 else GREEN if v >= 15 else (220, 110, 90) if v < -14 else GREEN_DIM
        surf.blit(fs.render(f"{TOWNS[t][0]:<16} {rank(v, REP_RANKS):<9} {v:+d}", True, color), (cx, cy))
    y += ((len(rows) + 1) // 2) * 24 + 24
    surf.blit(fs.render("ЗВАНИЯ", True, GREEN), (x, y))
    y += 28
    titles = game.titles()
    if not titles:
        surf.blit(fs.render("Пока никто не придумал про вас прозвища.", True, GREEN_DIM), (x, y))
    for _, name, desc in titles:
        if y > box.bottom - 60:
            break
        surf.blit(fs.render(f"★ {name}", True, AMBER), (x, y))
        surf.blit(ft.render(desc, True, GREEN_DIM), (x + 260, y + 2))
        y += 26
