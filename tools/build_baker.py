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
  data/maps/baker_outskirts.json «Бейкер: окраина» (119×81). Посёлок тех, кого город не
      пустил: лачуги и палатки у костров, свалка машин со «скупщиком» Холлисом, водонапорная
      башня, бункер склада «Бейкер-7» с караулом.

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
# Фабрика на карту: у трассы и у миссии свои MapKit, а правила расстановки одни и те же.
def helpers(mk, lights):
    """place/pbox/oskin/ptable/swall/lamp/npc/enemy для конкретной карты (mk) и её списка света."""
    def pwhy(name, x, y, blocked=None, soft=None, reserved=None):
        """Почему предмет не встал — как why_not() в build_town.py."""
        foot = mk.footprint(name, x, y)
        blocked = mk.blocked if blocked is None else blocked
        soft = mk.soft_obj if soft is None else soft
        reserved = mk.reserved if reserved is None else reserved
        why = []
        if any(c in blocked for c in foot):
            why.append("блок: " + str([c for c in foot if c in blocked]))
        if any(c in soft for c in foot):
            why.append("мягкий предмет: " + str([c for c in foot if c in soft]))
        if any(c in reserved for c in foot):
            why.append("резерв")
        h = mk.hides(name, x, y)
        if h:
            why.append(f"заслоняет {h[0]} ({h[1]}, {h[2]})")
        why.append("земля: " + "".join(mk.ground[b][a] for a, b in foot))
        return f"«{name}» не встал в ({x}, {y}): " + "; ".join(why)

    def _undo(snap):
        """Неудачная попытка не оставляет следов: предмет, его клетки и контейнер убираются."""
        n_props, n_conts, blocked, soft_obj, reserved = snap
        del mk.props[n_props:], mk.containers[n_conts:]
        mk.blocked, mk.soft_obj, mk.reserved = blocked, soft_obj, reserved
        mk._reach = None

    def place(name, x, y, **kw):
        """Явная расстановка: предмет обязан встать и остаться там, куда его поставили (logic.md §2)."""
        snap = (len(mk.props), len(mk.containers), set(mk.blocked), set(mk.soft_obj), set(mk.reserved))
        ok = mk.put(name, x, y, **kw)
        if ok and mk.props[-1][1:3] == [x, y]:
            return True
        why = pwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
        _undo(snap)
        raise AssertionError(why)

    def pbox(name, x, y, title, loot, **kw):
        """Ящик с нужной добычей — как place(): не встал, так с причиной."""
        snap = (len(mk.props), len(mk.containers), set(mk.blocked), set(mk.soft_obj), set(mk.reserved))
        try:
            mk.box(name, x, y, title, loot, **kw)
        except AssertionError:
            why = pwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
            _undo(snap)
            raise AssertionError(why) from None
        if mk.props[-1][1:3] == [x, y]:
            return True
        moved = mk.props[-1][1:3]
        _undo(snap)
        raise AssertionError(pwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
                             + f"; встал в ({moved[0]}, {moved[1]})")

    def oskin(name, x, y):
        """Мелочь на полу (пятно масла, лопата): не блокирует, но и в стену не лезет."""
        if not mk.put(name, x, y, check=False) or mk.props[-1][1:3] != [x, y]:
            raise AssertionError(pwhy(name, x, y))

    def ptable(name, x, y, dx=0, dy=-34):
        """Мелочь на столешнице: на клетке мебели, поднята на её высоту и в глубину — не у переднего края
        (замечание автора 24.10), рисуется сразу после стола (6-й элемент — порядок отрисовки)."""
        assert (x, y) in mk.blocked, f"«{name}» в ({x}, {y}): под ним нет стола"
        mk.props.append([name, x, y, dx, dy, 1 - dy])

    def swall(name, x, y0, dx=0, dy=-40):
        """Настенное — только на целой стене: ставится на ряд стены-пропа и поднимается так, чтобы висеть на
        фасаде (logic.md §2а). Где стены нет (проём ворот) — падает со счётом."""
        fw, fh = _props.info(name)["foot"]
        cells = [(x + i, y0 + j) for i in range(fw) for j in range(fh)]
        assert all(c in mk.blocked for c in cells), f"«{name}» в ({x}, {y0}): там нет целой стены"
        mk.props.append([name, x, y0 + 1, dx, dy])
        mk.soft_obj.add((x, y0 + 1))       # на клетке под настенным ничего не ставим
        mk._reach = None

    def lamp(x, y, r=130, color=(255, 176, 96), flick=0.03):
        """Лампа под потолком (без картинки): пятно света на полу. Пока крыша на месте, снаружи не видно."""
        lights.append([x * 48 + 24, y * 48 + 24, r, list(color), flick])

    def npc(nid, x, y):
        """Житель стоит там, где стоит: клетка свободна."""
        assert (x, y) not in mk.blocked, f"NPC {nid} в ({x}, {y}) — клетка занята"
        mk.npcs.append([nid, x, y])
        mk.reserve(x, y, x, y)

    def enemy(kind, x, y):
        assert (x, y) not in mk.blocked, f"{kind} в ({x}, {y}) — клетка занята"
        mk.enemies.append([kind, x, y])
        mk.reserve(x, y, x, y)

    return place, pbox, oskin, ptable, swall, lamp, npc, enemy


place, pbox, oskin, ptable, swall, lamp, npc, enemy = helpers(t, LIGHTS)


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

t.portal([(x, 0) for x in range(NR[0], NR[1] + 1)], "baker_mission", (54, 74), "Миссия")
t.portal([(x, H - 1) for x in range(NR[0], NR[1] + 1)], "baker_outskirts", (55, 3), "Окраина")

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
t.portal([(80, 17), (81, 17)], "baker_motel_2f", (42, 21), "Второй этаж мотеля")
place("x_fireext", 82, 13)                           # огнетушитель у лестницы
lamp(67, 13, 130)
lamp(75, 15, 135)
lamp(78, 18, 120)                                    # у лестницы, но не над самым входом
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
# «Бейкер: миссия» — двор «Детей Единства» за кирпичной оградой. Уличная карта выросла ×1.56 по стороне
# (70×50 → 109×78, как трасса и Пятнадцатая); планировка не растянута, а перестроена по смыслу
# (docs/furnish/logic.md §1), обстановка — поштучная: place / pbox / ptable / swall, никаких scatter и
# случайных куч посреди участков. План зон, кто где и сценки — docs/furnish/baker.md, раздел 2.
#
# Чем живёт миссия (двор 73×45 внутри ограды):
#   молятся  — молельня «Единство» (северо-запад): алтарь в апсиде, за алтарём каменная плита в крипту,
#              у входа сканер-терминал, молитвенные коврики рядами, канделябры-черепа, знамёна;
#   спят     — кельи за решёткой (северо-восток): четыре койки в нишах за прутьями, дед Эймос в восточной;
#              послушники — на нарах у западной стены трапезной;
#   едят     — трапезная (юго-запад): кухня в линию у северной стены, длинные столы с лавками и табуретами,
#              бочка «святой воды», ящик с припасами, котёл;
#   растят   — огород вдоль западной стены: четырнадцать грядок семи видов, дорожка, ведро, лопата, бочка;
#   хранят   — кладовая в трапезной, дрова и бочки за домом, «книга даров» в сундуке Ансельма;
#   хоронят  — кладбище «вознесённых» (песок, кресты, надгробия, доска с именами; свежие могилы — с лопатой);
#   караулят — страж снаружи ворот (с ним договариваются о пропуске), страж изнутри у створок, страж у кладбища,
#              послушник в молельне;
#              ночью — огневые бочки у ворот, костёр с котелком в рабочем дворе, фонари на дорожках;
#   выходы   — южные ворота на трассу (портал), калитка в северной стене в дюны (ломом), тропа вдоль
#              западной стены: по ней обходят ограду и выходят к калитке с севера.
W, H = 109, 78
m = MapKit(W, H, start=(54, 74), seed=31)
mput, mterminal = m.put, m.terminal
MLIGHTS = []                          # потолочный свет помещений; уличный — от предметов с light
mplace, mpbox, moskin, mptable, mswall, mlamp, mnpc, menemy = helpers(m, MLIGHTS)
MX0, MY0, MX1, MY1 = 18, 16, 92, 62                  # кирпичная ограда миссии

