"""Локации, переходы, карта мира, случайные встречи и камера."""
import pygame

from .. import settings as S
from ..entities import _hitbox_in_tile
from ..location import Location, LOCATION_DEFS
from ..encounters import make_encounter
from ..worldmap import to_screen
from ..ui.common import PANEL_H


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


class WorldMixin:
    # текущая локация
    @property
    def level(self):
        return self.loc.level

    @property
    def enemies(self):
        return self.loc.enemies

    @property
    def npcs(self):
        return self.loc.npcs

    def get_location(self, loc_id):
        """Локации создаются один раз и помнят, кто убит и что подобрано."""
        if loc_id not in self.locations:
            self.locations[loc_id] = Location(loc_id)
        return self.locations[loc_id]

    def place_player(self, pos):
        self.player.rect = _hitbox_in_tile(pos, self.player.rect.size)
        self.snap_camera()
        from .. import companion
        companion.place_near_player(self)  # спутник входит в локацию вместе с героем

    def enter_location(self, loc_id):
        d = LOCATION_DEFS[loc_id]
        if d.get("chapter_end"):  # следующий город ещё не построен — конец главы
            self.mode = "world"
            self.show_slides(d["chapter_end"])
            return
        self.loc = self.get_location(loc_id)
        self.place_player(self.loc.entry)
        self.mode = "local"
        self.log(f"Вы входите: {self.loc.name}.")

    def start_encounter(self):
        self.loc, text = make_encounter(self.flags)
        self.place_player(self.level.player_spawn)
        self.mode = "local"
        self.log(f"Случайная встреча! {text}")

    def go_world_map(self):
        if self.loc.world_pos:  # из случайной встречи остаёмся там, где она случилась
            self.worldmap.pos = to_screen(self.loc.world_pos)
        self.mode = "world"
        self.held_letters.clear()
        self.log("Вы выходите на просторы пустоши.")

    def update_world_map(self, dt_ms):
        event = self.worldmap.update(dt_ms)
        if not event:
            return
        kind, loc_id = event
        if kind == "encounter":
            self.start_encounter()
        elif kind == "arrived":
            self.enter_location(loc_id)

    def reveal_location(self, loc_id):
        self.worldmap.known.add(loc_id)
        self.log(f"На карте отмечено: {LOCATION_DEFS[loc_id]['name']}.")

    # ------------------------------------------------------------ камера
    def _camera_target(self):
        lvl_w, lvl_h = self.level.pixel_size
        target_x = clamp(self.player.rect.centerx - S.SCREEN_W // 2, 0, max(0, lvl_w - S.SCREEN_W))
        # низ экрана занят панелью — центрируем игрока в видимой части
        # и позволяем камере опуститься, чтобы нижний ряд карты не прятался под панелью
        view_h = S.SCREEN_H - PANEL_H
        target_y = clamp(self.player.rect.centery - view_h // 2, 0, max(0, lvl_h - view_h))
        return target_x, target_y

    def follow_camera(self, dt_ms):
        tx, ty = self._camera_target()
        self.cam.x += (tx - self.cam.x) * min(1, dt_ms / 120)
        self.cam.y += (ty - self.cam.y) * min(1, dt_ms / 120)

    def snap_camera(self):
        self.cam.x, self.cam.y = self._camera_target()
