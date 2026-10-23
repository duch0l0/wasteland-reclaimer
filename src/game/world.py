"""Локации, переходы, карта мира, случайные встречи и камера."""
import pygame

from .. import settings as S
from ..entities import _hitbox_in_tile
from ..combat import tile_of
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
            self.locations[loc_id] = Location(loc_id, hero=not getattr(self, "merc_mode", False))
        return self.locations[loc_id]

    def place_player(self, pos):
        self.player.rect = _hitbox_in_tile(pos, self.player.rect.size)
        self.snap_camera()
        from .. import companion
        companion.place_near_player(self)  # спутник входит в локацию вместе с героем

    def ambient_now(self):
        """(ключ, громкость) фона для текущего места: главное меню — тишина, карта мира — тихий
        ветер (там своя музыка), локация — по её полю ambient/музыке, ночью на улице — ночь."""
        from .. import audio
        if (getattr(self, "menu", None) or {}).get("screen") == "main":
            return None, 1.0
        if self.mode == "world":
            return "wind", 0.5
        return audio.ambient_key(self.loc.id, self.is_night(), LOCATION_DEFS), 1.0

    def refresh_ambient(self):
        """Переключить петлю, если место или время суток сменились (сам Audio тот же ключ не трогает)."""
        key, level = self.ambient_now()
        self.audio.play_ambient(key, level)

    def update_music_zone(self):
        """Музыка внутри городской карты: в салуне — граммофон, в казино — джаз (music_zones в
        data/locations.json: [x0, y0, x1, y1, ключ]); вышел — снова музыка локации. В бою не трогаем."""
        if self.mode != "local" or self.combat.active or self.loc is None:
            return
        d = LOCATION_DEFS.get(self.loc.id, {})
        zones = d.get("music_zones")
        if not zones:
            return
        x, y = tile_of(self.player)
        key = next((z[4] for z in zones if z[0] <= x <= z[2] and z[1] <= y <= z[3]), d.get("music", "desert"))
        if key != self.audio.music_key:
            self.audio.play_music(key, fadeout_ms=1200)

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
        if loc_id.startswith("baker") and loc_id != "baker7":
            self.baker_arrive(loc_id)
        self.restore_town_hostility()   # город помнит нападение: стража враждебна, убитые мертвы
        self.apply_world_changes()      # решения героя видны на карте (data/world_changes.json)
        self.sync_gates()
        self.mode = "local"
        self.refresh_ambient()   # после mode: на карте мира фон тише, в локации — свой
        self.log(f"Вы входите: {self.loc.name}.")
        self.ally_on_enter()
        seen = f"seen_{loc_id}"
        if d.get("arrival_slides") and not self.flags.get(seen):   # первый приход — слайды о городе
            self.flags[seen] = True
            self.show_slides(d["arrival_slides"])

    def start_encounter(self):
        p = self.player
        from ..worldmap import region_at
        region = region_at(self.worldmap.pos)
        loc, text = make_encounter(self.flags, p.level_sys.level, p.skill("survival"), region)
        if loc is None:    # следопыт обошёл опасную встречу
            self.log(text)
            return
        self.loc = loc
        self.audio.play_music("raiders")
        self.apply_view()
        self.place_player(self.level.player_spawn)
        self.mode = "local"
        self.refresh_ambient()
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
        self.refresh_ambient()   # на карте мира — тихий ветер: своя музыка там уже звучит
        self.held_letters.clear()
        self.log("Вы выходите на просторы пустоши.")

    def update_world_map(self, dt_ms):
        self.worldmap.chance_mult = max(0.4, 1 - (self.player.skill("survival") - 20) / 150)
        if self.worldmap.target:   # в пути время бежит по расстоянию (src/game/clock.py)
            from ..worldmap import TRAVEL_SPEED
            from .clock import MAP_MIN_PER_UNIT
            self._travel_acc = getattr(self, "_travel_acc", 0.0) + TRAVEL_SPEED * dt_ms / 1000 * MAP_MIN_PER_UNIT
            if self._travel_acc >= 10:
                whole = int(self._travel_acc)
                self._travel_acc -= whole
                self.advance_time(whole)
        event = self.worldmap.update(dt_ms)
        for lid in self.worldmap.discovered:   # прошли рядом с придорожным местом
            self.log(f"Вы замечаете в стороне от дороги: {LOCATION_DEFS[lid]['name']}. Отмечено на карте.")
        self.worldmap.discovered.clear()
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
        if LOCATION_DEFS[loc_id].get("world_pos"):
            self.worldmap.reveal(LOCATION_DEFS[loc_id]["world_pos"], 90)
        self.log(f"На карте отмечено: {LOCATION_DEFS[loc_id]['name']}.")

    def reveal_from_node(self):
        """Житель рассказал о месте — оно появляется на карте мира (поле "reveal" у реплики диалога)."""
        if not self.dialogue.is_active():
            return
        for lid in self.dialogue.current_node().get("reveal", []):
            if lid not in self.worldmap.known and lid in LOCATION_DEFS:
                self.reveal_location(lid)

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
