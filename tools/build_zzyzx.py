"""
Зайзикс — курорт «целебных источников» у солёного озера Сода (реальное место: Zzyzx Mineral Springs
Кёртиса Спрингера, 1944 год, — жульничество с «чудо-водой»). Сценарий — docs/story.md, раздел 8.

  zzyzx          «Зайзикс: Бульвар Мечты» (70×50): въезд по старой дороге с запада, мощёный бульвар
                 с пальмами к озеру Туэнде (оазис с лодками), купальни и «Замок» Спрингера к северу,
                 лагерь паломников и рынок к югу, глинобитные дома целителей, колодец.
  zzyzx_bath     купальни (интерьер): приёмная, раздевалки, зал с целебным бассейном, кабинет
                 целителя (терминал), насосная (люк вниз — по ключу смотрителя Гаса).
  zzyzx_hotel    «Замок» Спрингера (интерьер): холл, столовая, гостевые номера, покои Спрингера.
  zzyzx_cistern  цистерна под купальнями: каналы с водой, фильтр Vault-Tec «Чистый лист», терминал.

Наборы: desert-town (destown), desert-natural-environment (desnat), backrooms-poolcore (pool),
modern-hotel (hotel), nuclear-bunker-interior (nbunk), wasteland-laboratory (wlab).
Запуск из папки game_project:  .venv/bin/python tools/build_zzyzx.py
"""
import json
import os

from citykit import City, CityMap
from src import props as _props
from vaultkit import Lamps

city = City("zzyzx", "Зайзикс")
LM = Lamps(city)


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


# ------------------------------------------------------------ объекты
PALMS = [P(f"zz_palm{i}", f"pk:desnat/desnat_4_{n:03d}", foot=[1, 1]) for i, n in enumerate((49, 50, 51, 52))]
BUSHES = [P(f"zz_bush{i}", f"pk:desnat/desnat_4_{n:03d}", block=False) for i, n in enumerate((20, 21, 24, 46, 47, 48))]
CACTI = [P(f"zz_cactus{i}", f"pk:destown/destown_1_{n:03d}", foot=[1, 1]) for i, n in enumerate((0, 2, 5, 28, 39, 66))]
DEAD = [P(f"zz_deadtree{i}", f"pk:destown/destown_1_{n:03d}", foot=[1, 1]) for i, n in enumerate((8, 9, 43, 96))]
ROCKS = [P(f"zz_rock{i}", f"pk:destown/destown_2_{n:03d}") for i, n in enumerate((46, 47, 60, 67))]
HOUSE_A = P("zz_adobe_a", "pk:destown/destown_3_000", foot=[3, 2], sight=True)
HOUSE_B = P("zz_adobe_b", "pk:destown/destown_3_002", foot=[3, 2], sight=True, scale=1.3)
HOUSE_C = P("zz_adobe_c", "pk:destown/destown_3_003", foot=[4, 2], sight=True, scale=1.3)
HOUSE_D = P("zz_adobe_d", "pk:destown/destown_3_012", foot=[2, 2], sight=True, scale=1.3)   # домик поменьше
HOUSE_BIG = P("zz_adobe_big", "pk:destown/destown_3_014", foot=[4, 2], sight=True)
TENT_BIG = P("zz_tent_big", "pk:destown/destown_3_004", foot=[3, 2], sight=True)
TENT_AWN = P("zz_tent_awning", "pk:destown/destown_3_011", foot=[4, 2], sight=True)
TENT = P("zz_tent", "pk:destown/destown_3_015", foot=[2, 2], sight=True)   # шатёр: пятно 3×3 (prop_scale 1.5)
TENT_S = P("zz_tent_small", "pk:destown/destown_3_018", foot=[2, 1])       # пятно 3×2
STALL = P("zz_stall", "pk:destown/destown_4_010", foot=[2, 1], keybg=True)      # прилавок, красный навес
STALL_B = P("zz_stall_b", "pk:destown/destown_4_011", foot=[2, 1], keybg=True)  # прилавок, холщовый навес
RUG = P("zz_rug", "pk:destown/destown_3_008", block=False, layer="floor")
WELL = P("zz_well", "pk:desnat/desnat_3_006", foot=[2, 1])
WELL_B = P("zz_well_b", "pk:desnat/desnat_3_027", foot=[2, 1])
POTS = [P(f"zz_pot{i}", f"pk:desnat/desnat_3_{n:03d}", search="shelf", title="кувшин") for i, n in enumerate((16, 41, 59, 85))]
CRATE = P("zz_crate", "pk:desnat/desnat_3_018", search="crate", title="ящик")
BARREL = P("zz_barrel", "pk:desnat/desnat_3_014", search="junk", title="бочка")
FIRE = P("zz_campfire", "pk:destown/destown_3_034",
         light={"r": 130, "color": [255, 150, 70], "at": [0.5, 0.5], "flicker": 0.45, "flame": True})
LAKE = "pk:destown/p5/8,5,8,11"
ADOBE_WALL = [P(f"zz_wall{i}", f"pk:destown/p3/{x},8,2,1", foot=[2, 1], keybg=True) for i, x in enumerate((6, 8, 10, 12))]
ADOBE_GATE = P("zz_gate_arch", "pk:destown/p3/12,10,4,2", foot=[4, 1], sight=True, keybg=True,
               holes=[[1, 0], [2, 0]])               # арка: проход 2 клетки посередине (пятно не запирает)
RUG_R = P("zz_rug_red", "pk:destown/p3/2,11,2,1", block=False, layer="floor", keybg=True)
RUG_B = P("zz_rug_blue", "pk:destown/p3/4,11,2,1", block=False, layer="floor", keybg=True)
SACKS = [P(f"zz_sack{i}", f"pk:destown/p3/{x},8,1,1", search="crate", title="мешок") for i, x in enumerate((2, 3))]
SKIN = [P(f"zz_skin{i}", f"pk:destown/p3/{x},11,1,1", block=False, layer="floor", keybg=True) for i, x in enumerate((5, 6))]
REEDS = [P(f"zz_reeds{i}", f"pk:desnat/p4/{x},{y},1,1", block=False, keybg=True) for i, (x, y) in enumerate(((8, 10), (9, 10), (7, 12), (9, 12)))]
LANTERN_ZZ = P("zz_lantern", "pk:destown/p4/14,4,1,1", block=False, keybg=True, light={"r": 110, "color": [255, 190, 110], "at": [0.5, 0.4], "flicker": 0.25})

BED = P("ht_bed", "pk:hotel/hotel_1_007", foot=[2, 2])
BED_S = P("ht_bed_single", "pk:hotel/hotel_1_004", foot=[1, 2])
NIGHT = P("ht_nightstand", "pk:hotel/hotel_1_000", search="drawer", title="тумбочка")
WARDROBE = P("ht_wardrobe", "pk:hotel/hotel_1_084", foot=[2, 1], sight=True, search="cloth", title="шкаф")
DESK = P("ht_desk", "pk:hotel/hotel_1_086", foot=[2, 1])
DESK_B = P("ht_desk_b", "pk:hotel/hotel_1_079", foot=[2, 1])
ARMCHAIR = P("ht_armchair", "pk:hotel/hotel_1_092")
LAMP = P("ht_lamp", "pk:hotel/hotel_1_102")
SINK = P("ht_sink", "pk:hotel/hotel_1_095")
TOILET = P("ht_toilet", "pk:hotel/hotel_1_096")
PLANT = P("ht_plant", "pk:hotel/hotel_1_127")
LOCKERS = P("zz_lockers", "pk:wschool/p1/6,12,2,2", foot=[2, 1], sight=True)
TANK = P("zz_tank", "pk:wlab/wlab_1_008", sight=True)
VATS = P("zz_vats", "pk:wlab/wlab_1_002", sight=True)
DESK_LAB = P("zz_desk_lab", "pk:wlab/wlab_1_012")
GEN = P("zz_generator", "pk:nbunk/nbunk_2_028")
TANKS_W = P("zz_water_tanks", "pk:nbunk/nbunk_2_021", sight=True)

SAND = ["pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1"]   # песок под цвет окружающей пустыни, без скачка
CRACK = ["noise:pk:destown/p2/8,0,1,1"]
COBBLE = cells("destown/p2", [(4, 0), (5, 0), (4, 1), (5, 1)])   # утоптанный гравий бульвара
TILE_W = ["pk:zcity/zcity_f1_23"]
TILE_B = ["pk:zcity/zcity_f1_22"]
WOOD = ["pk:hotel/hotel_f1_02"]
CARPET = ["pk:hotel/hotel_f1_03"]
METAL = cells("nbunk/p2", [(4, 8), (5, 9), (6, 10), (4, 10)])
POOL_WATER = "pk:pool/p1/4,4,4,2"
DIRTY_WATER = "pk:pool/p1/4,8,4,4"
SEWER_PIPE_ZZ = P("zz_pipes", "pk:sewer/sewer_1_042", foot=[2, 1])

