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
# Свет — в самом предмете (набор «свеча», «канделябр», «котёл»): в крипте у каждого пятна должен быть
# видимый источник, а «потолочных» ламп там не бывает.
CANDLE = P("cu_candelabra", "pk:cult/cult_1_005", foot=[1, 1],
           light={"r": 120, "color": [255, 176, 96], "at": [0.5, 0.2], "flicker": 0.35})
CANDLE_B = P("cu_candelabra_b", "pk:cult/cult_1_008", foot=[1, 1],
             light={"r": 110, "color": [255, 176, 96], "at": [0.5, 0.2], "flicker": 0.35})
TORCH = P("cu_candles_floor", "pk:cult/cult_2_068", block=False,
          light={"r": 150, "color": [255, 160, 70], "at": [0.5, 0.25], "flicker": 0.5})
ALTAR = P("cu_altar", "pk:cult/cult_2_045", foot=[2, 1], sight=True,
          light={"r": 100, "color": [255, 170, 90], "at": [0.5, 0.35], "flicker": 0.3})
ALTAR_B = P("cu_altar_b", "pk:cult/cult_2_046", foot=[2, 1], sight=True)
SHELF = P("cu_bookshelf", "pk:cult/cult_2_006", foot=[2, 1], sight=True, search="shelf",
          title="шкаф с писаниями")
SHELF_B = P("cu_bookshelf_b", "pk:cult/cult_2_040", foot=[2, 1], sight=True, search="shelf",
            title="шкаф с писаниями")
BANNER = P("cu_banner", "pk:cult/cult_2_131", sight=True)
BONES = P("cu_bones", "pk:cult/cult_2_097", search="grave", title="груда костей")
SKULLS = P("cu_skulls", "pk:cult/cult_2_099")
STATUE = P("cu_statue", "pk:cult/cult_2_094", sight=True)
ARCH = P("cu_arch", "pk:cult/cult_2_033", foot=[2, 1], sight=True)
PEW = P("cu_pew", "pk:cult/cult_3_044", foot=[2, 1])            # каменная лавка
PILLAR = P("cu_pillar", "pk:cult/cult_2_143", sight=True)       # столб, простенок
SLAB = P("cu_slab", "pk:cult/cult_3_042", foot=[2, 1], sight=True)   # каменный стол
COFFIN = P("cu_coffin", "pk:cult/cult_2_154", foot=[2, 1], search="grave", title="каменный гроб")
CHEST = P("cu_chest", "pk:cult/cult_2_124", search="crate", title="сундук")
CELL_BARS = P("cu_cell_bars", "pk:cult/cult_3_020", sight=True)   # решётчатая дверь клетки
VAT = P("lb_vat", "pk:wlab/wlab_1_000", sight=True)
VATS = P("lb_vats", "pk:wlab/wlab_1_002", foot=[2, 1], sight=True)
TANK = P("lb_tank", "pk:wlab/wlab_1_008", sight=True)
TANK_B = P("lb_tank_b", "pk:wlab/wlab_1_034", sight=True)
ARM = P("lb_arm", "pk:wlab/wlab_1_029", foot=[2, 1])
DESK_PC = P("lb_desk_pc", "pk:wlab/wlab_1_018", foot=[2, 1])
DESK_CHEM = P("lb_desk_chem", "pk:wlab/wlab_1_012", foot=[2, 1])
SHELF_LAB = P("lb_shelf", "pk:wlab/wlab_2_069", foot=[2, 1], sight=True, search="shelf",
              title="полка с реактивами")
CASE = P("lb_case", "pk:wlab/wlab_2_084", foot=[2, 1], search="military", title="ящик")
BED_OP = P("hp_bed", "pk:hosp/hosp_1_007", foot=[3, 1])
DRIP = P("hp_drip", "pk:hosp/hosp_1_010")
TABLE = P("cu_table", "pk:west/west_5_001", foot=[2, 1])         # стол ключника/писца
CHAIR = "chair_wood"
VENDING = P("mt_vending", "pk:motel/motel_1_002", sight=True, search="shelf", title="торговый автомат")
ICE = P("mt_ice", "pk:motel/motel_1_022", sight=True)
PLANT = P("mt_plant", "pk:motel/motel_1_063")
STAIRS = P("mt_stairs", "pk:motel/p1/4,8,2,2", foot=[2, 2], block=False, layer="floor")

STONE = cells("cult/p1", [(4, 0), (5, 0), (4, 1), (5, 1)])
DARK_WOOD = ["pk:cult/cult_f2_21", "pk:cult/cult_f2_20"]
GREY_WOOD = ["pk:cult/cult_f2_22", "pk:cult/cult_f2_23"]


