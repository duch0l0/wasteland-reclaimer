"""
Миникарта — как автокарта в Fallout: показывает только разведанное.

Туман войны: клетки открываются в радиусе обзора вокруг героя (стены и
высокие объекты заслоняют). Отмечены герой, найденные NPC (подошёл близко —
появился на карте), враги в поле зрения и рамка того, что сейчас на экране.

Режимы (клавиша M): маленькая в углу -> большая на весь экран -> скрыта.
Клик по разведанному месту — герой идёт туда.
"""
import pygame

from .. import settings as S
from ..combat import tile_of, has_los
from .common import fonts, font_tiny, hotspot, PANEL_H

T = S.TILE
REVEAL_RADIUS = 8     # клеток: столько видно вокруг
MEET_RADIUS = 5       # так близко надо подойти к NPC, чтобы он появился на карте
MODES = ("small", "big", "off")

COL_DIRT = (104, 84, 60)
COL_ASPHALT = (70, 70, 72)
COL_GRAVEL = (128, 124, 112)
COL_FLOOR = (96, 90, 82)
COL_WALL = (42, 34, 28)
COL_PROP = (70, 56, 42)
COL_EXIT = (230, 200, 90)
COL_FOG = (14, 12, 10)


def _tile_color(level, x, y):
    if level.is_exit(x, y):
        return COL_EXIT
    if level.is_wall(x, y):
        return COL_WALL if level.blocks_sight(x, y) else COL_PROP
    ground = getattr(level, "ground", None)
    code = ground[y][x] if ground else "."
    return {"a": COL_ASPHALT, "h": COL_ASPHALT, "v": COL_ASPHALT, "g": COL_GRAVEL, "c": COL_FLOOR}.get(code, COL_DIRT)


def _fog_surface(level):
    """Картинка 1 px на клетку: разведанное — цветом местности, остальное — туман.
    Живёт на самой карте и дорисовывается по мере разведки."""
    if getattr(level, "_mm_fog", None) is None:
        base = pygame.Surface((level.width, level.height))
        for y in range(level.height):
            for x in range(level.width):
                base.set_at((x, y), _tile_color(level, x, y))
        fog = pygame.Surface((level.width, level.height))
        fog.fill(COL_FOG)
        for t in getattr(level, "explored", ()):
            fog.set_at(t, base.get_at(t))
        level._mm_base, level._mm_fog = base, fog
    return level._mm_fog