# ---- рынок, лагерь, берег, улица: наборы west / bazaar / fishv / town50 / iresort / bcyber
# В destown этого нет: повозка, тележка, корыто, весы, бельё, лодки, сети, фонари 1950-х.
BENCH = "bench_7"                                                    # скамья, 2 клетки, лицом к камере
BENCH_N = "w_bench"                                                  # скамья спинкой к камере: сидят лицом на север
CANOPY_S = "r_awning"                                                # малый навес над столом (2 клетки)
PIPE_RUST = "nc_pipes"                                               # ржавая труба с коленом и течью
FLAG = "x_flag"                                                      # флажок на древке
POT = P("zz_pot_palm", "pk:bazaar/bazaar_3_206", foot=[1, 1])        # пальма в кадке на бульваре
JUG = P("zz_jug", "pk:destown/p3/3,6,1,1")                           # глиняный кувшин
JARS = P("zz_jars", "pk:bazaar/bazaar_2_048", search="shelf", title="кувшины")
BASKET = P("zz_basket", "pk:fishv/p1/12,2,2,2", foot=[2, 1])
HAY = P("zz_hay", "pk:west/west_1_004", block=False)                 # тюк сена
HIDE = P("zz_hide", "pk:destown/destown_3_023", block=False, layer="floor")
HIDE_B = P("zz_hide_b", "pk:destown/destown_3_033", block=False, layer="floor")
STALL_C = P("zz_stall_c", "pk:destown/destown_4_012", foot=[2, 1], keybg=True)   # прилавок, полосатый навес
CART = P("zz_cart", "pk:bazaar/bazaar_1_023", foot=[2, 1], sight=True)           # ручная тележка
TROUGH = P("zz_trough", "pk:west/west_1_016", foot=[2, 1])                       # корыто
SCALES = P("zz_scales", "pk:bazaar/bazaar_1_022", foot=[2, 1])                   # чашечные весы
LAUNDRY = P("zz_laundry", "pk:wfarm/p3/0,0,4,3", foot=[4, 1], keybg=True)        # бельё на верёвке
STOVE = P("zz_stove", "pk:west/west_2_018")                                      # чугунная печка
OUTHOUSE = P("zz_outhouse", "x_outhouse", foot=[1, 1], sight=True)               # сортир на отшибе
HERB = P("zz_herb", "pk:wfarm/p1/0,8,2,2", foot=[2, 1], keybg=True)              # грядка с травами
SIGN_BOARD = P("zz_sign_board", "pk:west/p1/12,4,2,2", foot=[2, 1], sight=True)  # доска на двух столбах
SIGN_ENTRY = P("zz_sign_road", "pk:zcity/zcity_3_035", foot=[1, 1], keybg=True)  # указатель со стрелкой
SIGN_MARKET = P("zz_neon_market", "pk:bcyber/bcyber_2_021", block=False,          # неоновая вывеска рынка
                light={"r": 90, "color": [255, 160, 90], "at": [0.5, 0.4], "flicker": 0.1})
GAZEBO = P("zz_gazebo", "pk:iresort/iresort_4_013", foot=[2, 2], sight=True)     # эстрада-беседка
RUG_SHOW = P("zz_rug_show", "pk:casino/p3/0,0,2,2", block=False, layer="floor")
PRAYER = P("zz_prayer", "pk:lhotel/p2/10,12,2,2", block=False, layer="floor")    # молитвенный коврик
FOUNTAIN = P("zz_fountain", "pk:bcyber/bcyber_2_013", keybg=True, scale=2.0,   # чаша фонтана в рост
             foot=[1, 1], light={"r": 80, "color": [150, 210, 255], "at": [0.5, 0.3]})
BASIN = P("zz_basin", "pk:destown/destown_3_027")                                # каменная чаша источника
PIPE = P("zz_pipe", "x_pipe", foot=[1, 1])                                       # труба от пруда
AWNING = TENT_AWN                                                                # навес над розливом
LOGS = [P("zz_logs_a", "r22_051", foot=[1, 1]), P("zz_logs_b", "r22_065", foot=[1, 1])]
PILLAR = P("zz_pillar", "pk:cult/cult_2_143", sight=True)                        # каменный столб
LAMP50 = P("zz_lamp50", "pk:town50/town50_1_120", foot=[1, 1],                   # фонарь 1950-х на столбе
           light={"r": 150, "color": [255, 210, 140], "at": [0.5, 0.1]})
FIRE_PIT = "hb_firepit"                                                          # огневая яма (в каталоге с огнём)
BOAT = P("zz_boat", "pk:fishv/p3/0,10,2,1", foot=[2, 1], block=False, layer="floor", keybg=True)
BOAT_B = P("zz_boat_b", "pk:fishv/p3/0,11,2,1", foot=[2, 1], block=False, layer="floor", keybg=True)
ROWBOAT = P("zz_rowboat", "pk:fishv/p2/6,12,2,4", foot=[2, 3], block=False, layer="floor")
SHED_BOAT = P("zz_boatshed", "pk:fishv/p4/12,8,2,3", foot=[2, 2], sight=True)    # лодочный сарай
NET = P("zz_net", "pk:fishv/fishv_1_012", block=False)                           # сеть на просушке
OARS = P("zz_oars", "pk:fishv/p1/2,6,2,2", block=False)                          # вёсла
NET_RACK = P("zz_net_rack", "pk:fishv/p2/12,4,2,2", foot=[2, 1])
PLANK_W = ["pk:zcity/zcity_f1_00"]                                               # доски причала
STONE_PLAZA = ["pk:apark/p2/8,0,1,1", "pk:apark/p2/9,0,1,1",
               "pk:apark/p2/8,1,1,1", "pk:apark/p2/9,1,1,1"]                       # каменные плиты
SACK = P("zz_sack", "pk:destown/p3/2,8,1,1")                                  # мешок на земле
BUCKET = "bucket"                                                                # ведро
LANTERN = "lantern_lit"                                                          # фонарь со стеклом (свет у него самого)
JUG_BIG = P("zz_jug_big", "pk:destown/p3/2,10,1,1")                             # большая амфора
TANK_FILTER = "zz_tank"                                                         # корпус фильтра под навесом

# ---- парадная часть: доски, огни, чаша, клумбы, вешала, шлагбаум (наборы west / cult / apark / wschool)
# В destown нет ни каменной чаши, ни лампад, ни клумб, ни гирлянд — берём из наборов cult / apark / wschool.
SIGN_WOOD = "zz_sign_board"                                        # доска на двух столбах
BOARD_SMALL = "x_board"                                            # вывеска-знак у двери
BILLBOARD = "by_billboard1"                                         # целый щит на двух столбах у въезда
GATE_BAR = "by_site_gate"                                          # шлагбаум-рогатка у ворот
TORCH = P("zz_torch", "pk:iresort/iresort_1_036", foot=[1, 1],   # факел на стойке у святыни
          light={"r": 130, "color": [255, 180, 90], "at": [0.5, 0.2], "flicker": 0.35, "flame": True})
CANDLES = P("zz_candles", "pk:cult/cult_2_068", foot=[1, 1], block=False,   # лампады у чаши
            light={"r": 70, "color": [255, 205, 130], "at": [0.5, 0.35], "flicker": 0.3, "flame": True})
LIGHTS = P("zz_lights", "pk:apark/apark_3_063", block=False,      # гирлянда ламп по террасе «Замка»
           light={"r": 120, "color": [255, 225, 170], "at": [0.5, 0.3], "flicker": 0.08})
CHALICE = "hb_small_well"                                          # каменная чаша с бортиком и водой
CARPET = "x_carpet"                                               # ковровая дорожка к дверям
RAIL = "bar_fence_a"                                               # барьер очереди
# Жердевая ограда одной породы: звено 2 клетки, вертикальное звено и торцевой столб (набор west).
# Прежние w_fence + side_fence("wood") давали сбоку «тонкие шесты» — ограда не читалась как ограда.
FENCE_RAIL = P("zz_rail", "pk:west/west_1_013", foot=[2, 1])        # звено по горизонтали, 2 клетки
FENCE_UP = P("zz_rail_v", "pk:west/west_1_015", foot=[1, 1])        # то же звено вдоль севера—юга
FENCE_END = P("zz_rail_c", "pk:west/west_1_014", foot=[1, 1])       # угол/торцевой столб
COACH = P("zz_coach", "pk:west/west_1_012", foot=[6, 2], sight=True)   # повозка гостей, видна колёсами
UMBRELLA = P("zz_umbrella", "pk:iresort/iresort_1_009", foot=[2, 1], sight=True)   # соломенный зонт
UMBRELLA_B = P("zz_umbrella_b", "pk:iresort/iresort_1_010", foot=[2, 1], sight=True)
PLANTER = "ar2_planter"                                            # белая кадка с пальмами
PLANTER0, PLANTER1 = "v15_planter0", "v15_planter1"                # кадки с травами у домов целителей
POT2 = "hb_palm_pot"                                               # пальма в кадке поменьше
FLOWERBED = "ws_flowerbed"                                         # клумба
HEDGE = "pr_hedge"                                                 # стриженая изгородь
FISH_RACK = "nd_fish_rack"                                         # вешала с рыбой
STATUE = "cu_statue"                                               # статуя основателя
TROUGH_W = "gs_trough"                                             # колода с водой
CAULDRON = "x_cauldron"                                            # котёл над огнём
CROSS = "x_cross"                                                  # крест у лазарета
TOMATO, CABBAGE = "v22_tomato", "v22_cabbage"                      # грядки огорода
TOMATO_B, CABBAGE_B = "v22_tomato_b", "v22_cabbage_b"


