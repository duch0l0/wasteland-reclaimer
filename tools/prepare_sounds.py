"""
Готовит звуки для игры из исходников в sounds/ (нужен ffmpeg):

  - обрезает тишину в начале и в конце, чтобы звук совпадал с ударом;
  - выравнивает громкость эффектов (пик −1 дБ);
  - фоновую музыку из sounds/music/*.wav сжимает в OGG (32 МБ -> ~3 МБ).

Результат: assets/sounds/<имя>.ogg, assets/music/<имя>.ogg.
Какой исходник каким игровым звуком становится — таблица SOUNDS ниже.

Запуск из папки game_project:  .venv/bin/python tools/prepare_sounds.py
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sounds")
OUT_SFX = os.path.join(ROOT, "assets", "sounds")
OUT_MUSIC = os.path.join(ROOT, "assets", "music")

# исходник в sounds/ -> имя звука в игре (src/audio.py)
SOUNDS = {
    "gun-shot.wav": "shot",                          # выстрел
    "udar-po-zaschite--priglushnno.wav": "melee",    # удар ломом
    "the-bullet-hit-the-human-body.wav": "hit",      # попадание по телу
}

# обрезка тишины с обеих сторон: развернуть, срезать, развернуть обратно
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.01,"
        "areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,areverse")


def run(args):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + args, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)


def main():
    if not shutil.which("ffmpeg"):
        print("нужен ffmpeg: sudo apt install ffmpeg")
        return 1
    os.makedirs(OUT_SFX, exist_ok=True)
    os.makedirs(OUT_MUSIC, exist_ok=True)
    for src, name in SOUNDS.items():
        path = os.path.join(SRC, src)
        if not os.path.isfile(path):
            print(f"нет файла sounds/{src} — пропускаю")
            continue
        out = os.path.join(OUT_SFX, f"{name}.ogg")
        # 44.1 кГц стерео — как у микшера игры; пик нормализуем, чтобы звуки были одной громкости
        run(["-i", path, "-af", TRIM + ",loudnorm=I=-16:TP=-1:LRA=11", "-ar", "44100", "-ac", "2",
             "-c:a", "libvorbis", "-q:a", "6", out])
        print(f"sounds/{src} -> assets/sounds/{name}.ogg")
    music_dir = os.path.join(SRC, "music")
    for f in sorted(os.listdir(music_dir)) if os.path.isdir(music_dir) else []:
        if f.lower().endswith((".wav", ".mp3", ".flac", ".ogg")):
            out = os.path.join(OUT_MUSIC, os.path.splitext(f)[0] + ".ogg")
            run(["-i", os.path.join(music_dir, f), "-ar", "44100", "-ac", "2", "-c:a", "libvorbis", "-q:a", "4", out])
            print(f"sounds/music/{f} -> assets/music/{os.path.basename(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
