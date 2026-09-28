"""Game: создание мира, главный цикл и обновление кадра."""
import json

import pygame

MOVE_KEYS = (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d,
             pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)

from .. import settings as S
from .. import loader
from .. import perks
from .. import wander
from ..parallax import Parallax
from ..entities import Player
from ..location import LOCATION_DEFS
from ..worldmap import WorldMap
from ..inventory import Inventory
from ..dialogue import DialogueRunner
from ..combat import Combat, tile_of

from .controls import ControlsMixin
from .world import WorldMixin
from .interaction import InteractionMixin
from .quests import QuestMixin
from .backpack import BackpackMixin
from .trade import TradeMixin
from .render import RenderMixin
from .mouse import MouseMixin


class Game(ControlsMixin, MouseMixin, WorldMixin, InteractionMixin, QuestMixin, BackpackMixin, TradeMixin, RenderMixin):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(S.TITLE)
        self.screen = pygame.display.set_mode((S.SCREEN_W, S.SCREEN_H))
        self.clock = pygame.time.Clock()
        self.running = True
        self.log_lines = []
        self.game_over = False
        self.flags = {}            # флаги квестов и последствий: q_scrap_done, gena_robbed, ...

        # мир
        self.parallax = Parallax()
        self.locations = {}
        self.loc = self.get_location("ruins")
        known = {lid for lid, d in LOCATION_DEFS.items() if d.get("known")}
        self.worldmap = WorldMap(LOCATION_DEFS, known)
        self.mode = "local"        # "local" — внутри локации, "world" — карта мира

        # игрок
        player_anims = loader.load_humanoid_animations(
            S.PLAYER_DIR, loader.FRAME_SIZE, base_color=(90, 110, 90), accent_color=(200, 190, 160))
        self.player = Player(self.level.player_spawn, player_anims)
        self.inventory = Inventory("data/recipes.json")
        self.player.inventory = self.inventory
        self.inventory.on_add = self.on_item_added
        self.regen_ms = 0

        # системы и открытые окна
        with open("data/traders.json", "r", encoding="utf-8") as f:
            self.traders = json.load(f)
        self.dialogue = DialogueRunner("data/dialogues.json", self.check_condition)
        self.dialogue_speaker = None   # NPC или враг, с которым говорим
        self.combat = Combat(self)
        self.perk_choices = None       # 3 перка, пока открыто окно выбора
        self.craft_open = False
        self.inv_open = False
        self.inv_tab = "all"           # вкладка рюкзака
        self.inv_sel = None            # выбранный в рюкзаке предмет
        self.inv_last_click = -10**6   # для двойного клика по ячейке
        self.trade = None              # {"id": торговец, "tab": "buy"/"sell"}

        self.cam = pygame.Vector2(0, 0)
        self.held_letters = set()
        self.autowalk = None       # путь по клику мыши вне боя
        self.combat_queue = None   # путь/атака по клику мыши в бою

    def log(self, text):
        self.log_lines.append(text)
        if len(self.log_lines) > 30:
            self.log_lines.pop(0)

    def modal_open(self):
        return bool(self.dialogue.is_active() or self.craft_open or self.inv_open or self.trade
                    or self.game_over or self.perk_choices)

    # --------------------------------------------------------------- кадр
    def update(self, dt_ms):
        if self.mode == "world":
            self.update_world_map(dt_ms)
            return

        self.player.update(dt_ms)
        for e in self.enemies:
            e.update(dt_ms)
        for npc in self.npcs:
            npc.update(dt_ms)
        self.combat.update(dt_ms)
        busy = self.modal_open() or self.combat.active
        wander.update(self, dt_ms, frozen=busy)
        if busy:
            self.autowalk = None
            self._stand_still()
        self.run_combat_queue()

        if not self.player.alive and not self.game_over:
            self.game_over = True
            self.log("Вы погибли. Esc — выйти.")

        # новый уровень — после боя открываем выбор перка
        if self.player.pending_perks > 0 and not self.modal_open() and not self.combat.active:
            self.perk_choices = perks.roll_choices(self.player)
            if not self.perk_choices:
                self.player.pending_perks = 0

        self._regen(dt_ms)

        if not (self.modal_open() or self.combat.active):
            self._explore(dt_ms)

        self.follow_camera(dt_ms)

    def _stand_still(self):
        """В бою и в окнах герой стоит, а не шагает на месте — кроме своего шага или удара."""
        p = self.player
        if not p.attacking and not any(tw["ent"] is p for tw in self.combat.tweens):
            p.anim.set_action("idle")

    def _regen(self, dt_ms):
        """Вне боя раны понемногу заживают."""
        if self.combat.active or not self.player.alive or self.player.hp >= self.player.max_hp:
            self.regen_ms = 0
            return
        self.regen_ms += dt_ms
        if self.regen_ms >= S.HP_REGEN_MS:
            self.regen_ms = 0
            self.player.hp += 1

    def _explore(self, dt_ms):
        """Режим исследования: ходьба, подбор, выходы, кто нас заметил."""
        keys = self.held_keys()
        if any(keys[k] for k in MOVE_KEYS):
            self.autowalk = None  # клавиши перебивают ходьбу по клику
        if not self.update_autowalk(dt_ms):
            self.player.handle_input(keys, dt_ms, self.level.solid_rects)
        if self.mode != "local" or self.modal_open() or self.combat.active:
            return  # по клику дошли и заговорили / напали
        self.level.collect_pickups(self.player.rect.inflate(4, 4), self.inventory, log_fn=self.log)
        if self.level.is_exit(*tile_of(self.player)):
            self.go_world_map()
            return
        self.check_talkers()
        if not self.dialogue.is_active() and any(
                e.alive and self.combat.enemy_notices_player(e) for e in self.enemies):
            self.combat.start(player_first=False)  # враг заметил игрока — пошаговый бой

    def run(self):
        while self.running:
            dt_ms = self.clock.tick(S.FPS)
            self.handle_events()
            self.update(dt_ms)
            self.draw()
        pygame.quit()