# ------------------------------------------------------------ помощники ручной расстановки
# Те же, что в tools/build_baker.py: явно поставленный предмет обязан встать и остаться там, куда его
# поставили; не встал — ошибка с причиной («блок», «мягкий предмет», «резерв», «заслоняет»).
def helpers(mk, lights):
    """place/pbox/oskin/ptable/swall/lamp/npc/enemy для карты mk (CityMap) и её списка света."""
    def pwhy(name, x, y, blocked=None, soft=None, reserved=None):
        foot = mk.footprint(name, x, y)
        blocked = mk.blocked if blocked is None else blocked
        soft = mk.soft_obj if soft is None else soft
        reserved = mk.reserved if reserved is None else reserved
        why = []
        if any(c in blocked for c in foot):
            who = {}
            for c in foot:
                if c in blocked:
                    who[str(c)] = next((p[0] for p in mk.props if c in mk.footprint(p[0], p[1], p[2])), "вода/стена")
            why.append("блок: " + str(who))
        if any(c in soft for c in foot):
            why.append("мягкий предмет: " + str([c for c in foot if c in soft]))
        if any(c in reserved for c in foot):
            why.append("резерв")
        h = mk.hides(name, x, y)
        if h:
            why.append(f"заслоняет {h[0]} ({h[1]}, {h[2]})")
        if not why:
            why.append("put отказал: перекрыл бы проход или мягкий предмет под ним")
        why.append("земля: " + "".join(mk.ground[b][a] for a, b in foot))
        return f"«{name}» не встал в ({x}, {y}): " + "; ".join(why)

    def _undo(snap):
        n_props, n_conts, blocked, soft_obj, reserved = snap
        del mk.props[n_props:], mk.containers[n_conts:]
        mk.blocked, mk.soft_obj, mk.reserved = blocked, soft_obj, reserved
        mk._reach = None

    def place(name, x, y, **kw):
        """Явная расстановка: предмет обязан встать и остаться там, куда его поставили (logic.md §2).
        ZZYZX_SOFT=1 — собрать все отказы разом (подбор мест), не падая на первом."""
        snap = (len(mk.props), len(mk.containers), set(mk.blocked), set(mk.soft_obj), set(mk.reserved))
        try:
            ok = mk.put(name, x, y, **kw)
        except AssertionError:                 # CityMap.put падает сам — считаем это отказом
            ok = False
        if ok and mk.props and mk.props[-1][1:3] == [x, y]:
            return True
        why = pwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
        _undo(snap)
        if os.environ.get("ZZYZX_SOFT") == "1":
            place.fails.append(why)
            return False
        raise AssertionError(why)

    def pbox(name, x, y, title, loot, **kw):
        """Ящик с нужной добычей — как place(): не встал, так с причиной."""
        snap = (len(mk.props), len(mk.containers), set(mk.blocked), set(mk.soft_obj), set(mk.reserved))
        try:
            mk.box(name, x, y, title, loot, **kw)
        except AssertionError:
            _undo(snap)
            raise AssertionError(pwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])) from None
        if mk.props[-1][1:3] == [x, y]:
            return True
        moved = mk.props[-1][1:3]
        _undo(snap)
        raise AssertionError(pwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
                             + f"; встал в ({moved[0]}, {moved[1]})")

    def oskin(name, x, y):
        """Мелочь на земле, которую топчут (лужа, пятно): не блокирует, но и в стену не лезет."""
        if not mk.put(name, x, y, check=False) or mk.props[-1][1:3] != [x, y]:
            raise AssertionError(pwhy(name, x, y))

    def ptable(name, x, y, dx=0, dy=-34):
        """Мелочь на столешнице: на клетке мебели, поднята в глубину столешницы (logic.md §2)."""
        assert (x, y) in mk.blocked, f"«{name}» в ({x}, {y}): под ним нет стола"
        mk.props.append([name, x, y, dx, dy, 1 - dy])

    def swall(name, x, y0, dx=0, dy=-40):
        """Настенное — только на целой стене (logic.md §2а)."""
        fw, fh = _props.info(name)["foot"]
        cells = [(x + i, y0 + j) for i in range(fw) for j in range(fh)]
        assert all(c in mk.blocked for c in cells), f"«{name}» в ({x}, {y0}): там нет целой стены"
        mk.props.append([name, x, y0 + 1, dx, dy])
        mk.soft_obj.add((x, y0 + 1))
        mk._reach = None

    def lamp(x, y, r=130, color=(255, 176, 96), flick=0.03):
        """Потолочная лампа без картинки — только для интерьеров. На улице пятен без предмета нет."""
        lights.append([x * 48 + 24, y * 48 + 24, r, list(color), flick])

    def npc(nid, x, y):
        assert (x, y) not in mk.blocked, f"NPC {nid} в ({x}, {y}) — клетка занята"
        mk.npcs.append([nid, x, y])
        mk.reserve(x, y, x, y)

    def enemy(kind, x, y):
        assert (x, y) not in mk.blocked, f"{kind} в ({x}, {y}) — клетка занята"
        mk.enemies.append([kind, x, y])
        mk.reserve(x, y, x, y)

    place.fails = []
    return place, pbox, oskin, ptable, swall, lamp, npc, enemy

# ================================================================ Бульвар Мечты
# Уличная карта выросла ×1.56 по каждой стороне: 70×50 → 109×78 (docs/furnish/logic.md §1). Планировка
# не растянута, а перестроена по смыслу: с запада — старая дорога и ворота с караулом; через весь курорт
# Бульвар Мечты с пальмами, фонтаном и эстрадой — к озеру Туэнде (набережная, причал, лодки). Севернее
# бульвара — купальни, источник «Сладкая вода» и «Замок» Спрингера; южнее, за саманной стеной-фасадом, —
# рынок и лагерь паломников, где живут те, ради кого курорт и стоит; юго-восток — глинобитные дома
# целителей. Колодец — на торговой улице, где сходятся рынок и лагерь. Расстановка поштучная:
# place/pbox (не встал — ошибка с причиной), случайного рассева посреди площадок нет.
#
# Зайзикс — витрина жулика: бульвар, купальни и «Замок» ухоженные и богатые (целые светлые фасады,
# колонны, ковровая дорожка, фонари, клумбы), а бедность — за стеной: лагерь паломников из куч шатров
# вокруг костров, рынок с товаром на прилавках, квартал целителей улочкой. Пальмы — только вдоль дорожек
# и на берегу: ни на ковриках, ни перед дверями.
W, H = 109, 78
z = CityMap(city, "zzyzx", "Зайзикс: Бульвар Мечты", W, H, start=(3, 38), seed=81, music="desert",
            world_pos=(1880, 1140))
z.floor_code("s", *SAND)
z.floor_code("k", *CRACK)
z.floor_code("p", *COBBLE)
z.floor_code("q", *STONE_PLAZA)
z.floor_code("w", *PLANK_W)                       # доски причала у воды
z.paint("s", 0, 0, W - 1, H - 1)
z.tint = None
place, pbox, oskin, ptable, swall, lamp, npc, enemy = helpers(z, [])

# Фасады витрины: в «целых» наборах генератор всё равно подмешивает куски с проломами
# (wall_concrete_brick — дыра в штукатурке, wall_brick_long — осыпавшийся угол). Курорт, который
# Спрингер показывает паломникам, облупленным быть не может: в наборе одна чистая стена — светлая
# штукатурка wall_concrete, её и берём обоим зданиям (logic.md §1). Дома различаются крышей, входом и
# убранством, а не материалом стен.
FACADE_PLASTER = {2: ["wall_concrete"]}            # ровная светлая стена без выбоин


def pond(cx, cy, rx, ry, wobble=0.12):
    """Вода карты: непроходима, берег и пену движок рисует сам (src/townmap.py _shore)."""
    z.blob("~", cx, cy, rx, ry, wobble=wobble)
    for wy in range(max(0, int(cy - ry * 2)), min(H, int(cy + ry * 2) + 1)):
        for wx in range(max(0, int(cx - rx * 2)), min(W, int(cx + rx * 2) + 1)):
            if z.ground[wy][wx] == "~":
                z.blocked.add((wx, wy))