# ---- земля: дорога с трассы, двор, дорожки, огород, кладбище
# Дорога на юг — та же, что на трассе (x 52..55), с тротуарами: за воротами она сужается до проёма.
m.paint("a", 52, 63, 55, H - 1)
m.paint("u", 51, 63, 51, H - 1)
m.paint("u", 56, 63, 56, H - 1)
for y in range(66, H - 1, 6):
    m.ground[y][53] = "v"                            # пунктир по оси дороги
m.reserve(51, 63, 56, H - 1)                         # по дороге и тротуарам ничего не ставим
m.portal([(x, H - 1) for x in range(52, 56)], "baker", (54, 2), "Трасса")   # назад, на дорогу к трассе
m.paint_ragged("E", 19, 17, 91, 61, depth=2)         # двор — утоптанная глина, а не дюнный песок
m.paint("q", 53, 17, 54, 61)                         # от ворот в глубину двора и вокруг молельни
m.paint("q", 25, 43, 88, 44)                         # поперечная: молельня — кельи — восточная стена
m.paint("q", 40, 37, 41, 42)                         # к дверям молельни
m.paint("q", 82, 34, 83, 42)                         # к решётке кельи
m.paint("q", 64, 39, 65, 42)                         # к кладбищенской дорожке
m.paint("q", 88, 17, 89, 42)                         # вдоль восточной стены, от калитки
m.paint("q", 21, 19, 21, 41)                         # дорожка между грядками огорода
m.paint_ragged("d", 55, 24, 72, 38, depth=1)         # кладбище — сухой песок
m.paint("q", 64, 24, 65, 38)                         # дорожка между могилами

# ---- ограда, ворота, калитка
m.wall_row(WALLS_INTACT["brick"], MX0, MX1, MY0, gaps={89})            # северная стена, калитка
m.wall_row(WALLS_INTACT["brick"], MX0, MX1, MY1, gaps={53, 54})        # южная стена, ворота
m.side_wall("brick", "w", MX0, MY0 + 1, MY1 - 1)
m.side_wall("brick", "e", MX1, MY0 + 1, MY1 - 1)
mput("pr_cell_bars", 89, MY0, force=True)            # калитка в дюны — кованая дверца в стене, ломом
back_gate = len(m.props) - 1
mput("hb_sew_gate", 53, MY1, force=True)             # ворота на дорогу — створчатые, заперты изнутри
front_gate = len(m.props) - 1

# ---- объекты культа из набора cult-temple (регистрируются здесь, в карте миссии)
MS_ALTAR = P("ms_altar", "pk:cult/cult_2_045", foot=[2, 1], sight=True)
MS_CANDLE = P("ms_candelabra", "pk:cult/cult_1_005", foot=[1, 1])
MS_STATUE = P("ms_statue", "pk:cult/cult_2_094", foot=[1, 1], sight=True)
MS_SHELF = P("ms_bookshelf", "pk:cult/cult_2_006", foot=[2, 1], sight=True)

# ---- молельня «Единство»: 28×19, вход с юга по осевой дорожке от ворот
# Апсида — каменная солея в три ряда; алтарь на ней, за алтарём плита в крипту (её не видно от двери —
# только подойдя к алтарю сбоку). Скамей в зале нет: культ молится на ковриках, лицом к алтарю, коврики
# лежат рядами по обе стороны осевого прохода. Свет — три подвесные лампы, у алтаря свечи и канделябры.
m.building(24, 18, 28, 19, "brick", south=(16,), sign="ЕДИНСТВО")
m.paint("q", 25, 19, 50, 35)                         # пол молельни — каменные плиты
m.paint("Z", 37, 19, 45, 25)                         # солея/апсида — бетонные плиты
for x in (40, 41):
    m.props.append(["bk_door", x, 36])               # створки входных дверей
mplace(MS_ALTAR, 40, 23)                             # алтарь с горящими свечами — на солее, лицом в зал
mplace(MS_CANDLE, 36, 19)                            # черепа-канделябры по краям солеи
mplace(MS_CANDLE, 46, 19)
mplace(MS_STATUE, 43, 19)                            # «Совершенный» — у северной стены апсиды
mplace(MS_SHELF, 25, 19)                             # книги и писания — у северной стены, в углу
mplace("candles", 37, 24)                            # свечи на солее, по сторонам от алтаря
mplace("candles", 44, 24)
mterminal(46, 34, "baker_scanner")                   # сканер у входа: метка «вознесённого», журнал
mplace("bk_banner_a", 38, 35)                        # знамёна по сторонам двери
mplace("bk_banner_b", 43, 35)
for rx in (26, 28, 30, 32, 43, 45, 47):              # коврики вплотную, рядами по обе стороны прохода
    for ry in (27, 31):
        stamp(m, f"bk_prayer_rug_{rx}_{ry}", PRAYER_RUG, rx, ry)
mplace("bk_banner_a", 25, 25)                        # знамёна у солеи, на боковых стенах
mplace("bk_banner_b", 50, 25)
mplace("table_2", 36, 34)                            # свечная лавка у входа: свечи и ящик для даров
mptable("candles", 36, 34, dx=-6, dy=-36)
mptable("junk_small_1", 36, 34, dx=8, dy=-36)
mplace("barrel_wood", 26, 34)                        # кадка для омовения у двери: руки и ноги перед молитвой
mplace("bucket", 27, 34)
mplace("bench_16", 30, 34)                           # скамьи, где разуваются перед ковриками, лицом в зал
mplace("bench_16", 34, 34)
mplace("candles", 25, 29)                            # обетные свечи вдоль боковых стен
mplace("candles", 25, 33)
mplace("candles", 50, 29)
mplace("candles", 50, 33)
mlamp(31, 24, 130)
mlamp(45, 28, 130)
mlamp(38, 33, 120)
# плита в крипту — за алтарём: подход с боков, ключ у Ансельма
m.props.append(["x_manhole", 40, 21])
m.portal([(40, 21)], "baker_crypt", (3, 4), "Крипта Единства",
         requires={"item": "ключ от крипты",
                   "msg": "За алтарём — каменная плита с замочной скважиной в форме круга. Ключ — у брата Ансельма."})

# ---- кельи за решёткой: 14×16, вход с юга, за прутьями — четыре койки в нишах
# Решётка — на самом проёме: отпер её ключом (или выломал на штурме) — и ты внутри. В передней половине
# стол ключника с фонарём, скамья для ожидающих; в задней — койки, ведра, тряпьё, свечи у изголовья.
m.building(74, 18, 14, 16, "concrete", south=(8,), sign="КЕЛЬИ")
m.paint("Z", 75, 19, 86, 32)                         # бетонный пол келий
mput("ws_gate", 82, 33, force=True)                  # решётка на проёме — кованые створы в 2 клетки
cell_gate = len(m.props) - 1
for x in (76, 79, 82, 85):                           # койки вдоль северной стены, по одной в нише
    mplace("bed", x, 19)
for x in (78, 81, 84):                               # простенки-прутья между нишами
    mplace("bar_fence_a", x, 20)
mplace("bucket", 78, 22)                             # ведро в первой нише
mplace("bucket", 84, 22)
mplace("pile_rags", 76, 22)                          # тряпьё у стены
mplace("candles", 75, 21)                            # свечи у изголовья — единственный свет в нишах
mplace("candles", 86, 21)
mplace("table_2", 77, 30)                            # стол ключника в передней половине
mplace("chair_wood", 78, 30)
mptable("w_table_lantern", 77, 30, dx=-4, dy=-34)
mplace("bench_16", 84, 30)                           # скамья ожидающих у восточной стены
mplace("bucket", 86, 31)                             # вода для узников
mplace("candles", 75, 31)
mlamp(78, 24, 110)
mlamp(84, 30, 110)

