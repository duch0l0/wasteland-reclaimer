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
    surf.blit(f.render("ПИП-БОЙ 2000 · ЗАДАНИЯ", True, GREEN), (box.x + 24, box.y + 16))
    close_button(surf, box)
    pygame.draw.line(surf, GREEN_DIM, (box.x + 20, box.y + 52), (box.right - 20, box.y + 52))

    quests = journal_list(game)
    if not quests:
        surf.blit(fs.render("Заданий пока нет.", True, GREEN_DIM), (box.x + 24, box.y + 70))
        surf.blit(_crt_overlay(box.size), box)
        return
    if game.journal_sel not in quests:
        game.journal_sel = quests[0]
    list_w = 340
    y = box.y + 66
    for q in quests:
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
    surf.blit(ft.render("J или Esc — закрыть · клик — выбрать задание", True, GREEN_DIM), (box.x + 24, box.bottom - 30))
    surf.blit(_crt_overlay(box.size), box)