def rail_h(x0, x1, y, gaps=()):
    """Жердевой забор по строке y: звенья по 2 клетки, нечётный хвост — торцевым столбом."""
    x = x0
    while x <= x1:
        if x in gaps:
            x += 1
            continue
        if x + 1 <= x1 and (x + 1) not in gaps:
            place(FENCE_RAIL, x, y)
            x += 2
        else:
            place(FENCE_END, x, y)
            x += 1


def rail_v(x, y0, y1, gaps=()):
    """Тот же забор вдоль севера—юга: вертикальные звенья, на концах — торцевые столбы."""
    for y in range(y0, y1 + 1):
        if y in gaps:
            continue
        place(FENCE_END if y in (y0, y1) else FENCE_UP, x, y)


# ---- земля курорта: дорога, бульвар, дворы, лагерь, квартал целителей
# Контуры ровные (paint, не paint_ragged): утоптанная земля лагеря и рынка не обрывается кляксой с вырезами,
# а тропы к колодцу, рынку и улочке целителей — светлый гравий по тёмной земле, их видно.
z.paint("p", 0, 36, 9, 40)                        # въезд с запада — утоптанный гравий до самых ворот
z.paint("q", 10, 36, 84, 40)                      # Бульвар Мечты: каменные плиты начинаются у ворот
z.paint("q", 17, 22, 38, 35)                      # двор купален — зал ожидания под открытым небом
z.paint("q", 44, 20, 52, 22)                      # плиты святыни у источника
z.paint("q", 58, 22, 82, 35)                      # парадный двор «Замка»
z.paint("q", 42, 34, 50, 42)                      # площадь у фонтана посреди бульвара
z.paint("q", 80, 36, 86, 43)                      # набережная: плиты у воды, дальше — песок пляжа
z.paint("k", 12, 44, 52, 53)                      # рынок за стеной
z.paint("k", 8, 54, 48, 72)                       # лагерь паломников
# квартал целителей: земля только там, где ей место, — полоса вдоль домов, приёмный двор, огород.
# Прежде это была одна клякса 33×25 клетки: под домами пустой утоптанный пустырь (замечание Claude).
z.paint("k", 56, 44, 88, 51)                      # улочка целителей: земля вдоль домов в обе стороны
z.paint("k", 58, 51, 77, 59)                      # приёмный двор за домами
z.paint("k", 76, 52, 87, 64)                      # огород и подход к берегу
z.paint("q", 30, 51, 36, 55)                      # площадка колодца на стыке рынка и лагеря
z.paint("p", 26, 44, 29, 50)                      # торговая улица от арки к колодцу
z.paint("p", 10, 60, 46, 61)                      # тропа через лагерь, между кучками
z.paint("p", 33, 56, 34, 61)                      # от колодца к тропе
z.paint("p", 34, 62, 35, 64)                      # ответвление к общему котлу
z.paint("p", 58, 44, 60, 49)                      # от восточной арки в квартал целителей
z.paint("p", 58, 48, 86, 50)                      # улица целителей: дома лицом к ней
z.paint("q", 81, 51, 82, 54)                      # мощёная дорожка от улицы к калитке огорода
z.reserve(0, 36, 84, 40)                          # по бульвару и въезду ничего не ставим
z.reserve(82, 36, 84, 42)                         # и по дорожке набережной
for _y in range(34, 43):                          # кроме площади у фонтана: там стоит чаша
    for _x in range(42, 51):
        z.reserved.discard((_x, _y))
z.exits = [(0, y) for y in range(37, 40)]

# озеро Туэнде на востоке — вода уходит за край карты; у источника — пруд «Сладкая вода»
z.floor_code("~", *["pk:mport/p1/8,4,1,1", "pk:mport/p1/9,4,1,1",
                    "pk:mport/p1/10,4,1,1", "pk:mport/p1/11,4,1,1"])
z.water_codes = tuple(set(getattr(z, "water_codes", ())) | {"~"})
pond(99, 38, 12, 15, wobble=0.08)                 # озеро
pond(48, 16, 6, 3.2, wobble=0.16)                 # пруд у источника
z._palm = "zz_palm0"

# ------------------------------------------------------------ въезд с запада
# Дорога из пустоши упирается в ворота: пилоны стоят ровно на линии плит, по сторонам — короткие
# крылья белой стены, за ними фонари; будка караула — в трёх шагах от дороги, с навесом-навесом нет,
# со столом, за которым записывают входящих, и огневой ямой. Гравий кончается там, где начинается
# брусчатка, — в створе ворот, а не прямоугольником посреди песка.
z.side_wall("concrete", "w", 9, 31, 35)           # северное крыло стены у ворот
z.side_wall("concrete", "w", 9, 41, 42)           # южное — до саманной стены рынка
z.paint("p", 10, 36, 11, 40)                      # створ ворот: ещё гравий, плиты — с x=12
place(PILLAR, 10, 36, allow_reserved=True)        # пилоны ворот — по краям дороги
place(PILLAR, 10, 40, allow_reserved=True)
place(LAMP50, 8, 35)                              # фонари на крыльях стены
place(LAMP50, 8, 41)
place(POT, 13, 35)                                # пальмы в кадках сразу за воротами
place(POT, 13, 41)
place(SIGN_WOOD, 12, 34)                          # доска «ЗАЙЗИКС. ЦЕЛЕБНЫЕ ИСТОЧНИКИ»
place(SIGN_ENTRY, 6, 41)                          # указатель со стрелкой на южной обочине
place(BILLBOARD, 2, 42)                           # щит с рекламой курорта — тем, кто идёт с пустоши
place(GATE_BAR, 12, 39, allow_reserved=True)      # шлагбаум на южной половине дороги
place(HOUSE_D, 5, 33)                             # будка караула у самых ворот
place("table_2", 8, 34)                           # стол, за которым записывают входящих
place("chair_0", 7, 34)                           # караульный сидит сбоку стола, лицом к дороге
place(FIRE_PIT, 3, 33)                            # огневая яма: ночи в пустыне холодные
place(BARREL, 4, 35)
place(SACK, 8, 32)

# ------------------------------------------------------------ Бульвар Мечты
# Фонари 1950-х через каждые шесть клеток, скамьи лицом на бульвар (с севера это правильно: скамья
# нарисована лицом к камере, то есть на юг, в бульвар). Вдоль северной обочины — кадки с пальмами: высокая
# пальма ростом в пять клеток накрыла бы лавки ожидальни, поэтому у купален и «Замка» они в кадках.
place(POT, 19, 35)
place(BENCH, 22, 35)
place(POT, 25, 35)
place(POT, 31, 35)
place(BENCH, 34, 35)
place(POT, 37, 35)
for x in (16, 28, 40):
    place(LAMP50, x, 35)
for x, y in ((15, 42), (21, 42), (33, 42), (39, 42), (51, 42),
             (63, 42), (69, 42), (75, 42)):
    place(PALMS[(x + y) % 4], x, y)
for x in (18, 30, 36, 48, 54, 66, 72, 78):
    place(LAMP50, x, 41)

# фонтан посреди бульвара — главный знак «процветания»: вода, которая льётся просто так
place(FOUNTAIN, 45, 37)                           # чаша фонтана посреди площади: вода льётся просто так
place(BENCH, 44, 35)
place(BENCH, 48, 35)
for x, y in ((42, 34), (50, 34), (42, 42), (50, 42)):
    place(POT, x, y)
place(FIRE_PIT, 42, 40)                           # жаровня у фонтана: вечером тут свет и люди
place(BARREL, 50, 37)

# эстрада: по вечерам играет оркестр, с неё же Спрингер говорит проповедь о воде
place(GAZEBO, 57, 34)
place(BENCH, 61, 35)                              # где сидят те, кто слушает проповедь
place(POT, 63, 34)

# ------------------------------------------------------------ киоск «чудо-воды»
# Два прилавка лицом на бульвар, за ними — кувшины, ящик с бутылями и бочка. Очередь стоит на площади
# перед фонтаном; кто не дошёл — сидит на скамье у аллеи. Всё это стоит на трубе от пруда (см. ниже).
place(STALL_B, 51, 35)
place(STALL, 54, 35)
place(SIGN_BOARD, 55, 34)                         # доска над прилавком: «ЦЕЛЕБНАЯ ВОДА»
pbox(CRATE, 47, 32, "бутыли с «чудо-водой»", {"вода Зайзикса": 3}, owner="springer")   # ящик у калитки двора
place(BARREL, 49, 32)
place(BENCH, 43, 41)                              # где ждут те, кому уже невмоготу стоять
place(LAMP50, 56, 35)                             # фонарь у прилавков чудо-воды


