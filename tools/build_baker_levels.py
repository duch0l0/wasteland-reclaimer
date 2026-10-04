"""
Бейкер, новые уровни (районы — tools/build_baker.py). Сценарий — docs/story.md, раздел 7.

  baker_crypt      «Крипта Единства» под молельней. Лестница за алтарём, плита на ключе Ансельма
                   (ключ — в его сундуке). Зал ожидания с клетками (выживший Оскар), купель
                   «причастия» — чаны с мутной жидкостью, механическая рука, операционный стол,
                   терминал с журналом опытов; оссуарий; в купели живёт «Сплетённый» — то, что
                   вышло из троих.
  baker_motel_2f   второй этаж мотеля «Последняя миля»: коридор и пять номеров со своими историями —
                   семья, которая прячется от культа; мёртвый охранник каравана; номер Холлиса
                   (запертый сундук с бумагами Анклава); крысиная нора; номер с обвалившейся крышей.

Наборы: cult-temple (cult), wasteland-laboratory (wlab), modern-hospital (hosp), modern-motel (motel).
Запуск из папки game_project (после tools/build_baker.py):  .venv/bin/python tools/build_baker_levels.py
"""
from citykit import City, CityMap

city = City("baker_levels", "Бейкер: уровни")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


# ------------------------------------------------------------ объекты
CANDLE = P("cu_candelabra", "pk:cult/cult_1_005")
CANDLE_B = P("cu_candelabra_b", "pk:cult/cult_1_008")
ALTAR = P("cu_altar", "pk:cult/cult_2_045", sight=True)
ALTAR_B = P("cu_altar_b", "pk:cult/cult_2_046", sight=True)
SHELF = P("cu_bookshelf", "pk:cult/cult_2_006", sight=True)
SHELF_B = P("cu_bookshelf_b", "pk:cult/cult_2_040", sight=True)
BANNER = P("cu_banner", "pk:cult/cult_2_131", sight=True)
BONES = P("cu_bones", "pk:cult/cult_2_097", search="grave", title="груда костей")
SKULLS = P("cu_skulls", "pk:cult/cult_2_099")
STATUE = P("cu_statue", "pk:cult/cult_2_094", sight=True)
ARCH = P("cu_arch", "pk:cult/cult_2_033", block=True, sight=True)
COFFIN = P("cu_coffin", "pk:cult/cult_2_154", search="grave", title="каменный гроб")
CHEST = P("cu_chest", "pk:cult/cult_2_124", search="crate", title="сундук")
VAT = P("lb_vat", "pk:wlab/wlab_1_000", sight=True)
VATS = P("lb_vats", "pk:wlab/wlab_1_002", sight=True)
TANK = P("lb_tank", "pk:wlab/wlab_1_008", sight=True)
TANK_B = P("lb_tank_b", "pk:wlab/wlab_1_034", sight=True)
ARM = P("lb_arm", "pk:wlab/wlab_1_029")
DESK_PC = P("lb_desk_pc", "pk:wlab/wlab_1_018")
DESK_CHEM = P("lb_desk_chem", "pk:wlab/wlab_1_012")
SHELF_LAB = P("lb_shelf", "pk:wlab/wlab_2_069", sight=True, search="shelf", title="полка с реактивами")
CASE = P("lb_case", "pk:wlab/wlab_2_084", search="military", title="ящик")
BED_OP = P("hp_bed", "pk:hosp/hosp_1_007")
DRIP = P("hp_drip", "pk:hosp/hosp_1_010")
CAGE = P("bk_cage", "pk:wschool/p1/12,2,4,2", foot=[4, 1], sight=False)     # решётчатая ограда — клетки
VENDING = P("mt_vending", "pk:motel/motel_1_002", sight=True, search="shelf", title="торговый автомат")
ICE = P("mt_ice", "pk:motel/motel_1_022", sight=True)
PLANT = P("mt_plant", "pk:motel/motel_1_063")
STAIRS = P("mt_stairs", "pk:motel/p1/4,8,2,2", foot=[2, 2], block=False, layer="floor")

