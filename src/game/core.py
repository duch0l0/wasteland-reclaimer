"""Game: создание мира, главный цикл и обновление кадра."""
import json
import os
import random

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
from ..iso import Camera

from .controls import ControlsMixin
from .world import WorldMixin
from .interaction import InteractionMixin
from .quests import QuestMixin
from .backpack import BackpackMixin
from .trade import TradeMixin
from .render import RenderMixin
from ..ui.minimap import Minimap
from ..gore import Gore
from ..audio import Audio
from .. import companion

with open("data/barks.json", "r", encoding="utf-8") as _f:
    BARKS = {k: v for k, v in json.load(_f).items() if not k.startswith("_")}
# кто не пересказывает слухи (роботы, звери, враги-собеседники)
NO_RUMORS = {"dog", "purity_bot", "cleaner_bot", "sphinx", "radio_bot", "robo_sentry", "robo_sgt", "robot"}
from .mouse import MouseMixin
from .terminals import TerminalMixin
from .slides import SlidesMixin, SLIDES
from .looting import LootingMixin
from .menu import MenuMixin
from .saveload import SaveMixin
from .merc import MercMixin
from .baker import BakerMixin
from .crime import CrimeMixin
from .reputation import ReputationMixin


class Game(ControlsMixin, MouseMixin, WorldMixin, InteractionMixin, QuestMixin, BackpackMixin, TradeMixin,
           TerminalMixin, SlidesMixin, LootingMixin, MenuMixin, SaveMixin, MercMixin, BakerMixin, CrimeMixin, ReputationMixin,
           RenderMixin):
    def __init__(self, intro=True, _screen=None, _prologue=False):
        """intro — начать с главного меню (для проверок без окна его пропускают).
        _screen, _prologue — для «Новой игры» из меню: то же окно, сразу пролог."""
        pygame.init()
        pygame.display.set_caption(S.TITLE)
        self.screen = _screen or self._open_window()
        self.clock = pygame.time.Clock()
        self.running = True
        self.log_lines = []
        self.game_over = False
        self.flags = {}            # флаги сюжета и последствий: gena_robbed, bos_ally, ...
        self.quests = {}           # стадии квестов (data/quests.json): id -> стадия
        self.journal_open = False
        self.journal_sel = None
        self.journal_tab = "quests"   # задания | репутация
        self.journal_scroll = 0

        # мир
        self.parallax = Parallax()
        self.locations = {}
        self.loc = self.get_location("ruins")
        known = {lid for lid, d in LOCATION_DEFS.items() if d.get("known")}
        self.worldmap = WorldMap(LOCATION_DEFS, known)
        self.mode = "local"        # "local" — внутри локации, "world" — карта мира

        # игрок
        from .. import hero_look
        if hero_look.available():   # герой по слоям: надетое и оружие в руках видны (tools/make_hero.py)
            player_anims = hero_look.animations()
        else:
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
        from ..lighting import Lighting
        self.lighting = Lighting()
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

        self.cam = Camera()   # прямая или изометрическая — см. src/iso.py
        from ..action import ActionMode
        self.action = ActionMode(self)   # Барстоу за Дэкса — стрельба в реальном времени
        self.held_letters = set()
        self.minimap = Minimap()
        self.gore = Gore()
        self.companion = None      # спутник (пёс) — появляется по квесту
        self.ally = None           # спутник-человек (src/companion.ALLIES) — один за раз
        self.zoom = S.ZOOM_DEFAULT  # масштаб мира, колёсико мыши — ближе/дальше
        self.speech = None         # реплика над головой: {"ent", "text", "t"}
        self.bark_ms = 4000        # до следующей реплики жителя
        self._portal_refused = None
        from .. import fallout2
        self.audio = Audio(os.getcwd(), fallout2.CACHE_DIR)
        self.audio.play_music(LOCATION_DEFS.get(self.loc.id, {}).get("music", "desert"))
        self.autowalk = None       # путь по клику мыши вне боя
        self.combat_queue = None   # путь/атака по клику мыши в бою
        self.term = None           # открытый терминал или документ
        self.loot = None           # открытый обыск: {"box": контейнер, "side", "sel"}
        self.slides = None         # идущее слайд-шоу
        self.menu = None           # открытое меню (main / pause / save / load / confirm)
        self.last_frame = None     # кадр игры без меню — миниатюра сохранения
        self.play_ms = 0           # время в игре — для сохранений
        if _prologue:
            self.show_slides("prologue")
        elif intro:
            self.open_menu("main")
        else:
            for eff in SLIDES["prologue"].get("on_end", []):
                self.apply_effect(eff)

    @staticmethod
    def _open_window():
        """Окно с масштабированием: SCALED растягивает логический экран на окно
        (мышь пересчитывается сама), RESIZABLE — окно можно тянуть за край."""
        pygame.display.set_caption(S.TITLE)
        if os.environ.get("SDL_VIDEODRIVER") == "dummy":  # проверки без окна
            return pygame.display.set_mode((S.SCREEN_W, S.SCREEN_H))
        return pygame.display.set_mode((S.SCREEN_W, S.SCREEN_H), pygame.SCALED | pygame.RESIZABLE)

    def toggle_fullscreen(self):
        try:
            pygame.display.toggle_fullscreen()
        except pygame.error:
            self.log("Полный экран здесь не поддерживается.")

    def log(self, text):
        self.log_lines.append(text)
        if len(self.log_lines) > 30:
            self.log_lines.pop(0)

    def refresh_hero_look(self):
        """Переоделся или сменил оружие — спрайт героя собирается заново (кэш — в hero_look)."""
        from .. import hero_look
        if (self.merc_mode or not hero_look.available() or getattr(self.cam, "iso", False)
                or getattr(self.level, "iso", False)
                or getattr(self.player.anim, "direction", "down") not in hero_look.DIRS):
            return   # на изометрической карте у героя свой аниматор (8 сторон) — его не трогаем
        key = hero_look.look_key(self.player)
        if key != getattr(self, "_hero_key", None):
            self._hero_key = key
            self.player.anim.frames_by_action = hero_look.animations(*key)

    def modal_open(self):
        return bool(self.dialogue.is_active() or self.craft_open or self.inv_open or self.trade
                    or self.game_over or self.perk_choices or self.term or self.slides or self.journal_open
                    or self.loot or self.menu)

    # --------------------------------------------------------------- кадр
    def update(self, dt_ms):
        self.audio.update(dt_ms)
        if self.menu:  # пауза: мир стоит
            return
        self.play_ms += dt_ms
        if self.slides:
            self.update_slides(dt_ms)
            return
        if self.mode == "world":
            self.update_world_map(dt_ms)
            return

        Minimap.reveal(self)  # туман войны: открыть клетки вокруг героя
        self.refresh_hero_look()
        self.player.update(dt_ms)
        for e in self.enemies:
            e.update(dt_ms)
        for npc in self.npcs:
            npc.update(dt_ms)
        self.combat.update(dt_ms)
        self.gore.update(dt_ms)
        companion.update(self, dt_ms)
        self.action.update(dt_ms)
        if hasattr(self.level, "update_roofs") and self.mode == "local":
            self.level.update_roofs(tile_of(self.player), dt_ms)
        if self.speech:
            self.speech["t"] -= dt_ms
            if self.speech["t"] <= 0:
                self.speech = None
        self._barks(dt_ms)
        busy = self.modal_open() or self.combat.active
        wander.update(self, dt_ms, frozen=busy)
        if busy:
            self.autowalk = None
            self._stand_still()
        self.run_combat_queue()

        if not self.player.alive and not self.game_over:
            self.game_over = True
            self.log("Вы погибли. Esc — выйти.")

        # новый уровень — после боя открываем выбор: сперва навык (каждый уровень), потом перк (чётные)
        if not self.modal_open() and not self.combat.active:
            from .. import skills
            if self.player.pending_skills > 0:
                self.perk_choices = skills.choices(self.player)
                if not self.perk_choices:
                    self.player.pending_skills = 0
            elif self.player.pending_perks > 0:
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
        if not p.attacking and not p.anim.busy and not any(tw["ent"] is p for tw in self.combat.tweens):
            p.anim.set_action("idle")

    def bark_lines(self, npc):
        """Что житель может сказать сейчас: свои фразы, слухи города (@город) и всей пустоши (@all).
        Строка — всегда; {"text", "if"} — только когда условие верно (эхо поступков героя, карма, репутация)."""
        from .reputation import town_of
        town = town_of(self.loc.id) if self.loc else None
        pool = list(BARKS.get(npc.npc_id, []))
        if npc.npc_id not in NO_RUMORS:
            pool += BARKS.get(f"@{town}", []) + BARKS.get("@all", [])
        out = []
        for line in pool:
            if isinstance(line, str):
                out.append(line)
            elif self.check_condition(line.get("if", {})):
                out.append(line["text"])
        return out

    def _barks(self, dt_ms):
        """Жители иногда говорят что-нибудь, когда герой проходит рядом (data/barks.json)."""
        self.bark_ms -= dt_ms
        if self.bark_ms > 0 or self.speech or self.mode != "local" or self.combat.active or self.modal_open():
            return
        near = [n for n in self.npcs if not self.hidden_by_roof(n) and self.bark_lines(n)
                and pygame.Vector2(n.rect.center).distance_to(self.player.rect.center) < 4 * S.TILE]
        if not near:
            self.bark_ms = 1500
            return
        n = random.choice(near)
        self.speech = {"ent": n, "text": random.choice(self.bark_lines(n)), "t": 2600}
        self.bark_ms = random.randint(9000, 16000)

    def _regen(self, dt_ms):
        """Вне боя раны понемногу заживают."""
        if self.combat.active or not self.player.alive or self.player.hp >= self.player.hp_cap:
            self.regen_ms = 0
            return
        self.regen_ms += dt_ms
        # Выживание и перк «Быстрое заживление» ускоряют заживление ран
        need = S.HP_REGEN_MS * 100 // (100 + max(0, self.player.skill("survival") - 20) * 2) // (
            1 + self.player.perk_rank("fast_heal"))
        if self.regen_ms >= need:
            self.regen_ms = 0
            self.player.hp += 1

    def _explore(self, dt_ms):
        """Режим исследования: ходьба, подбор, выходы, кто нас заметил."""
        keys = self.held_keys()
        if any(keys[k] for k in MOVE_KEYS):
            self.autowalk = None  # клавиши перебивают ходьбу по клику
        if not self.update_autowalk(dt_ms):
            self.player.handle_input(keys, dt_ms, self.level.solids_near(self.player.rect))
        if self.mode != "local" or self.modal_open() or self.combat.active:
            return  # по клику дошли и заговорили / напали
        if self.level.is_exit(*tile_of(self.player)):
            self.go_world_map()
            return
        portal = getattr(self.level, "portal_at", lambda *_: None)(*tile_of(self.player))
        if portal and portal.get("requires") and not self.check_condition(portal["requires"]):
            if self._portal_refused is not portal:   # сообщить один раз, пока стоим на пороге
                self._portal_refused = portal
                self.log(portal["requires"].get("msg", "Не пройти."))
            portal = None
        elif not portal:
            self._portal_refused = None
        if portal:
            self.enter_location(portal["to"], at=portal["at"])
            return
        self.check_talkers()
        self.baker_watch()
        if self.action.active:
            return   # экшен: никакого пошагового боя — гули бегут, Дэкс стреляет
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