# ------------------------------------------------------------ купальни
# Здание с целым светлым фасадом (курорт, который Спрингер показывает, не облуплен: формат фасада —
# только чистые куски, см. FACADE_PLASTER). Перед входом — зал ожидания под открытым небом: два ряда
# лавок лицом ко входу (спинка к камере) под соломенными зонтами, пальмы в кадках по краям, касса с
# расписанием у двери, колода с питьевой водой, очередь к двери вдоль двух барьеров. Тележка с бельём —
# у служебной западной стены, бельё сушат на заднем дворе за домом: в центре площади не склад и не
# прачечная.
z.building(19, 10, 18, 12, "concrete", south=(8,), sign="КУПАЛЬНИ", facade=FACADE_PLASTER)
z.portal([(27, 21), (28, 21)], "zzyzx_bath", (19, 23), "Купальни")
place(CARPET, 27, 22)                             # дорожка от дверей
place(CARPET, 27, 23)
place(POT, 25, 22)                                # кадки с пальмами по сторонам двери
place(POT, 30, 22)
place(PLANTER, 21, 22)                            # белые кадки с зеленью вдоль террасы
place(PLANTER, 34, 22)
place(LAMP50, 23, 22)                             # фонари на фасаде
place(LAMP50, 32, 22)
# касса, расписание и вода — восточная половина двора, у самой двери
place(STALL_B, 32, 24)                            # касса под навесом: прилавок и окошко
place(SIGN_WOOD, 35, 24)                          # расписание купаний и цена — у кассы
place(TROUGH_W, 36, 26)                           # колода с питьевой водой для ждущих
place(BUCKET, 37, 26)
place(JUG, 36, 27)
place(BENCH, 34, 27)                              # где ждут, пока откроют
for y in range(26, 31):                           # очередь к двери: два барьера вдоль дорожки
    place(RAIL, 26, y)
    place(RAIL, 29, y)
# ожидальня: два ряда лавок лицом ко входу (спинкой к камере, как сидят в ожидальне) — без навесов,
# которые читались торговыми палатками: тень дают соломенные зонты над рядами и пальмы в кадках по краям
for x in (17, 19, 21):
    place(BENCH_N, x, 28)
    place(BENCH_N, x, 32)
place(UMBRELLA, 18, 27)
place(UMBRELLA_B, 18, 31)
place(LAMP50, 23, 29)
place(LAMP50, 23, 33)
place(POT, 16, 28)                                # пальмы в кадках — по краям ожидальни
place(POT, 24, 28)
place(POT, 16, 32)
place(POT, 24, 32)
# служба: тележка с бельём у западной стены; прачечная — на заднем дворе за купальнями (см. ниже)
place(CART, 17, 24)
place(BARREL, 17, 26)
place(CRATE, 37, 28)
place(BARREL, 37, 30)
# задний служебный двор купален: тут сушат бельё на верёвке (Полина стирает и для купален, и для
# «Замка») — не на парадной площади перед входом
z.paint("k", 20, 6, 31, 8)                        # утоптанная земля за домом
place(LAUNDRY, 23, 7)
place(BUCKET, 22, 8)
place(BARREL, 28, 8)
place(CRATE, 30, 8)
place(LAMP50, 20, 7)
# западный проулок купален — дровяной двор: печи греют воду, дрова завозят сюда
for i, (x, y) in enumerate(((13, 14), (15, 14), (13, 15), (15, 15))):
    place(LOGS[i % 2], x, y)
place(CART, 13, 17)
place(BARREL, 16, 17)
place(CRATE, 13, 19)
place(BARREL, 16, 19)
place(LAMP50, 18, 15)

# ------------------------------------------------------------ источник «Сладкая вода»
# Пруд в пальмовой роще между купальнями и «Замком» — святыня всего курорта. На южном берегу, на плитах,
# каменная чаша с бортиком и водой: лампады по сторонам, факелы на стойках по углам, подношения в чаше,
# ковровая дорожка к подножию. Ряд молитвенных ковриков — ниже ступени, на открытом месте лицом к воде;
# пальмы стоят по берегам и на пляже, ни одна не растёт на коврике.
pbox(CHALICE, 48, 20, "подношения у чаши", {"крышки": 12, "стимулятор": 1})
place(CANDLES, 46, 20)                            # лампады по сторонам чаши
place(CANDLES, 50, 20)
place(TORCH, 44, 22)                              # факелы на стойках по углам площадки
place(TORCH, 52, 22)
place(CARPET, 48, 21)                             # ковровая дорожка к подножию чаши
place(JUG, 46, 21)                                # кувшины тех, кто принёс воду домой
for x in (44, 46, 48, 50):
    place(RUG, x, 23)                             # коврики рядком лицом к воде, на краю площадки
place(BENCH, 42, 23)                              # где сидят те, кто ждёт своей очереди к чаше
place(SIGN_WOOD, 43, 25)                          # доска исцелённых: имена, даты, благодарности
for x, y in ((40, 14), (41, 19), (56, 13), (56, 19), (49, 8), (44, 8)):
    place(PALMS[(x + y) % 4], x, y)
for x, y in ((41, 12), (55, 12), (41, 18), (55, 18)):
    place(REEDS[(x + y) % 4], x, y)

# ------------------------------------------------------------ рабочий двор источника
# То, чего с бульвара не видно: за жердевым забором одной породы со всех сторон — фильтр и розлив.
# Труба от пруда идёт под землёй и выходит наружу только здесь, у корпуса фильтра: видно стык и течь,
# под ним лужа и ведро. Через молитвенные коврики и дорожку к чаше она не идёт (замечание Claude, 2-й
# заход): обломков труб, разбросанных по двору поштучно, больше нет. Кувшины — при розливе под навесом.
rail_h(39, 57, 26)                                # северный забор — целиком, без проёма под трубу
rail_h(39, 47, 33)                                # южный забор: калитка 48..49, к бульвару
rail_h(50, 57, 33)
rail_v(39, 27, 32)                                # западный (восточный — общий с садом «Замка», x=58)
place(PIPE_RUST, 51, 28)                          # стояк у фильтра: труба вышла из земли, стык течёт
oskin("x_puddle", 52, 29)                         # лужа только под стыком, а не посреди дорожки
place(BUCKET, 51, 29)                             # ведро под течь
place(TANK_FILTER, 53, 28)                        # корпус фильтра «Чистый лист»
place("vg_bottles", 55, 28)                       # стеллаж с готовыми бутылями — у восточного края
place(CANOPY_S, 48, 30)                           # навес над розливом
place("table_2", 49, 31)                          # стол розлива: воронка, бутыли
place(JARS, 50, 31)                               # кувшины — при розливе, под навесом
place(BARREL, 41, 28)                             # бочки в ряд у западного забора
place(BARREL, 41, 30)
place(CRATE, 43, 32)                              # ящики — у южного
place(CRATE, 44, 32)
place(CART, 55, 31)                               # тележка — у восточного
place(SACK, 42, 30)
place(LOGS[0], 41, 32)
place(LAMP50, 40, 29)                             # фонарь над двором, у западного забора

# ------------------------------------------------------------ «Замок» Спрингера
# Кирпичный дом с целым фасадом (только целые куски кирпича — FACADE_BRICK) — «дворец» Спрингера.
# Парадный двор — сад за саманной стеной: ворота с аркой на юге, от них мощёная аллея к дверям, по бокам
# фонари, кадки и клумбы, у входа парные колонны, флаги, ковровая дорожка, белые кадки с пальмами; у
# двери — пост управляющего с книгой гостей. Статуя основателя — на газоне западнее аллеи, не на проходе.
# Повозка гостей и кухня — на хозяйственном дворе сбоку, за домом: парадный двор не склад.
z.building(62, 9, 20, 13, "concrete", south=(8,), sign="ЗАМОК", facade=FACADE_PLASTER)
z.roofs[-1]["theme"] = "castle"                   # на крыше флаг и одна-две холодные машины, а не россыпь
z.portal([(70, 21), (71, 21)], "zzyzx_hotel", (21, 23), "«Замок» Спрингера")
# сад: стена с воротами и аллея от ворот к дверям. Боковые стороны закрыты с фасада до стены —
# иначе арка на юге не ворота, а проём в одном заборе (замечание Claude): западная ограда — она же
# восточный забор рабочего двора источника, восточная отделяет парадный двор от хозяйственного
z.hwall(ADOBE_WALL, 58, 82, 35, gaps=(69, 70, 71, 72))
place(ADOBE_GATE, 69, 35)                          # ворота сада: проход 70..71
rail_v(58, 22, 33)                                # западная ограда: от фасада до угла у беседки
rail_v(82, 22, 34)                                # восточная
z.paint("p", 70, 23, 71, 34)                       # аллея: мощёная дорожка от ворот до двери
place(CARPET, 70, 22)                              # ковровая дорожка к дверям
place(CARPET, 70, 23)
place(PILLAR, 69, 22)                              # парные колонны по сторонам входа
place(PILLAR, 72, 22)
place(PLANTER, 64, 22)                             # белые кадки с пальмами на террасе
place(PLANTER, 74, 22)
place(FLAG, 63, 22)                                # флаги на фасаде: «у нас всё как в столице»
place(FLAG, 76, 22)
place(LAMP50, 66, 22)                              # фонари по террасе
place(LAMP50, 73, 22)
place("table_2", 74, 24)                           # пост управляющего: книга гостей
place("chair_0", 73, 24)
place(BENCH, 63, 27)                               # где ждут, пока выйдет хозяин
place(BENCH, 77, 27)
# аллея: фонари и кадки по сторонам
for x, y in ((69, 26), (72, 26), (69, 31), (72, 31)):
    place(LAMP50, x, y)
