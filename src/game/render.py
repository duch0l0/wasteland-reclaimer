"""Отрисовка кадра: карта мира или локация + интерфейс поверх."""
import pygame

from .. import settings as S
from ..ui import hud, menus, combat_ui, cursor, inventory_ui, terminal_ui, journal_ui, slides_ui, loot_ui, menu_ui
from ..ui.common import fonts, begin_frame, PANEL_H
from ..entities import sprite_of
from .. import fonts as fontlib


class RenderMixin:
    def draw(self):
        begin_frame()  # кликабельные зоны отмечаются заново каждый кадр
        if self.menu and menu_ui._root(self.menu) == "main":  # титульный экран — без игры за ним
            menu_ui.draw_menu(self.screen, self)
            pygame.display.flip()
            return
        if self.slides:
            slides_ui.draw_slides(self.screen, self)
            pygame.display.flip()
            return
        if self.mode == "world":
            self._draw_world()
        else:
            self._draw_local()
        if self.perk_choices:
            menus.draw_perk_menu(self.screen, self.perk_choices, self.player)
        if self.journal_open:
            journal_ui.draw_journal(self.screen, self)
        if self.term:
            terminal_ui.draw_terminal(self.screen, self)
        if self.menu:  # пауза — поверх игры; клики по игре под меню не проходят
            self.last_frame = self.screen.copy()  # кадр игры без меню — миниатюра сохранения
            begin_frame()
            menu_ui.draw_menu(self.screen, self)
        pygame.display.flip()

    def _draw_world(self):
        status = f"HP {self.player.hp}/{self.player.max_hp} · крышки: {self.inventory.count('крышки')}"
        self.worldmap.draw(self.screen, fonts(), status)
        hud.draw_log_overlay(self.screen, self.log_lines)

    def _world_canvas(self):
        """Холст мира: при масштабе < 1 он больше экрана и потом ужимается."""
        if self.zoom == 1:
            return self.screen
        size = self.view_size()
        if getattr(self, "_canvas", None) is None or self._canvas.get_size() != size:
            self._canvas = pygame.Surface(size).convert()
        return self._canvas

    def _draw_local(self):
        screen, cam, combat, z = self.screen, self.cam, self.combat, self.zoom
        shake = (0, 0)
        if self.action.active and self.action.shake_ms > 0:   # толпа вывалилась — экран дрогнул
            import random as _r
            shake = (_r.randint(-6, 6), _r.randint(-4, 4))
            cam.x += shake[0]
            cam.y += shake[1]
        try:
            self._draw_local_inner(screen, cam, combat, z)
        finally:
            cam.x -= shake[0]
            cam.y -= shake[1]

    def _draw_local_inner(self, screen, cam, combat, z):
        surf = self._world_canvas()
        if self.level.parallax:
            self.parallax.draw(surf, cam.x)
        else:
            surf.fill((20, 17, 14))  # за краем карты
        self.level.draw(surf, cam)
        self.gore.draw_ground(surf, self.level, cam)
        self.level.draw_corpses(surf, cam)
        if self.action.active:
            self.action.draw_world(surf, cam)   # гильзы и бонусы на земле

        # персонажи и объекты карты — вперемешку, кто ниже, тот ближе к камере
        from ..companion import party
        pals = [c for c in party(self) if not c.down]
        entities = [self.player] + [e for e in self.enemies if e.alive] + self.npcs + pals
        for c in party(self):
            if c.down:  # выбитый из боя спутник лежит
                from ..corpse import corpse_image
                img = corpse_image(c)
                fx, fy = cam.foot(c)
                surf.blit(img, img.get_rect(center=(fx, fy - 6)))
        if not getattr(cam, "iso", False):   # мягкая тень под ногами — персонажи стоят на земле, а не висят
            for e in entities:
                frame, r = sprite_of(e, cam)
                if r.colliderect(surf.get_rect()):
                    sh = _shadow(max(20, min(64, int(e.rect.w * 1.25))))
                    surf.blit(sh, sh.get_rect(center=(r.centerx, r.bottom - 3)))
        key = getattr(self.level, "entity_key", lambda e: e.rect.bottom)   # глубина: y или u+v в изометрии
        layers = [(key(e), e) for e in entities] + \
            [(y, (img, pos)) for y, img, pos in self.level.drawables(cam, surf.get_size())]
        layers.sort(key=lambda item: item[0])
        outlined = combat_ui.highlights(combat)
        for _, thing in layers:
            if isinstance(thing, tuple):
                surf.blit(*thing)
                continue
            frame, r = sprite_of(thing, cam)
            if getattr(thing, "flash_ms", 0) > 0:   # попадание в экшене — вспышка белым
                frame = _white(frame)
            if thing in outlined:
                combat_ui.draw_outline(surf, frame, r, outlined[thing])
            surf.blit(frame, r)
            if thing is self.player and self.action.active and self.action.firing_ms > 0:   # вспышка у ствола
                fl = thing.anim.frames_by_action.get(f"flash_{thing.anim.direction}")
                if fl:
                    surf.blit(fl[(pygame.time.get_ticks() // 40) % len(fl)], r)

        self.gore.draw_air(surf, self.level, cam)
        if getattr(self.level, "night", None):   # ночь: темнота, фонари, огонь (src/lighting.py)
            fx, fy = cam.foot(self.player)
            self.lighting.apply(surf, self.level, cam, (fx, fy - 30), pygame.time.get_ticks())
            self.level.draw_arrows(surf, cam)

        # под курсором — то, с чем можно взаимодействовать, обведено контуром
        for img, r in self.hover_highlight():
            combat_ui.draw_outline(surf, img, r, (245, 215, 110))
            surf.blit(img, r)
        combat_ui.draw_tracers(surf, combat.tracers, cam)
        combat_ui.draw_throws(surf, combat, cam)
        combat_ui.draw_blasts(surf, combat, cam)
        if getattr(self.level, "dark", False):
            me = self.player.rect
            fx, fy = cam.foot(self.player)
            combat_ui.draw_darkness(surf, (fx, fy - 30), self.level.dark)
        hint = self.cursor_hint()
        cursor.draw_cursor_hint(surf, hint and (None, *hint[1:]), cam)
        if surf is not screen:  # мир — на экран с масштабом; подписи дальше — в размер экрана
            view = pygame.Rect(0, 0, S.SCREEN_W, S.SCREEN_H - PANEL_H)
            screen.blit(pygame.transform.smoothscale(surf, view.size), view)
        surf = screen

        if self.speech and (self.speech["ent"] in self.npcs or self.speech["ent"] is self.player) \
                and not self.hidden_by_roof(self.speech["ent"]):
            combat_ui.draw_speech(surf, self.speech, cam, z)
        combat_ui.draw_health_bars(surf, self, cam, z)
        if combat.active:
            combat_ui.draw_combat_markers(surf, combat, cam, z)
        combat_ui.draw_floaters(surf, combat.floaters, cam, z)
        if self.action.active:
            self.action.draw_overlay(surf, cam, z)
        if hint and hint[0]:
            cursor.draw_cursor_hint(surf, (hint[0], hint[1], None, None), cam)
        self.minimap.draw(surf, self)
        hud.draw_panel(surf, self)
        if combat.active and combat.aim_menu:
            combat_ui.draw_aim_menu(surf, combat)

        if self.dialogue.is_active():
            name = getattr(self.dialogue_speaker, "name", "???")
            labels = [self.dialogue.option_label(o) for o in self.dialogue.visible_options()]
            sp = self.dialogue_speaker
            portrait = None
            frames = getattr(getattr(sp, "anim", None), "frames_by_action", {}) if sp is not None else {}
            if frames:
                portrait = (frames.get("idle_down") or frames.get("walk_down") or [None])[0]
            menus.draw_dialogue(surf, self.dialogue.current_node(), labels, name[:1].upper() + name[1:], portrait)
        if self.craft_open:
            menus.draw_craft_menu(surf, self.inventory)
        if self.inv_open:
            inventory_ui.draw_inventory(surf, self)
        if self.trade:
            menus.draw_trade(surf, self)
        if self.loot:
            loot_ui.draw_loot(surf, self)

        if self.game_over:
            txt = fontlib.get("dejavusans", 40).render("ВЫ ПОГИБЛИ", True, (220, 60, 50))
            surf.blit(txt, txt.get_rect(center=(S.SCREEN_W // 2, (S.SCREEN_H - PANEL_H) // 2)))


_SHADOWS = {}


def _shadow(w):
    """Полупрозрачный овал тени шириной w (кэш по ширине)."""
    w = w // 4 * 4
    if w not in _SHADOWS:
        h = max(6, w // 3)
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        for i in range(4):   # к краю — прозрачнее
            k = i / 4
            pygame.draw.ellipse(s, (0, 0, 0, 34), (w * k / 2, h * k / 2, w * (1 - k), h * (1 - k)))
        _SHADOWS[w] = s
    return _SHADOWS[w]


_WHITE = {}


def _white(frame):
    """Тот же силуэт, высветленный почти до белого (кэш по кадру)."""
    key = id(frame)
    hit = _WHITE.get(key)
    if hit is None or hit[0] is not frame:
        w = frame.copy()
        w.fill((85, 70, 60, 0), special_flags=pygame.BLEND_RGBA_ADD)   # тёплая вспышка, силуэт читается
        hit = _WHITE[key] = (frame, w)
    return hit[1]
