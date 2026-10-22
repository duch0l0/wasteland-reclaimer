"""
Готовит выбранную автором музыку (incoming_audio/selection_music.json) в assets/music/.

Ключ -> файлы из incoming_audio/music/<ключ>/ (порядок из json; для world первый — главный,
остальные — варианты <ключ>_2, <ключ>_3). Обработка: срезается только тишина в начале и в конце
(содержимое не трогаем), громкость −16 LUFS, стерео 44.1 кГц, ogg q5.

Громкости в игре: музыка 0.5, эффекты 0.8, фон 0.48 (src/audio.py → DEFAULTS);
фон нормализован в −20 LUFS, эффекты — в −18 → музыка слышна над фоном, но не глушит эффекты.

  .venv/bin/python tools/prepare_music.py            # всё
  .venv/bin/python tools/prepare_music.py --only world combat
"""
import argparse
import json
import os
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "music")
SRC = os.path.join(ROOT, "incoming_audio", "music")
SEL = os.path.join(ROOT, "incoming_audio", "selection_music.json")

TARGET = -16.0          # LUFS: громче фона (−20), тише эффектов
CEIL = 0.84             # -1.5 dBFS для лимитера
# тишина по краям: порог ниже любого звучащего материала (−55 dB), срезаем не больше, чем тишину
TRIM = ("silenceremove=start_periods=1:start_threshold=-55dB:start_silence=0.05,"
        "areverse,silenceremove=start_periods=1:start_threshold=-55dB:start_silence=0.05,areverse")


def run(cmd):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + cmd,
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("ffmpeg: " + r.stderr[-2000:])
    return r


def lufs(path):
    """(интегральная громкость, true peak) — как их видит loudnorm."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af",
                        "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    d = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    return float(d["input_i"]), float(d["input_tp"])


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def one(src, dst, tmp):
    """Обрезка тишины, −16 LUFS (статическое усиление + лимитер), стерео, ogg q5."""
    raw = os.path.join(tmp, "music.wav")
    run(["-i", src, "-af", TRIM, "-ac", "2", "-ar", "44100", "-c:a", "pcm_s16le", raw])
    cur, gain = raw, 0.0
    for _ in range(4):
        i_, _tp = lufs(cur)
        d = TARGET - i_
        if abs(d) < 0.5:
            break
        nxt = os.path.join(tmp, "norm.wav")
        run(["-i", cur, "-af", f"volume={d:.2f}dB,alimiter=limit={CEIL}:level=disabled",
             "-c:a", "pcm_s16le", nxt])
        os.replace(nxt, cur)
        gain += d
    i_, tp = lufs(cur)
    if tp > -1.5:                 # трек уже громкий: пики режет лимитер, громкость не двигаем
        nxt = os.path.join(tmp, "norm.wav")
        run(["-i", cur, "-af", f"alimiter=limit={CEIL}:level=disabled", "-c:a", "pcm_s16le", nxt])
        os.replace(nxt, cur)
    run(["-i", cur, "-c:a", "libvorbis", "-q:a", "5", dst])
    return gain


def main(only=None):
    with open(SEL, encoding="utf-8") as f:
        sel = json.load(f)
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp()
    for key, files in sel.items():
        if only and key not in only:
            continue
        for old in [os.path.join(OUT, f) for f in os.listdir(OUT)
                    if f.startswith(key + "_") and f.endswith(".ogg")]:
            os.remove(old)          # старые варианты ключа, чтобы не остались лишние _4
        for i, name in enumerate(files, 1):
            src = os.path.join(SRC, key, name)
            dst = os.path.join(OUT, f"{key}_{i}.ogg")
            gain = one(src, dst, tmp)
            i_, tp = lufs(dst)
            print(f"{os.path.basename(dst):24s} {duration(dst):7.1f} с  {i_:6.1f} LUFS  "
                  f"TP {tp:5.1f} dB  усиление {gain:+.1f} дБ  ({name})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", help="только эти ключи")
    main(ap.parse_args().only)