# ---- дом Ансельма: 14×11, вход с севера из двора
# Не келья и не кабинет: кровать, тумбочка с лампой, шкаф с книгами, стол с лампой и стулом, шифоньер.
# Сундук с книгой даров и ключом от крипты — в северо-восточном углу, за столом.
m.building(60, 47, 14, 11, "brick", north=(6,), sign=None)
m.paint("W", 61, 48, 72, 56)                         # доски
for x in (66, 67):
    m.props.append(["bk_door", x, 47])
mplace("bed", 61, 48)
mplace("nightstand", 63, 48)
mptable("w_table_lantern", 63, 48, dx=-2, dy=-30)
mpbox("metal_chest", 70, 48, "сундук Ансельма", {"крышки": 80, "стимулятор": 1, "святая вода": 2,
                                                 "книга даров": 1, "ключ от крипты": 1}, owner="anselm")
mplace(MS_SHELF, 61, 53)                             # писания — у западной стены
mplace("table_2", 66, 51)                            # рабочий стол Ансельма
mplace("chair_wood", 67, 51)
mptable("w_table_lantern", 66, 51, dx=6, dy=-34)
mplace("candles", 65, 49)
mplace("wardrobe", 72, 50)                           # шифоньер у восточной стены
mplace("bk_rug_a", 68, 53)
mplace("stool_3", 69, 54)                            # табурет у стола
mplace("candles", 71, 55)                            # свеча в углу у шифоньера
mlamp(66, 52, 120)

# ---- трапезная: 24×13, два входа с севера (общий зал и кухня)
# Кухня — в линию у северной стены: холод, плита, мойка, разделочный стол, полка с посудой. Два длинных
# стола: лавки в самом спрайте стола (лишние табуреты рядом читались кашей), между рядами проход. Спят послушники
# в палатках рабочего двора, не в трапезной (в столовой не ночуют). Кладовая — у восточной: бочка «святой воды», припасы, котёл.
m.building(22, 47, 24, 13, "planks", north=(8, 18), sign="ТРАПЕЗНАЯ")
m.paint("W", 23, 48, 44, 58)                         # доски
for x in (30, 31, 40, 41):
    m.props.append(["bk_door", x, 47])
mplace("jt_fridge", 34, 48)                          # холод
mplace("jt_kitchen_stove", 36, 48)                   # плита
mplace("jt_sink", 38, 48)                            # мойка
mplace("counter", 42, 48)                            # разделочный стол
mplace("shelf_goods", 44, 48)                        # полка с посудой в углу
mptable("canteen", 42, 48, dx=-6, dy=-36)             # миска на разделочном столе
for x in (26, 28, 30, 32):                           # длинные столы: лавки в спрайте, табуреты с ближней стороны
    mplace("w_table_set", x, 51)
    mplace("w_table_set", x, 55)
mptable("canteen", 26, 51, dx=-8, dy=-38)            # миски на общем столе
mptable("canteen", 30, 55, dx=6, dy=-38)
mplace("bucket", 24, 57)                             # ведро с водой у западной стены
mplace("glass_cabinet", 44, 50)                      # посуда в кладовой
mplace("barrel_wood", 44, 53)
mpbox("barrel_wood", 44, 54, "бочка «святой воды»", {"святая вода": 3}, owner="anselm")
mplace("x_cauldron", 42, 57)                         # котёл на огне — обед и «причастие»
mpbox("crate", 35, 57, "ящик с припасами", {"чистая вода": 1, "крышки": 6})   # сюжет: чистая вода
mplace("w_sacks", 37, 57)
mplace("bk_laundry", 49, 47)                         # бельё сушится во дворе, между трапезной и домом
mlamp(30, 50, 130)
mlamp(38, 55, 130)
mplace("candles", 23, 49)                            # свечи у нар — ночник послушников

# ---- огород вдоль западной стены: 14 грядок семи видов, дорожка посередине
# Культ кормится сам: капуста, зелень, редис, рассада. Грядки разные, между ними протоптанная дорожка,
# у дорожки ведро и лопата, у стены — бочка под воду.
GARDEN = ((19, 21), (22, 22), (19, 24), (22, 25), (19, 27), (22, 28), (19, 30), (22, 31),
          (19, 33), (22, 34), (19, 36), (22, 37), (19, 39), (22, 40))
for _i, (_gx, _gy) in enumerate(GARDEN):
    mplace(BEDS[_i % len(BEDS)], _gx, _gy)
mplace("bucket", 21, 23)
moskin("shovel", 21, 29)
mplace("barrel_wood", 21, 42)                        # бочка под дождь — в конце дорожки
mplace("r_logs", 19, 42)

# ---- кладбище «вознесённых»: песок, кресты, надгробия; свежие могилы — только с лопатой
# Ряд «вознесённых» этого года — кресты и разрытые могилы (9), дальше старые надгробия (6). Между ними
# каменная дорожка, у входа — доска с именами (doc:doc_ascended).
def grave(gx, gy):
    mplace("x_cross", gx, gy - 1)
    mplace("x_grave", gx, gy)
    m.containers[-1].update({"name": "могила «вознесённого»",
                             "requires": {"item": "лопата", "msg": "Свежая могила «вознесённого». Без лопаты — никак."}})


for _gy in (27, 36):
    for _gx in ((57, 60, 63, 66, 69, 72) if _gy == 27 else (57, 63, 69)):
        grave(_gx, _gy)
for _gx in (57, 60, 63, 66, 69, 72):                 # старые надгробия — второй ряд
    mplace("x_tombstone", _gx, 32)
mplace("x_board", 60, 39)                            # доска с именами «вознесённых» у входа
m.terminals.append({"prop": len(m.props) - 1, "id": "doc:doc_ascended"})
mplace("lantern_lit", 62, 39)                        # фонарь у доски: у могил и ночью кто-то сидит со светом
moskin("shovel", 62, 30)                             # лопата у свежей могилы
moskin("shovel", 58, 35)
mplace("bucket", 66, 38)                             # ведро у дорожки

# ---- склад урожая и утвари: 8×6 в пустом углу за кладбищем, дверь на поперечную дорожку
# Урожай с огорода и утварь культа не лежат под открытым небом: дощатый сарай — мешки с зерном,
# полка с банками, ящики, бочка под засол, ведро; дрова — в проулке между сараем и кельями.
m.building(74, 37, 8, 6, "planks", south=(4,), sign=None)
m.paint("W", 75, 38, 80, 41)                         # доски
for x in (78, 79):
    m.props.append(["bk_door", x, 42])
mplace("w_crate_sacks", 75, 38)                      # мешки с зерном
mplace("crate", 78, 38)
mplace("shelf_goods", 80, 38)                        # полка с банками и посудой — у восточной стены
mplace("bucket", 76, 40)
mplace("crate_b", 80, 40)
mplace("barrel_wood", 75, 40)                        # бочка под засол
# (мешки убраны: не встают у стены)
mlamp(77, 39, 110)
mplace("firewood", 76, 35)                           # дрова в проулке под стеной келий
mplace("r_logs", 79, 35)

# ---- двор: колодец, знамёна вдоль дорожки, скамьи, фонари, огонь у ворот
mplace(WELL, 47, 39)                                 # колодец — в развилке дорожек
mplace("bucket", 46, 39)
mplace("bench_16", 49, 41)
mplace("bench_16", 44, 41)
for _x, _y in ((51, 39), (56, 40), (52, 45), (56, 48)):   # знамёна вдоль осевой дорожки
    mplace(BANNER[_x % 2], _x, _y)