# ------------------------------------------------------------ помощники ручной расстановки
def _why(m, name, x, y):
    """Почему предмет не встал — как why_not() в build_town.py и _why() в build_fifteen.py."""
    foot = m.footprint(name, x, y)
    why = []
    if any(t in m.blocked for t in foot):
        why.append("блок: " + str([t for t in foot if t in m.blocked]))
    if any(t in m.soft_obj for t in foot):
        why.append("мягкий предмет: " + str([t for t in foot if t in m.soft_obj]))
    if any(t in m.reserved for t in foot):
        why.append("резерв (проём/портал)")
    h = m.hides(name, x, y)
    if h:
        why.append(f"заслоняет {h[0]} ({h[1]}, {h[2]})")
    why.append("земля: " + "".join(m.ground[yy][xx] for xx, yy in foot))
    return f"«{name}» не встал в ({x}, {y}): " + "; ".join(why)


def _place(m, name, x, y, **kw):
    """Явная постановка: только на полу комнаты и ровно туда, куда ставили (иначе — с причиной)."""
    foot = m.footprint(name, x, y)
    assert all(m.ground[yy][xx] in m.floors for xx, yy in foot), \
        f"«{name}» в ({x}, {y}): не на полу — " + " ".join(m.ground[yy][xx] for xx, yy in foot)
    try:
        ok = m.put(name, x, y, **kw)
    except AssertionError:
        raise AssertionError(_why(m, name, x, y)) from None
    if ok and m.props[-1][1:3] == [x, y]:
        return True
    raise AssertionError(_why(m, name, x, y) + f"; встал в ({m.props[-1][1]}, {m.props[-1][2]})")


def _box(m, name, x, y, title, loot, **kw):
    try:
        return m.box(name, x, y, title, loot, **kw)
    except AssertionError:
        raise AssertionError(_why(m, name, x, y)) from None


def _wall(m, name, x, y):
    """Настенное (знамя): клетка стены, картинка висит на ней, под ней должно быть пусто."""
    assert m.ground[y][x] in m.walls, f"«{name}» в ({x}, {y}): там нет стены"
    m.props.append([name, x, y])
    m.blocked.add((x, y))
    m._reach = None


def _table(m, name, x, y, dx=0, dy=-34):
    """Мелочь на столешнице: на клетке стола, поднята на его высоту, рисуется сразу после него."""
    assert (x, y) in m.blocked, f"«{name}» в ({x}, {y}): под ним нет стола"
    m.props.append([name, x, y, dx, dy, 1 - dy])


def cwhy(name, x, y):
    return _why(cr, name, x, y)


def cplace(name, x, y, **kw):
    return _place(cr, name, x, y, **kw)


def cbox(name, x, y, title, loot, **kw):
    return _box(cr, name, x, y, title, loot, **kw)


def cwall(name, x, y):
    return _wall(cr, name, x, y)


def ctable(name, x, y, dx=0, dy=-34):
    return _table(cr, name, x, y, dx=dx, dy=dy)


# ================================================================ Крипта Единства
# Подземелье культа под молельней миссии (docs/story.md §7; журнал опытов — data/terminals.json,
# «crypt_log»). Культ приходит сюда не молиться, а делать: в купели готовят «причастие» (ВРЭ в воде
# из колонки), в кабинете записывают, что из этого вышло, в хранилище складывают приношения и «святую
# воду», в кельях держат избранных перед причастием, в кельях наказаний — тех, кто передумал,
# в склепе — тех, кто не выдержал.
#
# Планировка по смыслу, не по сетке: от лестницы (плита за алтарём молельни) попадаешь в зал обрядов;
# восточная стена зала — купель, из купели на восток кабинет опытов и на юг хранилище даров;
# из зала на юг — кельи ожидания, из них на запад кельи наказаний, на юг — склеп (самое глубокое
# место, дальше только камень). Пол 701 клетка: зал 13×11, купель 13×11, кельи 13×7, хранилище 13×7,
# кабинет 7×11, карцер 7×9, склеп 27×5 (галерея с нишами по обе стороны).
#
# Свет — только от предметов: свечи и черепа-канделябры у алтаря, огневая бочка в карцере, котёл
# с огнём в купели, фонарь на столе ключника и в руке сторожа склепа. Потолочных ламп нет (night задан
# вручную — auto_ambient в citykit.save тогда молчит): в крипте лампе на шнуре взяться неоткуда.
W, H = 39, 34
cr = CityMap(city, "baker_crypt", "Крипта Единства", W, H, start=(3, 4), seed=71, interior=True,
             music="vats", furnish=False)
cr.night = [88, 96, 108]
cr.floor_code("S", *STONE)
cr.wall_code("K", "pk:cult/cult_w1_07")       # бурый камень — весь культовый низ
cr.room(1, 1, 15, 15, "K", "S")               # зал обрядов (и спуск)
cr.room(15, 1, 29, 15, "K", "S")              # купель
cr.room(29, 1, 37, 15, "K", "S")              # кабинет опытов
cr.room(1, 15, 9, 27, "K", "S")               # кельи наказаний
cr.room(9, 15, 23, 25, "K", "S")              # кельи ожидания
cr.room(23, 15, 37, 25, "K", "S")             # хранилище даров
cr.room(1, 25, 37, 33, "K", "S")              # склеп
cr.opening(15, 6, 15, 7, "S")                 # зал -> купель
cr.opening(29, 6, 29, 7, "S")                 # купель -> кабинет
cr.opening(11, 15, 12, 17, "S")               # зал -> кельи ожидания
cr.opening(26, 15, 27, 17, "S")               # купель -> хранилище даров
cr.opening(9, 21, 9, 22, "S")                 # кельи ожидания -> кельи наказаний
cr.opening(15, 25, 16, 27, "S")               # кельи ожидания -> склеп

