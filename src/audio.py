"""
Звук: эффекты боя и фоновая музыка.

  shot  — выстрел (герой и враги-стрелки);
  melee — удар ломом / удар в ближнем бою;
  hit   — попадание по телу (чуть позже удара — вместе с вздрагиванием цели).

Эффекты берутся из assets/sounds/<имя>.ogg (готовит tools/prepare_sounds.py),
музыка — первый файл в assets/music/, крутится по кругу. Громкость музыки и
эффектов настраивается в меню «Звук» и хранится в saves/settings.json.
Звук слева/справа от центра экрана слышен больше левым/правым ухом.
Если звуковой карты нет (проверки без окна), всё молча работает без звука.
"""
import json
import os
import random

import pygame

from . import settings as S

SFX_DIR = os.path.join("assets", "sounds")
MUSIC_DIR = os.path.join("assets", "music")
DEFAULTS = {"music": 0.5, "sfx": 0.8}
# базовая громкость каждого эффекта (выстрел громкий — его чуть приглушаем)
BASE = {"shot": 0.7, "melee": 0.9, "hit": 0.9}


class Audio:
    def __init__(self):
        self.ok = False
        self.sounds = {}
        self.pending = []   # [(мс до звука, имя, громкость, pan)]
        self.volume = dict(DEFAULTS)
        self._load_settings()
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)
            pygame.mixer.set_num_channels(24)
            self.ok = True
        except pygame.error:
            return
        for name in BASE:
            path = os.path.join(SFX_DIR, f"{name}.ogg")
            if os.path.isfile(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except pygame.error:
                    pass

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
        self.save_settings()

    # ------------------------------------------------------------ музыка
    def start_music(self):
        if not self.ok or pygame.mixer.music.get_busy():
            return
        tracks = sorted(f for f in os.listdir(MUSIC_DIR) if f.endswith(".ogg")) if os.path.isdir(MUSIC_DIR) else []
        if not tracks:
            return
        try:
            pygame.mixer.music.load(os.path.join(MUSIC_DIR, tracks[0]))
            pygame.mixer.music.set_volume(self.volume["music"])
            pygame.mixer.music.play(-1, fade_ms=2000)
        except pygame.error:
            pass

    # ------------------------------------------------------------ эффекты
    def play(self, name, screen_x=None, delay_ms=0, volume=1.0):
        """screen_x — где на экране источник (для стерео); delay_ms — сыграть чуть позже."""
        if not self.ok or name not in self.sounds:
            return
        if delay_ms > 0:
            self.pending.append([delay_ms, name, screen_x, volume])
            return
        v = self.volume["sfx"] * BASE.get(name, 1.0) * volume * random.uniform(0.85, 1.0)
        if v <= 0:
            return
        ch = self.sounds[name].play()
        if ch is None:
            return
        if screen_x is None:
            ch.set_volume(v)
        else:  # панорама: левее центра — громче слева
            pan = max(-1.0, min(1.0, (screen_x - S.SCREEN_W / 2) / (S.SCREEN_W / 2)))
            ch.set_volume(v * min(1.0, 1 - pan * 0.6), v * min(1.0, 1 + pan * 0.6))

    def update(self, dt_ms):
        due = [p for p in self.pending if p[0] - dt_ms <= 0]
        self.pending = [p for p in self.pending if p[0] - dt_ms > 0]
        for p in self.pending:
            p[0] -= dt_ms
        for _, name, x, vol in due:
            self.play(name, x, volume=vol)
