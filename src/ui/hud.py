"""Постоянный интерфейс: полоски HP/XP, оружие, крышки, лог событий."""
import pygame

from .. import settings as S
from ..weapons import WEAPONS
from .common import fonts, wrap_text


def weapon_label(game):
    w = WEAPONS[game.player.weapon]
    name = game.weapon_name()
    if w.get("ammo"):
        return f"{name} (патроны: {game.inventory.count(w['ammo'])})"
    return name


def draw_hud(surf, game, show_log=True):
    player = game.player
    font, font_small = fonts()
    pad = 10
    bar_w, bar_h = 200, 16

    pygame.draw.rect(surf, S.COLOR_HP_BG, (pad, pad, bar_w, bar_h))
    hp_ratio = player.hp / player.max_hp if player.max_hp else 0
    pygame.draw.rect(surf, S.COLOR_HP, (pad, pad, int(bar_w * hp_ratio), bar_h))
    surf.blit(font_small.render(f"HP {player.hp}/{player.max_hp}", True, S.COLOR_TEXT), (pad + 6, pad - 1))

    y2 = pad + bar_h + 6
    lv = player.level_sys
    pygame.draw.rect(surf, S.COLOR_XP_BG, (pad, y2, bar_w, bar_h))
    pygame.draw.rect(surf, S.COLOR_XP, (pad, y2, int(bar_w * lv.xp / lv.xp_needed), bar_h))
    surf.blit(font_small.render(f"Ур. {lv.level}  XP {lv.xp}/{lv.xp_needed}", True, S.COLOR_TEXT),
              (pad + 6, y2 - 1))

    info = f"{weapon_label(game)} · крышки: {game.inventory.count('крышки')}"
    surf.blit(font_small.render(info, True, (210, 200, 170)), (pad, y2 + bar_h + 6))
    loc = font_small.render(game.loc.name, True, (190, 180, 150))
    surf.blit(loc, (S.SCREEN_W - loc.get_width() - pad, pad))

    if not show_log:  # в бою лог рисует боевая панель, а под окнами он только мешает
        return

    # лог последних событий снизу слева
    ly = S.SCREEN_H - pad - 18
    for line in reversed(game.log_lines[-4:]):
        surf.blit(font_small.render(line, True, S.COLOR_TEXT), (pad, ly))
        ly -= 18

    hint = "WASD — идти · Space — напасть · F — оружие · E — говорить/обыскать · I — рюкзак · C — крафт"
    surf.blit(font_small.render(hint, True, (170, 160, 140)), (pad, S.SCREEN_H - 20 - 90))


def draw_log_overlay(surf, log_lines, n=4):
    """Лог поверх карты мира."""
    _, font_small = fonts()
    y = 10
    for line in log_lines[-n:]:
        for part in wrap_text(font_small, line, S.SCREEN_W - 20):
            surf.blit(font_small.render(part, True, (245, 235, 210)), (10, y))
            y += 18
