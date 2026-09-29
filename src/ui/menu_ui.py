"""Отрисовка меню: титульный экран, пауза, слоты сохранений, подтверждение."""
import os

import pygame

from .. import settings as S
from .common import hotspot, font_tiny
from .. import fonts as fontlib
from .slide_art import slide_image, W as ART_W, H as ART_H
from ..game.saveload import slot_info, QUICK

AMBER = (240, 200, 120)
AMBER_DIM = (150, 115, 70)
TEXT = (235, 220, 190)
DISABLED = (95, 80, 60)
_F = {}
_THUMBS = {}


def _font(name, size, bold=False):
    key = (name, size, bold)
    if key not in _F:
        _F[key] = fontlib.get(name, size, bold=bold)
    return _F[key]


def _root(menu):
    while menu.get("back"):
        menu = menu["back"]
    return menu["screen"]


def _title_bg(surf, game):
    surf.fill((12, 9, 7))
    art = pygame.transform.smoothscale(slide_image("war", game), (S.SCREEN_W, int(S.SCREEN_W * ART_H / ART_W)))
    art.set_alpha(110)
    surf.blit(art, (0, S.SCREEN_H - art.get_height()))
    shade = pygame.Surface((S.SCREEN_W, S.SCREEN_H), pygame.SRCALPHA)
    for y in range(S.SCREEN_H):  # сверху темнее — под заголовок
        a = max(0, 220 - y * 220 // (S.SCREEN_H * 2 // 3))
        pygame.draw.line(shade, (12, 9, 7, a), (0, y), (S.SCREEN_W, y))
    surf.blit(shade, (0, 0))
    t = _font("dejavuserif", 64, bold=True).render("WASTELAND RECLAIMER", True, AMBER)
    surf.blit(t, t.get_rect(center=(S.SCREEN_W // 2, 110)))
    sub = _font("dejavuserif", 24).render("Хроники Пятнадцатой · 2121", True, AMBER_DIM)
    surf.blit(sub, sub.get_rect(center=(S.SCREEN_W // 2, 170)))


def _item(surf, game, i, label, action, enabled, center, width=320):
    m = game.menu
    font = _font("dejavuserif", 30)
    r = pygame.Rect(0, 0, width, 46)
    r.center = center
    hover = enabled and hotspot(r, action)
    if hover:
        m["sel"] = i
    sel = m["sel"] == i and enabled
    if sel:
        pygame.draw.rect(surf, (60, 45, 28), r, border_radius=6)
        pygame.draw.rect(surf, AMBER, r, 1, border_radius=6)
    t = font.render(label, True, AMBER if sel else TEXT if enabled else DISABLED)
    surf.blit(t, t.get_rect(center=r.center))


def _thumb(slot):
    from ..game import saveload
    path = os.path.join(saveload.SAVE_DIR, f"{slot}.png")
    if not os.path.isfile(path):
        return None
    mtime = os.path.getmtime(path)
    if _THUMBS.get(slot, (None, 0))[1] != mtime:
        _THUMBS[slot] = (pygame.image.load(path).convert(), mtime)
    return _THUMBS[slot][0]


def _slots(surf, game, items, title):
    m = game.menu
    font, small = _font("dejavusans", 20), _font("dejavusans", 16)
    head = _font("dejavuserif", 32, bold=True).render(title, True, AMBER)
    surf.blit(head, head.get_rect(center=(S.SCREEN_W // 2, 40)))
    cols, w, h = 2, 520, 112
    x0 = S.SCREEN_W // 2 - w - 10
    y0 = 76
    slot_items = [it for it in items if it[0] != "Назад"]
    for i, (slot, action, enabled) in enumerate(slot_items):
        r = pygame.Rect(x0 + (i % cols) * (w + 20), y0 + (i // cols) * (h + 12), w, h)
        hover = enabled and hotspot(r, action)
        if hover:
            m["sel"] = i
        sel = m["sel"] == i and enabled
        pygame.draw.rect(surf, (40, 32, 24) if sel else (26, 21, 16), r, border_radius=6)
        pygame.draw.rect(surf, AMBER if sel else (80, 64, 44), r, 2 if sel else 1, border_radius=6)
        info = slot_info(slot)
        name = "Быстрое сохранение (F5)" if slot == QUICK else f"Слот {slot}"
        surf.blit(font.render(name, True, AMBER if enabled else DISABLED), (r.x + 184, r.y + 10))
        thumb = _thumb(slot) if info else None
        tr = pygame.Rect(r.x + 10, r.y + 11, 160, 90)
        if thumb:
            surf.blit(pygame.transform.smoothscale(thumb, tr.size), tr)
        else:
            pygame.draw.rect(surf, (18, 14, 10), tr)
            t = small.render("пусто", True, DISABLED)
            surf.blit(t, t.get_rect(center=tr.center))
        if info:
            played = info.get("played", 0)
            lines = [info["where"], f"Уровень {info['level']} · HP {info.get('hp', '?')}",
                     info["time"], f"В игре: {played // 3600} ч {played // 60 % 60} мин"]
            for j, line in enumerate(lines):
                surf.blit(small.render(line, True, TEXT if j == 0 else AMBER_DIM), (r.x + 184, r.y + 34 + j * 18))
    back = next(it for it in items if it[0] == "Назад")
    _item(surf, game, len(slot_items), back[0], back[1], True, (S.SCREEN_W // 2, y0 + 4 * (h + 12) + 30), 240)


def _slider(surf, game, i, label, kind, y):
    """Ползунок громкости: клик по шкале ставит значение, «−»/«+» — шаг 10%."""
    m = game.menu
    font = _font("dejavuserif", 28)
    vol = game.audio.volume[kind]
    row = pygame.Rect(S.SCREEN_W // 2 - 330, y - 28, 660, 56)
    if hotspot(row, lambda: None):
        m["sel"] = i
    sel = m["sel"] == i
    if sel:
        pygame.draw.rect(surf, (40, 32, 24), row, border_radius=6)
        pygame.draw.rect(surf, AMBER, row, 1, border_radius=6)
    t = font.render(label, True, AMBER if sel else TEXT)
    surf.blit(t, t.get_rect(midleft=(row.x + 20, y)))
    bar = pygame.Rect(row.x + 230, y - 7, 280, 14)

    def set_from_mouse(b=bar, k=kind):
        x = pygame.mouse.get_pos()[0]
        game.audio.set_volume(k, (x - b.x) / b.w)
        if k == "sfx":
            game.audio.play("hit")

    def step(d, k=kind):
        game.audio.set_volume(k, game.audio.volume[k] + d)
        if k == "sfx":
            game.audio.play("hit")
    pygame.draw.rect(surf, (30, 24, 18), bar, border_radius=7)
    pygame.draw.rect(surf, AMBER, (bar.x, bar.y, int(bar.w * vol), bar.h), border_radius=7)
    pygame.draw.circle(surf, (255, 235, 180), (bar.x + int(bar.w * vol), bar.centery), 10)
    hotspot(bar.inflate(0, 20), set_from_mouse)
    small = _font("dejavusans", 26, bold=True)
    for sign, dx, d in (("−", -30, -0.1), ("+", bar.w + 30, 0.1)):
        r = pygame.Rect(0, 0, 34, 34)
        r.center = (bar.x + dx, y)
        hov = hotspot(r, lambda d=d: step(d))
        pygame.draw.rect(surf, (60, 45, 28) if hov else (30, 24, 18), r, border_radius=5)
        s = small.render(sign, True, AMBER)
        surf.blit(s, s.get_rect(center=r.center))
    pct = _font("dejavusans", 20).render(f"{int(round(vol * 100))}%", True, TEXT)
    surf.blit(pct, pct.get_rect(midright=(row.right - 16, y)))


def _sound(surf, game, items):
    t = _font("dejavuserif", 40, bold=True).render("ЗВУК", True, AMBER)
    surf.blit(t, t.get_rect(center=(S.SCREEN_W // 2, 240)))
    _slider(surf, game, 0, "Музыка", "music", 320)
    _slider(surf, game, 1, "Звуки", "sfx", 400)
    _item(surf, game, 2, "Назад", game._back, True, (S.SCREEN_W // 2, 520), 240)
    if not game.audio.ok:
        w = _font("dejavusans", 16).render("Звуковое устройство не найдено — звука не будет.", True, AMBER_DIM)
        surf.blit(w, w.get_rect(center=(S.SCREEN_W // 2, 580)))
    h = _font("dejavusans", 16).render("←→ — громкость · клик по шкале — сразу нужное значение", True, AMBER_DIM)
    surf.blit(h, h.get_rect(center=(S.SCREEN_W // 2, 460)))


def draw_menu(surf, game):
    m = game.menu
    root = _root(m)
    if root == "main":
        _title_bg(surf, game)
    else:
        dim = pygame.Surface((S.SCREEN_W, S.SCREEN_H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 190))
        surf.blit(dim, (0, 0))
    items = game.menu_items()
    scr = m["screen"]
    if scr in ("main", "pause"):
        if scr == "pause":
            t = _font("dejavuserif", 44, bold=True).render("ПАУЗА", True, AMBER)
            surf.blit(t, t.get_rect(center=(S.SCREEN_W // 2, 150)))
        y0 = 290 if scr == "main" else 240
        for i, (label, action, enabled) in enumerate(items):
            _item(surf, game, i, label, action, enabled, (S.SCREEN_W // 2, y0 + i * 58))
        if scr == "pause":
            why = game.can_save()
            if why:
                t = _font("dejavusans", 16).render(why, True, AMBER_DIM)
                surf.blit(t, t.get_rect(center=(S.SCREEN_W // 2, y0 + len(items) * 58 + 10)))
    elif scr == "save":
        _slots(surf, game, items, "СОХРАНИТЬ ИГРУ")
    elif scr == "load":
        _slots(surf, game, items, "ЗАГРУЗИТЬ ИГРУ")
    elif scr == "sound":
        _sound(surf, game, items)
    elif scr == "confirm":
        box = pygame.Rect(0, 0, 560, 200)
        box.center = (S.SCREEN_W // 2, S.SCREEN_H // 2)
        pygame.draw.rect(surf, (26, 21, 16), box, border_radius=8)
        pygame.draw.rect(surf, AMBER, box, 1, border_radius=8)
        t = _font("dejavusans", 20).render(m["confirm"]["text"], True, TEXT)
        surf.blit(t, t.get_rect(center=(box.centerx, box.y + 60)))
        for i, (label, action, enabled) in enumerate(items):
            _item(surf, game, i, label, action, enabled, (box.centerx - 90 + i * 180, box.y + 140), 150)
    hint = "↑↓ — выбор · Enter/клик — выполнить · Esc — назад · F5/F9 — быстрое сохранение/загрузка"
    h = font_tiny().render(hint, True, AMBER_DIM)
    surf.blit(h, h.get_rect(center=(S.SCREEN_W // 2, S.SCREEN_H - 14)))