# ------------------------------------------------------------ зал обрядов: спуск и молитва
# Лестница встаёт на северную стену у западного угла: выходишь — и сразу видишь алтарь и весь зал
# (вход не за спинами). Плита в молельне над лестницей — (40, 21) в baker_mission, прибытие сюда —
# на клетку у подножия (3, 4).
cr.props.append(["x_ladder", 2, 4])
cr.portal([(2, 4)], "baker_mission", (40, 22), "Наверх, в молельню")
cr.reserve(2, 4, 4, 5)                        # площадка у лестницы — не заставлять
# Алтарь по оси зала, по сторонам черепа-канделябры (свет на алтарь и на солею), за спиной алтаря
# на стене — писания, а знамёна — на целых простенках, где перед ними ничего высокого не стоит.
cwall(BANNER, 4, 3)
cplace(SHELF, 5, 4)                           # писания слева от алтаря
cplace(CANDLE, 7, 4)
cplace(ALTAR, 8, 4)                           # алтарь: на нём горят свечи (свет в спрайте)
cplace(CANDLE_B, 10, 4)
cplace(SHELF_B, 11, 4)                        # писания справа
cwall(BANNER, 14, 3)
# Каменные лавки рядами по обе стороны осевого прохода (x 8–9), лицом к алтарю; между рядами проход.
for px in (2, 5, 10, 12):
    for py in (7, 10):
        cplace(PEW, px, py)
# Обетные свечи по боковым стенам и две стойки со свечами в глубине зала — чтобы зал был освещён
# целиком, а не только у алтаря.
cplace("candles", 2, 6)
cplace("candles", 14, 6)
cplace(TORCH, 4, 13)
cplace(TORCH, 11, 13)

# ------------------------------------------------------------ купель «причастия»
# Чаны стоят в ряд у северной стены — как купель в церкви, только с ВРЭ: три стеклянных чана на станине,
# два цилиндра с мутной зеленью и один чан с трубой. Механическая рука опускает «избранного» в чан;
# рядом операционный стол с капельницей. «Сплетённый» (Причастие 4 из журнала) держится в юго-восточном
# углу, у своего чана: он уже не человек, и его не приковывают.
cplace(VATS, 17, 4)                           # три чана на станине
cplace(TANK, 20, 4)
cplace(TANK_B, 22, 4)
cplace(VAT, 24, 4)
cplace(STATUE, 27, 4)                         # «Совершенный» над чанами, лицом в купель
cplace(ARM, 21, 6)                            # рука, которая опускает в чан
cplace(BED_OP, 18, 9)                         # стол, на который кладут перед причастием
cplace(DRIP, 17, 9)
cplace("x_cauldron", 25, 13)                  # котёл у южной стены: в нём греют воду для чанов (и свет)
cplace(CANDLE, 26, 6)
cplace("candles", 28, 6)
cplace("candles", 16, 5)                      # свечи у западного чана
cplace("bench_16", 16, 11)                    # скамья, где ждут очереди к столу
cplace("bucket", 16, 13)
cplace("candles", 17, 13)                      # свеча у скамьи — юго-запад купели не в темноте
cplace("pile_rags", 27, 10)                   # подстилка Сплетённого
cr.enemies += [["joined", 28, 12], ["cultist", 23, 12]]   # Сплетённый в углу, служка у стола

# ------------------------------------------------------------ кабинет опытов
# Комната Ансельма: терминал с журналом (crypt_log), стол с колбами, полка реактивов, стол с монитором
# и армейский ящик, куда складывают «дары» — то, что приносят посланники с запада.
cr.terminal(30, 4, "crypt_log")
cplace(DESK_CHEM, 32, 4)
cplace(SHELF_LAB, 35, 4)
cplace(TABLE, 31, 7)                          # рабочий стол посреди кабинета
ctable("candles", 31, 7, dx=-16, dy=-38)
cplace("w_chair_l", 33, 7)                    # стул с торца, лицом к столу (в профиль)
cplace(DESK_PC, 34, 10)
cplace("crate_b", 30, 10)                      # ящик с посудой и реактивами у западной стены
cplace("w_chair_r", 33, 10)                    # стул к столу с монитором, в профиль
cbox(CASE, 31, 12, "ящик с «дарами»", {"стимулятор": 2, "аптечка армейская": 1, "антирадин": 1})
cplace("bucket", 30, 13)
cplace("candles", 36, 12)                      # свеча у восточной стены кабинета
cr.enemies += [["radroach", 35, 8], ["radroach", 33, 13]]