for _x, _y in ((52, 42), (55, 45), (52, 51), (55, 58)):   # фонари на дорожке — у каждого свой свет
    mplace("lantern_lit", _x, _y)
mplace("x_fire_barrel", 50, 59)                      # огонь у ворот изнутри — ночной караул видит въезд
mplace("x_fire_barrel", 55, 59)
mplace("table_2", 48, 59)                            # стол караульных у ворот: фонарь, кружки
mptable("w_table_lantern", 48, 59, dx=-6, dy=-34)
mplace("crate", 47, 60)
mplace("w_sacks", 56, 59)
# проход вдоль восточной стены молельни: припасы под рукой, фонарь на повороте
mplace("barrel_wood", 52, 26)
mplace("crate", 52, 29)
mplace("r_logs", 52, 32)
mplace("lantern_lit", 52, 35)

# ---- рабочий двор (между трапезной и домом Ансельма): костёр, котелок, дрова, палатки богомольцев
mplace("campfire", 49, 52)
mplace("x_cauldron", 50, 53)
mplace("r_logs", 48, 53)
mplace("bench_16", 47, 51)
mplace("bench_16", 51, 50)
mplace("barrel_wood", 47, 55)
mplace("crate", 47, 56)
mplace("r_tent_beige", 56, 50)                       # палатки тех, кто ждёт «вознесения»
mplace("r_tent_purple", 56, 55)
mplace("x_outhouse", 57, 59)
mplace("barrel_wood", 45, 45)
mplace("r_logs", 44, 45)
mplace("pile_rags", 20, 45)                          # за огородом: тряпьё, бочка, тележка
mplace("barrel_wood", 20, 46)
mplace("x_cart", 24, 45)
# задворки: за трапезной — дрова и бочки, за домом Ансельма — хлам и поленница
mplace("r_logs", 24, 60)
mplace("barrel_wood", 27, 60)
mplace("crate_b", 30, 60)
mplace("crate", 33, 60)
mplace("barrel_wood", 62, 59)
mplace("r_logs", 64, 60)
mplace("crate_b", 68, 59)
mplace("w_sacks", 71, 60)
# вдоль восточной стены: от калитки вниз к кельям — скамья караульного, фонарь, бочка
mplace("bench_16", 90, 24)
mplace("lantern_lit", 88, 30)
mplace("barrel_wood", 90, 40)
mplace("r_logs", 90, 19)

# ---- дровяной двор в юго-восточном углу: культ топит плиту, котёл и огневые бочки — дрова под рукой.
# Поленница сложена вплотную к восточной стене, рядом телега, на которой возят дрова и урожай, и бочка.
mplace("r_logs", 90, 44)
mplace("firewood", 89, 45)
mplace("r_logs", 90, 46)
mplace("x_cart", 86, 48)                             # телега
mplace("barrel_wood", 89, 50)
mplace("w_sacks", 87, 50)

# ---- дюны снаружи: костёр Панка у калитки, тропа вдоль западной стены, огни на дороге
mplace("campfire", 85, 11, allow_reserved=True)      # костерок Панка в дюнах
mplace("r_logs", 86, 12, allow_reserved=True)
mplace("w_sacks", 84, 10, allow_reserved=True)
m.paint_ragged("E", 8, 9, 14, 73, depth=1)           # тропа вдоль западной стены
m.paint_ragged("E", 10, 68, 50, 73, depth=1)         # от дороги — на западную тропу
m.paint_ragged("E", 8, 8, 90, 11, depth=1)           # по дюнам — к калитке с севера
m.paint_ragged("E", 87, 11, 91, 15, depth=1)         # последний поворот к калитке
m.reserve(8, 7, 15, H - 2)                           # по тропам ничего не сеем…
m.reserve(8, 7, 91, 12)
m.reserve(87, 12, 91, 15)
for _sx, _sy in ((44, 42), (48, 67), (86, 10), (85, 13)):   # …и держим свободными клетки сюжетных гостей
    m.reserve(_sx, _sy, _sx, _sy)
mplace("x_fire_barrel", 50, 66)                      # огни вдоль дороги к воротам
mplace("x_fire_barrel", 57, 70)
mplace("r_streetlamp", 58, 63, allow_reserved=True)  # фонарь у ворот снаружи

# ---- кто где
# Ансельм — перед алтарём, лицом к залу; Эймос — в восточной нише келий; Искра — у кладбища, где её и
# ищет Панк; Марла — в трапезной у столов; послушники — один за столом, другой у колодца.
mnpc("anselm", 33, 23)
mnpc("amos", 86, 22)
mnpc("iskra", 59, 41)
mnpc("marla", 38, 54)
mnpc("acolyte_a", 30, 49)
mnpc("acolyte_b", 46, 41)
# караул: страж снаружи ворот (с ним договариваются о пропуске), страж изнутри у створок (ворота заперты —
# ключ у него), страж у кладбища, послушник в молельне, боец у палаток богомольцев. Кельи стерегут не ногами,
# а замком и ключом у Ансельма: у решётки стража нет — потому по восточной стене и можно пройти тихо.
menemy("cult_guard", 57, 66)
menemy("cult_guard", 69, 44)
menemy("cult_guard", 51, 58)
menemy("cultist", 30, 29)
menemy("cultist", 56, 52)

# ---- пустыня вокруг: сухие деревья, кусты, камни, кости — только за оградой
desert(m, 1, 1, 16, H - 2, trees=7, bushes=18, junk=6)
desert(m, 18, 1, 91, 15, trees=8, bushes=22, junk=6)      # дюны за северной стеной
desert(m, 93, 1, W - 2, H - 2, trees=9, bushes=22, junk=8)
desert(m, 18, 63, 50, H - 2, trees=4, bushes=12, junk=5)  # западнее дороги
desert(m, 58, 63, 92, H - 2, trees=4, bushes=11, junk=5)  # восточнее дороги
save(m, "data/maps/baker_mission.json", floors=FLOORS_TOWN, lights=MLIGHTS,
     gates=[{"prop": front_gate, "flag": "mission_gate_open",
             "msg": "Ворота миссии заперты изнутри. За решёткой — шатры, костёр и белые балахоны."},
            {"prop": back_gate, "flag": "mission_back_open", "pry": True,   # лом у героя всегда при себе
             "open_msg": "Вы поддеваете гнилой засов ломом. Калитка со скрипом подаётся."},
            {"prop": cell_gate, "flag": "cells_open", "key": "ключ от келий",
             "open_msg": "Ключ проворачивается в замке. Решётка кельи открыта.",
             "msg": "Решётка кельи на замке. Ключ — у брата-ключника."}],
     exempt=("anselm", "iskra", "amos", "marla", "acolyte_a", "acolyte_b"))


