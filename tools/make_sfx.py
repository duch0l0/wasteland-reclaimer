"""
Синтезирует простые интерфейсные звуки кодом (без внешних файлов, лицензия — наша).

Только стандартная библиотека + ffmpeg: сначала wav во временную папку, потом ogg в assets/sounds/.
Звуки с вариантами получают имена <ключ>_1.ogg, <ключ>_2.ogg… (audio.py берёт любой из них).
Запуск из папки game_project:  .venv/bin/python tools/make_sfx.py
"""
import math
import os
import random
import struct
import subprocess
import tempfile
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "sounds")
SR = 44100


# ------------------------------------------------------------ кирпичики
def n(sec):
    return int(SR * sec)


def silence(sec):
    return [0.0] * n(sec)


def sine(freq, sec, vol=1.0, glide=None):
    """glide — конечная частота (линейно)."""
    out, ph = [], 0.0
    total = n(sec)
    for i in range(total):
        f = freq if glide is None else freq + (glide - freq) * i / total
        ph += 2 * math.pi * f / SR
        out.append(math.sin(ph) * vol)
    return out


def square(freq, sec, vol=1.0):
    return [math.copysign(vol, math.sin(2 * math.pi * freq * i / SR)) for i in range(n(sec))]


def noise(sec, vol=1.0, rng=None):
    r = rng or random
    return [(r.random() * 2 - 1) * vol for _ in range(n(sec))]


def lowpass(x, cutoff):
    a = 1 - math.exp(-2 * math.pi * cutoff / SR)
    y, out = 0.0, []
    for v in x:
        y += a * (v - y)
        out.append(y)
    return out


def highpass(x, cutoff):
    lp = lowpass(x, cutoff)
    return [v - l for v, l in zip(x, lp)]


def env(x, attack=0.002, decay=None):
    """Атака и экспоненциальный спад (decay — постоянная времени, с; по умолчанию вся длина/4)."""
    total = len(x)
    tau = (decay if decay else total / SR / 4) * SR
    a = max(1, n(attack))
    return [v * min(1.0, i / a) * math.exp(-i / tau) for i, v in enumerate(x)]


def fade(x, sec=0.01):
    f = n(sec)
    out = list(x)
    for i in range(min(f, len(out))):
        out[-1 - i] *= i / f
    return out


def mix(*tracks, at=None):
    """Складывает дорожки; at — смещения в секундах."""
    at = at or [0] * len(tracks)
    total = max(len(t) + n(o) for t, o in zip(tracks, at))
    out = [0.0] * total
    for t, o in zip(tracks, at):
        s = n(o)
        for i, v in enumerate(t):
            out[s + i] += v
    return out


def gain(x, g):
    return [v * g for v in x]


def cat(*tracks):
    out = []
    for t in tracks:
        out += t
    return out


# ------------------------------------------------------------ звуки
def click(rng, bright=1800, dur=0.03, low=0.0):
    body = env(highpass(noise(dur, 1.0, rng), bright), 0.0005, 0.006)
    if low:
        body = mix(body, env(sine(low, dur, 0.5), 0.0005, 0.01))
    return body


def s_button(rng):
    return fade(mix(click(rng, 2500, 0.02), env(sine(1400, 0.03, 0.25), 0.0005, 0.008)), 0.005)


def s_empty(rng):
    """Сухой щелчок бойка: два удара, металлический призвук."""
    hit = mix(click(rng, 900, 0.05, 220), env(sine(3100, 0.05, 0.12), 0.0005, 0.012))
    return fade(mix(hit, gain(hit, 0.4), at=[0, 0.07]), 0.01)


def s_geiger(rng):
    """Серия щелчков трубки разной силы."""
    out = silence(0.55)
    t = 0.0
    while t < 0.48:
        c = gain(click(rng, 2500, 0.02, 120), rng.uniform(0.6, 1.0))
        out = mix(out, c, at=[0, t])
        t += rng.uniform(0.02, 0.12)
    return fade(out, 0.02)


def s_terminal_key(rng):
    return fade(mix(click(rng, 1400, 0.025, 350), env(sine(rng.choice([880, 990, 1100]), 0.04, 0.2), 0.001, 0.01)), 0.005)


def s_terminal_ok(rng):
    return fade(cat(env(sine(880, 0.09, 0.4), 0.003, 0.05), env(sine(1320, 0.14, 0.4), 0.003, 0.08)), 0.01)