STONE = cells("cult/p1", [(4, 0), (5, 0), (4, 1), (5, 1)])
DARK_WOOD = ["pk:cult/cult_f2_21", "pk:cult/cult_f2_20"]
GREY_WOOD = ["pk:cult/cult_f2_22", "pk:cult/cult_f2_23"]

# ================================================================ Крипта Единства
W, H = 42, 30
cr = CityMap(city, "baker_crypt", "Крипта Единства", W, H, start=(4, 6), seed=71, interior=True, music="vats")
cr.floor_code("S", *STONE)
cr.wall_code("K", "pk:cult/cult_w1_07")       # бурый камень
cr.wall_code("Q", "pk:nbunk/nbunk_w3_17")     # бетон купели
ENTRY = cr.room(1, 1, 12, 10, "K", "S")        # лестница вниз и молитвенный зал
WAIT = cr.room(12, 1, 28, 12, "K", "S")        # зал ожидания с клетками
FONT = cr.room(12, 12, 32, 28, "Q", "S")       # купель
BONE = cr.room(1, 10, 12, 28, "K", "S")        # оссуарий
LAB = cr.room(28, 1, 40, 12, "Q", "S")         # кабинет опытов
cr.opening(12, 5, 12, 6, "S")
cr.opening(19, 12, 20, 14, "S")
cr.opening(6, 10, 7, 12, "S")
cr.opening(12, 22, 12, 23, "S")
cr.opening(28, 7, 28, 8, "S")

cr.props.append(["x_ladder", 3, 4])
cr.portal([(3, 4)], "baker_mission", (34, 16), "Наверх, в молельню")
cr.reserve(2, 4, 5, 7)
# Проёмы: молельня -> зал ожидания (восток, x 12, y 5–6), молельня -> оссуарий (юг, x 6–7),
# зал ожидания -> купель (юг, x 19–20), зал ожидания -> кабинет (восток, x 28, y 7–8),
# оссуарий -> купель (восток, x 12, y 22–23). Перед проёмами ничего не стоит (citykit.opening).

# молельня: алтарь у северной стены справа от лестницы, по бокам — канделябры, на стене — знамя
cr.put(SHELF, 2, 3, check=False)
cr.put(CANDLE, 7, 4)
cr.put(ALTAR, 8, 4)
cr.put(CANDLE, 10, 4)
cr.put(BANNER, 8, 3, check=False)
# зал ожидания: ряд клеток (решётка вдоль зала), за ними — узники; у восточной стены — их одежда
cr.put(CAGE, 15, 6)
cr.put(CAGE, 21, 6)
cr.npcs += [["oskar", 16, 4]]
cr.put(CANDLE_B, 14, 10)
cr.put(CHEST, 26, 4)
cr.containers[-1].update({"name": "сундук с одеждой «вознесённых»",
                          "loot": {"ткань": 3, "плюшевый мишка": 1, "крышки": 15}})
cr.put(SKULLS, 26, 10)
# купель: чаны вдоль северной стены по обе стороны от входа, в центре — операционный стол,
# капельница и механическая рука, которая опускает в чан; в углу — статуя «Совершенного»
cr.put(VATS, 13, 15)
cr.put(TANK, 16, 15)
cr.put(TANK_B, 23, 15)
cr.put(VAT, 27, 15)
cr.put(DRIP, 17, 21)
cr.put(BED_OP, 18, 21)
cr.put(ARM, 21, 20)
cr.put(STATUE, 30, 26)
cr.enemies += [["joined", 24, 24], ["cultist", 16, 26], ["cultist", 29, 19]]
# оссуарий: кости вдоль стен, гробы
for x, y in ((3, 14), (9, 15), (3, 19), (5, 26), (9, 26)):
    cr.put(BONES if (x + y) % 2 else SKULLS, x, y)
