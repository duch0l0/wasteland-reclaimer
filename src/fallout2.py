"""
Музыка и звуки из установленного Fallout 2 — если он есть у игрока.

Файлы Fallout 2 защищены авторским правом (Bethesda/Interplay, музыка — Марк Морган),
поэтому в игру они НЕ кладутся: ни в git, ни в exe. Как и Fallout 2 Community Edition,
игра берёт их из копии игрока:
  1. ищет установку (FALLOUT2_DIR, папка Fallout2 рядом с игрой, GOG/Steam);
  2. один раз, в фоне, перекодирует нужное через ffmpeg в кэш f2cache/ рядом с сохранениями
     (музыка — sound/music/*.acm, эффекты — из архива master.dat);
  3. дальше звук играет из кэша. Нет Fallout 2 или ffmpeg — играют наши звуки.

Какие файлы Fallout 2 взяты и зачем — MUSIC и SFX ниже (разбор набора — README → «Звук»).
"""
import os
import shutil
import struct
import subprocess
import threading
import zlib

# ------------------------------------------------------------ что берём
# музыка локаций: наш ключ -> трек Fallout 2 (sound/music/<имя>.acm)
MUSIC = {
    "desert": "07desert",      # Пятнадцатая, пустошь
    "world": "03wrldmp",       # карта мира
    "caves": "13carvrn",       # ливнёвка
    "lab": "10labone",         # Убежище 57
    "raiders": "05raider",     # заправка, случайные встречи
    "hub": "01hub",            # Барстоу: трасса и караваны
    "junktown": "12junktn",    # Барстоу: депо
    "reno": "19reno",          # Барстоу: центр — неон и руины
    "vats": "08vats",          # святилище Ордена
    "title": "23world",        # главное меню
}

# эффекты: наш ключ -> варианты (имена в sound/sfx/ архива master.dat, без .acm)
SFX = {
    # оружие героя и врагов (коды звука оружия — из описаний предметов proto/items)
    "shot": ["waa1xxx1", "waa1xxx2"],             # 10-мм пистолет
    "shot_pipe": ["wae1xxx1", "wae1xxx2"],        # самопал — погромче и грубее
    "shot_enemy": ["wad1xxx1", "wad1xxx2"],       # стрелки: пистолет-пулемёт
    "shot_turret": ["magunnlc", "magunnld"],      # турель
    "melee": ["wa51xxx1"],                        # взмах ломом
    # экшен в Барстоу: автомат и дробовик Дэкса
    "ar_shot": ["wad1xxx1", "wad1xxx2"], "ar_reload": ["wrd1xxx1"], "ar_hit": ["whd1fxx1", "whd1fxx2"],
    "sg_shot": ["war1xxx1", "war1xxx2"], "sg_reload": ["wrr1xxx1"], "sg_hit": ["whr1fxx1", "whr1fxx2"],
    "empty": ["wod1xxx1"],
    "hit": ["wh51fxx1", "wh31fxx1", "wh21fxx1"],  # удар по телу
    "hit_bullet": ["wha1fxx1", "wha1fxx2"],       # пуля в тело
    "explosion": ["whn1xxx1", "whn1xxx2"],        # взрыв (ракета)
    # голоса: attack / hurt / death
    "human_attack": ["hmxxxxaq"], "human_hurt": ["hmxxxxao", "hmxxxxap"], "human_death": ["hmxxxxba", "hmxxxxbb"],
    "ghoul_attack": ["hmxxxxaq"], "ghoul_hurt": ["naghulao", "naghulap"], "ghoul_death": ["naghulba", "naghulbb"],
    "dog_attack": ["maddogaq"], "dog_hurt": ["maddogao", "maddogap"], "dog_death": ["maddogba"],
    "rat_attack": ["masrataq", "mamrataq"], "rat_hurt": ["masratao", "mamratao"], "rat_death": ["masratba", "mamratba"],
    "roach_attack": ["maanttaq"], "roach_hurt": ["maanttao"], "roach_death": ["maanttba"],
    "beetle_attack": ["mascrpaq"], "beetle_hurt": ["mascrpao"], "beetle_death": ["mascrpba"],
    "robot_attack": ["marobtaq"], "robot_hurt": ["magunnao", "marobtao"], "robot_death": ["magunnba", "marobtba"],
    # интерфейс и мир
    "combat_start": ["icombat1"], "combat_end": ["icombat2"],
    "open": ["iocntnra", "iocntnrb"], "close": ["iccntnra", "iccntnrb"],
    "pickup": ["ipickup1"], "putdown": ["iputdown"],
    "button": ["ib1p1xx1"], "levelup": ["levelup"], "geiger": ["geiger"],
}

MUSIC_DIR, SFX_DIR = "music", "sfx"
SOUNDS_FOLDER = "fallout2_sounds"   # готовая папка (кладётся вручную, в git её нет) — см. README → «Звук»


