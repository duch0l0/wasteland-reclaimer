"""
Фоновые петли (src/audio.play_ambient): у каждой локации есть файл amb_<ключ>.ogg, ночь на улице
даёт night, ливнёвка — sewer, эффекты не занимают каналы фона, главное меню — тишина.

    .venv/bin/python tests/test_ambient_audio.py
"""
import glob
import json
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from src import audio as A  # noqa: E402
from src.game import saveload  # noqa: E402
import tempfile  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()   # настройки громкости — во временной папке, не в saves/ игрока

SFX = os.path.join(ROOT, "assets", "sounds")
with open(os.path.join(ROOT, "data", "locations.json"), encoding="utf-8") as f:
    DEFS = json.load(f)

fails = []


def check(ok, text):
    print(("  ок   " if ok else "  БЕДА ") + text)
    if not ok:
        fails.append(text)


def have(key):
    """Есть ли файл петли для ключа (варианты amb_sewer_1/_2 — по префиксу)."""
    return bool(glob.glob(os.path.join(SFX, f"amb_{key}*.ogg"))) if key else False


print("1. Фон каждой локации: ключ вычисляется, файл amb_<ключ>.ogg есть")
bad = []
for lid, d in DEFS.items():
    key = A.ambient_key(lid, night=False, defs=DEFS)
    if not key or not have(key):
        bad.append(f"{lid}: ambient={d.get('ambient')!r} music={d.get('music')!r} -> {key!r}")
check(not bad, f"локаций {len(DEFS)}, без файла фона: {bad or 0}")

print("2. Ночь на открытом воздухе: wind -> night (у подземелий фон не меняется)")
outdoor = [lid for lid, d in DEFS.items()
           if not d.get("underground") and A.ambient_key(lid, night=False, defs=DEFS) == "wind"]
night_bad = [lid for lid in outdoor if A.ambient_key(lid, night=True, defs=DEFS) != "night"]
under_bad = [lid for lid, d in DEFS.items() if d.get("underground")
             and A.ambient_key(lid, night=True, defs=DEFS) != A.ambient_key(lid, night=False, defs=DEFS)]
check(outdoor and not night_bad, f"улиц с ветром {len(outdoor)}, не стали ночью: {night_bad or 0}")
check(not under_bad, f"под землёй фон не зависит от времени суток: {under_bad or 0}")
check(have("night"), "файл amb_night.ogg на месте")

print("3. Ливнёвка и похожие — sewer (днём и ночью), варианты amb_sewer_1/_2")
check(A.ambient_key("drain", night=False, defs=DEFS) == "sewer", "drain -> sewer")
check(A.ambient_key("drain", night=True, defs=DEFS) == "sewer", "drain ночью -> sewer")
check(len(glob.glob(os.path.join(SFX, "amb_sewer_*.ogg"))) >= 2, "у sewer есть варианты 1 и 2")
check(DEFS["drain"].get("ambient") == "sewer", "переопределение записано в data/locations.json")

print("4. Меню и карта мира: у главного меню фона нет, на карте — тихий ветер")
check(A.MUSIC_AMBIENT.get("title") is None, "музыка меню title без фона")

print("5. Runtime: та же петля не перезапускается, эффекты не занимают каналы фона")
au = A.Audio()
check(au.ok, "микшер поднялся (dummy)")
check(abs(au.volume["ambient"] - 0.48) < 1e-6, f"громкость фона по умолчанию {au.volume['ambient']} (0.6 от sfx)")
check(len(au.amb_chs) == A.AMBIENT_CHANNELS, f"каналов фона {len(au.amb_chs)}, все зарезервированы")
if au.ok:
    au.play_ambient("wind")
    ch = au.amb_chs[au._amb_i]
    snd = ch.get_sound()
    check(ch.get_busy() and snd is not None, "петля ветра играет на канале фона")
    au.play_ambient("wind")
    check(au.amb_chs[au._amb_i].get_sound() is snd, "повторный вызов с тем же ключом не перезапускает петлю")
    au.play("button")
    check(ch.get_sound() is snd, "эффект (button) не занял канал фона")
    au.play_ambient("sewer")
    check(au.ambient_key == "sewer", "другая локация — новый ключ (старый затухает 1,5 с)")
    au.play_ambient(None)
    check(au.ambient_key is None, "play_ambient(None) — тишина")
    au.set_volume("ambient", 0.3)
    check(abs(au.volume["ambient"] - 0.3) < 1e-6, "ползунок «Фон» двигает громкость петель")
else:
    check(au.ambient_key is not None, "без звука ключ всё равно запоминается")

print()
if fails:
    print(f"ПРОВАЛЫ ({len(fails)}):")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("ВСЁ ЧИСТО: фон подключён, файлы на месте, ночь и ливнёвка считаются верно.")
sys.exit(0)