# ------------------------------------------------------------ кельи ожидания
# Передняя половина — место ключника: стол у стены, фонарь, книга, стул; за ним — три ниши за прутьями,
# где ждут своей очереди. В восточной нише Оскар (Причастие 5): он ещё жив и говорит через прутья.
cplace(TABLE, 10, 22)                         # стол ключника
ctable("w_table_lantern", 10, 22, dx=-12, dy=-36)
ctable("w_newspaper", 11, 22, dy=-34)         # список имён
cplace(CHAIR, 10, 23)                         # ключник сидит лицом в комнату
cplace("bucket", 13, 23)                      # вода для узников
cplace("bench_16", 20, 23)                    # скамья для тех, кого привели на причастие
cplace("pile_rags", 21, 22)                   # их одежда и тряпьё
# Ниши вдоль северной стены: нары, прутья-простенки, ведро. Прутья — по одному на нишу, второе место
# открыто: за решёткой не запирают, её попросту не отпирают.
cplace("bed", 14, 19)
cplace("bed", 20, 19)
cplace(CELL_BARS, 14, 20)
cplace(CELL_BARS, 17, 20)
cplace(CELL_BARS, 20, 20)
cplace("bucket", 22, 19)
cplace("candles", 16, 18)                      # свечи в нишах у изголовья
cplace("candles", 21, 18)
cplace("candles", 12, 24)
cr.npcs += [["oskar", 18, 19]]                # в средней нише, за прутьями

# ------------------------------------------------------------ кельи наказаний
# Тусклая комната за кельями ожидания: два загона за решётчатыми дверями (в них умирают стоя),
# столб посреди — к нему вяжут, огневая бочка у стены — единственный свет, ведро и тряпьё.
cplace(CELL_BARS, 2, 20, check=False)         # решётка запирает загон наглухо — так и задумано
cplace(CELL_BARS, 3, 20, check=False)
cplace(CELL_BARS, 5, 20, check=False)
cplace(CELL_BARS, 6, 20, check=False)
cplace(PILLAR, 4, 20)                         # простенок между загонами
cplace(CELL_BARS, 7, 20, check=False)
cplace(CELL_BARS, 8, 20, check=False)
cplace("rag", 2, 19)                          # подстилка в загоне
cplace(SKULLS, 4, 18)                         # между загонами — черепа тех, кто не дождался
cplace(SKULLS, 6, 18)
cplace("bucket", 3, 18)
cplace("rag", 8, 19)
cplace(PILLAR, 4, 24)                         # столб, к которому вяжут
cplace("candles", 3, 24)
cplace("pile_rags", 6, 23)
cplace("x_fire_barrel", 8, 25)                # огневая бочка: свет и тепло карцера
cplace("bucket", 2, 25)

# ------------------------------------------------------------ хранилище даров
# Приношения миссии: бочки «святой воды» (той самой, со снотворным), ящики с зерном и тканью, мешки.
# У восточной стены — стол писца с фонарём и списком даров; рядом сундук с одеждой «вознесённых» —
# всё, что осталось от тех, кто ушёл в купель.
cplace("w_barrels", 29, 18)                   # бочки святой воды
cplace("crate", 32, 18)
cplace("crate_b", 34, 18)
cplace("barrel_wood", 36, 18)
cplace("barrel_wood", 25, 21)
cplace("crate_empty", 27, 21)
cplace("w_sacks", 29, 21)
cplace("w_sacks", 31, 21)
cplace(TABLE, 33, 23)                         # стол писца
ctable("w_table_lantern", 33, 23, dx=-12, dy=-36)
ctable("w_newspaper", 34, 23, dy=-34)         # книга даров
cplace(CHAIR, 33, 24)
cbox(CHEST, 36, 23, "сундук с одеждой «вознесённых»",
     {"ткань": 3, "плюшевый мишка": 1, "крышки": 15})
cplace("candles", 26, 20)
cplace("candles", 31, 18)                      # свеча у бочек со святой водой
cplace("barrel_wood", 24, 20)                   # бочки вдоль западной стены
cplace("crate", 35, 20)
cplace("w_sacks", 34, 21)

# ------------------------------------------------------------ склеп «вознесённых»
# Галерея на всю ширину крипты: в нишах вдоль северной стены лежат те, кто выдержал причастие и умер
# потом, и те, кто не выдержал сразу. Между гробами — кости без имён, на южной стороне — ещё три гроба
# и свечи. В дальнем восточном конце, отдельно от всех, — гроб без имени (в нём образец ВРЭ); на западе —
# заложенная кирпичом арка, туда уже не ходят. У восточной стены сидит сторож с фонарём: за склепом
# смотрят, хотя хоронить здесь давно некого.
for cx in (3, 8, 19, 24, 29):
    cplace(COFFIN, cx, 28)                    # гробы в нишах северной стены
cplace(BONES, 6, 28)
cplace(SKULLS, 11, 28)
cplace(BONES, 13, 28)
cplace(SKULLS, 22, 28)                        # кости в промежутках
cplace(BONES, 27, 28)
cplace(SKULLS, 32, 28)
for cx in (6, 17, 26):
    cplace(COFFIN, cx, 31)                    # вторая сторона галереи
