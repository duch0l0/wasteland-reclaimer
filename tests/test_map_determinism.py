"""
Страж детерминизма карт: все tools/build_*.py должны собирать ровно те файлы, что лежат в data/.
Если генератор и закоммиченные карты разошлись (правили генератор, но не пересобрали, или наоборот) — тест падает
и говорит, какой скрипт, какой файл и какой командой пересобрать.

Изоляция: рабочая копия не трогается — тест собирает песочницу во временной папке (tools, src, data,
index.json наборов; iso/ подключается символической ссылкой только на чтение) и запускает генераторы там:
mapkit.py делает os.chdir(ROOT), где ROOT — папка проекта, поэтому в песочнице ROOT указывает в песочницу.

Порядок: build_*.py по алфавиту, затем ещё раз tools/build_ambient.py — build_folks.py переписывает в
data/ambient.json число жителей по анкетам, а источник истины для этих чисел — build_ambient.py, поэтому
он идёт последним (иначе разойдётся 6 локаций: needles, junktown, necropolis, boneyard, searchlight, vegas_snakes).

Запуск из папки game_project:

    .venv/bin/python tests/test_map_determinism.py

Печатает OK/FAIL по каждому расхождению и ИТОГ; код выхода 1, если есть расхождения. Время — около 45 с.
"""
import glob
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SCRIPTS = sorted(glob.glob(os.path.join("tools", "build_*.py")))
FINAL = ["tools/build_ambient.py"]          # идёт последним: его числа жителей — исходные (см. шапку)
TIMEOUT = 300
failed = []          # (файл, подсказка)


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


def snap(base):
    """путь относительно data -> md5, чтобы знать, кто из генераторов какой файл переписал."""
    out = {}
    for dirpath, _dirs, files in os.walk(base):
        for fn in files:
            p = os.path.join(dirpath, fn)
            with open(p, "rb") as f:
                out[os.path.relpath(p, base)] = hashlib.md5(f.read()).hexdigest()
    return out


def make_sandbox(tmp):
    """Копия tools/src/data; assets/ (741 МБ) и iso/ — ссылками."""
    box = os.path.join(tmp, "proj")
    os.makedirs(box)
    for d in ("tools", "src", "data"):
        shutil.copytree(d, os.path.join(box, d), ignore=shutil.ignore_patterns("__pycache__"))
    # картинки нужны: mapkit.put не ставит предмет, который картинкой прячет соседа (маски пикселей);
    # генераторы в assets/ не пишут, поэтому — ссылка, а не копия
    os.symlink(os.path.abspath("assets"), os.path.join(box, "assets"))
    if os.path.isdir("iso"):                        # build_barstow.py читает изометрические тайлы (208 МБ)
        os.symlink(os.path.abspath("iso"), os.path.join(box, "iso"))
    return box


def hint(script):
    return f"перегенерируй: .venv/bin/python {script}"


def main():
    if not SCRIPTS:
        ok(False, "не найдено ни одного tools/build_*.py")
        return
    t0 = time.time()
    tmp = tempfile.mkdtemp(prefix="mapdet_")
    try:
        box = make_sandbox(tmp)
        data = os.path.join(box, "data")
        owner = {}                                  # файл -> последний генератор, который его переписал
        env = dict(os.environ)
        env.pop("PYTHONHASHSEED", None)           # тест не должен зависеть от хэш-сида (random.Random(hash()))
        bad_runs = []
        for script in SCRIPTS + FINAL:
            before = snap(data)
            r = subprocess.run([sys.executable, script], cwd=box, env=env, timeout=TIMEOUT,
                               capture_output=True, text=True)
            after = snap(data)
            for rel, h in after.items():
                if before.get(rel) != h:
                    owner[rel] = script
            for rel in before:
                if rel not in after:
                    owner[rel] = script             # генератор удаляет устаревший файл (build_barstow → town_iso.json)
            if r.returncode != 0:
                tail = (r.stderr.strip().splitlines() or ["?"])[-1][:200]
                bad_runs.append(f"{script}: код {r.returncode}: {tail}")
        for msg in bad_runs:
            ok(False, "генератор упал — " + msg)

        real = "data"
        cur = snap(real)
        diffs = 0
        for rel in sorted(cur):
            gen = os.path.join(data, rel)
            if not os.path.isfile(gen):
                diffs += 1
                ok(False, f"файл пропал: data/{rel} — {hint(owner.get(rel, 'tools/build_*.py'))}")
            elif open(gen, "rb").read() != open(os.path.join(real, rel), "rb").read():
                diffs += 1
                ok(False, f"data/{rel} расходится с генератором — {hint(owner.get(rel, 'tools/build_*.py'))}")
        extra = [rel for rel in snap(data) if rel not in cur]
        for rel in sorted(extra):
            diffs += 1
            ok(False, f"data/{rel} генератор создаёт, а в репозитории его нет — {hint(owner.get(rel, 'tools/build_*.py'))}")

        if not diffs and not bad_runs:
            ok(True, f"все {len(SCRIPTS)} генераторов воспроизводят data/ байт-в-байт ({len(cur)} файлов)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if failed:
        print(f"ИТОГ: ПРОВАЛ — расхождений {len(failed)}; рабочая копия data/ не тронута")
        sys.exit(1)
    print(f"ИТОГ: OK — {len(SCRIPTS)} генераторов, data/ воспроизведён байт-в-байт "
          f"({time.time() - t0:.1f} с)")
    sys.exit(0)


main()
