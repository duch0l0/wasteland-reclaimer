"""
Wasteland Reclaimer — прототип 2D RPG в духе Fallout 2: исследование в
реальном времени, пошаговый бой с ОД и прицельными ударами, перки,
торговля, квесты с несколькими решениями, карта мира и случайные встречи.

Запуск:  python main.py   (нужен pygame-ce, см. README.md)
Код игры — в src/ (где что лежит — см. src/game/__init__.py и README.md).
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)  # относительные пути к assets/ и data/ работают при запуске из любой папки

from src.game import Game  # noqa: E402 — импорт после chdir: модули читают data/ при загрузке


if __name__ == "__main__":
    Game().run()