cplace(SKULLS, 13, 31)
cplace(BONES, 28, 31)
cplace(SKULLS, 35, 31)
cplace("candles", 4, 31)
cplace(TORCH, 10, 31)                         # канделябры вдоль галереи
cplace("candles", 15, 31)
cplace(TORCH, 21, 31)
cplace("candles", 24, 31)
cplace(TORCH, 30, 31)
cplace(ARCH, 2, 30)                           # заложенный проход: дальше только камень
cbox(COFFIN, 34, 28, "гроб без имени", {"образец ВРЭ": 1, "крышки": 20})
cplace(TORCH, 33, 30)                         # канделябр сторожа — на полу у стены
cr.enemies += [["cultist", 35, 30]]           # сторож при канделябре

# ================================================================ Мотель: второй этаж
# Второй этаж «Последней мили» (docs/furnish/baker.md §4). Сначала планировка, потом мебель:
#   * коридор во всю длину этажа (4 клетки) — по нему ходят гости, двери пяти номеров в его северной стене;
#   * номера 201–205 — по северной стороне: спальня у северной стены, санузел за перегородкой в
#     юго-восточном углу (кафель, унитаз, раковина; у Холлиса и «новобрачных» ещё и ванна);
#   * южное крыло — служба: подсобка горничной (тележка, бельё, ведра), бельевая, кладовая и, у
#     восточного конца, лестничная клетка — вниз, в холл, к стойке Хэтти (портал на трассу).
# Номер 7×9 клеток: кровать у северной стены, тумбочка с лампой, шкаф, кресло, телевизор на тумбе,
# коврик, санузел 3×3. Угроза — в 204: крысиная нора; крысолюд вылез из трубы в санузел 202 и убил
# охранника каравана (его записка: «дверь держу стулом, патронов шесть» — стул у двери, тело у стены).
# Расстановка поштучная, автообстановка выключена (furnish=False). Свет — потолочные лампы на шнуре
# (движок рисует их сам) и лампы на тумбочках; night задан вручную, поэтому auto_ambient молчит.
W, H = 47, 24
mo = CityMap(city, "baker_motel_2f", "Мотель: второй этаж", W, H, start=(40, 21), seed=72,
             interior=True, music="home", furnish=False)
mo.night = [124, 112, 101]
mo.floor_code("C", "pk:cult/cult_f2_29")            # коридор и клетка — шашечный линолеум
mo.floor_code("R", *DARK_WOOD)                      # номера и бельевая — тёмные доски
mo.floor_code("T", "pk:cult/cult_f2_19")            # санузлы — белый кафель
mo.floor_code("G", *GREY_WOOD)                      # служба — серые доски
mo.wall_code("Y", "pk:motel/motel_w1_09")           # коридор — жёлтые обои в цветочек
mo.wall_code("Z", "pk:motel/motel_w2_15")           # номера — светлая штукатурка
mo.wall_code("B", "pk:motel/motel_w2_11")           # санузел — синий кафель
mo.wall_code("K", "pk:motel/motel_w2_17")           # служба — серая краска

# ------------------------------------------------------------ предметы мотеля (наборы motel/lhotel/west)
BED_D = P("mo_bed_d", "pk:lhotel/lhotel_2_009", foot=[2, 2], sight=True)       # двуспальная, кремовое бельё
BED_D_B = P("mo_bed_d_b", "pk:lhotel/lhotel_2_020", foot=[2, 2], sight=True)   # двуспальная, зелёное
BED_D_C = P("mo_bed_d_c", "pk:lhotel/lhotel_2_029", foot=[2, 2], sight=True)   # двуспальная, синее
BED_S = P("mo_bed_s", "pk:motel/motel_4_010", foot=[1, 2], sight=True)         # односпальная, кремовая
BED_S_B = P("mo_bed_s_b", "pk:motel/motel_4_011", foot=[1, 2], sight=True)     # односпальная, синяя
STAND = P("mo_stand", "pk:motel/motel_4_000", search="drawer", title="тумбочка")
STAND_B = P("mo_stand_b", "pk:motel/motel_4_027", search="drawer", title="тумбочка")
CHEST3 = P("mo_chest", "pk:motel/motel_4_051", search="drawer", title="комод")
WARD = P("mo_wardrobe", "pk:motel/motel_4_004", sight=True, search="cloth", title="шкаф")
WARD_B = P("mo_wardrobe_b", "pk:motel/motel_4_007", sight=True, search="cloth", title="шкаф")
TV = P("mo_tv", "pk:motel/motel_4_024", foot=[2, 1], sight=True)               # телевизор на тумбе
TV_B = P("mo_tv_b", "pk:motel/motel_4_075", foot=[2, 1], sight=True)           # телевизор на комоде
DESK = P("mo_desk", "pk:motel/motel_4_022", foot=[2, 1])                      # письменный стол
SIDE = P("mo_side_table", "pk:motel/motel_4_088")                            # низкий столик
CHAIR = P("mo_chair", "pk:motel/motel_4_017")
CHAIR_B = P("mo_chair_b", "pk:motel/motel_4_041")
ARM = P("mo_armchair", "pk:lhotel/lhotel_2_016")
ARM_B = P("mo_armchair_b", "pk:lhotel/lhotel_2_017")
TOILET = P("mo_toilet", "pk:motel/motel_5_000", sight=True)
SINK = P("mo_sink", "pk:hotel/hotel_1_095")                            # настенная раковина
TUB = P("mo_bathtub", "pk:west/west_2_023", foot=[2, 1], sight=True)
MIRROR = P("mo_mirror", "pk:west/west_2_028", block=False)
DOOR = P("mo_door", "pk:motel/motel_1_007", block=False, scale=1.06)      # створка: 1,48 клетки в высоту
DOOR_B = P("mo_door_b", "pk:motel/motel_1_010", block=False, scale=1.06)
MAT = P("mo_mat", "pk:motel/motel_1_065", block=False)                        # половичок у двери
CART = P("mo_cart", "pk:lhotel/lhotel_1_015", search="shelf", title="тележка горничной")
LUGGAGE = P("mo_luggage", "pk:lhotel/lhotel_1_008", search="bag", title="чемодан")
RADIO = P("mo_radio", "pk:jtown/jtown_5_019")
TV_SM = P("mo_tv_sm", "pk:jtown/jtown_5_040")
AC = P("mo_ac", "pk:motel/motel_1_032", block=False)                         # кондиционер под потолком
TRASH = P("mo_trash", "pk:motel/motel_1_023")
PLANT = P("mo_plant", "pk:motel/motel_1_063")
BENCH = P("mo_bench", "pk:west/west_2_015", foot=[2, 1])
SHELF = P("mo_shelf", "pk:west/west_2_106", foot=[2, 1], sight=True, search="cloth", title="полка с бельём")
LOCKER = P("mo_locker", "pk:west/west_5_007", search="locker", title="шкафчик горничной")


