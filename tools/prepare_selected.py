"""
Готовит выбранные автором звуки в assets/sounds/ (ambient-петли, SFX, шаги).

Подход тот же, что в tools/prepare_packs.py: обрезка тишины по краям, нормализация
громкости, моно для эффектов, ogg (libvorbis). Ambient — стерео, петля с кроссфейдом
конца в начало, −20 LUFS, ogg q4.

  .venv/bin/python tools/prepare_selected.py --ambient --sfx --steps
"""
import argparse
import glob
import json
import os
import re
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "sounds")
INCOMING = os.path.join(ROOT, "incoming_audio")
DL = os.path.expanduser("~/Загрузки")

# ключ -> (файл, имя результата, смещение старта, длина петли, кроссфейд)
AMBIENT = {
    "wind": (os.path.join(DL, "557552__szegvari__dark-sahara-egypt.wav"), "amb_wind.ogg", 5.0, 45.0, 1.5),
    # night: самолёты проходят 57–100 с и 155–195 с; чистый участок 195–250.9 с (55.9 с)
    "night": (os.path.join(DL, "616619__trp__120812-night-tree-crickets-overhead-airplanes-pass-summer-urban-residential-binaural-toronto.wav"),
              "amb_night.ogg", 195.5, 54.0, 1.5),
    "vault": (os.path.join(DL, "661007__kevp888__ls_34819_fr_ventilationsystem.wav"), "amb_vault.ogg", 5.0, 50.0, 1.5),
    "cave": (os.path.join(INCOMING, "ambient/cave/270387_LittleRobotSoundFactory.mp3"), "amb_cave.ogg", 2.0, 40.0, 1.5),
    "sewer_1": (os.path.join(INCOMING, "ambient/sewer/26910_thedapperdan.mp3"), "amb_sewer_1.ogg", 5.0, 45.0, 1.5),
    "sewer_2": (os.path.join(INCOMING, "ambient/sewer/342566_InspectorJ.mp3"), "amb_sewer_2.ogg", 3.0, 40.0, 1.5),
    "town": (os.path.join(INCOMING, "ambient/town/784415_soundandmelodies.mp3"), "amb_town.ogg", 10.0, 50.0, 1.5),
    "neon": (os.path.join(INCOMING, "ambient/neon/248217_jameswrowles.mp3"), "amb_neon.ogg", 2.0, 45.0, 1.5),
    "campfire": (os.path.join(INCOMING, "ambient/campfire/40699_Spandau.mp3"), "amb_campfire.ogg", 5.0, 50.0, 1.5),
    "machine": (os.path.join(INCOMING, "ambient/machine/606933_Garuda1982.mp3"), "amb_machine.ogg", 2.0, 45.0, 1.5),
}

# эффекты: ключ -> [(файл, макс. длина или 0)]; старые файлы ключа удаляются
SFX = {
    "shot": [(os.path.join(INCOMING, "sfx/shot/ffsl_shot_1911_03.wav"), 0),
             (os.path.join(INCOMING, "sfx/shot/ffsl_shot_1911_05.wav"), 0)],
    "hit_bullet": [(os.path.join(INCOMING, "sfx/hit_bullet/eldritchgrim_impact_4.mp3"), 0)],
    # hit: вместо прежнего hit.ogg с zvukogram (CC0, страница проверена 2026-10-22)
    "hit": [(os.path.join(INCOMING, "sfx/hit/v3_freesound_reitanna_thump.wav"), 0)],
    "human_hurt": [(os.path.join(INCOMING, f"sfx/human_hurt/{n}"), 0) for n in (
        "freesound_kodack_male_grunt_1.mp3", "freesound_mfgloom_grunt_pain_1.mp3", "freesound_mrfossy_paingrunt09.mp3",
        "freesound_unfa_paingrunt_a.mp3", "freesound_unfa_paingrunt_b.mp3")],
    "human_death_female": [(os.path.join(INCOMING, "sfx/human_death/freesound_johnson_human_male_scream_5.mp3"), 0)],
    "human_death": [(os.path.join(INCOMING, f"sfx/human_death/{n}"), 0) for n in (
        "freesound_blankened_male_death.mp3", "freesound_jdbrick_male_scream_death.mp3")],
    # melee: два удара вместо прежнего melee.ogg с zvukogram (CC0, проверено 2026-10-22)
    "melee": [(os.path.join(INCOMING, "sfx/melee/new_524956_magnuswaker.wav"), 0),
              (os.path.join(INCOMING, "sfx/melee/new_399183_janbezouska.wav"), 0)],
}

# шаги: ключ -> (файл, [начала шагов] или None = искать по тишине, сколько взять)
STEPS = {
    "step_gravel": (os.path.join(DL, "521588__fission9__hiking-boot-footsteps-on-gravel.wav"), None, 4),
    "step_sand": (os.path.join(DL, "725875__rnan_sounddesign__sand_footsteps.mp3"), None, 4),
    "step_metal": (os.path.join(DL, "696374__sanderboah__walking-on-metal.wav"), None, 4),
    "step_water": (os.path.join(DL, "849638__coffeemakessounds__step_water.wav"), [0.09], 3),
}

# как в prepare_packs.py: срезать тишину по краям, пик −1 дБ
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.01,"
        "areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,areverse,"
        "loudnorm=I=-18:TP=-1.5:LRA=7")


