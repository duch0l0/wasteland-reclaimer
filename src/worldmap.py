"""
Карта мира (как в Fallout 2): известные локации — точки на карте,
между ними идёшь пешком, и по дороге может случиться случайная встреча.

Клавиши: 1..9 — идти к локации, 0 — бродить по пустоши (гарантированная
встреча), E/Enter — войти в локацию, у которой стоишь.
"""
import math
import random

import pygame

from . import settings as S
from .ui.common import hotspot, digit_key

TRAVEL_SPEED = 140        # px/сек по карте
ENCOUNTER_CHANCE = 0.45   # шанс встречи за переход


class WorldMap:
    def __init__(self, location_defs, known):
        self.defs = location_defs
        self.known = known                  # множество id известных локаций
        self.pos = pygame.Vector2(location_defs["ruins"]["world_pos"])
        self.target = None                  # id локации, куда идём
        self.encounter_at = None            # доля пути, на которой случится встреча
        self.progress = 0.0
        self.start = pygame.Vector2(self.pos)
        self.wander = False
        self._bg = None

    # ------------------------------------------------------------ логика
    def known_list(self):
        return [lid for lid in self.defs if lid in self.known]

    def location_here(self):
        for lid in self.known_list():
            if self.pos.distance_to(self.defs[lid]["world_pos"]) < 6:
                return lid
        return None

    def travel_to(self, loc_id):
        if self.target:
            return
        self.target = loc_id
        self.start = pygame.Vector2(self.pos)
        self.progress = 0.0
        self.wander = False
        self.encounter_at = random.uniform(0.25, 0.8) if random.random() < ENCOUNTER_CHANCE else None

    def wander_around(self):
        """Бродить по окрестностям: короткий путь в случайную сторону и гарантированная встреча."""
        if self.target:
            return
        ang = random.uniform(0, math.tau)
        dest = self.pos + pygame.Vector2(math.cos(ang), math.sin(ang)) * 90
        dest.x = max(40, min(S.SCREEN_W - 40, dest.x))
        dest.y = max(80, min(S.SCREEN_H - 90, dest.y))
        self.target = "__wander__"
        self.wander_dest = dest
        self.start = pygame.Vector2(self.pos)
        self.progress = 0.0
        self.encounter_at = random.uniform(0.4, 0.9)

    def _dest(self):
        if self.target == "__wander__":
            return self.wander_dest
        return pygame.Vector2(self.defs[self.target]["world_pos"])

    def update(self, dt_ms):
        """Возвращает событие: None, ("arrived", loc_id) или ("encounter", None)."""
        if not self.target:
            return None
        dest = self._dest()
        total = max(1.0, self.start.distance_to(dest))
        self.progress = min(1.0, self.progress + TRAVEL_SPEED * dt_ms / 1000 / total)
        self.pos = self.start.lerp(dest, self.progress)
        if self.encounter_at is not None and self.progress >= self.encounter_at:
            self.encounter_at = None
            self.target = None  # после встречи путь выбирают заново
            return ("encounter", None)
        if self.progress >= 1.0:
            arrived = self.target
            self.target = None
            return None if arrived == "__wander__" else ("arrived", arrived)
        return None

    # ------------------------------------------------------------ отрисовка
    def _background(self):
        if self._bg is None:
            rnd = random.Random(7)
            bg = pygame.Surface((S.SCREEN_W, S.SCREEN_H))
            bg.fill((92, 78, 56))
            for _ in range(1600):
                x, y = rnd.randrange(S.SCREEN_W), rnd.randrange(S.SCREEN_H)
                c = rnd.randint(-18, 14)
                bg.set_at((x, y), (92 + c, 78 + c, 56 + c))
            for _ in range(14):  # холмы/кратеры
                x, y, r = rnd.randrange(S.SCREEN_W), rnd.randrange(S.SCREEN_H), rnd.randint(20, 70)
                pygame.draw.circle(bg, (80, 67, 48), (x, y), r, 3)
            # старая трасса
            pts = [(0, 420), (200, 350), (420, 300), (620, 190), (S.SCREEN_W, 120)]
            pygame.draw.lines(bg, (60, 55, 50), False, pts, 10)
            pygame.draw.lines(bg, (150, 140, 90), False, pts, 1)
            self._bg = bg
        return self._bg

    def draw(self, surf, fonts, player_hint):
        font, font_small = fonts
        surf.blit(self._background(), (0, 0))
        here = self.location_here()
        for i, lid in enumerate(self.known_list()):
            d = self.defs[lid]
            p = d["world_pos"]
            label = font_small.render(f"[{i + 1}] {d['name']}", True, (240, 230, 200))
            lrect = label.get_rect(midtop=(p[0], p[1] + 16))
            # клик: по локации, у которой стоишь, — войти; по другой — идти к ней
            key = pygame.K_e if lid == here and not self.target else digit_key(i)
            hover = hotspot(pygame.Rect(p[0] - 14, p[1] - 14, 28, 28).union(lrect), key)
            pygame.draw.circle(surf, (40, 30, 20), p, 13)
            pygame.draw.circle(surf, (230, 190, 90) if lid == here or hover else (190, 160, 100), p, 10)
            if hover:
                pygame.draw.circle(surf, (255, 240, 170), p, 15, 2)
                label = font_small.render(f"[{i + 1}] {d['name']}", True, (255, 240, 170))
            surf.blit(label, lrect)
        if self.target:
            pygame.draw.line(surf, (230, 90, 60), self.pos, self._dest(), 1)
        pygame.draw.circle(surf, (230, 60, 50), (int(self.pos.x), int(self.pos.y)), 6)
        pygame.draw.circle(surf, (20, 10, 10), (int(self.pos.x), int(self.pos.y)), 6, 2)

        panel = pygame.Surface((S.SCREEN_W, 70), pygame.SRCALPHA)
        panel.fill((*S.COLOR_PANEL, 230))
        surf.blit(panel, (0, S.SCREEN_H - 70))
        title = font.render("Карта пустоши", True, (230, 200, 110))
        surf.blit(title, (14, S.SCREEN_H - 64))
        if self.target:
            status = "В пути..." if self.target != "__wander__" else "Бродите по пустоши..."
        elif here:
            status = f"Вы у локации «{self.defs[here]['name']}». E — войти."
        else:
            status = "Вы посреди пустоши."
        surf.blit(font_small.render(status, True, (220, 210, 190)), (220, S.SCREEN_H - 60))
        surf.blit(font_small.render("Клик/1–9 — идти к локации · 0 — бродить · клик/E — войти · " + player_hint,
                                    True, (170, 160, 140)), (14, S.SCREEN_H - 30))
