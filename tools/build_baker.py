"""
Генератор Бейкера — вторая глава. Город ночной (src/lighting.py) и разбит на три района,
каждый — своя карта, переходы — порталы на дорогах (как районы Нью-Рено в Fallout 2):

  data/maps/baker.json           «Бейкер: трасса» (112×75) — сюда приходят с карты мира.
      Трасса I-15 с запада на восток, фонари и остовы машин по обочинам, блокпост культа у
      въезда; закусочная «Безумный грек» (Ник, пьющий брат Тобиас), площадь с Термометром,
      мотель «Последняя миля» (староста Хэтти), дом Роя, гараж. Дорога на север — к миссии,
      на юг — на окраину.
  data/maps/baker_mission.json   «Бейкер: миссия» (70×50). Миссия «Детей Единства» за
      кирпичной оградой: молельня (брат Ансельм, сканер), кельи за решёткой (дед Эймос),
      трапезная (послушники, Марла), дом Ансельма (книга даров), кладбище «вознесённых».
      Ворота на юг, к дороге; калитка на север — в дюны, куда ведёт тропа вдоль западной стены.
  data/maps/baker_outskirts.json «Бейкер: окраина» (76×52). Лачуги и палатки у костров,
      свалка машин со «скупщиком» Холлисом, водонапорная башня, бункер склада «Бейкер-7».

Кто появляется по ходу сюжета (Лира, Панк, Сайлас, Шрам, дед у склада, Искра, Марла у Роя),
ставит src/game/baker.py.

Запуск из папки game_project:  .venv/bin/python tools/build_baker.py
"""
from mapkit import MapKit, WALLS_INTACT, BENCHES, STONES, GRASS, BUSHES
from citykit import City, _cells
from src import props as _props

city = City("baker", "Бейкер")      # реестр объектов из наборов (town50, motel, apark): data/props/baker.json


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def stamp(m, name, img, x, y):
    """Плоский кусок набора на земле (ковёр, плита) — как CityMap.stamp, но для карты на MapKit."""
    city.prop(name, img, block=False, layer="floor", foot=_cells(img))
    m.props.append([name, x, y])


