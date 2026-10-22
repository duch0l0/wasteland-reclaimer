"""
Звук: эффекты, фоновая музыка и фоновые петли (ambient).

Свои звуки (assets/sounds/<имя>.ogg, готовит tools/prepare_sounds.py):
  shot, melee, hit — из tools/prepare_sounds.py; интерфейсные (клики, терминал, гейгер, левел-ап,
  ящики…) синтезирует tools/make_sfx.py; у звука могут быть варианты <имя>_1.ogg, <имя>_2.ogg…
  Музыка — assets/music/<ключ>_1.ogg, <ключ>_2.ogg… (готовит tools/prepare_music.py по выбору автора
  incoming_audio/selection_music.json: −16 LUFS, стерео, ogg q5). У ключа может быть несколько
  вариантов: при входе в ключ берётся следующий по кругу (world: 1, 2, 3, 1…), а когда трек кончился —
  следующий вариант того же ключа (см. _music_tick). Бой: play_combat_music/end_combat_music.

Если у игрока установлен Fallout 2 — берутся его музыка и звуки (src/fallout2.py:
ищется установка, в фоне один раз перекодируется в кэш f2cache/). Тогда у каждого
эффекта несколько вариантов, у существ свои голоса (атака, ранение, смерть), у
интерфейса — щелчки, у каждой локации — своя музыка (music в data/locations.json).
Чего нет — подменяется своим звуком (FALLBACK) или молчит.

Фоновые петли (assets/sounds/amb_<ключ>.ogg): ветер, ночь, пещеры, убежище, ливнёвка (варианты
amb_sewer_1/_2 — при входе берётся случайный), город, неон, костёр, машинный зал. Ключ локации —
поле "ambient" в data/locations.json, иначе по её музыке (MUSIC_AMBIENT); ночью на открытом воздухе
ветер сменяется ночью. Петля живёт на своих зарезервированных каналах — эффекты их не занимают.

Громкость музыки, эффектов и фона — меню «Звук», хранится в saves/settings.json.
Звук слева/справа от центра экрана слышен больше левым/правым ухом.
Если звуковой карты нет (проверки без окна), всё молча работает без звука.
"""
import glob
import json
import os
import random
import re
import time

import pygame

from . import settings as S
from . import fallout2

SFX_DIR = os.path.join("assets", "sounds")
MUSIC_DIR = os.path.join("assets", "music")
# все музыкальные ключи игры (файла может не быть — тогда запасной путь: Fallout 2 у игрока или
# старый трек из assets/music без номера варианта)
MUSIC_KEYS = ("world", "desert", "caves", "lab", "raiders", "hub", "junktown", "reno", "vats",
              "title", "combat", "ending")
# косметика (вариативность громкости, выбор дубля) — свой генератор, чтобы броски
# звука не сдвигали глобальный поток random у игровой логики
_rng = random.Random()
DEFAULTS = {"music": 0.5, "sfx": 0.8, "ambient": 0.48}   # фон тише эффектов: 0.6 от sfx
# фон локации по её музыке (см. ambient_key); поле "ambient" в data/locations.json важнее
MUSIC_AMBIENT = {"desert": "wind", "world": "wind", "caves": "cave", "lab": "vault", "raiders": "campfire",
                 "hub": "town", "junktown": "town", "reno": "neon", "vats": "cave", "title": None}
# каналы фона: два, чтобы старый затухал, пока новый набирает громкость; эффектам они недоступны
AMBIENT_CHANNELS = 2
AMBIENT_FADE_MS = 1500


def ambient_key(loc_id, night=False, defs=None):
    """Ключ фона локации: поле "ambient" из data/locations.json, иначе — по музыке;
    ночью на открытом воздухе (не underground) ветер сменяется ночью."""
    if defs is None:
        from .location import LOCATION_DEFS as defs
    d = defs.get(loc_id) or {}
    key = d.get("ambient") or MUSIC_AMBIENT.get(d.get("music", "desert"), "wind")
    if night and key == "wind" and not d.get("underground"):
        key = "night"
    return key


