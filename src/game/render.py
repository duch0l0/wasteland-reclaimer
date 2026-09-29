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

    def _draw_local(self):
        surf, cam, combat = self.screen, self.cam, self.combat
        if self.level.parallax:
            self.parallax.draw(surf, cam.x)
        else:
            surf.fill((20, 17, 14))  # за краем карты
        self.level.draw(surf, cam)
        self.gore.draw_ground(surf, self.level, cam)
        self.level.draw_corpses(surf, cam)

        # персонажи и объекты карты — вперемешку, кто ниже, тот ближе к камере
        pal = self.companion if self.companion is not None and not self.companion.down else None
        entities = [self.player] + [e for e in self.enemies if e.alive] + self.npcs + ([pal] if pal else [])
        if self.companion is not None and self.companion.down:  # выбитый из боя спутник лежит
            from ..corpse import corpse_image
            img = corpse_image(self.companion)
            surf.blit(img, img.get_rect(center=(self.companion.rect.centerx - int(cam.x),
                                                self.companion.rect.bottom - 6 - int(cam.y))))
        layers = [(e.rect.bottom, e) for e in entities] + [(y, (img, pos)) for y, img, pos in self.level.drawables(cam)]
        layers.sort(key=lambda item: item[0])
        outlined = combat_ui.highlights(combat)
        for _, thing in layers:
            if isinstance(thing, tuple):
                surf.blit(*thing)
                continue
            frame, r = sprite_of(thing, cam)
            if thing in outlined:
                combat_ui.draw_outline(surf, frame, r, outlined[thing])
            surf.blit(frame, r)

        self.gore.draw_air(surf, self.level, cam)
        if self.speech:
            combat_ui.draw_speech(surf, self.speech, cam)

        # под курсором — то, с чем можно взаимодействовать, обведено контуром
        for img, r in self.hover_highlight():
            combat_ui.draw_outline(surf, img, r, (245, 215, 110))
            surf.blit(img, r)

        combat_ui.draw_health_bars(surf, self, cam)
        if combat.active:
            combat_ui.draw_combat_markers(surf, combat, cam)
        combat_ui.draw_tracers(surf, combat.tracers, cam)
        combat_ui.draw_floaters(surf, combat.floaters, cam)
        cursor.draw_cursor_hint(surf, self.cursor_hint(), cam)
        self.minimap.draw(surf, self)
        hud.draw_panel(surf, self)
        if combat.active and combat.aim_menu:
            combat_ui.draw_aim_menu(surf, combat)

        if self.dialogue.is_active():
            name = getattr(self.dialogue_speaker, "name", "???")
            labels = [self.dialogue.option_label(o) for o in self.dialogue.visible_options()]
            menus.draw_dialogue(surf, self.dialogue.current_node(), labels, name[:1].upper() + name[1:])
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