def mput(name, x, y, **kw):
    return _place(mo, name, x, y, **kw)


def mbox(name, x, y, title, loot, **kw):
    return _box(mo, name, x, y, title, loot, **kw)


def mtable(name, x, y, dx=0, dy=-32):
    return _table(mo, name, x, y, dx=dx, dy=dy)


def mwall(name, x, y, dy=0):
    """Настенное на клетке стены: часы, зеркало над раковиной (картинка висит на стене)."""
    assert mo.ground[y][x] in mo.walls, f"«{name}» в ({x}, {y}): там нет стены"
    mo.props.append([name, x, y, 0, dy])
    mo.blocked.add((x, y))


def mbath(x0, mirror_x=None):
    """Санузел номера: кафельная клетка 3×3 в юго-восточном углу, дверь — в западной стене.

    Север — перегородка, запад — стена с одним проёмом на высоте ручки, восток и юг — стены номера.
    Кафель в три ряда (нижний скрыт фасадом южной стены), над раковиной зеркало, под потолком лампочка.
    """
    mo.paint("Z", x0 + 4, 9, x0 + 7, 9)             # перегородка — настоящая стена, не плитка на полу
    mo.paint("Z", x0 + 4, 10, x0 + 4, 10)           # западная стена над дверью
    mo.paint("Z", x0 + 4, 12, x0 + 4, 12)           # западная стена под дверью
    mo.paint("T", x0 + 5, 10, x0 + 7, 12)           # кафельный пол
    mo.paint("T", x0 + 4, 11, x0 + 4, 11)           # порог
    mo.reserve(x0 + 4, 10, x0 + 4, 12)              # в дверях и на стенах ничего не ставить
    mo.ceiling(x0 + 6, 10, r=105, color=(255, 214, 168), flick=0.02)


# ------------------------------------------------------------ стены и полы
X0 = (1, 10, 19, 28, 37)                            # левые стены пяти номеров (9 клеток на номер)
for x0 in X0:
    mo.room(x0, 1, x0 + 8, 13, "Z", "R")            # северная стена в три ряда, южная — в один
# коридор: 4 клетки между номерами и службой, стены — обои Y
mo.paint("Y", 1, 14, 45, 18)
mo.paint("C", 2, 14, 44, 17)
# южное крыло: подсобка, бельевая, кладовая, лестничная клетка
mo.paint("K", 1, 19, 45, 23)
mo.paint("G", 2, 19, 9, 22)                         # подсобка горничной
mo.paint("R", 11, 19, 20, 22)                       # бельевая
mo.paint("G", 22, 19, 33, 22)                       # кладовая
mo.paint("C", 35, 19, 44, 22)                       # лестничная клетка
mo.paint("C", 35, 18, 40, 18)                       # из коридора в клетку — широкий проём
for x0 in X0:                                       # дверь номера — в южной стене, не за спинами
    mo.opening(x0 + 3, 13, x0 + 3, 13, "R")
mo.opening(4, 18, 4, 18, "G")                       # подсобка горничной
mo.opening(15, 18, 15, 18, "R")                     # бельевая
mo.opening(27, 18, 27, 18, "G")                     # кладовая