def sounds_dir(game_dir):
    """Где лежат готовые звуки: папка fallout2_sounds рядом с игрой или внутри неё,
    иначе — кэш f2cache (туда перекодируется из установленного Fallout 2)."""
    for d in (os.environ.get("FALLOUT2_SOUNDS", ""), os.path.join(os.path.dirname(game_dir), SOUNDS_FOLDER),
              os.path.join(game_dir, SOUNDS_FOLDER)):
        if d and os.path.isdir(os.path.join(d, MUSIC_DIR)):
            return d
    return os.path.join(game_dir, "f2cache")


CACHE_DIR = sounds_dir(os.getcwd())   # main.py уточняет от папки игры/exe


# ------------------------------------------------------------ поиск установки
def candidates(game_dir):
    home = os.path.expanduser("~")
    return [os.environ.get("FALLOUT2_DIR", ""),
            os.path.join(os.path.dirname(game_dir), "Fallout2"),
            os.path.join(os.path.dirname(game_dir), "Fallout 2"),
            os.path.join(game_dir, "Fallout2"),
            os.path.join(home, "GOG Games", "Fallout 2"),
            os.path.join(home, ".local", "share", "Steam", "steamapps", "common", "Fallout 2"),
            r"C:\GOG Games\Fallout 2", r"C:\Program Files (x86)\GOG Galaxy\Games\Fallout 2",
            r"C:\Program Files (x86)\Steam\steamapps\common\Fallout 2"]


def find_install(game_dir):
    for d in candidates(game_dir):
        if d and os.path.isfile(os.path.join(d, "master.dat")) and os.path.isdir(os.path.join(d, "sound", "music")):
            return d
    return None


# ------------------------------------------------------------ архив DAT2 (master.dat)
def dat2_index(path):
    """Оглавление архива Fallout 2: {путь в нижнем регистре через '/': (сжат, размер, упак., смещение)}."""
    with open(path, "rb") as f:
        f.seek(-8, 2)
        tree_size, data_size = struct.unpack("<II", f.read(8))
        f.seek(data_size - tree_size - 8)
        n, = struct.unpack("<I", f.read(4))
        out = {}
        for _ in range(n):
            ln, = struct.unpack("<I", f.read(4))
            name = f.read(ln).decode("latin-1").replace("\\", "/").lower()
            comp, real, packed, off = struct.unpack("<BIII", f.read(13))
            out[name] = (comp, real, packed, off)
        return out


def dat2_read(path, entry):
    comp, real, packed, off = entry
    with open(path, "rb") as f:
        f.seek(off)
        data = f.read(packed)
    return zlib.decompress(data) if comp else data


# ------------------------------------------------------------ перекодировка в кэш
class Importer:
    """Разовая фоновая перекодировка ACM -> ogg/wav в кэш. status: idle / running / done / no_ffmpeg / none."""

    def __init__(self, game_dir, cache_dir):
        self.install = find_install(game_dir)
        self.cache = cache_dir
        self.ffmpeg = shutil.which("ffmpeg")
        self.status = "none" if not self.install else ("no_ffmpeg" if not self.ffmpeg else "idle")
        self.done_files = 0
        self._thread = None
        if self.complete():   # готовая папка звуков — ни Fallout 2, ни ffmpeg не нужны
            self.status = "done"

    def music_path(self, key):
        return os.path.join(self.cache, MUSIC_DIR, f"{MUSIC[key]}.ogg")

    def sfx_path(self, name):
        return os.path.join(self.cache, SFX_DIR, f"{name}.wav")

    def complete(self):
        return (all(os.path.isfile(self.music_path(k)) for k in MUSIC)
                and all(os.path.isfile(self.sfx_path(n)) for v in SFX.values() for n in v))

    def start(self):
        if self.status != "idle":
            return
        self.status = "running"
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _convert(self, src_bytes_or_path, dst, codec_args):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        tmp = dst + ".part"
        if isinstance(src_bytes_or_path, bytes):
            src = dst + ".acm"
            with open(src, "wb") as f:
                f.write(src_bytes_or_path)
        else:
            src = src_bytes_or_path
        try:
            subprocess.run([self.ffmpeg, "-v", "error", "-y", "-i", src, *codec_args, "-f",
                            "ogg" if dst.endswith(".ogg") else "wav", tmp],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
            os.replace(tmp, dst)
        except (subprocess.SubprocessError, OSError):
            pass
        finally:
            if isinstance(src_bytes_or_path, bytes) and os.path.exists(src):
                os.remove(src)

    def _run(self):
        try:
            master = os.path.join(self.install, "master.dat")
            index = dat2_index(master)
            for names in SFX.values():   # эффекты — маленькие, сначала они
                for n in names:
                    dst = self.sfx_path(n)
                    entry = index.get(f"sound/sfx/{n}.acm")
                    if entry and not os.path.isfile(dst):
                        self._convert(dat2_read(master, entry), dst, ["-ac", "2", "-ar", "22050"])
                    self.done_files += 1
            for key in MUSIC:
                dst = self.music_path(key)
                src = os.path.join(self.install, "sound", "music", f"{MUSIC[key]}.acm")
                if os.path.isfile(src) and not os.path.isfile(dst):
                    self._convert(src, dst, ["-c:a", "libvorbis", "-q:a", "4"])
                self.done_files += 1
        finally:
            self.status = "done"