place(POT, 68, 28)
place(POT, 73, 28)
place(STATUE, 67, 30)                              # статуя основателя — на газоне западнее аллеи
place(BENCH, 63, 31)
place(FLOWERBED, 62, 26)                           # клумбы на газоне по сторонам аллеи
place(FLOWERBED, 76, 26)
place(HEDGE, 62, 29)                               # стриженая изгородь вдоль аллеи
place(HEDGE, 76, 29)
place(PALMS[0], 59, 23)                            # пальмы у углов дома
place(PALMS[1], 81, 23)
# хозяйственный двор «Замка» — восточнее дома, за оградой: повозка гостей (та самая, что подают к
# воротам), кухонный стол с посудой (сюда Тоня выносит еду из столовой), ящики и бочки
z.paint("k", 83, 23, 87, 32)                      # утоптанная земля хозяйственного двора
place(COACH, 83, 25)
place(CRATE, 85, 29)
place(BARREL, 83, 29)
place(SACK, 85, 31)
place("table_2", 84, 32)
place(LAMP50, 87, 30)

# ------------------------------------------------------------ стена-фасад и ворота на юг
# Саманная стена вдоль южной обочины: с бульвара видно только её и пальмы. За стеной — рынок и лагерь.
# Две арки: торговая (к рынку) и восточная (к домам целителей, а дальше — к озеру). Фонари — на столбах
# у арок, а не фонарики на земле.
z.hwall(ADOBE_WALL, 10, 76, 43, gaps=(26, 27, 28, 29, 57, 58, 59, 60))
place(ADOBE_GATE, 26, 43)
place(ADOBE_GATE, 57, 43)
place(LAMP50, 24, 42)
place(LAMP50, 59, 42)

# ------------------------------------------------------------ рынок
# Северный ряд — прилавки с навесами (кто может платить Спрингеру за место). Товар — на прилавках и у
# прилавков, по одной-две вещи; проход от арки к колодцу свободен, посреди площадки ничего не разбросано.
# С земли торгует один — на своём коврике у западного края.
for name, x in (("hb_stall_bread", 14), ("hb_stall_veg", 18), ("hb_stall_fruit", 22),
                ("hb_stall_meat", 31), ("nd_fish_stall", 35), (STALL, 39), (STALL_B, 43), (STALL_C, 47)):
    place(name, x, 45)
place(SACK, 14, 46)                               # у каждого прилавка — его товар, по одной вещи
place(CRATE, 18, 46)
place(JUG, 22, 46)
place(JUG, 31, 46)
place(SCALES, 34, 46)                             # весы у рыбного прилавка: спорят о весе до хрипоты
place(BASKET, 36, 46)
place(CRATE, 39, 46)
place(JARS, 43, 46)
place(HIDE, 47, 46)
place(RUG, 13, 49)                                # с земли: коврик и две вещи у западного края
place(JUG, 13, 48)
place(SACK, 15, 48)
place(HAY, 47, 52)
place(BARREL, 12, 47)
place(CRATE, 51, 46)
place(SIGN_MARKET, 45, 44)                        # неоновая вывеска рынка на стене
place(LAMP50, 12, 45)
place(LAMP50, 52, 49)

# ------------------------------------------------------------ колодец
# На стыке рынка и лагеря — своя каменная площадка и тропа к ней: колодец общий на всех, кто живёт за
# стеной. Вокруг — корыто, ведро, кувшины в очереди, скамья сбоку, фонари на столбах.
place(WELL, 33, 53)
place(TROUGH, 30, 53)
place(BUCKET, 32, 54)
place(BENCH, 35, 54)
place(JUG, 34, 55)
place(JUG, 31, 55)
place(LAMP50, 30, 51)
place(LAMP50, 36, 56)

# ------------------------------------------------------------ лагерь паломников
# Лагерь — не сетка: четыре кучки шатров по три вокруг своего костра, у каждого шатра — свой скарб
# (мешок, кувшин, шкура) по одной-две вещи у входа, между кучками — утоптанные тропы к колодцу и общему
# котлу. Лазарет — отдельным шатром с крестом у входа и флажком, сортир — на дальнем краю, подальше от
# котла и колодца. Шатры большие (4×4), поэтому в кучке их три, а не шесть: между ними остаётся двор.
# западная кучка — те, кто пришёл давно
for name, x, y in ((TENT, 9, 54), (TENT_S, 13, 54), (TENT_BIG, 9, 58)):
    place(name, x, y)
place(FIRE_PIT, 13, 57)                           # общий костёр западной кучки
place(SACK, 12, 57)
place(JUG, 12, 56)
place(HIDE, 13, 60)
# северная кучка — у самой торговой улицы
for name, x, y in ((TENT, 20, 54), (TENT_AWN, 24, 54), (TENT_S, 20, 58)):
    place(name, x, y)
place(FIRE_PIT, 25, 58)
place(JUG, 23, 56)
place(SACK, 24, 57)
place(CAULDRON, 26, 57)                           # котёл над огнём второй кучки
place(BENCH, 24, 59)
# восточная кучка — пришлые
for name, x, y in ((TENT, 38, 54), (TENT_AWN, 42, 54), (TENT_S, 38, 58)):
    place(name, x, y)
place(FIRE_PIT, 43, 57)
place(SACK, 41, 56)
place(JUG, 41, 57)
place(LAUNDRY, 44, 61)                            # бельё на верёвке у шатров
place(HAY, 46, 58)
# южная кучка — у тропы к озеру
for name, x, y in ((TENT_BIG, 9, 62), (TENT, 14, 62), (TENT_S, 9, 66)):
    place(name, x, y)
place(FIRE_PIT, 13, 65)
place(HIDE, 13, 64)
place(JUG, 12, 66)
place(SACK, 17, 64)
# общий котёл — в середине лагеря, у тропы: сюда сходятся все кучки
place(FIRE_PIT, 30, 64)
place(CAULDRON, 31, 64)
place(CANOPY_S, 27, 62)                           # навес над общим столом
place("table_2", 28, 65)
place(BENCH, 27, 66)
place(JUG, 32, 65)
place(SACK, 33, 65)
# лазарет: отдельный шатёр с крестом у входа и флажком — видно издалека
place(TENT_BIG, 25, 68)
place(CROSS, 24, 70)
place(FLAG, 25, 67)
place(RUG, 28, 70)
place(CAULDRON, 23, 68)
place(JUG, 30, 70)
place(LAMP50, 22, 70)
# отхожее место — на дальнем краю, за кучками, подальше от котла и колодца
place(OUTHOUSE, 47, 71)
oskin("x_puddle", 46, 70)
for x, y in ((45, 68), (34, 58), (44, 64)):
    place(HAY, x, y)

# ------------------------------------------------------------ квартал целителей
# Улочка от восточной арки: дома стоят рядом, фасадами на общий проход, у каждого — своё дело у двери
# (скамья для больных, вывеска-знак, кадка, сушилка трав). За домами — приёмный двор под навесом: стол,
# скамьи, котёл с отваром; дальше огород с разными грядками за оградой с калиткой и тропинкой между рядами.
for name, x, y in ((HOUSE_A, 61, 46), (HOUSE_B, 67, 46), (HOUSE_C, 73, 46), (HOUSE_BIG, 79, 46)):
    place(name, x, y)
place(BENCH, 63, 48)                              # у дверей: где сидят больные
place(BENCH, 70, 48)
place(BENCH, 77, 48)
place(BOARD_SMALL, 65, 48)                        # вывеска-знак целителя у двери
place(BOARD_SMALL, 72, 48)
place(BOARD_SMALL, 79, 48)
place(PLANTER0, 65, 47)                           # грядки с травами — в проулках у стен домов,
place(PLANTER1, 71, 47)                           # а не посреди улочки перед дверями
place(POT2, 60, 48)
place(LAUNDRY, 66, 51)                            # травы и бинты сушат на верёвке у домов
place(LAMP50, 58, 51)
place(LAMP50, 63, 51)
place(LAMP50, 81, 51)
# приёмный двор за улицей: навес, где принимают, котёл, тележка, бочки
place(AWNING, 62, 52)                             # навес приёмного двора
place("table_2", 63, 54)
place(BENCH, 62, 56)
place(BENCH, 65, 56)
place(FIRE_PIT, 68, 55)
place(CAULDRON, 69, 55)
place(CART, 74, 57)
place(BARREL, 76, 58)
place(CRATE, 59, 58)
place(JUG, 60, 55)
place(LOGS[1], 70, 54)                            # дрова к котлу с отваром
place(SACK, 66, 54)
place(BUCKET, 71, 56)
place(BOARD_SMALL, 60, 52)                        # доска целителей у входа в квартал
# огород: разные грядки, тропинка, ограда одной породы со всех сторон, одна калитка с севера и
# дорожка к ней от улицы (прежде с боков стояли «тонкие шесты» вместо забора — замечание Claude)
rail_h(77, 86, 55, gaps=(82,))                    # северный забор с калиткой
rail_h(77, 86, 63)                                # южный
rail_v(77, 56, 62)                                # западный
rail_v(86, 56, 62)                                # восточный
z.paint("p", 82, 56, 82, 62)                      # тропинка между грядками от калитки
place(TOMATO, 79, 57)
place(TOMATO_B, 79, 60)
place(CABBAGE, 83, 57)
place(CABBAGE_B, 83, 60)
place(HERB, 79, 62)
place(BUCKET, 84, 62)
place(SACK, 78, 64)
place(BARREL, 85, 65)