# ================================================================ 3. Окраина
# «Бейкер: окраина» — посёлок тех, кого город не пустил. Уличная карта выросла ×1.56 по стороне
# (76×52 → 119×81, как трасса и миссия); планировка не растянута, а построена по смыслу
# (docs/furnish/logic.md §1), обстановка — поштучная: place / pbox / ptable / oskin, никаких
# scatter и случайных куч посреди дворов. План зон, кто где и сценки — docs/furnish/baker.md, §3.
#
# Как тут живут (и почему расставлено именно так):
#   входят     — по старому шоссе с севера: асфальт с обочинами и двумя живыми фонарями; шоссе
#                кончается площадью у водонапорной башни, дальше — только глина; за площадью
#                посёлок начинается сразу, без ворот и забора — забора на всех не нашлось;
#   селятся    — одиннадцатью дворами, а не рядами: лачуги лепятся по две-четыре вокруг общего
#                очага или просто вокруг одного двора, у каждого двора свой быт (бельё, поленница,
#                бочка, ящик, палатка), а между дворами — кривые пыльные улочки, которые ломаются,
#                огибая чей-то сарай. Пустошь начинается за краем посёлка, внутри пустырей нет:
#                где земля пустовала — дровяной двор, глиняная яма, прикол для приезжих;
#   берут воду — у башни кран с бочкой, мокрое пятно, ведро, водовозная тележка и скамья (воду
#                берут и караваны с трассы); второй, старый источник — колодец на перекрёстке
#                проулка: с вёдрами не ходят через полкарты;
#   готовят    — в каждом дворе свой очаг: где котёл на всех (двор 4), где костёр, где бочка,
#                в которой жгут мусор (двор 2), где только фонарь — там греются у соседей.
#                У каждого пятна света видно, чем греются: ни одной «потолочной» лампы на улице;
#   спят       — в лачугах, палатках и бытовках; кому дома не досталось — в палатке во дворе;
#   работают   — гончар Савва у печи и глиняной ямы, радиолюбитель Ян у будки с антенной,
#                могильщик Кузьма на погосте, охотница Рита в дюнах между складом и свалкой,
#                беглый послушник Тимур в лачуге у свалки (folk_spots ниже); у главной улицы —
#                дровяной двор, где колют на зиму, и прикол с чужой телегой;
#   хлам       — свалка машин на юго-востоке разобрана штабелями: кузова в ряд, за ними торчат
#                контейнер и куча корпусов; между штабелями проезды, за проездом — сортировка
#                (длинные баки, верстак, кучи железа, колёс и бытового хлама), в глубине «гора
#                хлама» (её обыскивают) и крысы; баки для мусора — у южного края;
#   торгуют    — двор скупщика Холлиса в углу свалки: трейлер, тент, прилавок с весами и кассой
#                (весы и касса — в глубине столешницы), сундук за спиной, мото у навеса; Холлис
#                стоит за прилавком лицом к тому, кто подошёл со двора;
#   охраняют   — вход в склад «Бейкер-7» на северо-востоке: бетонная площадка, мешки с песком
#                двумя линиями с проходом к бронедвери, грузовик поперёк, два фонаря, стол караула
#                с фонарём и ящик с патронами, тент; в этом проходе деда и ждёт Эймос.
W, H = 119, 81
o = MapKit(W, H, start=(55, 3), seed=41)
OLIGHTS = []                          # «потолочных» ламп на улице нет: свет — от костров и фонарей
oplace, opbox, ooskin, optable, oswall, olamp, onpc, oenemy = helpers(o, OLIGHTS)

# ------------------------------------------------------------ земля
o.paint("a", 54, 0, 57, 20)                           # старое шоссе с трассы
o.paint("u", 53, 0, 53, 20)                           # обочины-тротуары
o.paint("u", 58, 0, 58, 20)
o.paint_ragged("E", 44, 21, 69, 34, depth=2)          # площадь у башни — утоптанная глина
o.paint("E", 54, 21, 57, 78)                          # главная улица посёлка
o.paint_ragged("E", 3, 7, 53, 61, depth=2)            # жилой запад: земля истоптана дворами
# Улочки между дворами — пыльные и кривые: посёлок рос сам, линейкой тут никто не мерил. Каждая
# ломается два-три раза, огибая чей-то забор; поэтому и дворы получаются разной глубины.
# Пустошь начинается за краем посёлка — внутри пустырей нет, есть задворки и улочки.
o.tunnel("d", [(53, 17), (38, 16), (24, 18), (10, 16), (4, 11)], width=3)    # верхняя улочка
o.tunnel("d", [(53, 32), (41, 30), (30, 32), (18, 31), (4, 33)], width=3)    # средняя
o.tunnel("d", [(53, 48), (40, 46), (24, 48), (12, 47), (4, 50)], width=3)    # нижняя
o.tunnel("d", [(53, 59), (36, 60), (20, 58), (4, 59)], width=3)              # к огородам
o.tunnel("d", [(30, 15), (29, 33), (29, 47), (31, 60)], width=2)             # проулок с севера на юг
o.paint("E", 69, 27, 86, 29)                          # дорога от площади к складу «Бейкер-7»
o.paint_ragged("Z", 86, 6, 114, 32, depth=2)          # бетонная площадка склада
o.paint("E", 58, 48, 118, 50)                         # служебная дорога вдоль свалки
o.paint_ragged("Z", 62, 52, 102, 76, depth=2)         # свалка: бетон, масло, ржавчина
o.paint_ragged("E", 104, 51, 117, 66, depth=1)        # двор Холлиса
o.paint_ragged("E", 4, 62, 31, 76, depth=2)           # огороды и задворки юга
o.portal([(x, 0) for x in range(54, 58)], "baker", (54, 73), "Трасса")
o.reserve(53, 0, 58, 20)                              # по шоссе и обочинам ничего не ставим
o.reserve(69, 27, 86, 29)                             # по дороге к складу
o.reserve(58, 48, 118, 50)                            # по служебной дороге свалки
o.reserve(95, 11, 99, 13)                             # пятачок перед бронедверью — свободен

# ------------------------------------------------------------ площадь у водонапорной башни
# Башня видна с шоссе — она и есть причина, по которой тут вообще живут. Под ней кран с бочкой,
# мокрое пятно, ведро, водовозная тележка (воду возят и караванам) и скамья для очереди.
oplace("r_water_tower_tall", 62, 22)
oplace("x_pipe", 64, 23)                              # кран под баком
oplace("barrel_wood", 64, 24)                         # бочка под струёй
ooskin("x_vd_wet0", 63, 24)                           # тут всегда мокро
oplace("bucket", 65, 25)
oplace("x_cart", 66, 24)
oplace("bench_16", 60, 26)                            # очередь ждёт на лавке
oplace("lantern_lit", 61, 25)
# Костёр для тех, кто только пришёл: греются, пока не найдут себе угол.
oplace("campfire", 47, 26)
oplace("x_cauldron", 48, 27)
oplace("r_logs", 46, 27)
oplace("bench_16", 44, 25)                            # лавки севернее костра: сидят лицом к огню
oplace("bench_16", 49, 25)
oplace("table_2", 52, 26)
optable("canteen", 52, 26, dx=-6, dy=-36)             # чья-то миска на столе
oplace("barrel_wood", 44, 31)
oplace("crate", 45, 31)
oplace("r_streetlamp", 52, 21)                        # последний живой фонарь шоссе — на повороте

# ------------------------------------------------------------ склад «Бейкер-7»: вход и караул
oplace("r_bunker", 95, 9)
o.portal([(97, 11)], "baker7", (4, 18), "Склад «Бейкер-7»",   # прямо под бронедверью
         requires={"flag": "baker7_open",
                   "msg": "Бронедверь склада. Табло: «ДОСТУП: ПЕРСОНАЛ МАРИПОЗЫ. СЕТЧАТКА · ГОЛОС · КОД»."})
o.terminal(100, 11, "baker7_lock")                    # замок-табло справа от двери
oplace("x_vault_sign", 94, 11)                        # табличка у входа
# Караул: две линии мешков с проходом к бронедвери, огонь по краям, фонари на флангах.
for _x in (89, 92, 102, 105):
    oplace("r_sandbag_row", _x, 14)
oplace("x_fire_barrel", 88, 16)
oplace("x_fire_barrel", 107, 16)
oplace("r_streetlamp", 86, 12)
oplace("r_streetlamp_b", 110, 12)
oplace("table_2", 92, 18)                             # стол караула: фонарь, кружки, журнал
optable("w_table_lantern", 92, 18, dx=-4, dy=-34)
oplace("chair_wood", 93, 18)
opbox("ammo_box", 90, 19, "ящик караула", {"патроны": 12, "бинт": 1})
oplace("r_army_truck", 100, 20)                       # грузовик поперёк площадки
oplace("canister", 99, 19)
oplace("r_tent_beige", 86, 20)                        # тент караула
oplace("r_derrick", 108, 8)                           # мачта связи за складом
oplace("crate_b", 92, 12)
oplace("barrel_wood", 106, 10)

