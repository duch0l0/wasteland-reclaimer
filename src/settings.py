"""
Общие настройки игры: размер окна, цвета, тайлы, пути к ассетам.
"""

# Логический размер экрана: всё рисуется в нём, а окно масштабирует картинку
# под свой размер (окно можно растягивать, F11 — полный экран).
SCREEN_W, SCREEN_H = 1280, 720
# координаты локаций на карте мира (data/locations.json, world_pos) заданы для 960×540
WORLD_MAP_REF = (960, 540)
FPS = 60
TILE = 48
# Масштаб мира (колёсико мыши): меньше — дальше камера, больше видно, как в Fallout.
# Интерфейс не масштабируется.
ZOOMS = (1.0, 0.85, 0.72, 0.6)
ZOOM_DEFAULT = 0.72

TITLE = "Wasteland Reclaimer (прототип)"

# --- Цвета (плейсхолдер-палитра в духе выжженной пустоши) ---
COLOR_BG_SKY = (46, 40, 38)
COLOR_TEXT = (235, 225, 200)
COLOR_HP = (176, 46, 38)
COLOR_HP_BG = (60, 20, 20)
COLOR_XP = (86, 140, 74)
COLOR_XP_BG = (30, 40, 24)
COLOR_PANEL = (24, 20, 18)
COLOR_PANEL_BORDER = (110, 96, 60)

# --- Пути к ассетам (сюда можно подложить настоящие спрайты) ---
ASSET_ROOT = "assets"
PLAYER_DIR = f"{ASSET_ROOT}/sprites/player"   # кадры по направлениям: player/{down,left,right,up}/0.png..
TILE_DIR = f"{ASSET_ROOT}/tiles"              # ground.png, wall.png, scrap.png
BG_DIR = f"{ASSET_ROOT}/bg"                   # layer0.png (дальний план) ... layerN.png (ближний)

# Прозрачность тайлов земли (0..255). Карта целиком покрыта землёй, поэтому
# без полупрозрачности параллакс-фон под ней не виден совсем.
# 255 — земля непрозрачная (фон не виден).
GROUND_ALPHA = 150

ANIM_FRAME_MS = 110  # скорость смены кадров анимации

# --- Баланс ---
PLAYER_SPEED = 180  # px/sec
PLAYER_BASE_HP = 30
PLAYER_BASE_DMG = 5
PLAYER_ATTACK_RANGE = 46
PLAYER_ATTACK_COOLDOWN_MS = 420
XP_TO_LEVEL = lambda lvl: 20 + lvl * 15  # опыт, нужный для перехода с lvl на lvl+1

ENEMY_AGGRO_RANGE = 220  # px: радиус обзора врага по умолчанию (у каждого типа свой — data/enemies.json)

# --- Пошаговый бой (в духе Fallout 2) ---
# ОД — очки действия на ход; навык — базовый шанс попасть, % (минус КБ цели);
# КБ — класс брони; реакция (Sequence) — кто ходит раньше.
PLAYER_AP = 8
PLAYER_MELEE_SKILL = 65
PLAYER_GUNS_SKILL = 55
PLAYER_SKILL_PER_LEVEL = 5
PLAYER_AC = 10
PLAYER_SEQUENCE = 6
HP_REGEN_MS = 1500  # вне боя: +1 HP раз в столько мс (в Fallout 2 раны тоже заживают со временем)


AP_MOVE = 1       # шаг на соседнюю клетку
AP_ATTACK = 3     # обычный удар
AP_AIMED = 4      # прицельный удар
AP_CRAFT = 4      # использовать/скрафтить предмет в бою
BASE_CRIT_CHANCE = 5
HIT_CHANCE_MIN, HIT_CHANCE_MAX = 5, 95

COMBAT_STEP_MS = 160    # анимация шага по клетке
COMBAT_ATTACK_MS = 380  # пауза после удара, чтобы было видно, что произошло