def s_terminal_err(rng):
    return fade(cat(env(square(220, 0.12, 0.25), 0.003, 0.1), env(square(165, 0.2, 0.25), 0.003, 0.15)), 0.01)


def s_combat_end(rng):
    notes = [(392, 0.0), (330, 0.14), (262, 0.28)]
    return fade(mix(*[env(sine(f, 0.5, 0.35) , 0.004, 0.22) for f, _ in notes], at=[o for _, o in notes]), 0.05)


def s_levelup(rng):
    notes = [(523, 0.0), (659, 0.1), (784, 0.2), (1047, 0.32)]
    tracks = [mix(env(sine(f, 0.7, 0.3), 0.004, 0.3), env(sine(f * 2, 0.7, 0.08), 0.004, 0.2)) for f, _ in notes]
    return fade(mix(*tracks, at=[o for _, o in notes]), 0.08)


def s_quest(rng):
    notes = [(440, 0.0), (554, 0.12), (659, 0.24)]
    return fade(mix(*[env(sine(f, 0.55, 0.3), 0.004, 0.25) for f, _ in notes], at=[o for _, o in notes]), 0.06)


def s_pickup(rng):
    """Подобрать: как «положить», но выше и короче, со шорохом."""
    thump = env(sine(240, 0.1, 0.45, glide=330), 0.002, 0.04)
    rustle = env(lowpass(noise(0.08, 0.35, rng), 2500), 0.005, 0.03)
    return fade(mix(rustle, thump, at=[0, 0.03]), 0.01)


def s_putdown(rng):
    thump = env(sine(160, 0.12, 0.5, glide=100), 0.002, 0.05)
    return fade(mix(thump, env(lowpass(noise(0.1, 0.5, rng), 1800), 0.002, 0.03)), 0.01)




def s_close(rng):
    thud = mix(env(sine(110, 0.2, 0.6, glide=70), 0.002, 0.07), env(lowpass(noise(0.15, 0.6, rng), 1200), 0.002, 0.05))
    return fade(mix(thud, click(rng, 900, 0.04, 260), at=[0, 0.06]), 0.03)


def s_heal(rng):
    """Шприц: шипение + короткий писк."""
    hiss = env(highpass(noise(0.3, 0.4, rng), 3000), 0.05, 0.15)
    return fade(mix(click(rng, 1200, 0.03), hiss, env(sine(1760, 0.08, 0.15), 0.002, 0.04), at=[0, 0.05, 0.3]), 0.03)


def s_dialog(rng):
    return fade(mix(env(sine(660, 0.05, 0.2), 0.002, 0.02), click(rng, 2000, 0.015)), 0.005)




# ключ -> (функция, число вариантов)
SOUNDS = {
    "button": (s_button, 1), "empty": (s_empty, 1), "geiger": (s_geiger, 3),
    "terminal_key": (s_terminal_key, 4), "terminal_ok": (s_terminal_ok, 1), "terminal_err": (s_terminal_err, 1),
    "combat_end": (s_combat_end, 1),
    "levelup": (s_levelup, 1), "quest": (s_quest, 1),
    "pickup": (s_pickup, 3), "putdown": (s_putdown, 2), "close": (s_close, 2),
    "heal": (s_heal, 2), "dialog": (s_dialog, 1),
}


def write_wav(path, x):
    peak = max(1e-9, max(abs(v) for v in x))
    k = 0.89 / peak   # пик −1 дБ
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v * k)) * 32767)) for v in x))


def main():
    os.makedirs(OUT, exist_ok=True)
    count = 0
    with tempfile.TemporaryDirectory() as tmp:
        for key, (fn, variants) in SOUNDS.items():
            for i in range(variants):
                rng = random.Random(f"{key}{i}")
                name = key if variants == 1 else f"{key}_{i + 1}"
                wav = os.path.join(tmp, name + ".wav")
                write_wav(wav, fn(rng))
                r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", wav,
                                    "-c:a", "libvorbis", "-q:a", "5", os.path.join(OUT, name + ".ogg")],
                                   capture_output=True, text=True)
                if r.returncode:
                    raise SystemExit(r.stderr)
                count += 1
    print(f"готово: {count} файлов в {OUT}")


if __name__ == "__main__":
    main()