class Minimap:
    def __init__(self):
        self.mode = "small"

    def cycle(self):
        self.mode = MODES[(MODES.index(self.mode) + 1) % len(MODES)]

    # ------------------------------------------------------------ туман
    @staticmethod
    def reveal(game):
        """Открыть клетки вокруг героя (вызывается, когда он сменил клетку)."""
        level = game.level
        if not hasattr(level, "explored"):
            level.explored = set()
            level.met = set()
        px, py = tile_of(game.player)
        if getattr(level, "_last_reveal", None) == (px, py):
            return
        level._last_reveal = (px, py)
        center = game.player.rect.center
        r = REVEAL_RADIUS
        for y in range(py - r, py + r + 1):
            for x in range(px - r, px + r + 1):
                if (x, y) in level.explored or not (0 <= x < level.width and 0 <= y < level.height):
                    continue
                if (x - px) ** 2 + (y - py) ** 2 > r * r:
                    continue
                # стену видно, даже если за ней ничего не видно
                if has_los(level, center, (x * T + T // 2, y * T + T // 2)) or level.blocks_sight(x, y):
                    level.explored.add((x, y))
                    if getattr(level, "_mm_fog", None) is not None:
                        level._mm_fog.set_at((x, y), level._mm_base.get_at((x, y)))
        for npc in game.npcs:
            if max(abs(tile_of(npc)[0] - px), abs(tile_of(npc)[1] - py)) <= MEET_RADIUS:
                level.met.add(npc.npc_id)

    # ------------------------------------------------------------ отрисовка
    def draw(self, surf, game):
        if self.mode == "off" or game.mode != "local":
            return
        level = game.level
        explored = getattr(level, "explored", set())
        big = self.mode == "big"
        if big:
            avail_w, avail_h = S.SCREEN_W - 80, S.SCREEN_H - PANEL_H - 70
        else:
            avail_w, avail_h = 200, 134
        scale = max(1, min(avail_w // level.width, avail_h // level.height))
        w, h = level.width * scale, level.height * scale
        if big:
            frame = pygame.Rect((S.SCREEN_W - w) // 2 - 8, 20, w + 16, h + 62)
        else:
            frame = pygame.Rect(S.SCREEN_W - w - 20, 8, w + 12, h + 12)
        x0, y0 = frame.x + (8 if big else 6), frame.y + (34 if big else 6)

        bg = pygame.Surface(frame.size, pygame.SRCALPHA)
        bg.fill((*S.COLOR_PANEL, 235 if big else 200))
        pygame.draw.rect(bg, S.COLOR_PANEL_BORDER, bg.get_rect(), 1 if not big else 2)
        surf.blit(bg, frame)
        if big:
            font, font_small = fonts()
            surf.blit(font.render(f"Карта: {game.loc.name}", True, (210, 190, 120)), (frame.x + 10, frame.y + 6))
            hint = font_tiny().render("Клик по разведанному — идти · M — скрыть · Esc — свернуть",
                                      True, (160, 150, 130))
            surf.blit(hint, (frame.x + 10, frame.bottom - 20))

        # разведанное — карта, остальное — туман
        surf.blit(pygame.transform.scale(_fog_surface(level), (w, h)), (x0, y0))

        def to_map(tile):
            return (x0 + tile[0] * scale + scale // 2, y0 + tile[1] * scale + scale // 2)

        # рамка экрана
        vw, vh = game.view_size()
        cam = pygame.Rect(int(game.cam.x) * scale // T, int(game.cam.y) * scale // T,
                          vw * scale // T, vh * scale // T)
        if not game.cam.iso:
            pygame.draw.rect(surf, (200, 190, 150), cam.move(x0, y0).clip(pygame.Rect(x0, y0, w, h)), 1)

        dot = max(2, scale)
        view = pygame.Rect(int(game.cam.x), int(game.cam.y), vw, vh) if not game.cam.iso else \
            game.player.rect.inflate(vw * 1.4, vh * 2.2)
        for e in game.enemies:  # враги — только те, что сейчас на экране
            if e.alive and view.colliderect(e.rect) and tile_of(e) in explored:
                pygame.draw.circle(surf, (230, 60, 50), to_map(tile_of(e)), dot)
        met = getattr(level, "met", set())
        _, font_small = fonts()
        for npc in game.npcs:
            if npc.npc_id in met:
                c = to_map(tile_of(npc))
                pygame.draw.circle(surf, (80, 230, 110), c, dot + 1)
                if big:
                    surf.blit(font_tiny().render(npc.name, True, (170, 240, 180)), (c[0] + 6, c[1] - 7))
        blink = (pygame.time.get_ticks() // 350) % 2 == 0
        pc = to_map(tile_of(game.player))
        pygame.draw.circle(surf, (255, 255, 255) if blink else (255, 220, 90), pc, dot + 1)
        pygame.draw.circle(surf, (20, 16, 12), pc, dot + 1, 1)

        # клик по карте — идти туда (если место разведано); рамка сама по себе клики глотает
        hotspot(frame, lambda: None)
        area = pygame.Rect(x0, y0, w, h)
        hotspot(area, lambda: self._click(game, area, scale))

    def _click(self, game, area, scale):
        mx, my = pygame.mouse.get_pos()
        tile = ((mx - area.x) // scale, (my - area.y) // scale)
        explored = getattr(game.level, "explored", set())
        if game.combat.active:
            return
        if tile not in explored:
            game.log("Там вы ещё не были.")
            return
        if game.level.is_wall(*tile):
            game.log("Туда не пройти.")
            return
        if self.mode == "big":
            self.mode = "small"
        game._go_to(lambda c: c == tile)
