"""
Wasteland Reclaimer — прототип 2D RPG в духе Fallout 2: исследование в
реальном времени, пошаговый бой с ОД и прицельными ударами, перки,
торговля, квесты с несколькими решениями, карта мира и случайные встречи.

Запуск:  python main.py   (нужен pygame-ce, см. README.md)
Сборка exe: см. README.md, раздел «Сборка».
Код игры — в src/ (где что лежит — см. src/game/__init__.py и README.md).
"""
import os
import sys

if getattr(sys, "frozen", False):
    # собранный exe (PyInstaller): данные игры распакованы во временную папку,
    # а сохранения — рядом с самим exe, чтобы не пропадали
    BASE_DIR = sys._MEIPASS
    USER_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    USER_DIR = BASE_DIR
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)  # относительные пути к assets/ и data/ работают при запуске из любой папки

from src.game import Game, saveload  # noqa: E402 — импорт после chdir: модули читают data/ при загрузке

saveload.SAVE_DIR = os.path.join(USER_DIR, "saves")
from src import fallout2  # noqa: E402
fallout2.CACHE_DIR = fallout2.sounds_dir(USER_DIR)   # музыка и звуки: папка fallout2_sounds (см. README)


def smoke():
    """Проверка сборки без участия человека (--smoke): город, кадры, сохранение, карта мира, окна."""
    g = Game(intro=False)
    for _ in range(120):
        g.update(16)
        g.draw()
    g.quick_save()
    g.go_world_map()                     # карта мира, меню, терминал, журнал — всё рисуется
    g.draw()
    g.open_menu("pause")
    g.draw()
    g.close_menu()
    g.enter_location("ruins")
    g.open_terminal("grandpa")
    g.draw()
    g.close_terminal()
    g.journal_open = True
    g.draw()
    ok = os.path.isfile(os.path.join(saveload.SAVE_DIR, "quick.json"))
    print("SMOKE OK" if ok else "SMOKE FAIL", g.loc.name, len(g.level.objects), saveload.SAVE_DIR)
    sys.exit(0 if ok else 1)


def main():
    if "--smoke" in sys.argv:
        smoke()
    try:
        game = Game(intro="--iso" not in sys.argv)
        if "--iso" in sys.argv:   # сразу в изометрический Барстоу
            game.menu = None
            game.slides = None
            game.merc_start()     # за наёмника Дэкса, как по квесту «Контракт на Барстоу»
        game.run()
    except Exception:
        # в exe без консоли ошибку не видно — пишем её в файл рядом с игрой
        import traceback
        with open(os.path.join(USER_DIR, "crash.log"), "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        raise


if __name__ == "__main__":
    main()
