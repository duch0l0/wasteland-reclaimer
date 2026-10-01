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

    def enter_location(self, loc_id, at=None):
        """at — клетка появления (переход через люк/дверь), иначе вход локации."""
        d = LOCATION_DEFS[loc_id]
        if d.get("chapter_end"):  # следующий город ещё не построен — конец главы
            self.mode = "world"
            self.show_slides(d["chapter_end"])
            return
        self.loc = self.get_location(loc_id)
        self.audio.play_music(d.get("music", "desert"))
        self.autowalk = None
        self.speech = None
        self.apply_view()
        self.place_player((at[0] * S.TILE, at[1] * S.TILE) if at else self.loc.entry)
        if loc_id == "baker":
            self.baker_arrive()
        self.sync_gates()
        self.mode = "local"
        self.log(f"Вы входите: {self.loc.name}.")
        seen = f"seen_{loc_id}"
        if d.get("arrival_slides") and not self.flags.get(seen):   # первый приход — слайды о городе
            self.flags[seen] = True
            self.show_slides(d["arrival_slides"])

    def start_encounter(self):
        p = self.player
        east = self.worldmap.pos.x > S.SCREEN_W * 0.7   # восток, к реке Колорадо
        loc, text = make_encounter(self.flags, p.level_sys.level, p.skill("survival"), east)
        if loc is None:    # следопыт обошёл опасную встречу
            self.log(text)
            return
        self.loc = loc
        self.audio.play_music("raiders")
        self.apply_view()
        self.place_player(self.level.player_spawn)
        self.mode = "local"
        self.log(f"Случайная встреча! {text}")

    def go_world_map(self):
        if self.merc_mode:   # Дэкс не бродит по пустоши: возвращается в Пятнадцатую, выполнив контракт
            if not self.merc_leave_attempt():
                self._step_back_from_exit()
            return
        self._go_world_map()

    def _step_back_from_exit(self):
        from ..combat import tile_of, rect_pos_for_tile
        x, y = tile_of(self.player)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            t = (x + dx, y + dy)
            if not self.level.is_wall(*t) and not self.level.is_exit(*t):
                self.player.rect.topleft = rect_pos_for_tile(self.player, t)
                self.autowalk = None
                return

    def _go_world_map(self):
        if self.loc.world_pos:  # из случайной встречи остаёмся там, где она случилась
            self.worldmap.pos = to_screen(self.loc.world_pos)
        self.mode = "world"
        self.audio.play_music("world")
        self.held_letters.clear()
        self.log("Вы выходите на просторы пустоши.")

    def update_world_map(self, dt_ms):
        self.worldmap.chance_mult = max(0.4, 1 - (self.player.skill("survival") - 20) / 150)
        event = self.worldmap.update(dt_ms)
        if not event:
            return
        kind, loc_id = event
        if kind == "encounter":
            self.start_encounter()
        elif kind == "arrived":
            self.enter_location(loc_id)

    def apply_view(self):
        """Прямая или изометрическая карта: камера, кадры героя (в изометрии — 8 направлений)."""
        iso = getattr(self.level, "iso", False)
        self.cam.iso = iso
        p = self.player
        p.iso = iso
        if iso:
            if getattr(self, "_hero_iso", None) is None:
                from ..iso import char_animator
                self._hero_flat = p.anim
                self._hero_iso = char_animator("hero")
            p.anim = self._hero_iso
        elif getattr(self, "_hero_flat", None) is not None:
            p.anim = self._hero_flat

    def reveal_location(self, loc_id):
        self.worldmap.known.add(loc_id)
        self.log(f"На карте отмечено: {LOCATION_DEFS[loc_id]['name']}.")

    # ------------------------------------------------------------ камера
    def view_size(self):
        """Сколько мира видно (в пикселях мира): область над панелью, делённая на масштаб."""
        return int(S.SCREEN_W / self.zoom), int((S.SCREEN_H - PANEL_H) / self.zoom)

    def set_zoom(self, step):
        """Колёсико: step > 0 — ближе, < 0 — дальше."""
        zs = sorted(S.ZOOMS)
        i = min(range(len(zs)), key=lambda k: abs(zs[k] - self.zoom))
        self.zoom = zs[max(0, min(len(zs) - 1, i + step))]
        self.snap_camera()

    def _camera_target(self):
        view_w, view_h = self.view_size()
        if getattr(self.level, "iso", False):   # изометрия: герой в центре, края — по ромбу карты
            from ..iso import w2i
            px, py = w2i(self.player.rect.centerx, self.player.rect.bottom - S.TILE // 2)
            b = self.level.iso_bounds()
            tx = clamp(px - view_w / 2, b.left, max(b.left, b.right - view_w))
            ty = clamp(py - 60 - view_h / 2, b.top, max(b.top, b.bottom - view_h))
            return tx, ty
        lvl_w, lvl_h = self.level.pixel_size
        # карта меньше экрана — по центру, иначе герой в центре видимой части над панелью
        target_x = (lvl_w - view_w) / 2 if lvl_w <= view_w else \
            clamp(self.player.rect.centerx - view_w // 2, 0, lvl_w - view_w)
        target_y = (lvl_h - view_h) / 2 if lvl_h <= view_h else \
            clamp(self.player.rect.centery - view_h // 2, 0, lvl_h - view_h)
        return target_x, target_y

    def follow_camera(self, dt_ms):
        tx, ty = self._camera_target()
        self.cam.x += (tx - self.cam.x) * min(1, dt_ms / 120)
        self.cam.y += (ty - self.cam.y) * min(1, dt_ms / 120)

    def snap_camera(self):
        self.cam.x, self.cam.y = self._camera_target()