# ------------------------------------------------------------ дюны: стан охотницы Риты
# Между складом и свалкой — открытый песок: лежбище, кости, ведро. Здесь её и искать.
oplace("r_tent_low", 97, 38)
oplace("bucket", 100, 38)
oplace("r_bones", 101, 39)
oplace("stool_1", 96, 39)
oplace("r_logs", 95, 37)

# ------------------------------------------------------------ свалка машин
# Разбирают не в шеренгу, а штабелями: кузова стоят в два ряда (задний виден из-за переднего),
# между штабелями — проезды, где ходит тележка; за проездом — сортировка: длинные баки, куда
# разносят железо, провода и стекло, верстак, а рядом кучи — их и обыскивают. В глубине, у «горы
# хлама», держатся крысы; баки вынесены к южному краю, туда и носят мусор из посёлка.
#
# Штабель 1 — кузова: остов к остову, с щелями в клетку — меж ними пролезают; за рядом,
# из-за крыш, торчат контейнер и куча корпусов — как штабель металла за машинами.
oplace("jt_trailer", 65, 52)
oplace("jt_pile_big2", 93, 52)
oplace("r_car_wreck", 63, 56)                         # остов, который можно обыскать
oplace("jt_car0", 68, 55)                             # мятая легковушка
oplace("r_van", 75, 56)
oplace("jt_truck0", 81, 55)                           # самосвал, кузов снят
oplace("r_camper", 88, 55)
oplace("r_tanker", 95, 56)
ooskin("x_vd_oil0", 71, 58)                           # масло натекло из-под фургона
ooskin("x_vd_oil1", 90, 58)
# Проезд 1 (y=57..59): по нему возят тележкой.
oplace("x_fire_barrel", 76, 59)                       # кто-то жжёт мусор — тут и свет
# Сортировка: баки под железо, провода и стекло, верстак с инструментом, шины — рядом.
oplace("jt_sort_bins", 65, 61)                        # длинный ряд баков
oplace("jt_workbench", 74, 61)                        # верстак разборщика
optable("toolbox_open", 74, 61, dx=-8, dy=-34)
oplace("r_barrels", 78, 62)
oplace("metal_sheets", 64, 63)                        # листы в стопку
oplace("pile_tires", 66, 64)
oplace("jt_tire_stack", 69, 64)
# Кучи — по одной на каждый вид добра, каждая своей высоты и формы.
oplace("jt_pile_big1", 86, 60)                        # гора железа
oplace("jt_pile_big0", 80, 62)                        # гора бытового хлама
oplace("jt_pile_big2", 93, 63)                        # гора колёс и корпусов
# Проезд 2 (y=65..68) — сквозной, от посёлка к дальнему краю.
# Разборка: машина на подпорках, снятое — тут же под рукой.
oplace("r_car_red", 65, 69)
oplace("pile_scrap", 65, 71)
oplace("r_pickup", 70, 70)
oplace("jt_jpile0", 74, 71)
oplace("jt_jpile2", 77, 72)
oplace("r_junk_mound", 88, 69)                        # «гора хлама» — её обыскивают по квесту
oplace("jt_scrap0", 84, 71)
oplace("jt_scrap1", 93, 72)
oplace("r_moto", 96, 69)
# Проезд 3 (y=73..74).
oplace("r_dumpster", 66, 75)                          # баки — у края, туда же и носят мусор
oplace("r_dumpster_b", 72, 76)
oplace("r_bin_b", 80, 75)
oplace("pile_tires", 84, 76)
oplace("r_bones", 98, 75)                             # сбитый зверь в дальнем углу

# ------------------------------------------------------------ двор скупщика Холлиса
# Трейлер, под навесом прилавок с весами. Холлис стоит за прилавком — посетитель подходит с юга,
# со двора, и видит его лицом (спрайт у него один, лицом к камере). Весы и касса — в глубине
# столешницы, чтобы железо не лежало у посетителя под носом; сундук — за спиной Холлиса.
# Товар (шины, бочки, железо) — по двору, не у прилавка; за забором — мото, его личный.
oplace("r_rv", 105, 53)                               # его трейлер
oplace("jt_tarp", 112, 53)                            # тент-навес: под ним его товар
oplace("x_scales", 108, 55)                           # прилавок с весами для железа
optable("x_register", 108, 55, dx=20, dy=-40)         # касса — в глубине прилавка
optable("junk_small_1", 108, 55, dx=-20, dy=-40)      # что взвешивают
opbox("metal_chest", 110, 54, "сундук Холлиса",
      {"крышки": 60, "стимулятор": 2, "балахон послушника": 1}, owner="hollis")   # за спиной
oplace("crate_b", 110, 55)
oplace("sack", 111, 56)
o.terminal(112, 55, "hollis_radio")                   # рация: с кем-то он говорит каждый вечер
oplace("r_moto", 106, 56)                             # его мото — у навеса
oplace("x_fire_barrel", 105, 59)                      # свет и тепло его двора (у забора, не в проходе)
oplace("lantern_lit", 107, 54)                        # фонарь у двери трейлера
oplace("pile_tires", 111, 58)                         # товар: шины
oplace("r_barrels", 112, 60)
oplace("pile_scrap", 109, 61)                         # товар: железо
oplace("crate", 114, 54)
oplace("cardboard", 115, 55)
for _y in range(52, 67):                              # забор вокруг двора, вход — с дороги, с севера
    oplace("x_fs_wood", 104, _y)
for _x in range(105, 118):
    oplace("x_fs_wood", _x, 66)

# ------------------------------------------------------------ лачуга Тимура у свалки
# Беглый послушник живёт на самом краю свалки: доска, костёр, тряпьё, ведро.
oplace("r_cabin_b", 59, 54)
oplace("campfire", 62, 56)
oplace("r_logs", 63, 57)
oplace("pile_rags", 59, 57)
oplace("bucket", 61, 56)

# ------------------------------------------------------------ радиобудка Яна
# Консервная будка, антенна из столба, стол с приёмником: «ты мешаешь волне».
oplace("r_shed_tin", 34, 49)
oplace("r_pole_wire", 37, 49)                         # антенна
oplace("table_2", 35, 52)
optable("x_radio", 35, 52, dx=-4, dy=-36)
oplace("chair_wood", 36, 52)
oplace("crate_b", 33, 51)
oplace("lantern_lit", 37, 51)

# ------------------------------------------------------------ гончарня Саввы
# Печь из обломков чужих домов, стол с посудой, бочка с водой, тележка с глиной.
oplace("r_shed_tin", 5, 48)
oplace("w_forge", 9, 49)                              # печь: горит и вечером светит
oplace("table_2", 11, 49)
optable("junk_small_1", 11, 49, dx=-6, dy=-36)        # сырые горшки на столе
oplace("barrel_wood", 8, 51)
oplace("x_cart", 11, 51)                              # тележка с глиной
oplace("sack", 13, 52)
oplace("bucket", 10, 51)

# ------------------------------------------------------------ посёлок: одиннадцать дворов
# Посёлок вырос сам, а не по плану. Лачуги лепятся по две-четыре вокруг общего очага или двора,
# между дворами — кривые пыльные улочки (покрашены выше). У каждого двора свой быт, и он не
# повторяет соседний: где-то верёвка с бельём поперёк двора и корыто, где-то поленница и тележка,
# где-то только ящик у двери. У каждой лачуги в двух шагах от порога есть то, за чем выходят:
# дрова, вода, ведро, тряпьё; в каждом дворе — одна-две вещи, которые можно обыскать.
# Лачуги стоят северной стороной двора, а не вкруг него: спрайт у них один — лицом к камере,
# дверью на юг (logic.md §2а), поэтому двор всегда перед дверью, а не за спиной.
#
# Кто где живёт (для src/ambient.py и для того, кто будет тут ходить):
#   двор 1 «у шоссе»      — старик с сундуком и семья впятером в большом сарае;
#   двор 2 «у палатки»    — те, кому лачуг не досталось: палатка и бочка, в которой жгут мусор;
#   двор 3 «за проулком»  — четыре лачуги, бельё и фонарь на столбе;
#   двор 4 «общий котёл»  — варят на всех: котёл, лавки, стол с мисками;
#   двор 5 «у проулка»    — две лачуги и палатка, живут тихо;
#   двор 6 «у площади»    — те, кто побогаче: очаг во дворе и бельё на две семьи;
#   двор 7 «нижний запад» — три лачуги, тряпьё и фонарь у стены;
#   двор 8 «у колодца»    — южный, к огородам: огневая бочка, мешки;
#   двор 9 «у радиобудки» — восточный, рядом с Яном и погостом;
#   двор 10 «у главной улицы» — последний двор перед шоссе;
#   двор 11 «у огородов»  — палатки и лачуги тех, кто держит огород.