# ---- 1950-е у шоссе: цветные седаны, неон, колонки, будки — тот же набор, что и в Примме
CARS50 = [P(f"bk_car{i}", f"pk:town50/town50_1_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((29, 37, 45, 53, 41, 40))]
PUMPS = [P("bk_pump_red", "pk:town50/town50_1_102", foot=[1, 1]), P("bk_pump_yellow", "pk:town50/town50_1_103", foot=[1, 1])]
SIGN_DINER = P("bk_sign_diner", "pk:town50/town50_1_116", foot=[1, 1], sight=True, light={"r": 130, "color": [255, 90, 90], "at": [0.5, 0.4], "flicker": 0.4})
SIGN_MOTEL = P("bk_sign_motel_big", "pk:motel/motel_1_057", foot=[1, 1], sight=True, light={"r": 150, "color": [110, 200, 255], "at": [0.5, 0.4], "flicker": 0.2})
# придорожный указатель «МОТЕЛЬ» со стрелкой вправо (town50_1_117). Раньше звался bk_sign_gas — на картинке
# не «GAS», а стрелка с надписью MOTEL: это указатель на мотель, а не вывеска заправки.
SIGN_ARROW = P("bk_sign_motel_arrow", "pk:town50/town50_1_117", foot=[1, 1], sight=True, light={"r": 130, "color": [255, 120, 110], "at": [0.5, 0.4], "flicker": 0.3})
PHONE = P("bk_phone", "pk:town50/town50_1_100", foot=[1, 1])
HYDRANT = P("bk_hydrant", "pk:town50/town50_1_109", block=False)
LAMP50 = P("bk_lamp", "pk:town50/town50_1_120", light={"r": 150, "color": [255, 210, 140], "at": [0.5, 0.1]})
PICKET = P("bk_picket", "pk:town50/town50_1_135", foot=[2, 1], keybg=True)
JUKE = P("bk_jukebox", "pk:town50/town50_1_084", foot=[1, 1], sight=True, light={"r": 90, "color": [255, 170, 90], "at": [0.5, 0.4], "flicker": 0.2})
DINER_BAR = P("bk_diner_bar", "pk:town50/town50_1_097", foot=[4, 1], sight=True)
BENCH50 = P("bk_bench", "pk:town50/town50_1_130", foot=[1, 1], keybg=True)
ICE = P("bk_ice", "pk:motel/motel_1_022", foot=[1, 1], sight=True, light={"r": 70, "color": [150, 220, 255], "at": [0.5, 0.4]})
VEND = P("bk_vending", "pk:motel/motel_1_002", foot=[1, 1], sight=True, light={"r": 80, "color": [255, 210, 120], "at": [0.5, 0.4]})
PLANT_POT = [P("bk_pot_a", "pk:town50/town50_1_133", foot=[1, 1]), P("bk_pot_b", "pk:town50/town50_1_134", foot=[1, 1])]
P("bk_pot_c", "pk:bazaar/bazaar_3_206", foot=[1, 1], sight=True)      # папоротник в кадке — для холлов
SOFA_B = [P("bk_sofa_a", "pk:lhotel/lhotel_1_022", foot=[2, 1]), P("bk_sofa_b", "pk:lhotel/lhotel_1_024", foot=[2, 1])]
CLOCK_B = P("bk_clock", "pk:west/west_2_019", block=False)
TRASH50 = P("bk_trash", "pk:town50/town50_1_131", foot=[1, 1])
DOOR = P("bk_door", "pk:west/p2/12,6,1,2", block=False, layer="floor")
STONE_PLAZA = ["pk:apark/p2/8,0,1,1", "pk:apark/p2/9,0,1,1", "pk:apark/p2/8,1,1,1", "pk:apark/p2/9,1,1,1"]
SIDEWALK = ["pk:zcity/zcity_f1_22"]
EARTH = ["noise:pk:rvill/p2/0,11,1,1"]                 # тёплая утоптанная глина без сетки
CONCRETE_N = ["noise:pk:zcity/zcity_f3_10"]
SAND_B = ["pk:destown/p2/0,0,1,1", "pk:destown/p2/1,0,1,1", "pk:destown/p2/0,1,1,1"]       # тёплый жёлтый песок — Бейкер у Мохаве, а не снежная равнина
DINER_FL = ["pk:zcity/zcity_f3_00"]                  # шахматная плитка закусочной
MOTEL_FL = ["pk:hotel/hotel_f1_03"]                  # светлый ковёр вестибюля
WOOD_FL = ["pk:zcity/zcity_f1_00"]                   # доски в доме Роя
FLOORS_TOWN = {"T": DINER_FL, "R": MOTEL_FL, "W": WOOD_FL, "d": SAND_B, "q": STONE_PLAZA, "u": SIDEWALK, "E": EARTH, "Z": CONCRETE_N}
INDOOR_FLOOR = set("cRWT")          # пол зданий: рассев пустыни сюда не идёт (см. desert)
WELL = P("bk_well", "pk:desnat/desnat_3_006", foot=[2, 1])
BANNER = [P("bk_banner_a", "pk:cult/cult_2_141", block=False), P("bk_banner_b", "pk:cult/cult_2_142", block=False)]
PRAYER_RUG = "pk:lhotel/p2/10,12,2,2"
LAUNDRY = P("bk_laundry", "pk:wfarm/p3/0,0,4,3", foot=[4, 1], keybg=True)
GARDEN_BED = [P("bk_bed_a", "pk:wfarm/p1/0,8,2,2", foot=[2, 1], keybg=True), P("bk_bed_b", "pk:wfarm/p1/2,8,2,2", foot=[2, 1], keybg=True)]
CAMP_FIRE = "campfire"

# ---- приёмная мотеля «Последняя миля»: набор lhotel — та же мебель, что диваны у стены в холле
# (в других наборах стойки приёма нет). Стойка с креслом за ней, ключница-ячейки на стену за Хэтти,
# багажная тележка у стойки, уголок ожидания: диван, два кресла в профиль, журнальный столик.
DESK = P("bk_desk", "pk:lhotel/lhotel_1_014", foot=[2, 1], sight=True)
KEYBOX = P("bk_keybox", "pk:lhotel/lhotel_1_031", block=False)
TROLLEY = P("bk_trolley", "pk:lhotel/lhotel_1_015", foot=[1, 1])
ARMCHAIR_L = P("bk_armchair_l", "pk:lhotel/lhotel_1_026", foot=[1, 1])        # в профиль, лицом влево
ARMCHAIR_R = P("bk_armchair_r", "pk:lhotel/lhotel_1_046", foot=[1, 1])        # лицом вправо
SOFA_C = P("bk_sofa_c", "pk:lhotel/lhotel_1_041", foot=[2, 1])                # диван на два места
COFFEE = P("bk_coffee_table", "pk:lhotel/lhotel_1_052", foot=[1, 1])
FLOOR_LAMP = P("bk_floor_lamp", "pk:lhotel/lhotel_1_043", foot=[1, 1],
               light={"r": 110, "color": [255, 214, 150], "at": [0.5, 0.12]})

# ---- огород Роя: грядки РАЗНЫЕ (в наборе wfarm их полтора десятка; один вид на все пять — каша)
BEDS = [P("bk_bed_a", "pk:wfarm/p1/0,8,2,2", foot=[2, 1], keybg=True),      # дощатый короб с капустой
        P("bk_bed_b", "pk:wfarm/p1/2,8,2,2", foot=[2, 1], keybg=True),      # он же, с зеленью
        P("bk_bed_c", "pk:wfarm/wfarm_1_045", foot=[2, 1]),                 # длинный короб с рассадой
        P("bk_bed_d", "pk:wfarm/wfarm_1_046", foot=[2, 1]),                 # он же, с цветами
        P("bk_bed_e", "pk:wfarm/wfarm_1_053", foot=[2, 1]),                 # квадратная грядка, зелень рядами
        P("bk_bed_f", "pk:wfarm/wfarm_1_080", foot=[2, 1]),                 # грядка с высокими растениями
        P("bk_bed_g", "pk:wfarm/wfarm_1_033", foot=[2, 1])]                 # низкий короб, только капуста
FENCE = P("bk_fence", "pk:west/west_1_013", foot=[2, 1])                   # жердевой забор, 2 клетки
FENCE_V = P("bk_fence_v", "pk:west/west_1_015", foot=[1, 1])               # он же, уходящий в глубину
FENCE_C = P("bk_fence_c", "pk:west/west_1_014", foot=[1, 1])               # угол забора

# ---- 1950-е внутри: стойка закусочной и приёмной мотеля (в масштабе героя: 4 клетки, по грудь)
BAR50 = P("bc_bar", "pk:lhotel/lhotel_1_012", foot=[4, 1], sight=True)

NIGHT = [118, 108, 146]     # цвет ночной темноты — светлее прежнего и теплее: город ночной, но читается
TINT = [255, 238, 206]      # песок пожелтее
DRY = ["r_dry_bush"] + BUSHES   # у сухой травы «War ruins» под картинкой квадрат песка — не берём
TREES = [f"r_dtree_{c}" for c in "abcdefg"]
TABLES = ["round_table_42", "round_table_45", "round_table_58"]
STOOLS = ["stool_round_41", "stool_round_55", "stool_round_56"]


def desert(m, x0, y0, x1, y1, trees=10, bushes=24, junk=12):
    """Пустыня вокруг: сухие деревья, кусты, камни, кости, мусор.
    На пол зданий рассев не идёт: куртины grow() гуляют от центра на ±2 клетки и раньше заносили
    куст в холл мотеля. Пока пустыня сеется, put отказывает на полу дома (логика.md §2а)."""
    real_put = m.put

    def put_out(name, x, y, *a, **kw):
        if 0 <= y < m.H and 0 <= x < m.W and m.ground[y][x] in INDOOR_FLOOR:
            return False
        return real_put(name, x, y, *a, **kw)

    m.put = put_out
    try:
        for _ in range(trees):
            m.put(m.rnd.choice(TREES), m.rnd.randint(x0, x1), m.rnd.randint(y0, y1))
        m.grow(x0, y0, x1, y1, bushes, DRY)
        m.grow(x0, y0, x1, y1, bushes // 4, DRY + GRASS[:4])
        m.scatter(["r_rocks", "r_bones", "r_trash"] + STONES, x0, y0, x1, y1, junk)
    finally:
        del m.put


def save(m, path, gates=(), exempt=(), floors=None, **extra):
    gate_tiles = [t for g in gates for t in m.footprint(*m.props[g["prop"]])]
    reach = m.check(passable=gate_tiles, gap_exempt=exempt)
    m.save(path, tint=TINT, night=NIGHT, gates=list(gates), **({"floors": floors} if floors else {}), **extra)
    print(f"{path}: {m.W}×{m.H}, объектов {len(m.props)}, обыскиваемых {len(m.containers)}, "
          f"врагов {len(m.enemies)}, NPC {len(m.npcs)}; доступно клеток {len(reach)}")


# ================================================================ 1. Трасса
# «Бейкер: трасса» — улица города. Уличная карта по решению автора выросла ×1.56 по каждой стороне
# (docs/furnish_guide.md «Масштаб»): 72×48 → 112×75. Планировка не растянута, а перестроена по смыслу
# (docs/furnish/logic.md §1), обстановка — поштучная: place / pbox / ptable / swall, автообстановки и
# scatter посреди площадок нет. План зон и сценки — docs/furnish/baker.md.
#
# С севера на юг: задворки и пустошь → квартал у трассы (закусочная «Безумный грек» на западе,
# площадь с Термометром в центре, мотель «Последняя миля» на востоке) → трасса I-15 y=41..44 с
# тротуарами и блокпостом культа у западного въезда → южнее дом Роя с огородом (запад), двор
# караванщиков (центр), гараж (восток). Дорога x=52..55: на север — к миссии, на юг — на окраину.
W, H = 112, 75
ROAD = (41, 44)                       # I-15: асфальт 41..44, тротуары 40 и 45
NR = (52, 55)                         # дорога на север (к миссии) и на юг (на окраину)
t = MapKit(W, H, start=(4, 42), seed=21)
put, box, terminal = t.put, t.box, t.terminal
t.exits = [(0, y) for y in range(ROAD[0], ROAD[1] + 1)] + [(W - 1, y) for y in range(ROAD[0], ROAD[1] + 1)]
LIGHTS = []                           # потолочные лампы помещений: [x, y, радиус, цвет, мерцание] в пикселях


# ------------------------------------------------------------ помощники ручной расстановки
# Те же, что в tools/build_station.py: явно поставленный предмет обязан встать и остаться там, куда
# его поставили; не встал — ошибка с причиной («блок», «мягкий предмет», «резерв», «заслоняет»).
def pwhy(name, x, y, blocked=None, soft=None, reserved=None):
    """Почему предмет не встал — как why_not() в build_town.py."""
    foot = t.footprint(name, x, y)
    blocked = t.blocked if blocked is None else blocked
    soft = t.soft_obj if soft is None else soft
    reserved = t.reserved if reserved is None else reserved
    why = []
    if any(c in blocked for c in foot):
        why.append("блок: " + str([c for c in foot if c in blocked]))
    if any(c in soft for c in foot):
        why.append("мягкий предмет: " + str([c for c in foot if c in soft]))
    if any(c in reserved for c in foot):
        why.append("резерв")
    h = t.hides(name, x, y)
    if h:
        why.append(f"заслоняет {h[0]} ({h[1]}, {h[2]})")
    why.append("земля: " + "".join(t.ground[b][a] for a, b in foot))
    return f"«{name}» не встал в ({x}, {y}): " + "; ".join(why)


def _undo(snap):
    """Неудачная попытка не оставляет следов: предмет, его клетки и контейнер убираются."""
    n_props, n_conts, blocked, soft_obj, reserved = snap
    del t.props[n_props:], t.containers[n_conts:]
    t.blocked, t.soft_obj, t.reserved = blocked, soft_obj, reserved
    t._reach = None


def place(name, x, y, **kw):
    """Явная расстановка: предмет обязан встать и остаться там, куда его поставили (logic.md §2)."""
    snap = (len(t.props), len(t.containers), set(t.blocked), set(t.soft_obj), set(t.reserved))
    ok = t.put(name, x, y, **kw)
    if ok and t.props[-1][1:3] == [x, y]:
        return True
    why = pwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
    _undo(snap)
    raise AssertionError(why)


def pbox(name, x, y, title, loot, **kw):
    """Ящик с нужной добычей — как place(): не встал, так с причиной."""
    snap = (len(t.props), len(t.containers), set(t.blocked), set(t.soft_obj), set(t.reserved))
    try:
        t.box(name, x, y, title, loot, **kw)
    except AssertionError:
        why = pwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
        _undo(snap)
        raise AssertionError(why) from None
    if t.props[-1][1:3] == [x, y]:
        return True
    moved = t.props[-1][1:3]
    _undo(snap)
    raise AssertionError(pwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
                         + f"; встал в ({moved[0]}, {moved[1]})")


def oskin(name, x, y):
    """Мелочь на полу (пятно масла, лопата): не блокирует, но и в стену не лезет."""
    if not t.put(name, x, y, check=False) or t.props[-1][1:3] != [x, y]:
        raise AssertionError(pwhy(name, x, y))


def ptable(name, x, y, dx=0, dy=-34):
    """Мелочь на столешнице: на клетке мебели, поднята на её высоту и в глубину — не у переднего края
    (замечание автора 24.10), рисуется сразу после стола (6-й элемент — порядок отрисовки)."""
    assert (x, y) in t.blocked, f"«{name}» в ({x}, {y}): под ним нет стола"
    t.props.append([name, x, y, dx, dy, 1 - dy])


def swall(name, x, y0, dx=0, dy=-40):
    """Настенное — только на целой стене: ставится на ряд стены-пропа и поднимается так, чтобы висеть на
    фасаде (logic.md §2а). Где стены нет (проём ворот) — падает со счётом."""
    fw, fh = _props.info(name)["foot"]
    cells = [(x + i, y0 + j) for i in range(fw) for j in range(fh)]
    assert all(c in t.blocked for c in cells), f"«{name}» в ({x}, {y0}): там нет целой стены"
    t.props.append([name, x, y0 + 1, dx, dy])
    t.soft_obj.add((x, y0 + 1))       # на клетке под настенным ничего не ставим
    t._reach = None


def lamp(x, y, r=130, color=(255, 176, 96), flick=0.03):
    """Лампа под потолком (без картинки): пятно света на полу. Пока крыша на месте, снаружи не видно."""
    LIGHTS.append([x * 48 + 24, y * 48 + 24, r, list(color), flick])


def npc(nid, x, y):
    """Житель стоит там, где стоит: клетка свободна."""
    assert (x, y) not in t.blocked, f"NPC {nid} в ({x}, {y}) — клетка занята"
    t.npcs.append([nid, x, y])
    t.reserve(x, y, x, y)


def enemy(kind, x, y):
    assert (x, y) not in t.blocked, f"{kind} в ({x}, {y}) — клетка занята"
    t.enemies.append([kind, x, y])
    t.reserve(x, y, x, y)


def board(x, y):
    """Доска объявлений = терминал doc:doc_baker_board (сюжетный, не удалять)."""
    place("x_board", x, y)
    t.terminals.append({"prop": len(t.props) - 1, "id": "doc:doc_baker_board"})


# ------------------------------------------------------------ земля: участки, трасса, тротуары
# Пятен-клякс на земле нет: где земля истоптана, она истоптана по делу — дворы, стоянки, площадь.
t.paint_ragged("Z", 1, 26, 29, 39, depth=1)          # стоянка у закусочной — бетон с рваным краем
t.paint_ragged("Z", 57, 26, 100, 39, depth=1)        # стоянка у мотеля
t.paint_ragged("q", 31, 9, 50, 38, depth=2)          # площадь у Термометра — каменные плиты
t.paint("q", 36, 39, 41, 39)                         # сход с тротуара на площадь
t.paint_ragged("E", 2, 47, 25, 67, depth=2)          # двор Роя: утоптанная глина, огород
t.paint_ragged("E", 27, 47, 50, 66, depth=2)         # двор караванщиков
t.paint("Z", 56, 46, 81, 49)                         # бетонный въезд в гараж — до самых ворот
t.paint_ragged("Z", 56, 65, 81, 70, depth=2)         # задворки гаража
# Дороги — последними: они проходят поверх площадок, иначе бетон ложится на асфальт.
t.paint("u", 0, ROAD[0] - 1, W - 1, ROAD[0] - 1)     # северный тротуар
t.paint("u", 0, ROAD[1] + 1, W - 1, ROAD[1] + 1)     # южный
t.paint("a", 0, ROAD[0], W - 1, ROAD[1])             # трасса I-15
for x in range(0, W, 6):                             # прерывистая разметка по оси
    t.ground[ROAD[0] + 1][x] = t.ground[ROAD[0] + 1][x + 1] = "h"
t.paint("a", NR[0], 0, NR[1], ROAD[0] - 2)           # на север — к миссии
t.paint("a", NR[0], ROAD[1] + 2, NR[1], H - 1)       # на юг — на окраину
t.paint("u", NR[0] - 1, 0, NR[0] - 1, ROAD[0] - 2)
t.paint("u", NR[1] + 1, 0, NR[1] + 1, ROAD[0] - 2)
t.paint("u", NR[0] - 1, ROAD[1] + 2, NR[0] - 1, H - 1)
t.paint("u", NR[1] + 1, ROAD[1] + 2, NR[1] + 1, H - 1)
for y in list(range(2, ROAD[0] - 2, 6)) + list(range(ROAD[1] + 4, H - 2, 6)):
    t.ground[y][NR[0] + 1] = "v"
t.reserve(0, ROAD[0] - 1, W - 1, ROAD[1] + 1)        # по трассе и тротуарам ничего не ставим
t.reserve(NR[0] - 1, 0, NR[1] + 1, ROAD[0] - 2)      # и по дороге на север…
t.reserve(NR[0] - 1, ROAD[1] + 2, NR[1] + 1, H - 1)   # …и на юг (перекрёсток уже в полосе трассы)

t.portal([(x, 0) for x in range(NR[0], NR[1] + 1)], "baker_mission", (35, 46), "Миссия")
t.portal([(x, H - 1) for x in range(NR[0], NR[1] + 1)], "baker_outskirts", (35, 2), "Окраина")

# ------------------------------------------------------------ закусочная «Безумный грек»
# Прокуренный придорожный ресторан 1950-х: кухня вдоль северной стены, стойка через зал, за ней Ник,
# перед ней табуреты и пьяный Тобиас, южнее — столы со стульями. Вход с юга, против стоянки;
# чёрный ход в северо-восточном углу — через него носят бочки и выносят мусор.
DIN = t.building(4, 9, 22, 17, "planks", south=(10,), north=(16,), sign="БЕЗУМНЫЙ ГРЕК")
t.paint("T", *DIN)                                   # шахматный пол закусочной
t.props.append(["bk_door", 14, 25])
t.props.append(["bk_door", 15, 25])
t.props.append(["bk_door", 20, 9])          # чёрный ход на задворки
t.props.append(["bk_door", 21, 9])
place("jt_fridge", 6, 10)                            # холод
place("jt_kitchen_stove", 10, 10)                    # плита
place("jt_sink", 12, 10)                             # мойка
place("counter", 14, 10)                             # разделочный стол у стены (2 клетки)
place("crate", 17, 10)                               # припасы у чёрного хода
place("barrel_wood", 23, 10)
place("st_counter", 6, 14)                            # стойка закусочной: 8 клеток, табуреты в спрайте
place("st_counter", 10, 14)
place("glass_cabinet", 5, 12)                        # бутылки у западной стены, за стойкой
place("shelf_goods", 5, 16)
pbox("cabinet_small", 6, 12, "шкафчик Ника", {"самогон": 2, "крышки": 25}, owner="nick")
ptable("w_table_lantern", 8, 14, dx=8, dy=-34)           # лампа на стойке, в глубине
ptable("canteen", 10, 14, dx=-10, dy=-36)            # фляга Тобиаса на стойке
for tx, ty in ((8, 19), (12, 19), (17, 19), (21, 19)):   # столы со стульями вплотную
    place("table_2", tx, ty)
    place("w_chair_r", tx - 1, ty)
    place("w_chair_l", tx + 1, ty)
ptable("canteen", 12, 19, dx=-8, dy=-38)            # накрытый стол на двоих
ptable("junk_small_1", 12, 19, dx=10, dy=-38)
place("round_table_42", 7, 23)                       # угловой столик: два стула по бокам, лицом к столу
place("w_chair_r", 6, 23)
place("w_chair_l", 8, 23)
place("round_table_45", 19, 23)
place("w_chair_r", 18, 23)
place("w_chair_l", 20, 23)
ptable("canteen", 7, 23, dx=-4, dy=-36)              # чья-то чашка на угловом столике
place("w_jukebox", 24, 17)                           # музыкальный автомат у восточной стены
place("bk_pot_c", 5, 23)
place("bk_pot_c", 24, 23)
place("x_fireext", 21, 23)                           # огнетушитель в конце зала, не в проходе
place("bk_trash", 22, 23)
lamp(11, 11, 120)
lamp(20, 12, 120)
lamp(9, 20, 135)
lamp(19, 21, 135)

# ------------------------------------------------------------ площадь с Термометром
# Сердце города: «самый высокий градусник в мире» (стрелка застряла на 134 °F) стоит в центре мощёной
# площади, и на него смотрят — поэтому скамьи стоят рядами к северу от него, лицом к нему, а не как
# попало. У восточного края — колонка: сюда подъезжают караваны за водой (тележка, бочки, ящик и фургон
# при ней, а не посреди брусчатки). Доска объявлений — у схода с тротуара, где её увидят с дороги.
# Водонапорному баку на брусчатке не место: он вынесен за площадь, на пустырь у северной дороги.
place("x_thermometer", 38, 18)
place("bench_16", 35, 16)                            # два ряда лицом к Термометру
place("bench_16", 41, 16)
place("bench_16", 35, 13)
place("bench_16", 41, 13)
pbox("w_pump", 45, 16, "колонка с водой", {"чистая вода": 2})
place("barrel_wood", 44, 18)                         # бочки под колонкой
place("barrel_wood", 47, 18)
place("x_cart", 43, 17)                              # тележка водовоза — у колонки
place("crate", 47, 20)                               # ящик с кружками и ковшом
board(35, 36)                                        # доска объявлений у схода с тротуара
place("bk_trash", 37, 36)                            # урна при доске
place("bk_lamp", 33, 11)                             # фонари 1950-х по краям площади
place("bk_lamp", 48, 11)
place("bk_lamp", 33, 33)
place("bk_lamp", 48, 33)
place("bk_pot_c", 32, 10)                            # кадки только в углах, у фонарей
place("bk_pot_c", 49, 10)
place("bk_pot_c", 49, 34)
place("bk_trash", 44, 12)                            # урна у скамей
place("water_tank_a", 42, 5)                         # водонапорный бак — за площадью, у северной дороги
place("barrel_wood", 45, 7)                          # бочка под сливом бака
oskin("x_vd_wet0", 44, 7)                            # мокрое пятно у бочки

# ------------------------------------------------------------ мотель «Последняя миля»
# Лобби придорожного мотеля 1950-х. Зал — 18×10, а не 28×15: прежний холл был вдвое больше, чем нужно
# пяти номерам, и в нём тонула любая мебель. Что тут есть: стойка приёма у северной стены, за ней Хэтти,
# за её спиной на стене — доска с ключами и ячейками; в глубине за стойкой конторка и ключница; восточнее
# уголок ожидания — диван, два кресла в профиль и журнальный столик на ковре; ряд автоматов у стены;
# лестница на второй этаж в юго-восточном углу, проход к ней свободен. Растения — только в углах.
MOT = t.building(64, 8, 20, 12, "brick", south=(8,), sign="МОТЕЛЬ")
t.paint("R", *MOT)                                   # ковёр вестибюля
t.props.append(["bk_door", 72, 19])
t.props.append(["bk_door", 73, 19])
# приёмная: за стойкой — конторка с долговой книгой и ключница, над стойкой на стене — доска ключей
pbox("filecab_2", 66, 9, "конторка Хэтти", {"крышки": 40, "бинт": 2, "долговая книга": 1}, owner="hattie")
pbox("cabinet_small", 67, 9, "ключница", {"крышки": 12, "отмычка": 1})
swall(KEYBOX, 69, 8, dy=-40)                         # доска ключей/ячейки — на стене за спиной Хэтти
place("bc_bar", 66, 11)                              # стойка приёма: 4 клетки, Хэтти за ней
ptable("x_register", 68, 11, dx=6, dy=-36)           # касса на стойке, в глубине
ptable("w_table_lantern", 66, 11, dx=-8, dy=-34)     # лампа на стойке
place("bk_trolley", 70, 12)                          # багажная тележка: гостя только что проводили
# уголок ожидания: диван спиной к северной стене, кресла в профиль вокруг столика, ковёр под ними
place("bk_rug_a", 74, 10)                            # ковёр первым — он ложится под столик и кресла
place(SOFA_C, 74, 9)
place(COFFEE, 75, 11)
place(ARMCHAIR_R, 74, 11)                            # лицом вправо, к столику
place(ARMCHAIR_L, 76, 11)                            # лицом влево, к столику
place(FLOOR_LAMP, 77, 9)                             # торшер у дивана
place("bk_vending", 79, 9)                           # автоматы в ряд у стены
place("bk_ice", 80, 9)
swall("bk_clock", 72, 8, dy=-42)                     # часы на северной стене
place("bk_pot_c", 65, 9)                             # папоротники только в углах
place("bk_pot_c", 82, 9)
place("bk_pot_c", 65, 17)
t.props.append(["mt_stairs", 80, 15])                # лестница на второй этаж — юго-восточный угол
t.portal([(80, 17), (81, 17)], "baker_motel_2f", (37, 17), "Второй этаж мотеля")
place("x_fireext", 82, 13)                           # огнетушитель у лестницы
lamp(67, 13, 130)
lamp(75, 15, 135)
lamp(80, 18, 120)
# перед фасадом: дорожка от двери к стоянке, кадки парой по бокам двери, скамья у стены
t.paint("u", 72, 20, 73, 25)                         # бетонная дорожка от двери до стоянки
place("bk_pot_c", 71, 20)
place("bk_pot_c", 74, 20)
place("bk_bench", 76, 20)                            # скамья у фасада: курят, ждут такси
place("x_cart", 69, 21)                              # тележка горничной с бельём
place("crate_b", 68, 21)

# ------------------------------------------------------------ дом Роя
# Дом работяги, а не сарай с кроватью. У северной стены — кровать с тумбочкой и лампой, в восточном
# углу — шкаф с его вещами и стол с двумя стульями (не посреди пустой комнаты); у южной стены — кухня
# в одну линию: плита с котелком, полка с посудой, умывальник с ведром. Коврик у кровати, дрова у плиты.
# Дом 12×9 внутренних, а не 16×12: в прежнем зале мебель стояла по краям, а середина была пустой.
ROY = t.building(5, 50, 14, 11, "brick", north=(8,), sign="РОЙ")
t.paint("W", *ROY)                                   # доски
t.props.append(["bk_door", 13, 50])
t.props.append(["bk_door", 14, 50])
place("bed", 6, 51)                                  # кровать вдоль северной стены
place("nightstand", 8, 51)                           # тумбочка с лампой
ptable("w_table_lantern", 8, 51, dx=-2, dy=-30)
place("bk_rug_a", 6, 53)                             # коврик у кровати
place("w_cookstove", 6, 57)                          # плита с трубой — юго-западный угол
ptable("canteen", 6, 57, dx=-6, dy=-44)              # котелок на плите
place("r_logs", 6, 58)                               # дрова под рукой
place("shelf_goods", 10, 51)                         # полка с посудой — спиной к северной стене, не посреди комнаты
place("bucket", 7, 58)                               # ведро с водой у плиты
pbox("wardrobe", 16, 51, "шкаф Роя", {"ткань": 2, "крышки": 10}, owner="roy")
place("table_2", 15, 54)                             # стол с двумя стульями — у шкафа, в углу
place("w_chair_r", 14, 54)
place("w_chair_l", 16, 54)
ptable("w_table_lantern", 15, 54, dx=6, dy=-34)
ptable("canteen", 15, 54, dx=-8, dy=-38)             # фляга Роя на столе
lamp(11, 54, 130)

# ------------------------------------------------------------ гараж
# Гараж стоит южнее трассы — значит ворота у него в СЕВЕРНОЙ стене, к дороге: из боксов машины
# выезжают прямо на бетонный въезд, а не в глухой южный фасад. Ворота по четыре клетки, между ними
# простенок; полотно ворот продолжается внутрь бетоном, чтобы проём читался. В каждом боксе — машина
# и своя работа: яма, инструмент, шины, канистры; у каждой машины свой ящик. Верстак с доской
# инструмента и стеллаж с запчастями — у северной стены, масло и шины — у восточной, стол механика
# с рацией и нарядами — в юго-западном углу. Сухого дерева внутри нет (росло в прежнем северо-восточном
# углу — убрано).
GAR = t.building(58, 49, 22, 16, "concrete", north=(4, 6, 10, 12), sign="ГАРАЖ")
t.paint("Z", 62, 50, 65, 51)                         # бетонный въезд продолжается в первый бокс
t.paint("Z", 68, 50, 71, 51)                         # и во второй — ворота читаются по полотну
place("st_workbench", 59, 50)                        # верстак у северной стены, в простенке
ptable("w_table_lantern", 59, 50, dx=-6, dy=-40)     # фонарь на верстаке
pbox("toolbox_red", 59, 51, "ящик механика", {"лом": 3, "химикаты": 1, "дробь": 4})
swall("st_toolboard", 59, 49, dy=-44)                # доска с инструментом над верстаком
place("x_fireext", 61, 50)                           # огнетушитель у верстака
place("bk_car2", 62, 51)                             # первая машина — под воротами первого бокса
place("ar_pit_b", 63, 53)                            # смотровая яма в полу бокса — под носом машины
oskin("x_vd_oil0", 64, 53)                           # масло под машиной
oskin("x_vd_oil1", 64, 56)
place("jt_tire_stack", 65, 54)                       # шины столбиком у простенка
place("rack_parts", 66, 50)                          # стеллаж с запчастями в простенке
place("bk_car3", 68, 51)                             # вторая машина — под воротами второго бокса
place("toolbox_red", 72, 56)                         # инструмент у второй машины — не под лампой, чтобы не читался «лампа на ящике»
place("canister", 72, 54)                            # канистры
place("pile_tires", 73, 51)                          # шины у восточной стены
place("r_car_wreck", 69, 58)                         # донор: с него и снимают
place("metal_sheets", 73, 60)
place("w_oil_drum", 77, 51)                          # бочка масла
place("jt_tire_stack", 78, 53)
place("table_2", 59, 60)                             # стол механика в углу: рация, наряды, лампа
place("w_chair_l", 60, 60)
ptable("x_radio", 59, 60, dx=-6, dy=-36)
ptable("w_table_lantern", 59, 60, dx=8, dy=-36)
place("crate", 62, 62)                               # ящик с крепежом у южной стены
place("barrel_wood", 76, 62)
place("bucket", 61, 61)
lamp(62, 53, 130)
lamp(70, 55, 130)
lamp(60, 59, 120)

# ------------------------------------------------------------ блокпост культа у западного въезда
# Мешки и огонь поперёк тротуаров, знамя, стол с фонарём: мимо не пройдёшь, не объяснившись.
# Стражники стоят по сторонам дороги, а не в самой дороге.
place("r_sandbag_row", 9, 40, allow_reserved=True)
place("r_sandbag_row", 15, 40, allow_reserved=True)
place("r_sandbag_row", 12, 45, allow_reserved=True)
place("x_fire_barrel", 12, 40, allow_reserved=True)
place("bk_banner_a", 8, 39)
place("bk_banner_b", 19, 39)
place("table_2", 21, 40, allow_reserved=True)
ptable("w_table_lantern", 21, 40, dx=-6, dy=-34)
place("crate", 23, 40, allow_reserved=True)

# ------------------------------------------------------------ трасса: фонари, машины, обочины
# Фонари 1950-х по обеим обочинам (у каждого свой свет), брошенные машины у бордюра, будка, гидрант,
# почтовый ящик, билборд. По трассе не ходят пешком: разметка и обочины остаются чистыми.
for x in range(8, W - 4, 12):
    place("r_streetlamp", x, 40, allow_reserved=True)
for x in range(14, W - 4, 12):
    place("r_streetlamp_b", x, 45, allow_reserved=True)
place("bk_phone", 30, 40, allow_reserved=True)
place("bk_hydrant", 33, 45, allow_reserved=True)
place("t50_mailbox", 62, 40, allow_reserved=True)
place("bk_sign_diner", 6, 28)                        # неон закусочной видно с трассы
place("bk_sign_motel_big", 86, 27)                   # пилон «MOTEL / VACANCY» на въезде в стоянку
place("bk_sign_motel_arrow", 57, 37)                 # указатель «МОТЕЛЬ →» на столбе у обочины: мотель
#                                                      восточнее, за стоянкой — стрелка смотрит туда
for name, x, y in (("bk_car0", 10, 36), ("bk_car1", 16, 36), ("bk_car2", 64, 30),
                   ("bk_car3", 72, 30), ("bk_car4", 90, 36), ("bk_car5", 24, 33),
                   ("bk_car0", 8, 30), ("bk_car1", 96, 33)):
    place(name, x, y)
place("r_dumpster", 2, 37)                           # бак у западного края стоянки
place("pile_tires", 1, 33)
oskin("x_vd_oil0", 15, 38)
oskin("x_vd_oil1", 73, 32)
place("r_car_wreck", 28, 30)                         # остов в углу стоянки
place("pile_tires", 27, 37)
place("r_dumpster", 95, 37)                          # бак — у края стоянки, не посреди асфальта
place("pile_cans", 96, 27)
place("r_car_wreck", 24, 47)                         # остов на южной обочине, у дома Роя
place("r_billboard", 100, 36)                        # щит на въезде с востока

# ------------------------------------------------------------ двор Роя: огород за домом
# Огород по-живому: грядки РАЗНЫЕ (капуста, зелень, рассада, высокие растения, цветы), дорожка от
# калитки между ними, участок обнесён жердевым забором целиком, калитка — против дорожки. Вёдра,
# лопата, бочка под дождь, тележка — при деле; «пять одинаковых квадратов в ряд» больше нет.
t.paint("E", 3, 61, 22, 70)                          # вскопанная земля участка
t.paint("q", 10, 61, 11, 69)                         # дорожка от дома через калитку
for x in (4, 6, 8, 12, 14, 16, 18, 20):              # северный забор, калитка 10..11
    place(FENCE, x, 63)
for x in (4, 6, 8, 10, 12, 14, 16, 18, 20):          # южный забор
    place(FENCE, x, 70)
for y in (64, 65, 66, 67, 68, 69):                   # западный и восточный забор
    place(FENCE_V, 3, y)
    place(FENCE_V, 22, y)
for x in (3, 22):                                    # углы забора
    place(FENCE_C, x, 63)
    place(FENCE_C, x, 70)
for i, (x, y) in enumerate(((5, 65), (8, 65), (14, 65), (17, 65), (5, 67), (8, 67), (14, 67), (17, 67))):
    place(BEDS[i % len(BEDS)], x, y)                 # восемь грядок семи разных видов
place("bucket", 12, 66)                              # ведро на дорожке
oskin("shovel", 9, 68)                               # лопата, воткнутая в землю
place("barrel_wood", 20, 64)                         # бочка под дождь у восточного забора
place("x_cart", 8, 62)                               # тележка у калитки, с мешками
place("crate", 4, 69)                                # ящик с семенами

# ------------------------------------------------------------ двор караванщиков (юг, центр)
# Караваны ждут воды: фургон и пикап, костёр с котелком, бочки и канистры, сарай, сортир и хлам.
place("r_van", 29, 50)
place("r_pickup", 36, 49)
place("campfire", 33, 54)
place("r_logs", 32, 55)
place("x_cauldron", 34, 55)
place("r_barrels", 30, 57)
place("canister", 31, 58)
place("crate", 37, 60)
place("sack", 38, 60)
place("x_fire_barrel", 42, 52)
place("r_shed_tin", 44, 61)
place("r_dumpster", 40, 63)
place("x_outhouse", 28, 64)
place("r_trash", 35, 63)
place("r_barrels", 46, 55)                            # бочки вдоль восточного края двора
place("barrel_wood", 48, 57)
place("canister", 49, 66)
for y in range(48, 60):                               # жердевая изгородь вдоль дороги: двор закрыт
    place("x_fs_wood" if y % 3 else "x_fs_wood_post", 50, y)

# ------------------------------------------------------------ задворки за домами (север) и пустошь
# За закусочной — мусор и бочки от чёрного хода, за мотелем — бельё и баки: город живёт, а не стоит.
place("r_dumpster", 7, 6)
place("barrel_wood", 10, 6)
place("crate", 11, 7)
place(LAUNDRY, 13, 5)
place(LAUNDRY, 68, 5)
place("r_dumpster", 72, 6)
place("crate_b", 74, 5)
place("barrel_wood", 78, 5)
# восточный пустырь за мотелем: старые машины, шины, хлам — свалка на отшибе, а не в центре
place("r_car_wreck", 96, 12)
place("jt_tire_stack", 102, 16)
place("pile_junk", 106, 22)
place("r_dumpster", 94, 30)
place("pile_tires", 107, 12)
place("r_trash", 100, 33)
place("r_car_b", 104, 36)
# юго-восточные задворки за гаражом: свалка города — остовы, шины, баки, сторожка сторожа
place("r_car_wreck", 84, 52)
place("r_pickup", 92, 50)
place("r_car_b", 100, 57)
place("pile_tires", 88, 60)
place("jt_tire_stack", 104, 54)
place("pile_junk", 96, 64)
place("r_dumpster", 82, 66)
place("pile_scrap", 108, 60)
place("r_shed_tin", 100, 68)
place("x_fire_barrel", 90, 68)
place("barrel_wood", 86, 63)
place("crate_b", 94, 57)
place("r_bones", 103, 62)                            # сбитый зверь у свалки — тут ему и место
place("r_trash", 80, 55)
for x, y in ((86, 54), (98, 50), (110, 66), (86, 70)):
    place(t.rnd.choice(TREES), x, y)
desert(t, 78, 50, 111, 72, trees=3, bushes=12, junk=6)

# пустошь по краям: сухие деревья, кусты, камни — кучками у дорог и заборов, не сеткой
for x, y in ((2, 3), (24, 3), (40, 3), (58, 20), (104, 4), (110, 20), (2, 30), (108, 46),
             (2, 72), (26, 72), (48, 72), (60, 72), (82, 69), (104, 68), (96, 47), (44, 68)):
    place(t.rnd.choice(TREES), x, y)
place("r_car_wreck", 45, 3)                          # брошенный у дороги на миссию
place("barrel_wood", 58, 3)
desert(t, 1, 1, 111, 8, trees=4, bushes=14, junk=6)
desert(t, 44, 0, 60, 7, trees=2, bushes=8, junk=3)     # севернее площади
desert(t, 92, 1, 110, 8, trees=2, bushes=8, junk=3)
desert(t, 93, 9, 110, 40, trees=3, bushes=10, junk=5)
desert(t, 23, 68, 111, 73, trees=5, bushes=14, junk=7)      # южное захолустье, кроме огорода Роя
desert(t, 1, 71, 22, 74, trees=2, bushes=6, junk=3)         # под забором огорода
desert(t, 60, 65, 111, 68, trees=2, bushes=6, junk=3)
# ------------------------------------------------------------ кто где
# Ник — за стойкой закусочной, Тобиас — перед ней (пьёт), Хэтти — за стойкой приёма мотеля (спиной к
# доске с ключами), Рой — за своим столом в углу дома, мальчишка — под Термометром, караванщица — у фургона.
npc("nick", 9, 13)
npc("tobias", 9, 15)
npc("hattie", 68, 10)
npc("roy", 15, 55)
npc("baker_kid", 36, 22)
npc("baker_folk_e", 35, 52)
# блокпост на въезде: двое по сторонам дороги
enemy("cult_guard", 11, 39)
enemy("cult_guard", 14, 46)

save(t, "data/maps/baker.json", exempt=("nick", "tobias", "roy", "baker_kid"), floors=FLOORS_TOWN,
     lights=LIGHTS)                                # блокпост культа нейтрален, пока герой не полез



# ================================================================ 2. Миссия
W, H = 70, 50
m = MapKit(W, H, start=(35, 47), seed=31)
put, box, terminal = m.put, m.box, m.terminal
MX0, MY0, MX1, MY1 = 12, 10, 59, 39                  # ограда миссии
m.npcs += [["anselm", 28, 15], ["amos", 52, 16], ["iskra", 45, 26], ["marla", 17, 32],
           ["acolyte_a", 22, 33], ["acolyte_b", 31, 27]]
m.enemies += [["cult_guard", 38, 41], ["cult_guard", 39, 26], ["cultist", 25, 30], ["cultist", 34, 20]]   # страж ворот — снаружи
for _, x, y in m.enemies + m.npcs:
    m.reserve(x, y, x, y)

m.paint("a", 34, 40, 37, H - 1)                      # дорога от ворот к трассе
m.paint_ragged("E", 13, 11, 58, 38, depth=2)         # двор миссии — утоптанная глина, а не дюнный песок
for _x0, _y0, _x1, _y1 in ((35, 25, 36, 39), (18, 26, 49, 27), (26, 24, 27, 25), (18, 28, 19, 29), (42, 28, 43, 29), (48, 22, 49, 25)):
    m.paint("q", _x0, _y0, _x1, _y1)                 # каменные дорожки: ворота — молельня, трапезная, дом Ансельма, кельи
m.paint("u", 33, 40, 33, H - 1)
m.paint("u", 38, 40, 38, H - 1)
m.portal([(x, H - 1) for x in range(34, 38)], "baker", (54, 2), "Трасса")
m.reserve(33, 40, 38, H - 1)
m.reserve(2, 2, 10, 46)                              # тропа вдоль западной стены в дюны
m.reserve(2, 1, 67, 8)                               # дюны за миссией: путь к калитке
m.reserve(56, 11, 58, 24)                            # двор вдоль восточной стены: от калитки к кельям

m.wall_row(WALLS_INTACT["brick"], MX0, MX1, MY0, gaps={52, 53})        # северная стена, калитка
m.wall_row(WALLS_INTACT["brick"], MX0, MX1, MY1, gaps={35, 36})        # южная стена, ворота
m.side_wall("brick", "w", MX0, MY0 + 1, MY1 - 1)
m.side_wall("brick", "e", MX1, MY0 + 1, MY1 - 1)
put("bar_fence_c", 52, MY0, force=True)
back_gate = len(m.props) - 1
put("bar_fence_b", 35, MY1, force=True)
front_gate = len(m.props) - 1

# молельня
m.building(18, 13, 20, 12, "brick", south=(8,), sign="ЕДИНСТВО")
terminal(19, 14, "baker_scanner")
put("display_case_b", 27, 14, check=False)           # алтарь
for x in (25, 30):
    put("candles", x, 14, check=False)
for y in (17, 19, 21):
    for x in (20, 22, 24, 30, 32, 34):
        put(m.rnd.choice(BENCHES), x, y, check=False)
for x in (19, 36):
    put("lantern_lit", x, 22, check=False)

# кельи: решётка, за ней дед
m.building(46, 13, 10, 10, "concrete", south=(2,), sign="КЕЛЬИ")
put("bar_fence_a", 48, 22, force=True)
cell_gate = len(m.props) - 1
put("bed_frame", 53, 14, check=False)
put("bucket", 47, 14, check=False)
put("pile_rags", 53, 19, check=False)
put("candles", 50, 14, check=False)

# дом Ансельма: сундук с книгой даров
m.building(40, 28, 8, 7, "brick", north=(2,), sign=None)
box("metal_chest", 45, 30, "сундук Ансельма", {"крышки": 80, "стимулятор": 1, "святая вода": 2,
                                                "книга даров": 1, "ключ от крипты": 1}, owner="anselm")
put("bed", 41, 32, check=False)
put("table_2", 44, 33, check=False)
put("candles", 46, 33, check=False)

# трапезная: столы, нары, «святая вода»
m.building(14, 28, 14, 8, "planks", north=(4,), sign="ТРАПЕЗНАЯ")
for x in (16, 20, 24):
    put("table_2", x, 30, check=False)
    put("chair_wood", x + 1, 30, check=False)
for x in (15, 19, 23):
    put("bed", x, 33, check=False)
box("barrel_wood", 26, 29, "бочка «святой воды»", {"святая вода": 3}, owner="anselm")
box("crate", 15, 29, "ящик с припасами", {"чистая вода": 1, "крышки": 6})
put("lantern_lit", 22, 31, check=False)

# двор: шатры, костёр, бочки с огнём у ворот, кладбище «вознесённых»
for name, x, y in [("r_tent_beige", 29, 30), ("r_tent_purple", 33, 33), ("r_tent_low", 38, 30)]:
    put(name, x, y)
put("campfire", 31, 30)
for x in (33, 38):
    put("x_fire_barrel", x, 37)
for gy in (27, 30, 33):
    for gx in (51, 53, 55):
        put("x_cross", gx, gy - 1, check=False)
        put("x_grave", gx, gy, check=False)
        m.containers[-1]["requires"] = {"item": "лопата", "msg": "Свежая могила «вознесённого». Без лопаты — никак."}
        m.containers[-1]["name"] = "могила «вознесённого»"
put("x_board", 49, 36, check=False)
m.terminals.append({"prop": len(m.props) - 1, "id": "doc:doc_ascended"})

# двор живёт: колодец, знамёна вдоль дорожки, молитвенные коврики у костра, грядки послушников, скамьи, лампы, ящики
put(WELL, 31, 36, check=False)
for x in (26, 28, 33, 38, 44, 46):
    put(BANNER[x % 2], x, 25, check=False)
for x, y in ((29, 31), (33, 31), (30, 33)):
    stamp(m, "bk_prayer_rug_%d_%d" % (x, y), PRAYER_RUG, x, y)
for i, (x, y) in enumerate(((14, 37), (17, 37), (20, 37), (14, 13), (17, 13))):
    put(GARDEN_BED[i % 2], x, y, check=False)
for x, y in ((24, 27), (30, 27), (38, 27), (44, 27)):
    put(BENCHES[x % len(BENCHES)], x, y, check=False)
for x, y in ((27, 24), (43, 25), (36, 36)):
    put("lantern_lit", x, y, check=False)
put(LAUNDRY, 14, 25, check=False)
put("crate", 28, 36, check=False)
put("barrel_wood", 29, 38, check=False)
# снаружи: дорога, дюны, фонарь у ворот
put("r_streetlamp", 39, 41, allow_reserved=True, check=False)
put("x_fire_barrel", 32, 42, allow_reserved=True, check=False)
put("campfire", 57, 4, allow_reserved=True)          # костерок Панка в дюнах
desert(m, 1, 1, W - 2, 8, trees=8, bushes=20)
desert(m, 1, 9, 11, H - 2, trees=4, bushes=10, junk=6)
desert(m, 60, 9, W - 2, H - 2, trees=6, bushes=14, junk=8)
desert(m, 12, 41, 32, H - 2, trees=3, bushes=8)
desert(m, 39, 41, 59, H - 2, trees=3, bushes=8)
# плита за алтарём — спуск в крипту (tools/build_baker_levels.py); ключ — в сундуке Ансельма
m.props.append(["x_manhole", 34, 15])
m.portal([(34, 15)], "baker_crypt", (4, 5), "Крипта Единства",
         requires={"item": "ключ от крипты",
                   "msg": "За алтарём — каменная плита с замочной скважиной в форме круга. Ключ — у брата Ансельма."})
save(m, "data/maps/baker_mission.json", floors=FLOORS_TOWN,
     gates=[{"prop": front_gate, "flag": "mission_gate_open",
             "msg": "Ворота миссии заперты изнутри. За решёткой — шатры, костёр и белые балахоны."},
            {"prop": back_gate, "flag": "mission_back_open", "pry": True,   # лом у героя всегда при себе
             "open_msg": "Вы поддеваете гнилой засов ломом. Калитка со скрипом подаётся."},
            {"prop": cell_gate, "flag": "cells_open", "key": "ключ от келий",
             "open_msg": "Ключ проворачивается в замке. Решётка кельи открыта.",
             "msg": "Решётка кельи на замке. Ключ — у брата-ключника."}],
     exempt=("anselm", "iskra", "amos", "marla", "acolyte_a", "acolyte_b"))


# ================================================================ 3. Окраина
W, H = 76, 52
o = MapKit(W, H, start=(35, 2), seed=41)
put, box, terminal, scatter = o.put, o.box, o.terminal, o.scatter
o.npcs += [["hollis", 60, 40], ["baker_folk_a", 9, 14], ["baker_folk_b", 17, 25], ["baker_folk_c", 24, 33],
           ["baker_folk_d", 12, 41], ["baker_kid_b", 30, 21]]
o.enemies += [["rat", 72, 49], ["rat", 70, 47]]
for _, x, y in o.enemies + o.npcs:
    o.reserve(x, y, x, y)

o.paint("a", 34, 0, 37, 12)                          # дорога с трассы
o.paint("E", 34, 13, 35, 46)                         # главная тропа посёлка — утоптанная глина
for _y in (13, 23, 33):
    o.paint("E", 3, _y, 33, _y + 1)                  # поперечные тропы между рядами лачуг
o.paint_ragged("E", 8, 14, 14, 18, depth=1)          # площадка у костра
o.paint_ragged("Z", 62, 9, 72, 20, depth=2)          # бетонная площадка перед складом «Бейкер-7»
o.paint_ragged("Z", 44, 31, 76, 50, depth=2)         # свалка — бетонное основание, масляные пятна
o.paint("u", 33, 0, 33, 12)
o.paint("u", 38, 0, 38, 12)
o.portal([(x, 0) for x in range(34, 38)], "baker", (54, 73), "Трасса")
o.reserve(33, 0, 38, 18)

# жилой запад: лачуги, палатки, костры
homes = [("r_shack", 3, 9), ("r_shack_tin", 10, 9), ("r_cabin", 19, 10), ("r_shed_tin", 25, 9),
         ("r_hut", 3, 19), ("r_tent_big", 9, 20), ("r_shanty", 19, 19), ("r_cabin_b", 26, 20),
         ("r_house_wood", 3, 29), ("r_tent_green", 10, 30), ("r_tent_orange", 14, 30), ("r_shack_e", 20, 29),
         ("r_cabin_d", 28, 29), ("r_shack_f", 4, 38), ("r_shanty_big", 16, 37), ("r_shack_blue", 26, 39)]
for name, x, y in homes:
    put(name, x, y)
for x, y in ((9, 16), (22, 26), (13, 35), (35, 15)):
    put("campfire", x, y)
for x, y in ((16, 14), (28, 34), (8, 45)):
    put("x_fire_barrel", x, y)
for name, x, y in [("r_dumpster", 14, 15), ("r_trash_can", 29, 24), ("r_logs", 24, 36), ("r_barrels", 6, 26),
                   ("r_bin", 31, 41)]:
    put(name, x, y)
box("metal_box_open", 18, 16, "ящик у лачуги", {"ткань": 1, "крышки": 4})
box("wardrobe", 7, 34, "сундук старика", {"крышки": 12, "бинт": 1})
put("r_water_tower_tall", 44, 6)
# посёлок живой: бельё между лачугами, штакетник, лавки у костров, колодец, огородики, лампы вдоль тропы
for x, y in ((6, 15), (22, 15), (12, 31), (24, 31)):
    put(LAUNDRY, x, y, check=False)
for x, y in ((7, 17), (11, 17), (24, 28), (14, 27)):
    put(BENCHES[x % len(BENCHES)], x, y, check=False)
put(WELL, 31, 17, check=False)
for i, (x, y) in enumerate(((12, 44), (15, 44), (18, 44), (6, 42), (9, 42))):
    put(GARDEN_BED[i % 2], x, y, check=False)
for y in (14, 24, 34, 42):
    put("lantern_lit", 36, y, check=False)
for x in (4, 6, 8, 10):
    put(PICKET, x, 12, check=False)
for x, y in ((5, 14), (28, 25), (30, 41)):
    put("barrel_wood", x, y, check=False)

# свалка машин и трейлер Холлиса
for name, x, y in [("r_rv", 54, 35), ("r_car_wreck", 64, 33), ("r_junk_mound", 70, 36), ("r_tanker", 46, 44),
                   ("r_van", 56, 47), ("r_camper", 66, 44), ("r_car_b", 48, 38), ("r_car_c", 72, 42),
                   ("r_moto", 62, 37), ("r_car_wreck", 44, 32)]:
    put(name, x, y)
box("metal_chest", 58, 39, "сундук Холлиса", {"крышки": 60, "стимулятор": 2, "балахон послушника": 1},
    owner="hollis")
put("r_awning", 61, 41)
put("lantern_lit", 59, 42)
terminal(64, 40, "hollis_radio")
for x, y in ((52, 41), (68, 40)):
    put("x_fire_barrel", x, y)

# склад «Бейкер-7»
put("r_bunker", 64, 8, check=False)
o.portal([(66, 10), (67, 10)], "baker7", (4, 18), "Склад «Бейкер-7»",
         requires={"flag": "baker7_open",
                   "msg": "Бронедверь склада. Табло: «ДОСТУП: ПЕРСОНАЛ МАРИПОЗЫ. СЕТЧАТКА · ГОЛОС · КОД»."})
terminal(70, 11, "baker7_lock")
o.reserve(63, 10, 69, 20)                            # перед дверью склада — свободно
for x, y in ((60, 12), (72, 13)):
    put("x_sandbags", x, y, check=False)
put("r_army_truck", 52, 6)
put("r_derrick", 72, 3)
put("r_streetlamp", 62, 15, allow_reserved=True, check=False)
put("r_streetlamp_b", 71, 17, allow_reserved=True, check=False)
scatter(["ammo_box", "crate", "crate_b"], 56, 21, 74, 28, 3)

desert(o, 1, 1, W - 2, H - 2, trees=12, bushes=30, junk=16)
save(o, "data/maps/baker_outskirts.json", exempt=("hollis",), floors=FLOORS_TOWN)

city.save()          # data/props/baker.json — объекты из наборов, что поставлены на картах выше
