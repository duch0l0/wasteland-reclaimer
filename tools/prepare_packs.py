"""
Берёт звуки из скачанных свободных пакетов и кладёт в assets/sounds/ как <ключ>_N.ogg
(тишина по краям срезается, пик −1 дБ). Список — таблица PACKS; каждая строка должна быть
записана в CREDITS_AUDIO.md (автор, ссылка, лицензия).

Пакеты (CC0) распаковать в любые папки и передать их так:
  .venv/bin/python tools/prepare_packs.py --pack rpg=путь --pack impact=путь --pack fire=путь --pack metal=путь
Пакеты: rpg, impact — Kenney; fire — «The Free Firearm Sound Library» (OpenGameArt, CC0, папка «Prepared SFX Library»);
metal — «Metal Impact Sounds» BMacZero (OpenGameArt, CC0). Нужный пакет не передан — его звуки пропускаются.
"""
import argparse
import glob
import re
import tempfile
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "sounds")

# ключ -> (пакет, [маски файлов], макс. длина в секундах или 0)
PACKS = {
    "step_dirt": ("rpg", ["footstep0[0-4].ogg"], 0),
    "step_concrete": ("impact", ["footstep_concrete_00[0-4].ogg"], 0),
    "step_wood": ("impact", ["footstep_wood_00[0-4].ogg"], 0),   # + EQ: дерево бубнит, ноутбучные колонки его не играют
    "door_open": ("rpg", ["doorOpen_*.ogg"], 0),
    "door_close": ("rpg", ["doorClose_*.ogg"], 0),
    "gate_open": ("rpg", ["creak*.ogg"], 0),
    "open": ("rpg", ["metalLatch.ogg", "metalClick.ogg"], 0),
    "coins": ("rpg", ["handleCoins*.ogg"], 0),
    "combat_start": ("rpg", ["beltHandle2.ogg"], 0),
    "miss": ("rpg", ["knifeSlice.ogg"], 0),
    "crit": ("eld", ["Impact 7.wav"], 0),      # Impacts.zip «impactsgunsfx» (Eldritch Grim, CC0)
    "door_break": ("wood", ["crack07.mp3.flac"], 0),
    # вскрики человека: пакет grunts режется по паузам; короткие — боль, длинные — смерть
    "human_hurt": ("grunts", ["short"], 0),
    "human_death": ("grunts", ["long"], 0),
    "armor_hit": ("metal", ["clink3.wav"], 0),
    "armor_ricochet": ("metal", ["bing1.wav"], 0.7),
    # оружие: настоящие записи выстрелов (близкая дистанция, одиночный выстрел)
    # винтовки и карабины (для будущих снайперов): записи дробовиков с усиленным басом
    "rifle_shot": ("fire", ["Model 12/K_17P.wav", "Nova/O_17P.wav", "CD/H_16P.wav", "Mossberg/N_26P.wav"], 2.4),
    "ar_reload": ("reload", ["assaultriflereload1_0.wav"], 0),   # Gun reload sounds (SpringySpringo, CC0)
    "sg_shot": ("freesound", ["427595__michorvath__20-gauge-shotgun-gunshot.wav"], 1.7),   # Freesound, michorvath, CC0
    "pistol_reload": ("freesound", ["467300__xfixy8__pistol-cock.wav"], 1.2),   # Freesound, XfiXy8, CC0; пока нигде не вызывается
    # дробовик: 8 патронов за 5 секунд перезарядки (action.py) — затвор Remington 870 восемь раз подряд
    "sg_reload": ("freesound", ["171630__pjkasinski3__rem870-slide-forward-1.mp3"], 0),   # Freesound, Pjkasinski3, CC0
    "shot_pipe": ("fire", ["Bersa/F_47P.wav", "Ruger Single Six/S_14P.wav"], 1.3),     # самопал: грубее и тише
    "shot_enemy": ("fire", ["Walther PPQ/X_39P.wav", "Smith & Wesson 642/V_27P.wav"], 1.3),
    "shot_turret": ("fire", ["PPSh/P_32P.wav", "AK-47/C_29P.wav"], 2.2),      # короткие очереди
    "ar_shot": ("fire", ["Carl Gustav M45/G_33P.wav", "AK-47/C_29P.wav"], 2.2),
    # голоса существ: пакет monster (Ogrebane), rat (qubodup), cc0 (rubberduck)
    "dog_attack": ("monster", ["monster-1.wav"], 0), "dog_hurt": ("monster", ["monster-1.wav"], 0),
    "dog_death": ("monster", ["monster-1.wav"], 0),
    "ghoul_attack": ("monster", ["monster-5.wav"], 0), "ghoul_hurt": ("monster", ["monster-5.wav"], 0),
    "ghoul_death": ("monster", ["monster-5.wav"], 0),
    "rat_attack": ("rat", ["qubodupSqueakyRatPain.ogg"], 0), "rat_hurt": ("rat", ["qubodupSqueakyRatAttack.ogg"], 0),
    "rat_death": ("rat", ["qubodupSqueakyRatDeath.ogg"], 0),
    "explosion": ("freesound", ["335152__apenguin73__explosion-test.wav"], 3.0),   # Freesound, Apenguin73, CC0
    "beetle_attack": ("beast", ["Yucky Beast 1.wav"], 0), "beetle_hurt": ("beast", ["Yucky Beast 1.wav"], 0),
    "beetle_death": ("beast", ["Yucky Beast 1.wav"], 0),
    "roach_attack": ("beast", ["Beast Growl 3.wav"], 0), "roach_hurt": ("beast", ["Beast Growl 3.wav"], 0),
    "roach_death": ("beast", ["Beast Growl 3.wav"], 0),
    "robot_attack": ("cc0", ["machine_01.ogg"], 0), "robot_hurt": ("cc0", ["machine_02.ogg"], 0),
    "robot_death": ("cc0", ["machine_02.ogg"], 0),
}
# звуки без верхов: подчеркнуть 1–4 кГц, срезать гул ниже 150 Гц
# высота голоса: один исходник на три состояния (атака выше, смерть ниже), 44100 Гц
PITCH = {"dog_attack": 1.15, "dog_death": 0.8, "ghoul_attack": 1.35,
         "beetle_attack": 1.2, "beetle_death": 0.75, "roach_attack": 1.7, "roach_hurt": 1.5, "roach_death": 1.25,
         "robot_death": 0.7}