# --- двор 1 «у шоссе» (4..22, 8..15): общий очаг, бельё поперёк двора
oplace("r_shanty_big", 4, 8)                          # большой сарай: живут впятером
oplace("r_shack_tin", 10, 9)                          # жестяная, крыша из старых вывесок
oplace("r_cabin_b", 16, 10)                           # сруб в две клетки
oplace("r_house_wood", 20, 9)                         # дощатый домик у края
oplace("campfire", 8, 13)                             # общий очаг двора
oplace("r_logs", 7, 13)                               # дрова под рукой
oplace("stool_1", 7, 12)                              # табуреты у огня
oplace("stool_3", 9, 12)
oplace("bk_laundry", 11, 14)                          # верёвка с бельём между лачугами
oplace("bucket", 10, 15)
oplace("barrel_wood", 16, 13)                         # бочка под дождь
oplace("crate", 18, 12)                               # ящик у двери старика
opbox("metal_chest", 19, 13, "сундук старика", {"крышки": 12, "бинт": 1})   # его пожитки — под рукой, не шкаф на улице
oplace("sack", 21, 12)
oplace("lantern_lit", 13, 12)                         # фонарь между лачугами — свет двора

# --- двор 2 «у палатки» (25..37, 9..15)
oplace("r_shack", 25, 9)
oplace("r_shack_f", 30, 11)
oplace("r_shack_e", 34, 9)
oplace("r_tent_green", 26, 13)                        # палатка: живёт тот, кому лачуги не досталось
oplace("x_fire_barrel", 31, 14)                       # в бочке жгут мусор — свет и тепло
oplace("r_logs_b", 33, 14)
oplace("crate_b", 28, 14)
oplace("pile_cloth", 36, 13)                          # тряпьё сушится у стены
oplace("bucket", 30, 15)

# --- двор 3 «за проулком» (38..52, 9..15)
oplace("r_house_wood", 38, 10)
oplace("r_cabin_c", 42, 9)
oplace("r_shed_tin_b", 45, 11)                        # сарай прилепился к домику
oplace("r_shack_g", 49, 10)
oplace("bk_laundry", 40, 14)
oplace("barrel_wood", 47, 14)
oplace("crate", 48, 13)
oplace("stool_2", 50, 13)
oplace("lantern_lit", 44, 14)

# --- двор 4 «общий котёл» (4..15, 19..28): тут варят на всех
oplace("r_shanty", 4, 19)
oplace("r_hut", 8, 19)
oplace("r_cabin_d", 12, 19)
oplace("campfire", 9, 23)
oplace("x_cauldron", 10, 24)                          # котёл над огнём
oplace("r_logs", 8, 23)
oplace("bench_16", 7, 22)                             # лавки севернее огня: лицом к нему
oplace("bench_16", 11, 22)
oplace("table_2", 13, 23)                             # где режут и раскладывают
optable("canteen", 13, 23, dx=-4, dy=-38)
oplace("crate", 6, 24)                                # посуда в ящике
oplace("barrel_wood", 14, 25)                         # вода для варева
oplace("bucket", 12, 26)

# --- двор 5 «у проулка» (18..27, 20..28)
oplace("r_shanty_big", 18, 20)
oplace("r_cabin_b", 24, 22)
oplace("r_tent_low", 25, 25)
oplace("bk_laundry", 20, 26)
oplace("crate_b", 22, 27)
oplace("barrel_wood", 26, 27)
oplace("lantern_lit", 23, 25)

# --- двор 6 «у площади» (30..43, 19..28)
oplace("r_shack", 31, 21)
oplace("r_shed_tin", 36, 22)
oplace("r_tent_big", 39, 19)
oplace("r_cabin_b", 42, 22)
oplace("campfire", 34, 26)
oplace("bench_16", 33, 25)
oplace("r_logs", 35, 27)
oplace("bk_laundry", 38, 27)
oplace("barrel_wood", 43, 26)

# --- двор 7 «нижний запад» (4..15, 35..44)
oplace("r_shack_e", 4, 36)
oplace("r_cabin_d", 7, 37)
oplace("r_shed_tin", 11, 36)
oplace("lantern_lit", 9, 41)
oplace("r_logs", 6, 41)
oplace("barrel_wood", 13, 41)
oplace("bucket", 8, 43)
oplace("clothes_72", 12, 43)                          # чьё-то тряпьё у стены

# --- двор 8 «у колодца», южный (18..25, 37..44)
oplace("r_shack_f", 18, 38)
oplace("r_cabin_c", 22, 41)
oplace("x_fire_barrel", 20, 43)
oplace("pile_bags", 24, 38)
oplace("stool_4", 19, 41)

# --- двор 9 «у радиобудки» (31..43, 35..44)
oplace("r_shack", 31, 36)
oplace("r_cabin", 35, 38)
oplace("r_tent_beige", 38, 36)
oplace("r_shed_tin_b", 32, 41)
oplace("campfire", 37, 42)
oplace("r_logs", 40, 42)
oplace("barrel_wood", 42, 40)
oplace("bucket", 36, 43)

# --- двор 10 «у главной улицы» (45..52, 36..44)
oplace("r_cabin_b", 46, 36)
oplace("r_shack_blue", 49, 38)
oplace("bk_laundry", 47, 41)
oplace("lantern_lit", 51, 40)
oplace("barrel_wood", 45, 42)

# --- двор 11 «у огородов» (14..30, 54..58)
oplace("r_tent_big", 14, 56)
oplace("r_shack_g", 19, 55)
oplace("r_shack_e", 23, 57)
oplace("r_shed_tin_b", 26, 55)
oplace("bk_laundry", 15, 58)                          # бельё сушат у самого огорода
oplace("barrel_wood", 29, 57)
oplace("bucket", 21, 57)
oplace("x_outhouse", 30, 58)                          # сортир — на отшибе, у дворов
oplace("bk_fence", 23, 12)                            # заборчик между двумя дворами
oplace("bk_fence", 23, 13)

# ------------------------------------------------------------ огородик у дворов (15..25, 50..53)
# Между нижней улочкой и дворами — маленький огородик, обнесённый жердями: тут растёт то, что
# нужно к столу каждый день, а общий огород за посёлком — на зиму. Калитка против дорожки.
for _x in (16, 18, 24):
    oplace("bk_fence", _x, 50)                        # северный забор с калиткой 20..23
for _x in (16, 18, 20, 22, 24):
    oplace("bk_fence", _x, 53)                        # южный
for _y in (51, 52):
    oplace("bk_fence_v", 15, _y)
    oplace("bk_fence_v", 25, _y)
oplace(BEDS[0], 17, 51)                               # капуста
oplace(BEDS[5], 21, 51)                               # высокая ботва
oplace(BEDS[3], 23, 51)                               # грядка с цветами — для пчёл
oplace("sack", 17, 52)                                # мешок с семенами на грядке
oplace("barrel_wood", 24, 52)

