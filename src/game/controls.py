"""Клавиатура: какие клавиши что делают в каждом режиме игры."""
import pygame

from ..combat import BODY_PARTS

# Буквенные клавиши определяем по физическому положению (scancode), а не по
# символу: иначе при русской раскладке C печатает «с» и игра её не узнаёт.
SCANCODE_TO_KEY = {getattr(pygame, f"KSCAN_{ch.upper()}"): getattr(pygame, f"K_{ch}")
                   for ch in "wasdceqrfimj"}

COMBAT_STEPS = {pygame.K_w: (0, -1), pygame.K_UP: (0, -1), pygame.K_s: (0, 1), pygame.K_DOWN: (0, 1),
                pygame.K_a: (-1, 0), pygame.K_LEFT: (-1, 0), pygame.K_d: (1, 0), pygame.K_RIGHT: (1, 0)}


class HeldKeys:
    """Нажатые клавиши для движения: pygame.key.get_pressed() + буквы,
    зажатые физически в любой раскладке."""
    def __init__(self, pressed, held_letters):
        self.pressed, self.held_letters = pressed, held_letters

    def __getitem__(self, key):
        return key in self.held_letters or self.pressed[key]


def number_key(key):
    """Цифры 1..9 -> индекс 0..8, 0 -> 9, иначе None."""
    if pygame.K_1 <= key <= pygame.K_9:
        return key - pygame.K_1
    if key == pygame.K_0:
        return 9
    return None


class ControlsMixin:
    def held_keys(self):
        return HeldKeys(pygame.key.get_pressed(), self.held_letters)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                key = SCANCODE_TO_KEY.get(event.scancode, event.key)
                if event.scancode in SCANCODE_TO_KEY:
                    self.held_letters.add(key)
                self.handle_key(key)
            elif event.type == pygame.KEYUP:
                self.held_letters.discard(SCANCODE_TO_KEY.get(event.scancode, event.key))
            elif event.type == pygame.MOUSEWHEEL:
                if self.mode == "local" and not (self.menu or self.term or self.slides or self.inv_open
                                                 or self.loot or self.trade or self.journal_open
                                                 or self.dialogue.is_active()):
                    self.set_zoom(1 if event.y > 0 else -1)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                self.handle_click(event.pos, event.button)

    def handle_key(self, key):
        """Одно нажатие. Открытое окно перехватывает ввод — как модальное."""
        if self.menu:
            self.menu_key(key)
            return
        if key == pygame.K_F5:
            self.quick_save()
            return
        if key == pygame.K_F9:
            self.quick_load()
            return
        if self.slides:
            self.slides_key(key)
            return
        if self.term:
            self.terminal_key(key)
            return
        if self.loot:
            self.loot_key(key)
            return
        if self.journal_open:
            if key in (pygame.K_ESCAPE, pygame.K_j):
                self.journal_open = False
            return
        if key == pygame.K_j and not self.modal_open() and not self.combat.active:
            self.journal_open = True
            return
        if key == pygame.K_ESCAPE:
            if self.minimap.mode == "big":
                self.minimap.mode = "small"
                return
            self._escape()
            return
        if key == pygame.K_F11:
            self.toggle_fullscreen()
            return
        if key == pygame.K_m and self.mode == "local" and not self.modal_open():
            self.minimap.cycle()
            return
        if self.game_over:
            return
        if self.perk_choices:
            self._perk_key(key)
        elif self.mode == "world":
            self._world_key(key)
        elif self.trade:
            self.trade_key(key)
        elif self.inv_open:
            self.inventory_key(key)
        elif self.dialogue.is_active():
            self._dialogue_key(key)
        elif self.craft_open:
            self.craft_key(key)
        elif key == pygame.K_f:
            self.switch_weapon()
        elif key == pygame.K_i:
            if not self.combat.active or self.combat.player_can_act():
                self.open_inventory()
        elif self.combat.active:
            self._combat_key(key)
        else:
            self._explore_key(key)

    def _escape(self):
        if self.dialogue.is_active():
            self.dialogue.close()
        elif self.trade:
            self.trade = None
        elif self.inv_open:
            self.inv_open = False
        elif self.craft_open:
            self.craft_open = False
        elif self.combat.aim_menu:
            self.combat.aim_menu = False
        elif self.mode == "local" or self.mode == "world":
            self.open_menu("pause")  # Esc, когда закрывать нечего, — меню паузы (и в бою тоже)

    def _explore_key(self, key):
        if self.action.active:
            if key == pygame.K_r:
                self.action.reload()
                return
            if key in (pygame.K_1, pygame.K_2):
                self.action.switch("ar" if key == pygame.K_1 else "sg")
                return
            if key == pygame.K_SPACE:
                return
        if key == pygame.K_c:
            self.craft_open = True
        elif key == pygame.K_SPACE:
            # ударить первым: если рядом есть враг, начинается бой и первый ход ваш
            if not self.combat.start(player_first=True):
                self.player.try_attack()
        elif key == pygame.K_e:
            self.interact()

    def _perk_key(self, key):
        idx = number_key(key)
        if idx is not None and idx < len(self.perk_choices):
            self.take_perk(self.perk_choices[idx])

    def _world_key(self, key):
        idx = number_key(key)
        known = self.worldmap.known_list()
        if key == pygame.K_0:
            self.worldmap.wander_around()
        elif idx is not None and idx < len(known):
            self.worldmap.travel_to(known[idx])
        elif key in (pygame.K_e, pygame.K_RETURN):
            here = self.worldmap.location_here()
            if here and not self.worldmap.target:
                self.enter_location(here)

    def _combat_key(self, key):
        c = self.combat
        if c.aim_menu:
            idx = number_key(key)
            if idx is not None and idx < len(BODY_PARTS):
                c.player_attack(idx)
            elif key == pygame.K_q:
                c.aim_menu = False
            return
        if key in COMBAT_STEPS:
            c.player_step(*COMBAT_STEPS[key])
        elif key == pygame.K_SPACE:
            c.player_attack(0)
        elif key == pygame.K_q:
            if c.player_can_act():
                c.aim_menu = True
        elif key == pygame.K_TAB:
            c.cycle_target()
        elif key == pygame.K_g:
            c.player_throw()
        elif key in (pygame.K_r, pygame.K_RETURN):
            if c.player_can_act():
                c.end_turn()
        elif key == pygame.K_c:
            if c.player_can_act():
                self.craft_open = True
        elif key == pygame.K_e:
            self.log("Не время болтать — тут дерутся.")

    def _dialogue_key(self, key):
        options = self.dialogue.visible_options()
        if not options:
            self.dialogue.close()
            return
        idx = number_key(key)
        if idx is None or idx >= len(options):
            return
        for eff in self.dialogue.choose(idx):
            self.apply_effect(eff)