# базовая громкость (выстрел громкий — его чуть приглушаем)
BASE = {"shot": 0.7, "shot_pipe": 0.75, "shot_enemy": 0.6, "shot_turret": 0.6, "melee": 0.9, "hit": 0.9,
        "hit_bullet": 0.8, "explosion": 1.0, "button": 0.5, "geiger": 0.6, "combat_start": 0.8, "combat_end": 0.7,
        "terminal_key": 0.6, "geiger": 0.6, "dialog": 0.5}
# чего нет — чем заменить
FALLBACK = {"shot_pipe": "shot", "shot_enemy": "shot", "shot_turret": "shot", "hit_bullet": "hit", "explosion": "shot"}


class Audio:
    def __init__(self, game_dir=None, cache_dir=None):
        self.ok = False
        self.sounds = {}          # имя -> [варианты]
        self.pending = []         # [(мс до звука, имя, pan, громкость)]
        self.volume = dict(DEFAULTS)
        self.music_key = None
        self.music_path = None     # что играет сейчас (None — тишина)
        self.music_prev = None     # ключ локации, игравший до боя (для возврата после боя)
        self._music_pos = {}       # ключ -> сколько раз входили (какой вариант по кругу)
        self._music_started = 0    # тики начала трека: не крутим вариант раньше, чем через 1 с
        self.ambient_key = None    # ключ играющей петли (None — тишина)
        self.ambient_level = 1.0   # множитель к volume["ambient"] (на карте мира фон тише)
        self.amb_files = {}        # ключ -> [путь, ...] вариантов amb_<ключ>[_N].ogg
        self._amb_snds = {}        # ключ -> [Sound] — загружаются при первой петле
        self.amb_chs = []          # каналы фона: играют по очереди, старый затухает под новым
        self._amb_i = 0
        self._amb_snd = None       # держим Sound живым, пока петля звучит
        self.f2 = None
        self._f2_loaded = False
        self._load_settings()
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)
            pygame.mixer.set_num_channels(32)
            pygame.mixer.set_reserved(AMBIENT_CHANNELS)   # 0..1 — только фон
            self.amb_chs = [pygame.mixer.Channel(i) for i in range(AMBIENT_CHANNELS)]
            self.ok = True
        except pygame.error:
            return
        self._load_own()
        if game_dir and cache_dir:
            self.f2 = fallout2.Importer(game_dir, cache_dir)
            self.f2.start()
            self.poll()

    def _load_own(self):
        """assets/sounds/<ключ>.ogg и варианты <ключ>_1.ogg, <ключ>_2.ogg…
        Фоновые петли amb_<ключ>[_N].ogg в звуки не грузятся (они длинные) — только путей список."""
        if not os.path.isdir(SFX_DIR):
            return
        for fn in sorted(os.listdir(SFX_DIR)):
            if not fn.endswith(".ogg"):
                continue
            path = os.path.join(SFX_DIR, fn)
            name = re.sub(r"_\d+$", "", fn[:-4])
            if name.startswith("amb_"):
                self.amb_files.setdefault(name[4:], []).append(path)
                continue
            try:
                self.sounds.setdefault(name, []).append(pygame.mixer.Sound(path))
            except pygame.error:
                pass

    # ------------------------------------------------------------ Fallout 2
    @property
    def f2_status(self):
        """Для меню «Звук»: что с музыкой и звуками Fallout 2."""
        if self.f2 is None or self.f2.status == "none":
            return "Fallout 2 не найден — играют свои звуки."
        if self.f2.status == "no_ffmpeg":
            return "Fallout 2 найден, но нет ffmpeg — звуки не перекодировать."
        if self.f2.status == "running":
            return f"Fallout 2 найден: подключаю музыку и звуки… ({self.f2.done_files})"
        if not self.f2.install:
            return f"Музыка и звуки — из папки {self.f2.cache}."
        return f"Музыка и звуки — из Fallout 2 ({self.f2.install})."

    def poll(self):
        """Кэш Fallout 2 готов — подгрузить эффекты и переключить музыку (раз)."""
        if not self.ok or self.f2 is None or self._f2_loaded or self.f2.status != "done":
            return
        self._f2_loaded = True
        for key, names in fallout2.SFX.items():
            snds = []
            for n in names:
                path = self.f2.sfx_path(n)
                if os.path.isfile(path):
                    try:
                        snds.append(pygame.mixer.Sound(path))
                    except pygame.error:
                        pass
            if snds:
                self.sounds[key] = snds
        if self.music_key:
            key, self.music_key = self.music_key, None
            self.play_music(key)

    # ------------------------------------------------------------ настройки
    @staticmethod
    def _settings_path():
        from .game import saveload
        return os.path.join(saveload.SAVE_DIR, "settings.json")

    def _load_settings(self):
        try:
            with open(self._settings_path(), "r", encoding="utf-8") as f:
                d = json.load(f)
            for k in DEFAULTS:
                self.volume[k] = max(0.0, min(1.0, float(d.get(k, DEFAULTS[k]))))
        except (OSError, ValueError):
            pass

    def save_settings(self):
        try:
            os.makedirs(os.path.dirname(self._settings_path()), exist_ok=True)
            with open(self._settings_path(), "w", encoding="utf-8") as f:
                json.dump(self.volume, f)
        except OSError:
            pass

    def set_volume(self, kind, value):
        self.volume[kind] = round(max(0.0, min(1.0, value)), 2)
        if kind == "music" and self.ok:
            pygame.mixer.music.set_volume(self.volume["music"])
        elif kind == "ambient" and self.ok:
            self._ambient_apply_volume()
        self.save_settings()

    # ------------------------------------------------------------ фоновые петли
    def _ambient_apply_volume(self):
        v = self.volume["ambient"] * self.ambient_level
        for ch in self.amb_chs:
            if ch.get_busy():
                ch.set_volume(v)

    def _ambient_sounds(self, key):
        """Варианты петли (amb_sewer_1/_2) — грузятся один раз, при первом входе."""
        if key not in self._amb_snds:
            snds = []
            for path in self.amb_files.get(key, []):
                try:
                    snds.append(pygame.mixer.Sound(path))
                except pygame.error:
                    pass
            self._amb_snds[key] = snds
        return self._amb_snds[key]

    def play_ambient(self, key, level=1.0):
        """Петля локации: тот же ключ не перезапускается; старый затухает за 1,5 с, новый входит
        за 1,5 с. key=None — тишина с затуханием. Варианты ключа (amb_sewer_1/_2) — случайно."""
        if key == self.ambient_key and abs(level - self.ambient_level) < 0.01:
            return
        same = key == self.ambient_key
        self.ambient_key, self.ambient_level = key, level
        if not self.ok or not self.amb_chs:
            return
        if same:   # изменилась только громкость (карта мира/локация) — без перезапуска петли
            self._ambient_apply_volume()
            return
        try:
            self.amb_chs[self._amb_i].fadeout(AMBIENT_FADE_MS)
            if key is None:
                return
            snds = self._ambient_sounds(key)
            if not snds:
                return
            self._amb_i = (self._amb_i + 1) % len(self.amb_chs)
            self._amb_snd = _rng.choice(snds)   # ливнёвка 1/2 — при каждом входе другая
            ch = self.amb_chs[self._amb_i]
            ch.set_volume(self.volume["ambient"] * self.ambient_level)
            ch.play(self._amb_snd, loops=-1, fade_ms=AMBIENT_FADE_MS)
        except pygame.error:
            pass

    # ------------------------------------------------------------ музыка
    def _music_variants(self, key):
        """Свои треки ключа: assets/music/<ключ>_1.ogg, <ключ>_2.ogg… — по номеру варианта."""
        found = []
        for path in glob.glob(os.path.join(MUSIC_DIR, f"{key}_*.ogg")):
            m = re.search(r"_(\d+)\.ogg$", path)
            if m:
                found.append((int(m.group(1)), path))
        return [p for _, p in sorted(found)]

    def _music_fallback(self, key):
        """Своего файла нет: музыка Fallout 2 у игрока, иначе старый трек из assets/music
        (файл без номера варианта — сейчас «Утомлённое солнце»), пока для ключа не выбрана музыка."""
        if self.f2 is not None and self._f2_loaded and key in fallout2.MUSIC:
            path = self.f2.music_path(key)
            if os.path.isfile(path):
                return path
        legacy = sorted(p for p in glob.glob(os.path.join(MUSIC_DIR, "*.ogg"))
                        if not re.search(r"_\d+\.ogg$", os.path.basename(p)))
        return legacy[0] if legacy else None

    def _music_file(self, key):
        """Первый файл ключа (свой вариант, иначе запасной путь) — для проверок и отладки."""
        variants = self._music_variants(key)
        return variants[0] if variants else self._music_fallback(key)

    def play_music(self, key, fadeout_ms=600):
        """Музыка по ключу: при каждом входе — следующий вариант по кругу (world: 1, 2, 3, 1…).
        Тот же ключ, который уже звучит, не перезапускается; трек доигрывает до конца.
        Один музыкальный поток pygame: старое гаснет (fadeout_ms), новое входит за ~2 с."""
        if not self.ok:
            self.music_key = key
            return
        if key == self.music_key and pygame.mixer.music.get_busy():
            return
        variants = self._music_variants(key)
        path = None
        if variants:
            pos = self._music_pos.get(key, 0)
            path = variants[pos % len(variants)]
            self._music_pos[key] = pos + 1
        else:
            path = self._music_fallback(key)   # один файл на все входы — просто играет заново
        self.music_key = key
        if not path:
            self.music_path = None
            return
        self.music_path = path
        self._music_started = time.monotonic()
        try:
            pygame.mixer.music.fadeout(fadeout_ms)
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.volume["music"])
            pygame.mixer.music.play(0, fade_ms=1200)
        except pygame.error:
            self.music_path = None

    def _music_tick(self):
        """Трек кончился, а ключ тот же — следующий вариант того же ключа (не зацикливаем один файл)."""
        if not self.ok or not self.music_key or not self.music_path:
            return
        try:
            if pygame.mixer.music.get_busy():
                return
        except pygame.error:
            return
        if time.monotonic() - self._music_started < 1.0:   # только что включили
            return
        key, self.music_key = self.music_key, None   # «ключ тот же» — play_music пустит дальше
        self.play_music(key)

    def play_combat_music(self):
        """Начало боя: запомнить музыку локации и включить combat (затухание ~1 с)."""
        if self.music_key == "combat":
            return
        if self.music_key:
            self.music_prev = self.music_key
        self.play_music("combat", fadeout_ms=1000)

    def end_combat_music(self):
        """Конец боя: вернуть музыку локации — тот ключ, что играл до боя."""
        key = self.music_prev or "desert"
        self.music_prev = None
        if self.music_key != "combat":
            return
        self.play_music(key, fadeout_ms=1000)

    def start_music(self):
        """Старый вызов: просто музыка по умолчанию (пустошь)."""
        if self.ok and not pygame.mixer.music.get_busy():
            self.play_music(self.music_key or "desert")

    # ------------------------------------------------------------ эффекты
    def has(self, name):
        return name in self.sounds or FALLBACK.get(name) in self.sounds

    def play(self, name, screen_x=None, delay_ms=0, volume=1.0):
        """screen_x — где на экране источник (для стерео); delay_ms — сыграть чуть позже."""
        if not self.ok:
            return
        if name not in self.sounds:
            name = FALLBACK.get(name)
            if name not in self.sounds:
                return
        if delay_ms > 0:
            self.pending.append([delay_ms, name, screen_x, volume])
            return
        v = self.volume["sfx"] * BASE.get(name, 1.0) * volume * _rng.uniform(0.85, 1.0)
        if v <= 0:
            return
        ch = _rng.choice(self.sounds[name]).play()
        if ch is None:
            return
        if screen_x is None:
            ch.set_volume(v)
        else:  # панорама: левее центра — громче слева
            pan = max(-1.0, min(1.0, (screen_x - S.SCREEN_W / 2) / (S.SCREEN_W / 2)))
            ch.set_volume(v * min(1.0, 1 - pan * 0.6), v * min(1.0, 1 + pan * 0.6))

    def update(self, dt_ms):
        self.poll()
        self._music_tick()   # трек кончился — следующий вариант того же ключа
        due = [p for p in self.pending if p[0] - dt_ms <= 0]
        self.pending = [p for p in self.pending if p[0] - dt_ms > 0]
        for p in self.pending:
            p[0] -= dt_ms
        for _, name, x, vol in due:
            self.play(name, x, volume=vol)