# ------------------------------------------------------------ озеро Туэнде
# Набережная, причал на сваях — мостки уходят от берега в воду на десять клеток (piers="w" — доски лежат
# поверх воды, берег под ними не рисуется). Лодки стоят у мостков и привязаны, третья вытащена на песок у
# сарая. Сеть сушится на вешалах, вёсла — у стены сарая. Пальмы по берегу, камыш у воды.
z.piers = ("w",)                                  # доски причала — поверх воды, без берега и размытия
z.paint("q", 82, 36, 86, 44)
z.paint("w", 85, 40, 96, 41)                      # мостки: от набережной в озеро
for wy in (40, 41):
    for wx in range(85, 97):
        z.blocked.discard((wx, wy))
        z.reserved.discard((wx, wy))
place(LAMP50, 96, 40)                             # фонарь на голове причала
place(LAMP50, 86, 39)                             # фонарь у начала мостков
place(SHED_BOAT, 84, 46)                          # лодочный сарай на берегу
place(OARS, 86, 47)                               # вёсла — к стене сарая, а не поперёк набережной
place(NET_RACK, 82, 48)                           # сеть сушится на вешалах
place(FISH_RACK, 78, 50)
place(BOAT, 93, 42, force=True)                   # лодка у мостков, в воде
place(ROWBOAT, 94, 39, force=True)                # вторая — у головы причала, борт к борту
place(BOAT_B, 84, 49, force=True)                 # третья вытащена на берег у сарая
place(BARREL, 84, 51)
place(CRATE, 82, 50)
place(JUG, 85, 43)
place(BENCH, 83, 43)                              # скамья на набережной, лицом к воде
for x, y in ((80, 42), (80, 53), (79, 45), (85, 52)):
    place(PALMS[(x + y) % 4], x, y)
for x, y in ((89, 49), (87, 51), (90, 27), (88, 24)):
    place(REEDS[(x + y) % 4], x, y)

# ------------------------------------------------------------ пустыня вокруг
# Кактусы, сухие деревья, камни и кости — только по краям карты, за пределами курорта и лагеря.
for name, x, y in ((CACTI[0], 7, 3), (CACTI[1], 23, 2), (CACTI[2], 41, 4), (CACTI[3], 57, 2),
                   (CACTI[4], 73, 5), (CACTI[5], 91, 2), (CACTI[0], 2, 8), (CACTI[1], 4, 16),
                   (CACTI[2], 1, 24), (CACTI[3], 3, 31), (CACTI[4], 14, 75), (CACTI[5], 36, 74),
                   (CACTI[0], 58, 76), (CACTI[1], 78, 74)):
    place(name, x, y)
for name, x, y in ((DEAD[0], 14, 5), (DEAD[1], 48, 1), (DEAD[2], 80, 3), (DEAD[3], 100, 6),
                   (DEAD[0], 20, 76), (DEAD[1], 50, 74), (DEAD[2], 96, 76)):
    place(name, x, y)
for name, x, y in ((ROCKS[0], 4, 1), (ROCKS[1], 31, 6), (ROCKS[2], 66, 1), (ROCKS[3], 96, 3),
                   (ROCKS[0], 5, 12), (ROCKS[1], 1, 20), (ROCKS[2], 8, 73), (ROCKS[3], 30, 76),
                   (ROCKS[0], 70, 75), (ROCKS[1], 90, 76)):
    place(name, x, y)
for name, x, y in ((BUSHES[0], 26, 6), (BUSHES[1], 62, 3), (BUSHES[2], 88, 4), (BUSHES[3], 33, 72),
                   (BUSHES[4], 55, 75), (BUSHES[5], 11, 74), (BUSHES[0], 3, 44), (BUSHES[1], 1, 52)):
    place(name, x, y)

# ------------------------------------------------------------ кто где
# Жители — у своего дела, не в проёмах: Спрингер на площади у фонтана, где его видят все; Гас у чаши
# источника (он смотритель воды); Корд у фильтра в рабочем дворе; Абдул за прилавком; Мария с Тимми в
# очереди за водой; Юдифь у своего огорода; Хэнк у костра западного стана; Броня у шлагбаума.
npc("springer", 52, 37)
npc("gus", 50, 21)
npc("merchant_zz", 25, 45)
npc("pilgrim_maria", 51, 36)
npc("pilgrim_timmy", 52, 36)
npc("healer_girl", 65, 55)
npc("pilgrim_hank", 20, 64)
z.walk_zones["springer"] = [43, 36, 56, 40]        # прохаживается по площади у фонтана
z.walk_zones["merchant_zz"] = [24, 45, 26, 47]     # у прилавка и перед ним
z.walk_zones["healer_girl"] = [62, 53, 72, 58]     # между домами квартала
z.walk_zones["pilgrim_hank"] = [10, 61, 18, 65]    # у костра южной кучки
# у авторов есть свои анкеты жителей (data/folks.json) — ставим их туда, где они и работают
z.folk_spots.update({
    "bronya": [11, 38],                            # часовой — у шлагбаума, на дороге
    "mirra": [29, 23],                             # банщица — у входа в купальни, с полотенцем
    "zakhar": [74, 23],                            # управляющий — за столом у дверей «Замка»
    "kord": [50, 29],                              # фильтровщик — у наливной трубы в рабочем дворе
    "tonya": [84, 31],                             # подавальщица — выносит еду на хозяйственный двор
    "esfir": [80, 58],                             # знахарка — у своего огородика
    "stepan": [27, 47],                            # старик торгует на рынке
    "pasha": [83, 45],                             # рыбак — у сетей
    "gerda": [87, 40],                             # смотрительница причала — на мостках
    "dina": [90, 41],                              # девочка у лодок
    "critter:cat": [[17, 57], [29, 62], [24, 71]],
    "critter:dog": [[13, 63]],
    "critter:chicken": [[43, 59], [44, 60], [45, 60]],
})
if place.fails:
    print("ОТКАЗОВ:", len(place.fails))
    for w in place.fails:
        print("  ", w)
    if not os.environ.get("ZZYZX_IGNORE"):      # временно: собрать карту с отказами, чтобы посмотреть
        raise AssertionError(f"не встало предметов: {len(place.fails)}")
enemy("rat", 12, 71)                               # крысы у помойки за лагерем
enemy("rat", 44, 70)
enemy("radroach", 80, 66)                          # радтаракан в траве у озера


# ================================================================ купальни
bt = CityMap(city, "zzyzx_bath", "Купальни Зайзикса", 40, 26, start=(19, 23), seed=82, interior=True, music="caves")
bt.floor_code("T", *TILE_W)
bt.floor_code("B", *TILE_B)
bt.wall_code("W", "pk:bazaar/bazaar_w2_12")
bt.wall_code("Q", "pk:bazaar/bazaar_w2_12")
LOBBY = bt.room(10, 15, 29, 25, "W", "T")          # приёмная у входа
CHANGE_L = bt.room(1, 15, 10, 25, "W", "T")         # мужская раздевалка
CHANGE_R = bt.room(29, 15, 38, 25, "W", "T")        # женская раздевалка
HALL = bt.room(1, 1, 30, 15, "Q", "B")             # зал с бассейном
OFFICE = bt.room(30, 1, 38, 8, "W", "T")            # кабинет целителя
PUMP = bt.room(30, 8, 38, 15, "W", "T")             # насосная
bt.opening(19, 25, 20, 25, "T")
bt.portal([(19, 25), (20, 25)], "zzyzx", (27, 22), "На бульвар")
bt.opening(10, 19, 10, 20, "T")
bt.opening(29, 19, 29, 20, "T")
bt.opening(19, 15, 20, 17, "B")
bt.opening(30, 5, 30, 6, "T")
bt.opening(34, 8, 35, 10, "T")
# приёмная: стойка лицом к двери, скамьи для ждущих вдоль стен, растения в углах
bt.put("counter", 17, 19)
bt.put("counter", 21, 19)
bt.put("bench_7", 12, 22)
bt.put("bench_7", 25, 22)
bt.put(PLANT, 12, 18)
bt.put(PLANT, 27, 18)
# раздевалки: шкафчики вдоль северной стены, скамья посредине
for x in (2, 6):
    bt.put(LOCKERS, x, 18)
