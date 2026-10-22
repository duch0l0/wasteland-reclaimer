"""
Звук шага — по клетке под ногами (src/stepsound.py): песок в руинах (Пятнадцатая, карта
town.json), гравий Арадеша, стальной пол Убежища 57, вода ливнёвки, лужа под ногами.
Женщина-житель умирает с human_death_female (файл human_death_female_1.ogg), мужчина —
human_death. Настройки громкости пишутся во временную папку, не в saves/ игрока.

    .venv/bin/python tests/test_step_sounds.py
"""
import glob
import json
import os
import sys
import tempfile
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ.setdefault("WASTELAND_AMBIENT", "1")   # без окна население тоже живо — нужны жители с полом
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame  # noqa: E402

pygame.mouse.get_pos = lambda: (-50, -50)
pygame.mouse.get_focused = lambda: True

from src.game import Game, saveload  # noqa: E402
from src.townmap import TownMap  # noqa: E402
from src.stepsound import step_sound  # noqa: E402
from src.combat import death_voice_of, voice_of  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()     # не трогаем saves/settings.json игрока
SFX = os.path.join(ROOT, "assets", "sounds")
with open(os.path.join(ROOT, "data", "locations.json"), encoding="utf-8") as f:
    LOCS = json.load(f)

_LEVELS = {}


def level_of(path):
    """Карта по пути из data/locations.json (грузим один раз)."""
    if path not in _LEVELS:
        _LEVELS[path] = TownMap(os.path.join(ROOT, path))
    return _LEVELS[path]


def cells(lv, code, n=3):
    """Проходимые клетки с нужным кодом земли."""
    out = []
    for y, row in enumerate(lv.ground):
        for x, ch in enumerate(row):
            if ch == code and (x, y) not in lv.blocked:
                out.append((x, y))
                if len(out) >= n:
                    return out
    return out


def sound_exists(key):
    return bool(glob.glob(os.path.join(SFX, key + "_*.ogg")) or glob.glob(os.path.join(SFX, key + ".ogg")))


class StepSounds(unittest.TestCase):
    def check_map(self, loc_id, code, want):
        path = LOCS[loc_id]["map"]
        lv = level_of(path)
        found = cells(lv, code)
        self.assertTrue(found, f"{loc_id}: на карте нет проходимых клеток с кодом {code!r}")
        for tile in found:
            with self.subTest(loc=loc_id, tile=tile):
                self.assertEqual(step_sound(lv, tile), want)

    def test_sand_in_ruins(self):
        """Песок Пятнадцатой (ruins → town.json, код s — тайл desnat)."""
        self.check_map("ruins", "s", "step_sand")

    def test_gravel_in_aradesh(self):
        self.check_map("aradesh", "g", "step_gravel")

    def test_metal_in_vault57(self):
        self.check_map("vault57", "m", "step_metal")

    def test_water_in_drain(self):
        self.check_map("drain", "w", "step_water")

    def test_water_glyphs(self):
        """Коды ~ и ≈ — вода в открытых картах (порт, каналы)."""
        for loc_id in ("hub", "catalina", "zzyzx", "needles"):
            path = LOCS[loc_id]["map"]
            lv = level_of(path)
            for code in set("".join(lv.ground)) & set("~≈"):
                found = cells(lv, code, 1)
                if found:
                    self.assertEqual(step_sound(lv, found[0]), "step_water", f"{loc_id} {code!r}")

    def test_puddle_under_feet(self):
        """Лужа-объект слоя «пол» под ногами — вода, рядом та же земля — земля."""
        class Stub:
            ground = ["dd"]
            floor_src = {}
            _water = set()
            objects = [{"name": "x_puddle", "floor": True, "foot": [(1, 0)]}]
        self.assertEqual(step_sound(Stub, (0, 0)), "step_dirt")
        self.assertEqual(step_sound(Stub, (1, 0)), "step_water")

    def test_files_exist(self):
        for key in ("step_dirt", "step_gravel", "step_sand", "step_metal", "step_water", "step_concrete"):
            with self.subTest(key=key):
                self.assertTrue(sound_exists(key), f"нет файла {key}_*.ogg")


class FemaleDeathCry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from src import ambient
        cls.ambient = ambient
        cls.game = Game(intro=False)
        cls.game.enter_location("ruins")
        while cls.game.slides:
            cls.game.update(5000)
            cls.game.slides_next()

    def test_female_npc_cries_female(self):
        female = [n for n in self.game.npcs
                  if self.ambient.AMBIENT.get(n.npc_id, {}).get("gender") == "f"]
        male = [n for n in self.game.npcs
                if self.ambient.AMBIENT.get(n.npc_id, {}).get("gender") == "m"]
        self.assertTrue(female, "в руинах нет жительниц — пол определять не на ком")
        self.assertTrue(male, "в руинах нет жителей-мужчин")
        self.assertEqual(death_voice_of(female[0]), "human_death_female", female[0].name)
        self.assertEqual(death_voice_of(male[0]), "human_death", male[0].name)
        self.assertTrue(sound_exists("human_death_female"), "нет файла human_death_female_1.ogg")

    def test_monsters_keep_own_voice(self):
        """У зверей пола нет — они кричат своим голосом вида, не human_death_female."""
        self.assertEqual(death_voice_of(type("E", (), {"type_id": "rat"})()), "rat_death")
        self.assertEqual(voice_of(type("E", (), {"type_id": "rat"})()), "rat")


if __name__ == "__main__":
    unittest.main(verbosity=2)