def run(cmd, **kw):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        raise SystemExit("ffmpeg: " + r.stderr[-2000:])
    return r


def lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "loudnorm=I=-20:TP=-1.5:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    d = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    return float(d["input_i"]), float(d["input_tp"])


def ambient():
    tmp = tempfile.mkdtemp()
    for key, (src, name, start, dur, xf) in AMBIENT.items():
        raw = os.path.join(tmp, "loop.wav")
        # петля: голова с нарастанием + хвост с затуханием; на стыке out(D) == out(0)
        fc = (f"[0:a]atrim={start}:{start + dur + xf},asetpts=PTS-STARTPTS,asplit=2[a][b];"
              f"[a]atrim=0:{dur},afade=t=in:st=0:d={xf}[ha];"
              f"[b]atrim={dur}:{dur + xf},asetpts=PTS-STARTPTS,afade=t=out:st=0:d={xf},"
              f"apad=whole_len={int(44100 * dur)}[tb];"
              f"[ha][tb]amix=inputs=2:normalize=0:duration=first")
        run(["-i", src, "-filter_complex", fc, "-c:a", "pcm_s16le", raw])
        # −20 LUFS: сначала статическое усиление, затем лимитер (пики треска/капель не дают
        # добрать громкость одним усилением). Повторяем, пока не попадём в ±0.7 LU.
        cur, gain_total = raw, 0.0
        for _ in range(4):
            i_, _tp = lufs(cur)
            d = -20.0 - i_
            if abs(d) < 0.7:
                break
            nxt = os.path.join(tmp, "norm.wav")
            run(["-i", cur, "-af", f"volume={d:.2f}dB,alimiter=limit=0.84:level=disabled",
                 "-c:a", "pcm_s16le", nxt])
            os.replace(nxt, cur)
            gain_total += d
        dst = os.path.join(OUT, name)
        run(["-i", cur, "-c:a", "libvorbis", "-q:a", "4", dst])
        print(f"{name}: {dur:.1f} с, усиление {gain_total:+.1f} дБ, {lufs(dst)[0]:.1f} LUFS")


def sfx(only=None):
    for key, items in SFX.items():
        if only and key not in only:
            continue
        for old in glob.glob(os.path.join(OUT, f"{key}.ogg")) + glob.glob(os.path.join(OUT, f"{key}_[0-9]*.ogg")):
            os.remove(old)
        for i, (src, maxdur) in enumerate(items, 1):
            dst = os.path.join(OUT, f"{key}_{i}.ogg")
            flt = TRIM + (f",atrim=0:{maxdur},afade=t=out:st={maxdur - 0.15}:d=0.15" if maxdur else "")
            run(["-i", src, "-af", flt, "-ac", "1", "-ar", "44100", "-c:a", "libvorbis", "-q:a", "5", dst])
        print(f"{key}: {len(items)}")


def bursts(src):
    """Звучащие куски: между silence_end и следующим silence_start (тишина короче 0.05 с не в счёт)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", "silencedetect=noise=-30dB:d=0.05", "-f", "null", "-"],
                       capture_output=True, text=True)
    ev = [(k, float(t)) for k, t in re.findall(r"silence_(start|end): ([\d.]+)", r.stderr)]
    res, prev = [], None
    for kind, t in ev:
        if prev and prev[0] == "end" and kind == "start" and t > prev[1]:
            res.append((prev[1], t))
        prev = (kind, t)
    if ev and ev[0][0] == "start" and ev[0][1] > 0.05:
        res.insert(0, (0.0, ev[0][1]))
    return res


def steps():
    for key, (src, offsets, count) in STEPS.items():
        for old in glob.glob(os.path.join(OUT, f"{key}_[0-9]*.ogg")):
            os.remove(old)
        segs = bursts(src)
        if offsets:                       # один шаг в исходнике — варианты по высоте
            pitches = [0.94, 1.0, 1.07][:count]
            picks = [(offsets[0], None, p) for p in pitches]
        else:                             # разные шаги записи
            good = [s for s in segs if 0.05 < s[1] - s[0] < 2.5]
            # равномерно по записи: разные шаги, а не первые подряд
            idx = [round(i * (len(good) - 1) / max(1, count - 1)) for i in range(count)] if len(good) > count else range(len(good))
            picks = [(good[i][0], good[i][1], 1.0) for i in sorted(set(idx))][:count]
        for i, (a, b, pitch) in enumerate(picks, 1):
            dst = os.path.join(OUT, f"{key}_{i}.ogg")
            flt = (f"asetrate={int(44100 * pitch)},aresample=44100," if pitch != 1.0 else "") + TRIM
            cmd = ["-i", src, "-ss", f"{max(0, a - 0.04):.3f}", "-af", flt]
            if b:
                cmd += ["-t", f"{b - a + 0.35:.3f}"]
            run(cmd + ["-ac", "1", "-ar", "44100", "-c:a", "libvorbis", "-q:a", "5", dst])
        print(f"{key}: {len(picks)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ambient", action="store_true")
    ap.add_argument("--sfx", action="store_true")
    ap.add_argument("--steps", action="store_true")
    ap.add_argument("--only", nargs="*", help="только эти ключи из --sfx (иначе все)")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.ambient:
        ambient()
    if a.sfx:
        sfx(a.only)
    if a.steps:
        steps()