# ------------------------------------------------------------ дровяной двор (38..51, 50..56)
# За огородами, у самой главной улицы: сюда свозят и колют дрова на всю зиму. Сарай под доски,
# поленницы под навесом и без, тележка, бочка. Тут же и столяр что-то мастерит для посёлка.
oplace("r_shed_tin", 47, 52)                          # сарай: доски и инструмент
oplace("r_awning", 40, 52)                            # навес над поленницей
oplace("r_logs", 39, 53)
oplace("r_logs_b", 41, 53)
oplace("plank_block", 43, 53)                         # доски в штабель
oplace("r_planks", 45, 53)
oplace("r_planks_b", 38, 55)
oplace("x_cart", 42, 55)                              # тележка: возят дрова
oplace("barrel_wood", 46, 55)
oplace("lantern_lit", 44, 51)                         # фонарь над поленницей
oplace("stool_4", 48, 55)

# ------------------------------------------------------------ глиняная яма Саввы (4..10, 52..57)
# За гончарней — яма, из которой берут глину: мокрое пятно, ведро, лопата, дрова для печи.
ooskin("dirt_patch", 6, 55)
oplace("bucket", 7, 54)
ooskin("shovel", 5, 55)
oplace("r_logs", 8, 56)                               # дрова для обжига
oplace("barrel_wood", 4, 56)

# ------------------------------------------------------------ прикол у главной улицы (49..52, 50..57)
# Кто приехал в посёлок с телегой или скотиной — встаёт здесь, у самой улицы: коновязь, сено,
# телега, вода. Дальше с телегой в переулки не сунешься.
oplace("w_wagon", 49, 50)                             # чужая телега (её и обыскивают)
oplace("w_hitch", 50, 53)                             # коновязь
oplace("w_hay", 52, 51)
oplace("barrel_wood", 51, 56)
oplace("bucket", 52, 57)

# ------------------------------------------------------------ колодец на перекрёстке
# Старый колодец: сюда идут с вёдрами изо всех дворов, тут и стоят, пока набирается вода.
# Скамья — сбоку от колодца, а не «вразнобой посреди площадки»: спрайт скамьи только лицом
# к камере, севернее колодца её заслонил бы сам сруб с крышей.
oplace("bk_well", 26, 33)
oplace("bench_16", 24, 33)                            # ждут очереди, глядя на воду
oplace("bucket", 27, 34)
oplace("stool_1", 28, 34)                             # кто-то присел у ведра
oplace("x_cart", 29, 33)                              # водовозная тележка
oplace("barrel_wood", 28, 36)

# ------------------------------------------------------------ костёр у огородов и огород
oplace("campfire", 10, 61)                            # тут варят то, что сняли с грядок
oplace("x_cauldron", 11, 61)
oplace("bench_16", 9, 60)
oplace("r_logs", 12, 61)
oplace("bucket", 13, 61)
oplace("x_outhouse", 33, 62)
# Огород общий, обнесён целиком: калитка против дорожки, грядки рядами, вода — бочка под дождём.
for _x in (4, 6, 8, 10, 12, 14, 18, 20, 22, 24, 26, 28, 30):   # северный забор, калитка 16..17
    oplace("bk_fence", _x, 62)
for _x in range(4, 32, 2):                                     # южный забор
    oplace("bk_fence", _x, 76)
for _y in range(63, 76):                                       # западный и восточный
    oplace("bk_fence_v", 3, _y)
    oplace("bk_fence_v", 31, _y)
for _i, _x in enumerate((5, 8, 11, 14, 17, 20, 23, 26)):       # восемь грядок семи видов
    oplace(BEDS[_i % len(BEDS)], _x, 66)
for _i, _x in enumerate((5, 8, 11, 14, 17, 20)):               # второй ряд — другие
    oplace(BEDS[(_i + 3) % len(BEDS)], _x, 72)
oplace("barrel_wood", 29, 64)                         # бочка под дождь у калитки
oplace("bucket", 28, 64)
oplace("x_cart", 26, 63)                              # тележка за урожаем
ooskin("shovel", 18, 70)                              # лопата на дорожке
oplace("barrel_wood", 5, 74)                          # вторая бочка с водой — у дальнего края
oplace("bucket", 6, 74)
oplace("w_hay", 4, 70)                                # тюк сена/соломы на мульчу, у забора

# ------------------------------------------------------------ погост Кузьмы
# Хоронят тут же, за огородами: крест и разрытая могила парой, надгробия рядком, фонарь у входа.
for _gx in (40, 44, 48):
    oplace("x_cross", _gx, 66)
    oplace("x_grave", _gx, 67)
for _gx in (42, 46):
    oplace("x_cross", _gx, 71)
    oplace("x_grave", _gx, 72)
oplace("x_tombstone", 38, 74)
oplace("x_tombstone", 43, 74)
ooskin("shovel", 41, 73)
oplace("bucket", 45, 73)
oplace("lantern_lit", 39, 65)

# ------------------------------------------------------------ свет по улицам
oplace("lantern_lit", 53, 36)                         # фонари на главной улице
oplace("lantern_lit", 58, 44)
oplace("x_fire_barrel", 52, 17)                       # огневые бочки на концах переулков
oplace("x_fire_barrel", 52, 59)

# ------------------------------------------------------------ кто где
onpc("hollis", 108, 54)                               # за прилавком, лицом к дороге
onpc("baker_folk_a", 27, 32)                          # у колодца с ведром
onpc("baker_folk_b", 16, 23)                          # у общего котла
onpc("baker_folk_c", 73, 64)                          # разбирает хлам на свалке
onpc("baker_folk_d", 109, 56)                         # у прилавка Холлиса, лицом к нему
onpc("baker_kid_b", 64, 25)                           # у крана под башней
oenemy("rat", 86, 70)                                 # крысы у «горы хлама»
oenemy("rat", 91, 71)

# места жителей-персонажей (src/ambient.py): каждый у своего дела, а не где попало
FOLK_SPOTS = {"savva": (10, 50),                      # у печи
              "ulyana": (48, 25),                     # у костра на площади
              "timur": (61, 55),                      # у своей лачуги на краю свалки
              "rita": (99, 39),                       # в дюнах
              "yan": (36, 51),                        # у приёмника
              "kuzma": (50, 73),                      # на погосте
              "critter:dog": [(76, 58), (44, 20)],    # собаки — на свалке и во дворе
              "critter:cat": [(107, 57)]}             # кошка — у трейлера Холлиса
_reach = o.reachable()
for _k, _t in FOLK_SPOTS.items():
    for _c in ([_t] if not _k.startswith("critter:") else _t):
        assert tuple(_c) in _reach and tuple(_c) not in o.blocked, f"место жителя {_k} {_c} занято"

# ------------------------------------------------------------ пустошь по краям
desert(o, 1, 1, 52, 6, trees=3, bushes=8, junk=4)          # северо-запад
desert(o, 59, 1, 84, 6, trees=2, bushes=6, junk=3)         # север между шоссе и складом
desert(o, 112, 1, 118, 40, trees=2, bushes=6, junk=3)      # восточная кромка
desert(o, 86, 33, 118, 46, trees=3, bushes=10, junk=6)     # дюны между складом и свалкой
desert(o, 60, 31, 85, 46, trees=4, bushes=12, junk=8)      # пустошь между посёлком и свалкой
desert(o, 58, 60, 61, 76, trees=1, bushes=4, junk=2)       # полоса у лачуги Тимура
desert(o, 32, 62, 35, 76, trees=1, bushes=4, junk=2)       # между огородом и погостом
desert(o, 33, 77, 118, 79, trees=2, bushes=6, junk=3)      # южная кромка
desert(o, 1, 30, 2, 79, trees=1, bushes=3, junk=1)         # западная кромка
save(o, "data/maps/baker_outskirts.json", exempt=("hollis",), floors=FLOORS_TOWN,
     folk_spots={k: ([list(t) for t in v] if k.startswith("critter:") else list(v))
                 for k, v in FOLK_SPOTS.items()})

city.save()          # data/props/baker.json — объекты из наборов, что поставлены на картах выше
