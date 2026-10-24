"""
Музыка (src/audio.py): каждый ключ игры разрешается в свой файл или в запасной путь,
у world три варианта и они чередуются по кругу (вход в ключ и конец трека), бой включает
combat и после конца возвращает музыку локации.

    .venv/bin/python tests/test_music.py
"""
import os
import sys
import tempfile
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame  # noqa: E402

from src import audio as A  # noqa: E402
from src.game import saveload  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()   # настройки громкости — во временную папку, не в saves/

MUSIC = os.path.join(ROOT, "assets", "music")
fails = []


def check(ok, text):
    print(("  ок   " if ok else "  БЕДА ") + text)
    if not ok:
        fails.append(text)


def name_of(a):
    return os.path.basename(a.music_path) if a.music_path else "—"


def own(key):
    """Свои варианты ключа — как их видит игра."""
    return [os.path.basename(p) for p in sorted(
        (p for p in os.listdir(MUSIC) if p.startswith(key + "_") and p.endswith(".ogg")),
        key=lambda p: int(p[len(key) + 1:-4]))]


a = A.Audio()                    # без Fallout 2: у каждого ключа свои треки, запасной путь не нужен
if not a.ok:
    print("  БЕДА звук не поднялся (SDL dummy)"); sys.exit(1)

# 1. ключ -> свой файл; старого трека без номера («Утомлённое солнце», лицензии нет) быть не должно
legacy = [f for f in os.listdir(MUSIC) if f.endswith(".ogg") and not any(
    f == f"{k}_{i}.ogg" for k in A.MUSIC_KEYS for i in range(1, 20))]
check(not legacy, f"посторонних треков нет: {legacy}")
for key in A.MUSIC_KEYS:
    path = a._music_file(key) or ""
    name = os.path.basename(path) if path else "—"
    check(bool(own(key)) and name == f"{key}_1.ogg" and os.path.isfile(path), f"{key}: свой файл ({name})")
for key in ("combat", "ending"):
    p_ = a._music_file(key) or ""
    check(bool(p_) and os.path.isfile(p_), f"{key}: разрешается в файл")

# 2. world: вход в ключ — следующий вариант по кругу 1, 2, 3, 1…
check(own("world") == ["world_1.ogg", "world_2.ogg", "world_3.ogg"], f"у world три варианта: {own('world')}")
a.play_music("world")
check(name_of(a) == "world_1.ogg", f"вход 1 — {name_of(a)}")
seen = []
for _ in range(4):               # конец трека, ключ тот же -> пауза с миром -> следующий вариант
    pygame.mixer.music.stop()
    a._music_started = time.monotonic() - 5   # «трек давно играет»
    a.update(16)                 # кадр: трек кончился — началась пауза, музыки нет
    check(not pygame.mixer.music.get_busy() and a._music_gap_until is not None, "между треками — пауза")
    a._music_gap_until = time.monotonic() - 1  # «пауза прошла»
    a.update(16)                 # следующий кадр двигает вариант
    seen.append(name_of(a))
check(seen == ["world_2.ogg", "world_3.ogg", "world_1.ogg", "world_2.ogg"], f"конец трека -> {seen}")

# 2а. музыка и фон не звучат вместе: под треком фон уходит в ноль, в паузе возвращается
a._amb_gain = 1.0
for _ in range(200):
    a.update(16)
check(not a.amb_chs or not pygame.mixer.music.get_busy() or a._amb_gain == 0.0,
      f"под музыкой фон заглушён ({a._amb_gain})")
pygame.mixer.music.stop()
a._music_started = time.monotonic() - 5
for _ in range(200):
    a.update(16)
check(not a.amb_chs or a._amb_gain == 1.0, f"в паузе между треками фон слышен ({a._amb_gain})")
check(a.music_key == "world", "ключ остался world")

# 3. вход в ключ заново (другая локация и обратно) — тоже следующий вариант
a.play_music("caves")
a.play_music("world")
check(name_of(a) == "world_3.ogg", f"повторный вход в world — {name_of(a)}")

# 4. бой: combat, затем возврат прежнего ключа локации
a.play_music("desert")
before = a.music_key
a.play_combat_music()
check(a.music_key == "combat" and name_of(a) == "combat_1.ogg", f"бой включил {a.music_key}/{name_of(a)}")
check(a.music_prev == before, f"запомнен ключ локации: {a.music_prev}")
a.end_combat_music()
check(a.music_key == before, f"после боя вернулся ключ {a.music_key}")
check(name_of(a) == "desert_1.ogg", f"после боя играет {name_of(a)}")
a.end_combat_music()             # вне боя — не трогает музыку
check(a.music_key == before, "повторный конец боя ничего не меняет")

# 5. запасной путь не ломает бой: ending -> старый трек, ключ запоминается и возвращается
a.play_music("ending")
check(a.music_key == "ending" and bool(a.music_path), f"ending играет запасной путь: {name_of(a)}")
a.play_combat_music()
a.end_combat_music()
check(a.music_key == "ending", "после боя вернулся ending")

print()
if fails:
    print(f"ПРОВАЛОВ: {len(fails)}")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("всё ок")