# ------------------------------------------------------------ лестница вниз, в холл
# Лестница (2×2) стоит у восточной стены клетки, площадка перед ней свободна: портал — на клетке
# у подножия (43, 21), ровно там, куда встаёт игрок; прибытие из холла — рядом, (42, 21).
mo.props.append([STAIRS, 43, 19])
mo.portal([(43, 21)], "baker", (79, 17), "Вниз, в холл")
mo.reserve(40, 18, 44, 22)                          # площадку у лестницы не заставлять

# ------------------------------------------------------------ 201 — семья прячется от культа
# Мать, сын и «вернувшийся» отец: две кровати, детская койка, чемодан, который так и не распаковали.
mput(WARD, 2, 4)                                    # шкаф семьи — в северо-западном углу
mput(BED_D, 4, 4)                                   # двуспальная: мать и отец
mput(STAND, 6, 4)                                   # тумбочка между кроватью и телевизором
mtable("w_table_lamp", 6, 4, dy=-34)                # лампа на тумбочке — своё пятно света
mput(TV, 7, 4)                                      # телевизор на тумбе у северной стены
mput(BED_S, 2, 6)                                   # детская койка вдоль западной стены
mput("w_rug_red", 6, 6)                             # ковёр посреди номера
mput(ARM, 2, 9)                                     # кресло в юго-западном углу
mput(SIDE, 3, 9)                                    # столик рядом с креслом
mtable("w_newspaper", 3, 9, dy=-24)                 # на столике — старый номер
mput("bag", 2, 11)                                  # дорожная сумка у западной стены (тележка носильщика — не в номер)
mbath(1)                                            # санузел: кафель, перегородка, дверь
mput(TOILET, 8, 10)
mput(SINK, 7, 10)
mput("bucket", 8, 12)                               # ведро под раковиной
mo.npcs += [["motel_mom", 5, 7], ["motel_kid", 7, 7]]

# ------------------------------------------------------------ 202 — мёртвый охранник каравана
# Он подпёр дверь стулом и отстреливался: стул у двери, тело у восточной стены, патронташ.
# Пришло не через дверь — крысолюд вылез из трубы в санузле (нора — в 204).
mput(BED_S_B, 11, 4)                                # койка, не убрана
mbox(STAND, 12, 4, "тумбочка охранника", {"патроны": 3, "бинт": 1, "жетон солдата": 1})
mput(WARD, 16, 4)                                   # шкаф у восточной стены
mput(CHAIR_B, 12, 12)                               # тот самый стул, которым он подпёр дверь — у самой двери
mput("table_upside", 15, 8)                         # опрокинутый стол — след драки
mbox("r_bones", 17, 7, "тело охранника", {"дробь": 6, "жетон солдата": 1, "записка охранника": 1})
mput("ammo_box", 16, 7)                             # патронташ
mo.maybe("x_vd_blood0", 17, 8, check=False, allow_reserved=True)     # кровь под телом
mo.maybe("x_vd_blood1", 16, 8, check=False, allow_reserved=True)
mbath(10)                                           # санузел — тут нора и вылезли
mput(TOILET, 17, 10)
mput(SINK, 16, 10)

# ------------------------------------------------------------ 203 — номер Холлиса
# Он живёт здесь давно: письменный стол с бумагами, запертый сундук, кресло, комод, ванна.
mput(WARD_B, 20, 4)
mput(BED_D_C, 22, 4)
mput(STAND_B, 24, 4)
mtable("w_table_lamp", 24, 4, dy=-34)
mtable(RADIO, 24, 4, dx=8, dy=-16)                  # радио на тумбочке
mput(TV, 25, 4)
mput(DESK, 25, 7)                                   # стол у восточной стены
mtable("w_table_lantern", 25, 7, dx=-10, dy=-38)    # фонарь на столе
mtable("w_newspaper", 26, 7, dx=6, dy=-34)          # бумаги
mput(CHAIR, 25, 6)                                  # стул с торца, лицом к столу
mput(ARM_B, 20, 7)                                  # кресло у западной стены
mput("bk_rug_b", 22, 7)                             # ковёр посреди номера
mput("bag", 20, 9)                                  # его сумка
mbox("metal_chest", 20, 10, "сундук Холлиса",
     {"шифроблокнот Анклава": 1, "крышки": 90, "стимулятор": 1},
     requires={"item": "отмычка", "msg": "Сундук на хорошем замке, такие возят издалека. Нужна отмычка."})
mbath(19, mirror_x=26)                              # санузел с ванной
mput(TUB, 24, 10)                                   # ванна вдоль перегородки
mput(SINK, 26, 10)
mput(TOILET, 25, 11)

# ------------------------------------------------------------ 204 — крысиная нора (угроза)
# Крысолюд и крысы: голый каркас кровати, изгрызенный чемодан, тряпьё, нора в стене санузла.
mput("bed_frame", 29, 4)                            # каркас без матраса
mput(WARD, 35, 4)                                   # шкаф с сорванной дверцей
mput("bag", 30, 7)                                  # изгрызенная сумка
mput("pile_rags", 34, 7)
mput("r_planks", 33, 8)                             # доски, выломанные из стены
mput("r_rocks", 31, 8)                              # штукатурка
mbath(28)                                           # санузел — сама нора
mput(TOILET, 35, 10)                                # унитаз, из которого лезут
mput("pile_rags", 33, 12)                           # тряпьё у норы, не на пороге санузла
mo.maybe("x_vd_blood1", 34, 12, check=False, allow_reserved=True)
mo.enemies += [["ratman", 34, 10], ["rat", 31, 6], ["rat", 30, 10], ["rat", 32, 9]]

