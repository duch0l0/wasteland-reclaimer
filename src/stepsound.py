"""Какой шаг слышен под ногами: код земли карты (ground), имя тайла из "floors" и лужи.

Коды земли (src/townmap.py): d земля, a асфальт, c бетонный пол, g гравий, s песок,
m стальной пол убежища, w мокрый бетон ливнёвки, h/v разметка, x скала, _ пустота.
Свои коды карта задаёт в "floors" {код: ["pk:…"]} — их разбираем по имени картинки
(desnat/sand/dust → песок, gravel/rubble → гравий, metal/steel/grate → металл,
water/wet/puddle/sewer → вода), а если имя ничего не говорит — по самому коду.
Вода, которую townmap уже нашёл по синему тону тайла (level._water), — всегда вода.
"""
STEP = {"d": "step_dirt", "s": "step_sand", "g": "step_gravel", "q": "step_gravel",
        "m": "step_metal", "w": "step_water", "~": "step_water", "≈": "step_water",
        "a": "step_concrete", "c": "step_concrete", "h": "step_concrete", "v": "step_concrete"}

# имя тайла из набора → звук (порядок важен: первое совпадение)
FLOOR_WORDS = (("desnat", "step_sand"), ("sand", "step_sand"), ("dust", "step_sand"),
               ("gravel", "step_gravel"), ("rubble", "step_gravel"), ("scree", "step_gravel"),
               ("metal", "step_metal"), ("steel", "step_metal"), ("grate", "step_metal"),
               ("catwalk", "step_metal"),
               ("water", "step_water"), ("wet", "step_water"), ("puddle", "step_water"),
               ("sewer", "step_water"))


def ground_code(level, tile):
    """Код земли в клетке (None — карта не из «ground»-строк: арена, изометрия)."""
    g = getattr(level, "ground", None)
    x, y = tile
    if g and 0 <= y < len(g) and 0 <= x < len(g[y]):
        return g[y][x]
    return None


def puddle_under(level, tile):
    """Лужа под ногами: объект слоя «пол» с puddle в имени (x_puddle, nv_puddle…)."""
    for o in getattr(level, "objects", ()):
        if o.get("floor") and "puddle" in o.get("name", "") and tile in o["foot"]:
            return True
    return False


def step_sound(level, tile, underground=False):
    """Ключ звука шага для клетки: step_dirt / step_gravel / step_sand / step_metal /
    step_water / step_concrete. Незнакомый код — как раньше: под землёй бетон, снаружи земля."""
    code = ground_code(level, tile)
    if code is None:
        return "step_concrete" if underground else "step_dirt"
    if puddle_under(level, tile) or code in getattr(level, "_water", ()):
        return "step_water"
    src = str((getattr(level, "floor_src", None) or {}).get(code) or "").lower()
    for word, key in FLOOR_WORDS:
        if word in src:
            return key
    return STEP.get(code) or ("step_concrete" if underground else "step_dirt")
