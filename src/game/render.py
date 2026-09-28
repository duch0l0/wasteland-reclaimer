"""Отрисовка кадра: карта мира или локация + интерфейс поверх."""
import pygame

from .. import settings as S
from ..ui import hud, menus, combat_ui, cursor, inventory_ui
from ..ui.common import fonts, begin_frame, PANEL_H
from ..entities import sprite_of


class RenderMixin:
    def draw(self):
        begin_frame()  # кликабельные зоны отмечаются заново каждый кадр
        if self.mode == "world":
            self._draw_world()
        else:
            self._draw_local()
        if self.perk_choices:
            menus.draw_perk_menu(self.screen, self.perk_choices, self.player)
        pygame.display.flip()

    def _draw_world(self):
        status = f"HP {self.player.hp}/{self.player.max_hp} · крышки: {self.inventory.count('крышки')}"
        self.worldmap.draw(self.screen, fonts(), status)
        hud.draw_log_overlay(self.screen, self.log_lines)

    def _draw_local(self):
        surf, cam, combat = self.screen, self.cam, self.combat
        self.parallax.draw(surf, cam.x)
        self.level.draw(surf, cam)

        entities = [self.player] + [e for e in self.enemies if e.alive] + self.npcs
        entities.sort(key=lambda e: e.rect.bottom)  # кто ниже — тот ближе к камере
        outlined = combat_ui.highlights(combat)
        for e in entities:
            frame, r = sprite_of(e, cam)
            if e in outlined:
                combat_ui.draw_outline(surf, frame, r, outlined[e])
            surf.blit(frame, r)

        combat_ui.draw_health_bars(surf, self, cam)
        if combat.active:
            combat_ui.draw_combat_markers(surf, combat, cam)
        combat_ui.draw_tracers(surf, combat.tracers, cam)
        combat_ui.draw_floaters(surf, combat.floaters, cam)
        cursor.draw_cursor_hint(surf, self.cursor_hint(), cam)
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

        if self.game_over:
            txt = pygame.font.SysFont("dejavusans", 40).render("ВЫ ПОГИБЛИ", True, (220, 60, 50))
            surf.blit(txt, txt.get_rect(center=(S.SCREEN_W // 2, (S.SCREEN_H - PANEL_H) // 2)))