BRIGHTER = set()   # сюда — звуки, которым нужно больше верхов (EQ2)
EQ2 = "equalizer=f=2500:t=q:w=1:g=8,equalizer=f=6000:t=q:w=1:g=6,"
REPEAT = {"sg_reload": (8, 0.62)}   # (сколько раз, шаг в секундах): один звук нарезается в серию
BASSY = {"rifle_shot"}
BRIGHT = {"step_wood"}
EQ = "highpass=f=150,equalizer=f=1200:t=q:w=1:g=9,equalizer=f=3000:t=q:w=1:g=10,"
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.01,"
        "areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,areverse,"
        "loudnorm=I=-18:TP=-1.5:LRA=7")


def rate_of(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=sample_rate", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return int(r.stdout.split()[0])


def split_grunts(root, tmp):
    """«death pain grunts.wav» -> {'short': [wav…], 'long': [wav…]} по паузам между вскриками."""
    src = os.path.join(root, "death pain grunts.wav")
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", "silencedetect=noise=-38dB:d=0.3", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    segs = [(e, starts[i + 1] if i + 1 < len(starts) else 49.6) for i, e in enumerate(ends)]
    res = {"short": [], "long": []}
    for i, (a, b) in enumerate([x for x in segs if 0.25 < x[1] - x[0] < 4][:12]):
        dst = os.path.join(tmp, f"g{i:02d}.wav")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(max(0, a - 0.05)), "-i", src,
                        "-t", str(b - a + 0.15), dst], check=True)
        res["short" if b - a < 1.3 else "long"].append(dst)
    return res


def find(root, mask):
    return sorted(glob.glob(os.path.join(root, "**", mask), recursive=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", action="append", default=[], metavar="имя=папка")
    a = ap.parse_args()
    roots = dict(x.split("=", 1) for x in a.pack)
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp()
    grunts = split_grunts(roots["grunts"], tmp) if "grunts" in roots else {}
    for key, (pack, masks, maxdur) in PACKS.items():
        if pack not in roots:
            continue
        def look(m):   # «пакет:маска» берёт файл из другого пакета
            pk, _, mk = m.rpartition(":")
            return find(roots[pk or pack], mk) if (pk or pack) in roots else []
        files = grunts[masks[0]] if pack == "grunts" else [f for m in masks for f in look(m)]
        if not files:
            raise SystemExit(f"{key}: нет файлов {masks} в {roots[pack]}")
        for old in glob.glob(os.path.join(OUT, f"{key}_[0-9]*.ogg")):
            os.remove(old)
        for i, src in enumerate(files, 1):
            dst = os.path.join(OUT, f"{key}_{i}.ogg")
            flt = ("bass=g=7:f=180," if key in BASSY else "") + (EQ if key in BRIGHT else "") + (EQ2 if key in BRIGHTER else "") + (
                f"asetrate={int(rate_of(src) * PITCH[key])},aresample=44100," if key in PITCH else "") + TRIM
            cmd = ["-i", src, "-af", flt + (f",atrim=0:{maxdur},afade=t=out:st={maxdur - 0.25}:d=0.25" if maxdur else ""),
                   "-ac", "1", "-ar", "44100", "-c:a", "libvorbis", "-q:a", "5", dst]
            if key in REPEAT:
                times, step = REPEAT[key]
                size = int(44100 * step)
                cmd[3] = (f"atrim=0:{step},apad=whole_len={size},aloop=loop={times - 1}:size={size},"
                          f"{TRIM.rsplit(',', 1)[0]},alimiter=limit=0.9")
            r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + cmd, capture_output=True, text=True)
            if r.returncode:
                raise SystemExit(r.stderr)
        print(f"{key}: {len(files)}")


if __name__ == "__main__":
    main()
