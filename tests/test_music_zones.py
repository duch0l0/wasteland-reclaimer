"""
Музыка заведений: ключи saloon / hotel / home у интерьеров и музыкальные зоны на городской карте
(music_zones в data/locations.json, Game.update_music_zone): вошёл в салун — граммофон, вышел —
музыка города; в бою зона музыку не трогает.

    .venv/bin/python tests/test_music_zones.py
"""
import os
import sys
import tempfile

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame  # noqa: E402

pygame.mouse.get_pos = lambda: (-50, -50)
pygame.mouse.get_focused = lambda: True

from src.game import Game, saveload  # noqa: E402
from src.location import LOCATION_DEFS  # noqa: E402
from src.combat import tile_of, rect_pos_for_tile  # noqa: E402
from src import settings as S  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()
failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


# 1. заведения получили свои ключи
venues = {"needles_saloon": "saloon", "hub_falcon": "saloon", "junktown_skum": "saloon", "goodsprings_saloon": "saloon",
          "junktown_casino": "reno", "primm_vikki": "reno", "catalina_casino": "reno",
          "primm_bison": "hotel", "zzyzx_hotel": "hotel",
          "goodsprings_doc": "home", "necropolis_cobbs": "home", "baker_motel_2f": "home"}
for lid, key in venues.items():
    ok(LOCATION_DEFS[lid].get("music") == key, f"{lid}: музыка {LOCATION_DEFS[lid].get('music')} (ждём {key})")
ok(any(z[4] == "saloon" and z[0] <= 63 <= z[2] and z[1] <= 25 <= z[3] for z in LOCATION_DEFS["ruins"].get("music_zones", [])),
   "салун Пятнадцатой: граммофон (63, 25) в зоне saloon")
for key in ("saloon", "hotel", "home", "reno", "title", "ending"):
    ok(os.path.isfile(f"assets/music/{key}_1.ogg"), f"{key}: есть свои треки")

# 2. зона на городской карте
g = Game(intro=False)
for _ in range(3):
    g.update(16)
lid = g.loc.id
base = LOCATION_DEFS[lid].get("music", "desert")
x, y = tile_of(g.player)
LOCATION_DEFS[lid]["music_zones"] = [[x - 1, y - 1, x + 1, y + 1, "saloon"]]   # зона вокруг героя
g.update(16)
ok(g.audio.music_key == "saloon", f"герой в зоне — играет {g.audio.music_key}")
g.player.rect.topleft = rect_pos_for_tile(g.player, (x + 5, y))
g.update(16)
ok(g.audio.music_key == base, f"вышел из зоны — снова {g.audio.music_key} (локация: {base})")

# 3. бой зону перекрывает
g.player.rect.topleft = rect_pos_for_tile(g.player, (x, y))
g.combat.active = True
g.audio.music_key = "combat"
g.update_music_zone()
ok(g.audio.music_key == "combat", "в бою зона не перебивает боевую музыку")
g.combat.active = False
LOCATION_DEFS[lid].pop("music_zones")

print("\nИТОГ:", "всё прошло" if not failed else f"провалено {len(failed)}")
sys.exit(1 if failed else 0)