cr.put(COFFIN, 8, 18)
cr.put(COFFIN, 2, 23)
cr.containers[-1].update({"name": "гроб без имени", "loot": {"образец ВРЭ": 1, "крышки": 20}})
# кабинет опытов: терминал, стол с колбами и полка реактивов — у северной стены, компьютер — у южной
cr.terminal(30, 4, "crypt_log")
cr.put(DESK_CHEM, 33, 4)
cr.put(SHELF_LAB, 37, 4)
cr.put(DESK_PC, 34, 10)
cr.put(CASE, 38, 10)
cr.containers[-1].update({"name": "ящик с «дарами»", "loot": {"стимулятор": 2, "аптечка армейская": 1, "антирадин": 1}})
cr.enemies += [["radroach", 32, 8], ["radroach", 37, 7]]

# ================================================================ Мотель: второй этаж
W, H = 40, 22
mo = CityMap(city, "baker_motel_2f", "Мотель: второй этаж", W, H, start=(37, 15), seed=72, interior=True,
             music="junktown")
mo.floor_code("C", *DARK_WOOD)
mo.floor_code("R", *GREY_WOOD)
mo.wall_code("Y", "pk:motel/motel_w1_09")      # жёлтые обои
mo.wall_code("Z", "pk:motel/motel_w2_15")      # номера: светлая штукатурка
HALL = mo.room(1, 11, 39, 18, "Y", "C")
rooms = [mo.room(x, 1, x + 7, 11, "Z", "R") for x in (1, 8, 15, 22, 29)]
for x0 in (1, 8, 15, 22, 29):
    mo.opening(x0 + 3, 11, x0 + 4, 13, "C")
mo.put(STAIRS, 37, 15, check=False)
mo.portal([(37, 16), (38, 16)], "baker", (67, 17), "Вниз, в холл")
mo.reserve(35, 14, 38, 17)
# Двери номеров — в северной стене коридора: x 4–5, 11–12, 18–19, 25–26, 32–33.
# Между дверями у стены — автомат с едой, растение, ледогенератор у лестницы.
mo.put(VENDING, 8, 14)
mo.put(PLANT, 22, 14)
mo.put(ICE, 29, 14)
# 201 — семья прячется от культа: две кровати у стены, тумбочка между ними
mo.put("bed", 2, 4)
mo.put("bed", 6, 4)
mo.box("cabinet_small", 4, 4, "тумбочка", {"консервы": 1, "бинт": 1})
mo.npcs += [["motel_mom", 3, 7], ["motel_kid", 6, 7]]
# 202 — мёртвый охранник каравана: опрокинутый стол (баррикада) и тело у стены
mo.put("bed", 9, 4)
mo.put("table_upside", 10, 7)
mo.box("r_bones", 13, 7, "тело охранника", {"дробь": 6, "жетон солдата": 1, "записка охранника": 1})
# 203 — номер Холлиса: кровать, стол со стулом, сундук в углу
mo.put("bed", 16, 4)
mo.box("metal_chest", 20, 4, "сундук Холлиса", {"шифроблокнот Анклава": 1, "крышки": 90, "стимулятор": 1},
       requires={"item": "отмычка", "msg": "Сундук на хорошем замке, такие возят издалека. Нужна отмычка."})
mo.put("table_2", 19, 7)
mo.put("chair_wood", 20, 7)
# 204 — крысиная нора: голый каркас кровати, тряпьё в углу
mo.put("bed_frame", 23, 4)
mo.put("pile_rags", 27, 7)
mo.enemies += [["rat", 24, 6], ["rat", 27, 9], ["rat", 23, 8]]
# 205 — обвалившаяся крыша: песок, обломки, уцелевший шкаф
mo.paint("d", 30, 4, 35, 7)
mo.put("r_rocks", 31, 5)
mo.put("r_planks", 33, 6)
mo.box("wardrobe", 35, 4, "шкаф в номере для новобрачных", {"сигареты": 2, "свадебная фотография": 1, "крышки": 25})

city.save(gap_exempt=("oskar", "motel_mom", "motel_kid"))