bt.put("bench_16", 4, 22)
for x in (30, 35):
    bt.put(LOCKERS, x, 18)
bt.put("bench_16", 32, 22)
bt.box("locker_1", 8, 23, "шкафчик паломника", {"крышки": 12, "бинт": 1})
# зал: целебный бассейн в центре, по краям — лежаки (скамьи)
bt.floor_code("~", "pk:mport/p1/8,4,1,1", "pk:mport/p1/9,4,1,1")
bt.water_codes = ("~",)
bt.paint("~", 8, 5, 21, 10)                           # чаша бассейна — настоящая вода с каменной кромкой
for x in (6, 12, 17, 24):
    bt.maybe(PLANT, x, 3)
bt.put("bench_16", 4, 7)
bt.put("bench_16", 22, 7)
bt.put("bench_16", 4, 11)
bt.put("bench_16", 22, 11)
bt.put(PLANT, 2, 4)
bt.put(PLANT, 28, 4)
# кабинет целителя: стол с терминалом у стены, шкаф с «лекарствами»
bt.terminal(31, 4, "zz_healer")
bt.put(DESK_B, 34, 4)
bt.box("glass_cabinet", 37, 4, "шкаф целителя", {"вода Зайзикса": 2, "антирадин": 1, "крышки": 40})
# насосная: насосы и бак, люк в цистерну
bt.put(TANKS_W, 36, 11)
bt.put(GEN, 31, 13)
bt.props.append(["x_manhole", 34, 12])
bt.portal([(34, 12)], "zzyzx_cistern", (4, 5), "Цистерна",
          requires={"item": "ключ от насосной",
                    "msg": "Люк в полу насосной, на нём замок. Ключ — у смотрителя источника Гаса."})
bt.npcs += [["bath_pilgrim", 6, 10], ["bath_pilgrim_b", 25, 10], ["nurse_ava", 17, 18]]   # Ава — за стойкой


# ================================================================ «Замок» Спрингера
ht = CityMap(city, "zzyzx_hotel", "«Замок» Спрингера", 44, 26, start=(21, 23), seed=83, interior=True, music="hotel")
ht.floor_code("C", "pk:hotel/hotel_f1_23")           # холл и покои — бежевый мрамор вместо шахматки
ht.floor_code("D", "pk:zcity/zcity_f1_00")          # столовая и номера — доски
ht.floor_code("R", "pk:aoffice/p3/3,1,1,1")         # ковровое покрытие номеров
ht.wall_code("V", "pk:hotel/hotel_w1_23")
ht.wall_code("Y", "pk:hotel/hotel_w1_15")
LOBBY = ht.room(12, 13, 31, 25, "V", "C")          # холл
DINE = ht.room(1, 13, 12, 25, "V", "D")             # столовая
SUITE = ht.room(31, 13, 43, 25, "V", "C")           # покои Спрингера
ROOMS = [ht.room(x, 1, x + 8, 13, "Y", "R") for x in (1, 9, 17, 25, 33)]
ht.opening(21, 25, 22, 25, "C")
ht.portal([(21, 25), (22, 25)], "zzyzx", (70, 22), "На бульвар")
ht.opening(12, 19, 12, 20, "C")
ht.opening(31, 19, 31, 20, "C")
for x0 in (1, 9, 17, 25, 33):
    ht.opening(x0 + 4, 13, x0 + 4, 15, "C")
# холл: стойка портье, кресла у стен, растения
ht.put("counter", 18, 17)
ht.put("counter", 22, 17)
ht.put(ARMCHAIR, 14, 20)
ht.put(ARMCHAIR, 28, 20)
ht.put(PLANT, 15, 16)
ht.put(PLANT, 27, 16)
ht.put(LAMP, 15, 23)
ht.put(LAMP, 28, 23)
# столовая: столы со стульями рядами
for x, y in ((3, 17), (7, 17), (3, 21), (7, 21)):
    ht.put("round_table_42", x, y)
    ht.put("stool_round_41", x + 1, y)
ht.box("cabinet_small", 10, 16, "буфет", {"консервы": 2, "энергетический батончик": 1, "обрывок карты (север)": 1})
# номера: кровать у стены, тумбочка, шкаф; в одном — постоялец
for i, x0 in enumerate((1, 9, 17, 25, 33)):
    ht.put(BED if i % 2 == 0 else BED_S, x0 + 2, 4)
    ht.put(NIGHT, x0 + 1, 4)
    ht.put(WARDROBE, x0 + 6, 4)
    ht.stamp(f"zz_room_rug{i}", "pk:lhotel/p2/10,12,2,2", x0 + 2, 7, water=False)
    ht.put(ARMCHAIR, x0 + 6, 9)
    ht.put(LAMP, x0 + 1, 10)
ht.npcs += [["guest_widow", 22, 8]]
# покои Спрингера: широкая кровать, письменный стол с терминалом, сейф
ht.put(BED, 39, 17)
ht.put(NIGHT, 41, 17)
ht.terminal(33, 17, "zz_springer")
ht.put(DESK, 34, 17)
ht.box("metal_chest", 41, 22, "сейф Спрингера",
       {"крышки": 220, "стимулятор": 2, "ключ от насосной": 1},
       requires={"flag": "springer_safe", "msg": "Сейф с кодом. Код Спрингер держит в голове — или в терминале."})
ht.put(PLANT, 32, 23)
ht.stamp("zz_lobby_rug", "pk:lhotel/p2/10,12,2,2", 20, 21, water=False)
ht.stamp("zz_suite_rug", "pk:lhotel/p2/10,12,2,2", 36, 20, water=False)
ht.put(ARMCHAIR, 37, 16)          # кресло в покоях, у северной стены рядом с кроватью
ht.put(LAMP, 33, 22)


# ================================================================ цистерна
cs = CityMap(city, "zzyzx_cistern", "Цистерна под купальнями", 34, 22, start=(4, 5), seed=84, interior=True,
             music="lab", night=[78, 92, 104])
cs.floor_code("M", *METAL)
cs.wall_code("K", "pk:nbunk/nbunk_w1_12")
cs.room(1, 1, 33, 21, "K", "M")
cs.props.append(["x_ladder", 4, 4])
cs.portal([(4, 4)], "zzyzx_bath", (34, 13), "Наверх, в насосную")
cs.reserve(2, 4, 7, 7)
# каналы с водой: две полосы воды через зал, между ними — мостки
cs.floor_code("~", "pk:mport/p1/8,4,1,1", "pk:mport/p1/9,4,1,1")
cs.water_codes = ("~",)
cs.paint("~", 9, 6, 18, 9)                            # отстойники — настоящая вода с каменной кромкой
cs.paint("~", 9, 14, 18, 17)
for x, y in ((6, 8), (20, 8), (6, 16), (20, 16), (13, 11), (13, 12), (22, 12), (8, 19)):
    cs.maybe(SEWER_PIPE_ZZ, x, y)
# фильтр «Чистый лист»: баки и чаны у восточной стены, терминал управления рядом
cs.put(TANK, 26, 4)
cs.put(TANK, 28, 4)
cs.put(VATS, 30, 4)
cs.terminal(24, 4, "zz_cistern")
cs.put(DESK_LAB, 26, 9)
cs.put(GEN, 29, 12)
cs.box(CRATE, 31, 18, "ящик Vault-Tec", {"антирадин": 2, "образец «Чистый лист»": 1, "батарейки": 2})
cs.enemies += [["radroach", 12, 11], ["radroach", 16, 12], ["radroach", 20, 18], ["rat", 7, 17], ["rat", 6, 19],
               ["robot_skel", 27, 16]]

# цистерна: сырость, подтёки, зелёная подсветка воды и красные лампы у фильтра, тросы и трубы по стенам
LM.lamps(cs, "green", [(8, 5), (20, 5), (13, 13), (22, 15), (8, 18)])
LM.lamps(cs, "cold", [(26, 7), (30, 10)])
LM.lamps(cs, "red", [(24, 14), (31, 15)])
LM.decals(cs, "x_vd_wet0", [(5, 10), (20, 11), (7, 12), (24, 18), (14, 4)])
LM.decals(cs, "x_vd_wet1", [(11, 19), (28, 8)])
LM.decals(cs, "x_vd_waterline", [(8, 7), (19, 7), (8, 15), (19, 15)])
LM.decals(cs, "x_vd_drip", [(10, 4), (17, 4), (30, 3)])
LM.decals(cs, "x_vd_rust0", [(3, 12), (23, 5)])
LM.decals(cs, "x_vd_hz_h", [(24, 11), (25, 11)])
LM.doors(cs)

city.save(gap_exempt=("springer", "nurse_ava", "gus", "bath_pilgrim", "bath_pilgrim_b"))
# на карте мира — «Зайзикс»; открывается, если пройти рядом, или после Бейкера (src/game/quests.py)
L = json.load(open("data/locations.json", encoding="utf-8"))
L["zzyzx"].update({"world_name": "Зайзикс", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