# ------------------------------------------------------------ 205 — номер новобрачных
# Потолок тут обещали починить «к утру» ещё в тот год: балки и штукатурка на полу, кровать, шкаф с
# фотографией, уцелевшее кресло, ковёр, который постелили к первой ночи.
mbox("wardrobe", 38, 4, "шкаф в номере для новобрачных",
     {"сигареты": 2, "свадебная фотография": 1, "крышки": 25})
mput(BED_D_B, 40, 4)
mput(STAND, 42, 4)
mtable("w_table_lamp", 42, 4, dy=-34)
mput("bk_rug_c", 41, 7)                             # ковёр первой ночи
mput("r_rocks", 43, 8)                              # штукатурка и балки с потолка — в углу
mput("r_planks", 39, 9)                             # доски у стены
mput(ARM, 44, 6)                                    # кресло у окна
mput("pile_rags", 39, 7)
mo.enemies += [["radroach", 41, 10]]
mbath(37, mirror_x=44)                              # санузел с ванной
mput(TUB, 42, 10)
mput(SINK, 44, 10)
mput(TOILET, 43, 11)

# ------------------------------------------------------------ коридор
for x0 in X0:                                       # створки в проёмах и половички снаружи
    mo.props.append([DOOR, x0 + 3, 13])
    mo.props.append([MAT, x0 + 3, 14])
mput(PLANT, 2, 14)                                  # кадка в западном конце коридора
mput("mt_ice", 7, 14)                               # ледогенератор между дверями 201 и 202
mput("mt_vending", 11, 14)                          # автомат с едой
mput(BENCH, 18, 14)                                 # скамья у стены, где ждут
mput(PLANT, 29, 14)                                 # кадка в восточном конце
mwall("bk_clock", 26, 13)                           # часы на стене коридора
mput(TRASH, 20, 16)                                 # урна у южной стены
mput("x_fireext", 44, 16)                           # огнетушитель у лестницы

# ------------------------------------------------------------ служба: подсобка горничной
mput(SHELF, 2, 19)                                  # полка с чистым бельём
mput(CART, 2, 20)                                   # тележка горничной (в ней бельё)
mput(LOCKER, 5, 19)                                 # шкафчик горничной
mput("sink", 7, 19)                                 # мойка в углу у двери
mput("bucket", 6, 22)                               # ведро
mput("w_sacks", 3, 22)                              # мешок со стиркой
mput("crate_empty", 2, 22)                          # ящик из-под мыла и ветоши
mput("rag", 4, 21)                                  # грязная простыня на полу

# ------------------------------------------------------------ служба: бельевая
mput(SHELF, 11, 19)                                 # стеллажи с бельём вдоль северной стены
mput(SHELF, 17, 19)
mput(SHELF, 19, 19)
mput(SIDE, 13, 21)                                  # стол, где складывают бельё
mtable("w_newspaper", 13, 21, dy=-26)               # опись белья
mput(CART, 20, 20)                                  # вторая тележка
mput("crate_b", 12, 22)                             # ящик с мылом
mput("w_sacks", 19, 22)                             # мешок с грязным

# ------------------------------------------------------------ служба: кладовая
mput(WARD, 22, 19)                                  # старый шкаф
mput("crate_b", 24, 19)                             # ящики и коробки
mput("crate", 26, 19)
mput("crate_empty", 28, 19)
mput(LUGGAGE, 31, 20)                               # чей-то забытый чемодан
mput(CHAIR_B, 24, 21)                               # сломанный стул
mput("barrel_wood", 33, 21)                         # бочка (в ней что-то плещется)
mput("w_sacks", 30, 22)
mput("pile_rags", 26, 22)

# ------------------------------------------------------------ служба: лестничная клетка
mput(PLANT, 35, 19)                                 # кадка на площадке
mput("x_fireext", 35, 21)                           # огнетушитель
mput(BENCH, 38, 21)                                 # скамья: тут ждут такси и курят

# ------------------------------------------------------------ свет
for x0 in X0:                                       # по лампе на шнуре в каждом номере
    mo.ceiling(x0 + 4, 7, r=185, color=(255, 196, 122), flick=0.03)   # посреди номера, не над кроватью
for cx in (4, 12, 20, 28, 36):                      # коридор — через пролёт
    mo.ceiling(cx, 15, r=165, color=(255, 196, 130), flick=0.02)
for cx in (5, 15, 27, 40):                          # служба и лестничная клетка
    mo.ceiling(cx, 20, r=155, color=(255, 190, 118), flick=0.05)

city.save(gap_exempt=("oskar", "motel_mom", "motel_kid"))
