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
# разные сосуды и бочки: одинаковые кувшины в трёх размерах издалека читались кучами-близнецами
JUGS = [JUG, P("zz_jug_pitcher", "pk:destown/p3/4,7,1,1"),           # кувшин-питчер с водой
        P("zz_jug_slim", "pk:destown/p3/14,3,1,1"),                  # узкая ваза
        P("zz_jug_blue", "pk:destown/p3/3,5,1,1")]                   # синяя глазурь — дорогая, с бульвара
BARRELS = [BARREL, P("zz_barrel_w", "pk:west/west_1_017", search="junk", title="бочка")]   # окованная бочка
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
JUG_BIG = P("zz_jug_big", "pk:destown/p3/1,10,1,1")                             # большая амфора
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
CHALICE = P("zz_chalice", "pk:destown/p3/8,9,1,1", foot=[2, 1], keybg=True, scale=2.0)   # чаша святыни — вдвое, в рост
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
place(BARRELS[(4 + 35) % 2], 4, 35)
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

# фонтан посреди бульвара — главный знак «процветания»: бассейн настоящей воды посреди пустыни, а в нём
# на постаменте — сам Спрингер в камне. Готового фонтана в наборах нет (только кибер-тумбы), поэтому
# вода — кафельный бассейн из пака pool; бульвар обходит бассейн по краям площади (y 36 и 40).
# бассейн — не пруд: прямой белый кафельный бортик, внутри вода с рябью (tools/make_fountain.py).
FOUNTAIN_POOL = P("zz_fountain_pool", "zz_fountain_pool", foot=[5, 4], layer="floor")
place(FOUNTAIN_POOL, 44, 37)
for _y in range(37, 41):
    for _x in range(44, 49):
        z.blocked.add((_x, _y))                    # для расстановки: сюда ничего не встанет
        z.solid_cells = getattr(z, "solid_cells", set()) | {(_x, _y)}   # и в карту: по воде не ходят
STATUE_BIG = P("zz_statue_big", "pk:cult/cult_2_094", sight=True, scale=2.0)   # та же статуя вдвое — по бассейну
z.put(STATUE_BIG, 46, 39, force=True, allow_reserved=True)   # Спрингер в камне посреди воды
place(BENCH, 44, 35)
place(BENCH, 48, 35)
for x, y in ((42, 34), (50, 34), (42, 42), (50, 42)):
    place(POT, x, y)
place(FIRE_PIT, 42, 40)                           # жаровня у фонтана: вечером тут свет и люди

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
place(BARRELS[(49 + 32) % 2], 49, 32)
place(BENCH, 43, 41)                              # где ждут те, кому уже невмоготу стоять
place(LAMP50, 56, 35)                             # фонарь у прилавков чудо-воды


# ------------------------------------------------------------ купальни
# Здание с целым светлым фасадом (курорт, который Спрингер показывает, не облуплен: формат фасада —
# только чистые куски, см. FACADE_PLASTER). Перед входом — зал ожидания под открытым небом: два ряда
# лавок лицом ко входу (спинка к камере), пальмы по краям, касса с
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
place(JUGS[(36 + 2 * 27) % 4], 36, 27)
place(BENCH, 34, 27)                              # где ждут, пока откроют
for y in range(26, 31):                           # очередь к двери: два барьера вдоль дорожки
    place(RAIL, 26, y)
    place(RAIL, 29, y)
# ожидальня: два ряда лавок лицом ко входу (спинкой к камере, как сидят в ожидальне) — без навесов,
# которые читались торговыми палатками, и без пляжных зонтов: тень дают пальмы по краям
for x in (17, 19, 21):
    place(BENCH_N, x, 28)
    place(BENCH_N, x, 32)
place(LAMP50, 23, 33)
place(PALMS[0], 16, 32)                           # тень — живые пальмы по краям переднего ряда
place(PALMS[2], 24, 32)
# служба: тележка с бельём у западной стены; прачечная — на заднем дворе за купальнями (см. ниже)
place(CART, 17, 24)
place(BARRELS[(17 + 26) % 2], 17, 26)
place(CRATE, 37, 28)
place(BARRELS[(37 + 30) % 2], 37, 30)
# задний служебный двор купален: тут сушат бельё на верёвке (Полина стирает и для купален, и для
# «Замка») — не на парадной площади перед входом
z.paint("k", 20, 6, 31, 8)                        # утоптанная земля за домом
place(LAUNDRY, 23, 7)
place(BUCKET, 22, 8)
place(BARRELS[(28 + 8) % 2], 28, 8)
place(CRATE, 30, 8)
place(LAMP50, 20, 7)
# западный проулок купален — дровяной двор: печи греют воду, дрова завозят сюда
for i, (x, y) in enumerate(((13, 14), (15, 14), (13, 15), (15, 15))):
    place(LOGS[i % 2], x, y)
place(CART, 13, 17)
place(BARRELS[(16 + 17) % 2], 16, 17)
place(CRATE, 13, 19)
place(BARRELS[(16 + 19) % 2], 16, 19)
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
# Труба от пруда: у самой кромки воды выходит из песка (дальше к пруду — под землёй, tools/make_pipes.py),
# коленом поворачивает на юг и лежит одной линией, в стороне от ковриков и дорожки к чаше, сквозь проём в северном заборе; у
# фильтра — колено у самой земли и вбок в основание бака. Из-под бака выходит вторая труба — чистая вода
# — и ведёт к навесу розлива: на конце кран с вентилем, под струёй ведро. Через трубы перешагивают.
PIPE_V = P("zz_pipe_v", "zz_pipe_v", block=False, layer="floor")
PIPE_H = P("zz_pipe_h", "zz_pipe_h", block=False, layer="floor")
PIPE_BURY = P("zz_pipe_bury_w", "zz_pipe_bury_w", block=False, layer="floor")
PIPE_SW = P("zz_pipe_sw", "zz_pipe_sw", block=False, layer="floor")
PIPE_NE = P("zz_pipe_ne", "zz_pipe_ne", block=False, layer="floor")   # колена для купален
PIPE_NW = P("zz_pipe_nw", "zz_pipe_nw", block=False, layer="floor")
PIPE_INLET = P("zz_pipe_inlet", "zz_pipe_inlet", block=False, layer="floor")
PIPE_OUTLET = P("zz_pipe_outlet", "zz_pipe_outlet", block=False, layer="floor")
PIPE_TAP = P("zz_pipe_tap", "zz_pipe_tap", block=False, layer="floor")
place(PIPE_BURY, 53, 19, allow_reserved=True)     # у самой кромки уходит в песок к пруду: дальше — под землёй
place(PIPE_SW, 54, 19, allow_reserved=True)       # колено: от берега на юг
for _y in range(20, 28):
    place(PIPE_V, 54, _y, allow_reserved=True)    # вдоль восточного края площадки святыни
place(PIPE_INLET, 54, 28)                         # колено у земли — вбок, в основание бака
place(PIPE_OUTLET, 55, 29)                        # чистая вода — из-под бака на запад
for _x in (54, 53):
    place(PIPE_H, _x, 29)
place(PIPE_TAP, 52, 29)                           # кран у навеса розлива
place(BUCKET, 52, 30)                             # ведро под струёй
rail_h(39, 57, 26, gaps=(54,))                    # северный забор — с проёмом только под трубу
rail_h(39, 47, 33)                                # южный забор: калитка 48..49, к бульвару
rail_h(50, 57, 33)
rail_v(39, 27, 32)                                # западный (восточный — общий с садом «Замка», x=58)
place(TANK_FILTER, 55, 28)                        # корпус фильтра «Чистый лист»: труба входит в основание
place("vg_bottles", 46, 30)                       # стеллаж с готовыми бутылями — рядом со столом розлива
place(CANOPY_S, 48, 30)                           # навес над розливом
place("table_2", 49, 31)                          # стол розлива: воронка, бутыли
place(JARS, 50, 31)                               # кувшины — при розливе, под навесом
place(BARRELS[(41 + 28) % 2], 41, 28)                             # бочки в ряд у западного забора
place(BARRELS[(41 + 30) % 2], 41, 30)
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
# «Замок» — не серая коробка-близнец купален: те же чистые бетонные куски, перекрашенные в тёплый
# песчаник (стены и крыша одним тоном), северная стена — тоже только целые куски, без кирпичных дыр
SANDSTONE = [255, 214, 160]
for _side in ("w", "e"):
    P(f"vwall_sandstone_{_side}", f"p1_vwall_concrete_{_side}", foot=[1, 1], sight=True, tint=SANDSTONE)
P("wall_sandstone", "p1_wall_concrete", sight=True, tint=SANDSTONE)
for _pr in z.props:
    if 62 <= _pr[1] <= 81 and 9 <= _pr[2] <= 21:
        if _pr[0] in ("wall_concrete", "wall_concrete_brick"):
            _pr[0] = "wall_sandstone"
        elif _pr[0].startswith("vwall_concrete_"):
            _pr[0] = "vwall_sandstone_" + _pr[0][-1]
z.roofs[-1]["tint"] = SANDSTONE
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
place(BARRELS[(83 + 29) % 2], 83, 29)
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
# Не строй солдат: прилавки северного ряда стоят вразнобой (кто раньше занял место — ближе к стене,
# кто позже — на шаг вперёд), промежутки разные; восточнее — второй, короткий ряд у южного края, между
# рядами — торговый проход. Товар — у своего прилавка, на шаг впереди.
for name, x, y in (("hb_stall_bread", 14, 45), ("hb_stall_veg", 18, 46), ("hb_stall_fruit", 21, 45),
                   ("hb_stall_meat", 31, 46), ("nd_fish_stall", 35, 45), (STALL, 40, 46), (STALL_B, 45, 45),
                   (STALL_C, 41, 50)):
    place(name, x, y)
place(SACK, 14, 46)                               # у каждого прилавка — его товар, по одной вещи
place(CRATE, 19, 47)
place(JUGS[(21 + 2 * 46) % 4], 21, 46)
place(JUGS[(32 + 2 * 47) % 4], 32, 47)
place(SCALES, 37, 46)                             # весы у рыбного прилавка: спорят о весе до хрипоты
place(BASKET, 35, 46)
place(CRATE, 40, 47)
place(JARS, 45, 46)
place(HIDE, 42, 51)
place(RUG, 46, 50)                                # с земли: коврик и две вещи у южного ряда
place(JUGS[(47 + 2 * 49) % 4], 47, 49)
place(SACK, 48, 50)
place(HAY, 47, 52)
place(BARRELS[(12 + 47) % 2], 12, 47)
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
place(JUGS[(34 + 2 * 55) % 4], 34, 55)
place(JUGS[(31 + 2 * 55) % 4], 31, 55)
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
place(JUGS[(12 + 2 * 56) % 4], 12, 56)
place(HIDE, 13, 60)
# северная кучка — у самой торговой улицы
for name, x, y in ((TENT, 20, 54), (TENT_AWN, 24, 54), (TENT_S, 20, 58)):
    place(name, x, y)
place(FIRE_PIT, 25, 58)
place(JUGS[(23 + 2 * 56) % 4], 23, 56)
place(SACK, 24, 57)
place(CAULDRON, 26, 57)                           # котёл над огнём второй кучки
place(BENCH, 24, 59)
# восточная кучка — пришлые
for name, x, y in ((TENT, 38, 54), (TENT_AWN, 42, 54), (TENT_S, 38, 58)):
    place(name, x, y)
place(FIRE_PIT, 43, 57)
place(SACK, 41, 56)
place(JUGS[(41 + 2 * 57) % 4], 41, 57)
place(LAUNDRY, 44, 61)                            # бельё на верёвке у шатров
place(HAY, 46, 58)
# южная кучка — у тропы к озеру
for name, x, y in ((TENT_BIG, 9, 62), (TENT, 14, 62), (TENT_S, 9, 66)):
    place(name, x, y)
place(FIRE_PIT, 13, 65)
place(HIDE, 13, 64)
place(JUGS[(12 + 2 * 66) % 4], 12, 66)
place(SACK, 17, 64)
# общий котёл — в середине лагеря, у тропы: сюда сходятся все кучки
place(FIRE_PIT, 30, 64)
place(CAULDRON, 31, 64)
place(CANOPY_S, 27, 62)                           # навес над общим столом
place("table_2", 28, 65)
place(BENCH, 27, 66)
place(JUGS[(32 + 2 * 65) % 4], 32, 65)
place(SACK, 33, 65)
# лазарет: отдельный шатёр с крестом у входа и флажком — видно издалека
place(TENT_BIG, 25, 68)
place(CROSS, 24, 70)
place(FLAG, 25, 67)
place(RUG, 28, 70)
place(CAULDRON, 23, 68)
place(JUGS[(30 + 2 * 70) % 4], 30, 70)
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
place(LAUNDRY, 70, 57)                            # травы и бинты сушат на верёвке в приёмном дворе, не поперёк улочки
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
place(BARRELS[(76 + 58) % 2], 76, 58)
place(CRATE, 59, 58)
place(JUGS[(60 + 2 * 55) % 4], 60, 55)
place(LOGS[1], 70, 54)                            # дрова к котлу с отваром
place(SACK, 66, 54)
place(BUCKET, 71, 56)
place(BOARD_SMALL, 60, 52)                        # доска целителей у входа в квартал
# огород: разные грядки, тропинка, ограда одной породы со всех сторон, одна калитка с севера и
# дорожка к ней от улицы (прежде с боков стояли «тонкие шесты» вместо забора — замечание Claude)
rail_h(77, 86, 55, gaps=(81, 82))                 # северный забор, в проёме — калитка
GARDEN_GATE = P("zz_garden_gate", "pk:west/west_1_020", foot=[2, 1], sight=True,
                holes=[[0, 0], [1, 0]])          # калитка на раме, двустворчатая: проходима, как арка
place(GARDEN_GATE, 81, 55)
rail_h(77, 86, 63)                                # южный
rail_v(77, 56, 62)                                # западный
rail_v(86, 56, 62)                                # восточный
z.paint("p", 81, 56, 82, 62)                      # тропинка между грядками от калитки
place(TOMATO, 79, 57)
place(TOMATO_B, 79, 60)
place(CABBAGE, 83, 57)
place(CABBAGE_B, 83, 60)
place(HERB, 79, 62)
place(BUCKET, 84, 62)
place(SACK, 78, 64)
place(BARRELS[(85 + 65) % 2], 85, 65)

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
place(NET_RACK, 82, 48)                           # сеть сушится на вешалах
place(FISH_RACK, 78, 50)
place(BOAT, 93, 42, force=True)                   # лодка у мостков, в воде
place(ROWBOAT, 94, 39, force=True)                # вторая — у головы причала, борт к борту
place(BOAT_B, 84, 49, force=True)                 # третья вытащена на берег у сарая
place(BARRELS[(84 + 51) % 2], 84, 51)
place(CRATE, 82, 50)
place(JUGS[(85 + 2 * 43) % 4], 85, 43)
place(BENCH, 83, 43)                              # скамья на набережной, лицом к воде
for x, y in ((80, 42), (80, 53), (79, 45), (85, 52)):
    place(PALMS[(x + y) % 4], x, y)
for x, y in ((89, 49), (87, 51), (90, 27), (88, 24)):
    place(REEDS[(x + y) % 4], x, y)

# ------------------------------------------------------------ стоянка караванов
# У въезда, к югу от дороги и вплотную к рынку: караваны из Нидлса приходят сюда (Абдул пришёл так же),
# разгружаются в рынок и поят браминов. Дилижанс и тележка, корыто с сеном, костёр погонщиков, товар
# под рукой у фургона. Земля утоптана копытами — своим ровным прямоугольником, не кляксой.
WAGON_C = P("zz_wagon_c", "pk:west/west_1_011", foot=[3, 2], sight=True, scale=2.0)   # крытый фургон: в рост, выше человека
z.paint("k", 1, 43, 10, 55)
place(WAGON_C, 1, 46)
place(CART, 6, 45)                                # ручная тележка — возить товар на рынок
place(CRATE, 4, 47)                               # товар у фургона, по-походному
place(SACKS[0], 5, 47)
place(TROUGH, 2, 50)                              # корыто для браминов
place(HAY, 4, 51)
place(HAY, 2, 52)
place(FIRE_PIT, 7, 52)                            # костёр погонщиков
place(BENCH, 7, 54)
place(LAMP50, 10, 44)                             # фонарь у съезда с дороги

# ------------------------------------------------------------ кладбище паломников
# За лазаретом, у южного края: тех, кого вода не спасла, хоронят здесь — подальше от бульвара, где о них
# не говорят. Ограда с проходом из лагеря, два ряда крестов и надгробий, одна свежая могила, лампады.
z.paint("k", 16, 73, 29, 77)
rail_h(16, 29, 73, gaps=(22, 23))                 # ограда с проходом из лагеря
rail_v(16, 74, 76)                                # нижний край карты — ограды не надо, дальше пустыня
rail_v(29, 74, 76)
for x, y, name in ((18, 74, CROSS), (20, 74, "x_tombstone"), (25, 74, CROSS), (27, 74, CROSS),
                   (18, 76, "x_tombstone"), (20, 76, CROSS), (25, 76, "x_grave"), (27, 76, "x_tombstone")):
    place(name, x, y)
FRESH_GRAVE = P("zz_fresh_grave", "pk:grave/grave_2_026", search="grave", title="свежая могила")
place(FRESH_GRAVE, 22, 76)                        # свежая: вчера из лазарета
place(CANDLES, 23, 75)                            # лампада у свежей могилы

# ------------------------------------------------------------ пустыня вокруг
# Кактусы, сухие деревья, камни и кости — только по краям карты, за пределами курорта и лагеря.
for name, x, y in ((CACTI[0], 7, 3), (CACTI[1], 23, 2), (CACTI[2], 41, 4), (CACTI[3], 57, 2),
                   (CACTI[4], 73, 5), (CACTI[5], 91, 2), (CACTI[0], 2, 8), (CACTI[1], 4, 16),
                   (CACTI[2], 1, 24), (CACTI[3], 3, 31), (CACTI[4], 14, 75), (CACTI[5], 36, 74),
                   (CACTI[0], 58, 76), (CACTI[1], 78, 74)):
    place(name, x, y)
for name, x, y in ((DEAD[0], 14, 5), (DEAD[1], 48, 1), (DEAD[2], 80, 3), (DEAD[3], 100, 6),
                   (DEAD[1], 50, 74), (DEAD[2], 96, 76)):
    place(name, x, y)
for name, x, y in ((ROCKS[0], 4, 1), (ROCKS[1], 31, 6), (ROCKS[2], 66, 1), (ROCKS[3], 96, 3),
                   (ROCKS[0], 5, 12), (ROCKS[1], 1, 20), (ROCKS[2], 8, 73), 
                   (ROCKS[0], 70, 75), (ROCKS[1], 90, 76)):
    place(name, x, y)
for name, x, y in ((BUSHES[0], 26, 6), (BUSHES[1], 62, 3), (BUSHES[2], 88, 4), (BUSHES[3], 33, 72),
                   (BUSHES[4], 55, 75), (BUSHES[5], 11, 74), ):
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
    "kord": [53, 31],                              # фильтровщик — у наливной трубы в рабочем дворе
    "tonya": [84, 31],                             # подавальщица — выносит еду на хозяйственный двор
    "esfir": [80, 58],                             # знахарка — у своего огородика
    "stepan": [27, 47],                            # старик торгует на рынке
    "pasha": [83, 45],                             # рыбак — у сетей
    "gerda": [87, 40],                             # смотрительница причала — на мостках
    "dina": [90, 41],                              # девочка у лодок
    "critter:cat": [[17, 57], [29, 62], [24, 71]],
    "critter:dog": [[13, 63]],
    "critter:brahmin": [[4, 53], [8, 49]],         # брамины каравана — у корыта и у костра
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
# Купальни (docs/furnish/zzyzx.md §2): приёмная у входа, по сторонам от неё две раздевалки, на севере зал
# с бассейном, в восточном крыле кабинет целителя и насосная. Автообстановка выключена (furnish=False):
# прежде движок доставлял сюда 22 случайных шкафа, стеллажа и тумбочки — «каша» из чужой мебели.
# Свет ночной задан вручную, пятна — от настенных плафонов и двух ламп на шнуре над чашей (auto_ambient молчит).
bt = CityMap(city, "zzyzx_bath", "Купальни Зайзикса", 40, 26, start=(19, 23), seed=82, interior=True,
             music="caves", furnish=False)
bt.night = [108, 100, 92]
bt.floor_code("C", "pk:pool/p1/0,0,1,1")                 # светлый кафель приёмной и раздевалок
bt.floor_code("D", "pk:cult/cult_f2_21", "pk:cult/cult_f2_20")   # доски кабинета целителя
bt.floor_code("B", *TILE_B)                              # плиты зала с бассейном
bt.floor_code("M", *METAL)                               # металл насосной
bt.wall_code("W", "pk:bazaar/bazaar_w2_12")
bt.wall_code("Q", "pk:bazaar/bazaar_w2_12")
LOBBY = bt.room(10, 15, 29, 25, "W", "C")                # приёмная у входа
CHANGE_L = bt.room(1, 15, 10, 25, "W", "C")              # мужская раздевалка
CHANGE_R = bt.room(29, 15, 38, 25, "W", "C")             # женская раздевалка
HALL = bt.room(1, 1, 27, 15, "Q", "B")                   # зал с бассейном
OFFICE = bt.room(27, 1, 38, 8, "W", "D")                 # кабинет целителя
PUMP = bt.room(27, 8, 38, 15, "W", "M")                  # насосная (люк в цистерну)
bt.opening(19, 25, 20, 25, "C")                          # вход с бульвара
bt.portal([(19, 25), (20, 25)], "zzyzx", (27, 22), "На бульвар")
bt.opening(10, 19, 10, 20, "C")                          # приёмная -> мужская раздевалка
bt.opening(29, 19, 29, 20, "C")                          # приёмная -> женская раздевалка
bt.opening(19, 15, 20, 17, "B")                          # приёмная -> зал
bt.opening(27, 5, 27, 6, "D")                            # зал -> кабинет целителя
bt.opening(27, 12, 27, 13, "M")                          # зал -> насосная

# ---- предметы купален (наборы pool / west / bazaar / hosp / nbunk)
POOL = P("zz_bath_pool", "zz_bath_pool", foot=[14, 6], block=False, layer="floor")   # чаша: кафель и вода
DRAIN = P("zz_bath_drain", "zz_bath_drain", block=False, layer="floor")              # решётка слива
HATCH = P("zz_hatch", "zz_hatch", block=False, layer="floor")                         # люк в цистерну
HOOKS = P("zz_hooks", "zz_hooks", block=False)                                       # доска с крючками
LOUNGER = P("zz_lounger", "pk:iresort/iresort_1_021", foot=[2, 1], sight=True)       # шезлонг у воды (pool_5_016 был буфетом с рыбой)
TOWELS = [P(f"zz_towel_{i}", f"pk:pool/pool_7_{n:03d}", block=False) for i, n in enumerate((80, 81, 82, 83))]
EXAM_BED = P("zz_exam_bed", "pk:hosp/hosp_1_007", foot=[3, 1], sight=True)           # кушетка для осмотра
SHELF_WOOD = "shelf_wood"                                                            # полка (без обыска)
TOWEL_SHELF = P("zz_towel_shelf", "pk:west/west_2_106", foot=[2, 1], sight=True)     # полка с бельём
BASKET = "zz_basket"                                                                 # корзина с бельём


def bput(name, x, y, **kw):
    """Явная постановка в купальнях: не встал — ошибка с причиной (как place() на бульваре)."""
    snap = (len(bt.props), len(bt.containers), set(bt.blocked), set(bt.soft), set(bt.soft_obj))
    try:
        ok = bt.put(name, x, y, **kw)
    except AssertionError as e:
        raise AssertionError(f"купальни: {e}") from None
    if ok and bt.props[-1][1:3] == [x, y]:
        return True
    foot = bt.footprint(name, x, y)
    why = []
    if any(c in snap[2] for c in foot):
        why.append("занято: " + str([c for c in foot if c in snap[2]]))
    if any(c in snap[3] or c in snap[4] for c in foot):
        why.append("мягкий предмет под ним")
    if any(c in bt.reserved for c in foot):
        why.append("резерв (проём)")
    h = bt.hides(name, x, y) if _props.info(name)["block"] else None
    if h:
        why.append(f"заслоняет {h[0]} ({h[1]}, {h[2]})")
    why.append("земля: " + "".join(bt.ground[b][a] for a, b in foot))
    raise AssertionError(f"купальни: «{name}» не встал в ({x}, {y}): " + "; ".join(why))


def bwall(name, x, y, dx=0, dy=-40):
    """Настенное (крючки, часы): клетка стены, картинка висит над полом под ней."""
    assert bt.ground[y][x] in bt.walls, f"купальни: «{name}» в ({x}, {y}) — там нет стены"
    bt.props.append([name, x, y + 1, dx, dy])


def bon(name, x, y, dx=0, dy=-34):
    """Мелочь на столешнице: клетка мебели, поднята в глубину, рисуется сразу после неё."""
    assert (x, y) in bt.blocked, f"купальни: «{name}» в ({x}, {y}) — под ним нет стола"
    bt.props.append([name, x, y, dx, dy, 1 - dy])


def bfp(name, x, y, dx=0, dy=0):
    """Плоское на полу и поверх мебели (труба, полотенце, решётка): не блокирует, не двигает ничего."""
    bt.props.append([name, x, y, dx, dy])

# ------------------------------------------------------------ приёмная
# Стойка лицом ко входу: за ней Ава, за её спиной — полки с чистыми полотенцами. Центр приёмной (x 17..22)
# свободен от двери до двери зала: вошедший сразу видит и стойку, и проход к воде.
bput("counter", 13, 20)
bput("counter", 15, 20)
bon("x_register", 13, 20, dx=-6, dy=-30)                  # касса на стойке
bon("w_newspaper", 15, 20, dx=-4, dy=-36)                 # книга записи
bput(TOWEL_SHELF, 13, 18)                                 # полка с полотенцами за спиной Авы
bput(TOWEL_SHELF, 16, 18)
for _x, _k in ((13, 0), (14, 2), (16, 1), (17, 3)):       # стопки чистых полотенец на полках
    bon(TOWELS[_k], _x, 18, dx=0, dy=-26)
    bon(TOWELS[(_k + 1) % 4], _x, 18, dx=0, dy=-50)
bwall("w_wall_clock", 24, 16)                             # часы над стойкой
bput("bench_7", 26, 19)                                   # где ждут, у восточной стены
bput("bench_24", 26, 21)
bput("stool_1", 27, 20)                                   # столик между скамьями
bput(PLANT, 27, 23)
bfp("x_carpet", 19, 24)                                   # дорожка у входа
LM.lamp(bt, "warm", 12, 17)                               # плафоны на северной стене приёмной
LM.lamp(bt, "warm", 22, 17)
bt.ceiling(18, 21, r=180, color=(255, 198, 138), flick=0.03)   # лампа на шнуре над стойкой

# ------------------------------------------------------------ раздевалки
# Шкафчики в ряд у северной стены (разные, один распахнут), крючки над скамьёй, скамья для разувания,
# корзина с бельём у стены. Сюжетный «шкафчик паломника» — в мужской.
for _x, _n in ((2, "locker_1"), (3, "locker_2"), (4, "locker_open_a")):
    bput(_n, _x, 18)
bput("bench_16", 3, 21)
bwall(HOOKS, 7, 17)                                       # крючки с полотенцем на стене
bput("bucket", 6, 23)
bfp("rag", 5, 22)
for _x, _n in ((33, "locker_3"), (34, "locker_4"), (35, "locker_open_b")):
    bput(_n, _x, 18)
bput("bench_24", 33, 21)
bwall(HOOKS, 31, 17)
bput("x_screen", 31, 22)                                  # ширма для переодевания
bput(PLANT, 37, 23)
bput("bucket", 30, 23)
LM.lamp(bt, "warm", 8, 17)                                # плафон в мужской
LM.lamp(bt, "warm", 30, 17)                               # плафон в женской
bt.ceiling(4, 21, r=165, color=(255, 198, 138), flick=0.05)   # лампочка на шнуре в раздевалках
bt.ceiling(34, 21, r=165, color=(255, 198, 138), flick=0.05)

# ------------------------------------------------------------ зал с бассейном
# Чаша — картинка из клеток пака pool (tools/make_bath.py): кафельный бортик, вода с рябью, ступени входа
# в южном борту, вход трубы в восточный борт, слив на дне. Вода непроходима, южная полоса бортика — нет:
# по ней ходят и с неё входят в воду. Прежде бассейн был прямоугольником воды кодом «~» — на снимке
# плоское синее пятно с тонкой каймой, то есть лужа посреди комнаты.
bput(POOL, 6, 6)
for _y in range(6, 11):                                   # вода чаши (нижняя полоса — проходимый бортик)
    for _x in range(6, 20):
        bt.blocked.add((_x, _y))                          # для расстановки: сюда ничего не встанет
        bt.solid_cells = getattr(bt, "solid_cells", set()) | {(_x, _y)}   # и в карту: вода непроходима
bt._reach = None
# скамьи с полотенцами у северной стены, лежаки на южной стороне, скамья у западной
bput("bench_16", 7, 4)
bput("bench_24", 13, 4)
for _x in (5, 8, 14, 17):                                 # шезлонги вдоль южного бортика, между ними — ступени
    bput(LOUNGER, _x, 13)
bput("bench_7", 2, 9)
bput(PLANT, 2, 4)
bput(PLANT, 26, 4)
bput("bucket", 13, 12)
bput("bench_16", 23, 6)                                   # скамья у восточной стороны зала
bfp(TOWELS[0], 23, 6, dx=8, dy=-20)
bput(PLANT, 26, 7)                                        # кадка у стены кабинета
bfp(TOWELS[0], 7, 4, dx=8, dy=-20)                        # полотенца на скамьях и лежаках
bfp(TOWELS[2], 13, 4, dx=8, dy=-20)
# мокро там, где выходят из воды: у ступеней и по бортику
bfp("x_vd_wet0", 10, 12)                                  # мокро там, где вышли из воды
bfp("x_vd_wet1", 14, 12)
# труба от насосной: по восточной стене зала, коленом на запад, к восточному борту чаши (y=9)
bfp(PIPE_NE, 26, 13)                                      # пришла из насосной через проём — и вверх
for _y in range(10, 13):
    bfp(PIPE_V, 26, _y)
bfp(PIPE_SW, 26, 9)
for _x in range(20, 26):
    bfp(PIPE_H, _x, 9)
for _x in (5, 11, 17, 23):                                # плафоны на северной стене зала
    LM.lamp(bt, "warm", _x, 3)
bt.ceiling(9, 12, r=200, color=(255, 200, 140), flick=0.03)    # лампы на шнуре над кромкой чаши
bt.ceiling(16, 12, r=200, color=(255, 200, 140), flick=0.03)

# ------------------------------------------------------------ кабинет целителя
# Стол с терминалом (журнал целителя, data/terminals.json) у северной стены, шкаф-аптека за стеклом,
# полка с журналами приёма, кушетка для осмотра, раковина. Антирадин из шкафа нужен, чтобы спасти Тимми.
bt.terminal(33, 4, "zz_healer")
bput("w_desk", 31, 4)
bon("w_newspaper", 31, 4, dx=-10, dy=-34)
bon("w_table_lamp", 31, 4, dx=14, dy=-30)
bput(SHELF_WOOD, 28, 4)                                  # журналы приёма
bput("w_chair_r", 30, 5)                                 # стул к столу, в профиль
bput(EXAM_BED, 32, 6)                                    # кушетка для осмотра
bput("sink", 37, 5)
bwall("w_wall_clock", 30, 3)
LM.lamp(bt, "warm", 34, 3)

# ------------------------------------------------------------ насосная
# Баки, насос, стояк, трубы по полу — от них вода и уходит в зал. Люк в полу (34,12) под замком,
# подход к нему (34,13) держим свободным.
bput(TANKS_W, 28, 11)                                    # баки с водой у северной стены
bput("bucket", 37, 11)
PIPE_FLOOR = P("zz_pipe_floor_w", "zz_pipe_floor_w", block=False, layer="floor")   # вода из цистерны — снизу, через пол
# вода идёт одной цепочкой: из пола (снизу, из цистерны) -> вдоль южной стены -> снизу в баки; из баков -> через
# проём в зал -> к восточному борту чаши (см. зал). Ничего не висит и не обрывается.
bfp(PIPE_FLOOR, 37, 14)                                  # выходит из пола (из цистерны) — на запад
for _x in range(32, 37):
    bfp(PIPE_H, _x, 14)
bfp(PIPE_NE, 31, 14)                                     # и вверх, снизу в правый бак
PIPE_V_UP = P("zz_pipe_v_up", "zz_pipe_v_up", block=False)   # между ножек до самого днища: фланец — стык с баком
bfp(PIPE_V_UP, 31, 11)                                   # клетка под баком занята им — ставим поверх
bfp(PIPE_V_UP, 29, 11, dx=24)                            # левый бак стоит на полклетки правее сетки — под его центр
for _y in (12, 13):                                      # в правый бак — снизу
    bfp(PIPE_V, 31, _y)
bfp(PIPE_V, 29, 12, dx=24)                               # из днища левого бака — вниз
bfp(PIPE_NW, 29, 13, dx=24)                              # и на запад, через проём в зал
for _x in (27, 28):
    bfp(PIPE_H, _x, 13)
bfp(PIPE_H, 28, 13, dx=24)                               # стык со сдвинутым коленом
bt.props.append([HATCH, 34, 12])                      # люк с замком — на клетке портала
bt.portal([(34, 12)], "zzyzx_cistern", (4, 5), "Цистерна",
          requires={"item": "ключ от насосной",
                    "msg": "Люк в полу насосной, на нём замок. Ключ — у смотрителя источника Гаса."})
LM.lamp(bt, "warm", 31, 10)
LM.lamp(bt, "warm", 36, 10)

# ------------------------------------------------------------ ящики и люди
bt.box("glass_cabinet", 35, 4, "шкаф целителя", {"вода Зайзикса": 2, "антирадин": 1, "крышки": 40})
bt.box("locker_1", 5, 18, "шкафчик паломника", {"крышки": 12, "бинт": 1})
bt.npcs += [["nurse_ava", 15, 19],                       # за стойкой приёмной, лицом ко входу
            ["bath_pilgrim", 11, 11],                    # на ступенях бассейна, у воды
            ["bath_pilgrim_b", 5, 20]]                   # в мужской раздевалке, у шкафчиков


# ================================================================ «Замок» Спрингера
# Гостиница и дом Спрингера (docs/furnish/zzyzx.md §3). За пятью номерами — коридор, как в настоящей
# гостинице: двери номеров выходят в него, а не в столовую и не в спальню хозяина; коридор широким
# проёмом смотрит в холл прямо напротив входных дверей. Парадный этаж: слева от входа — столовая с
# кухней-раздачей, посредине холл с приёмом и lounge-уголком, справа за дверью — покои Спрингера.
# Автообстановка выключена (furnish=False): прежде движок доставил сюда пять случайных тумбочек и пять
# шкафов с тряпками, а пять номеров вышли пятью копиями. Свет ночной задан вручную, пятна — от ламп.
ht = CityMap(city, "zzyzx_hotel", "«Замок» Спрингера", 44, 26, start=(21, 23), seed=83, interior=True,
             music="hotel", furnish=False)
ht.night = [126, 112, 98]
ht.floor_code("R", "pk:aoffice/p3/3,1,1,1")           # ковёр номеров
ht.floor_code("C", "pk:hotel/hotel_f1_23")            # мрамор холла и покоев
ht.floor_code("D", "pk:cult/cult_f2_21", "pk:cult/cult_f2_20")   # тёмные доски коридора (zcity_f1_00 — кирпичная кладка)
ht.floor_code("W", "pk:hotel/hotel_f1_03")            # кафель столовой
ht.wall_code("Y", "pk:hotel/hotel_w1_15")             # номера — кремовая штукатурка с панелью
ht.wall_code("Q", "pk:hotel/hotel_w1_18")             # номер вдовы — выцветшие обои с розетками
ht.wall_code("V", "pk:hotel/hotel_w1_23")             # холл, коридор, покои — панели с бордюром

X0 = (1, 9, 17, 25, 33)                               # левые стены пяти номеров
ROOMS = [ht.room(x0, 1, x0 + 8, 12, "Q" if x0 == 33 else "Y", "R") for x0 in X0]
ht.paint("V", 1, 13, 41, 17)                          # стены коридора и северная стена парадного этажа
ht.paint("D", 2, 13, 40, 15)                          # пол коридора — доски
RUNNER_T = P("ht_runner", "zz_runner", block=False, layer="floor")   # дорожка: клетки встык (tools/make_zzyzx_hotel.py)
for _x in range(2, 41):
    ht.props.append([RUNNER_T, _x, 14])                # по центру коридора — бордовая дорожка с золотой каймой
ht.paint("V", 1, 16, 43, 25)                          # стены парадного этажа и фасад
ht.paint("W", 2, 18, 11, 24)                          # столовая — белый кафель
ht.paint("C", 13, 18, 30, 24)                         # холл — мрамор
ht.paint("C", 32, 18, 42, 24)                         # покои Спрингера — мрамор
ht.opening(21, 25, 22, 25, "C")                       # вход с бульвара
ht.portal([(21, 25), (22, 25)], "zzyzx", (70, 22), "На бульвар")
ht.opening(20, 16, 21, 17, "C")                       # холл -> коридор, напротив входных дверей
for _x0 in X0:                                        # номера -> коридор
    ht.opening(_x0 + 4, 12, _x0 + 4, 12, "R")
ht.opening(12, 20, 12, 21, "W")                       # холл -> столовая
ht.opening(31, 20, 31, 21, "C")                       # холл -> покои

# ---- предметы «Замка» (наборы hotel / lhotel / west / iresort, колыбель — tools/make_zzyzx_hotel.py)
H_SOFA = P("ht_sofa", "pk:hotel/hotel_2_064", foot=[2, 1], sight=True)        # диван на три места
H_WINDOW = P("ht_window", "pk:hotel/hotel_2_008", block=False)                # окно на фасаде
H_KEYBOX = P("ht_keybox", "pk:lhotel/lhotel_1_031", block=False)              # доска с ключами номеров
H_PHOTO = P("ht_photo", "pk:hotel/hotel_1_070", block=False)                  # фотография в рамке
H_FLOWERS = P("ht_flowers", "pk:iresort/iresort_1_062")                       # цветы в горшке
H_SUITCASES = P("ht_luggage", "pk:hotel/hotel_5_080", foot=[2, 1], sight=True, search="bag", title="багаж")   # тележка с чемоданами
H_RECEPT = P("ht_reception", "pk:hotel/hotel_5_048", foot=[2, 1], sight=True)  # стойка портье со звонками
H_DESK_PH = P("ht_desk_phone", "pk:hotel/hotel_5_012", foot=[2, 1], sight=True)  # стойка с телефоном и кассой
H_SAFE = P("ht_safe", "zz_safe", foot=[1, 1], sight=True)                      # стальной сейф (tools/make_zzyzx_hotel.py)
H_RACK = P("ht_luggage_rack", "pk:hotel/hotel_4_160", foot=[1, 1])            # подставка под чемодан у кровати
H_VASE = P("ht_vase", "pk:hotel/hotel_4_221", block=False)                     # вазочка с цветами — на стол
H_TEA = P("ht_tea", "pk:hotel/hotel_4_132", block=False)                       # поднос с чайником и чашками
H_CLOCK = P("ht_clock", "pk:hotel/hotel_4_227", block=False, scale=0.5)                   # будильник
H_TOWELS = P("ht_towels", "pk:hotel/hotel_4_199", block=False)                 # стопка свежих полотенец
H_GUESTBOOK = P("ht_guestbook", "pk:hotel/hotel_4_146", block=False, scale=0.45)  # книга гостей «HOTEL»
H_LEDGER = P("ht_ledger", "pk:hotel/hotel_4_147", block=False, scale=0.6)        # тетрадь в коже
BEDS_H = [P(f"ht_bed{i}", f"pk:hotel/hotel_1_{n:03d}", foot=[2, 2], sight=True) for i, n in enumerate((8, 21, 85, 73))]
RUGS_H = ["w_rug_red", P("ht_rug_straw", "pk:iresort/iresort_1_056", block=False, layer="floor"),   # плетёная циновка
          P("ht_rug_blue", "pk:lhotel/p2/10,12,2,2", block=False, layer="floor")]                  # выцветший узорный
CRADLE = P("zz_cradle", "zz_cradle", foot=[1, 1], sight=False)               # детская кроватка вдовы (40×60)                # детская колыбель вдовы
H_JUG = P("ht_jug", "pk:destown/p3/4,7,1,1", block=False, scale=0.45)         # кувшин у постели (не амфора)
COUNTER, REGISTER, BOOK = "counter", "x_register", "w_newspaper"
CHAIR_R, CHAIR_L = "w_chair_r", "w_chair_l"                                   # стулья в профиль
T_LONG, T_PLAIN = "w_table_long", "w_table_plain"
RUG, RUNNER = "w_rug_red", "x_carpet"
SCREEN = "x_screen"                                                             # ширма для переодевания
T_LAMP = "w_table_lamp"


def hput(name, x, y, **kw):
    """Явная постановка в «Замке»: не встал — ошибка с причиной (как bput в купальнях)."""
    snap = (len(ht.props), set(ht.blocked), set(ht.soft), set(ht.soft_obj))
    try:
        ok = ht.put(name, x, y, **kw)
    except AssertionError as e:
        raise AssertionError(f"«Замок»: {e}") from None
    if ok and ht.props[-1][1:3] == [x, y]:
        return True
    foot = ht.footprint(name, x, y)
    if any(ht.ground[b][a] not in ht.floors for a, b in foot):
        raise AssertionError(f"«Замок»: «{name}» в ({x}, {y}) — под ним не пол, а стена: "
                             + str([(a, b, ht.ground[b][a]) for a, b in foot]))
    why = []
    if any(c in snap[1] for c in foot):
        why.append("занято: " + str([c for c in foot if c in snap[1]]))
    if any(c in snap[2] or c in snap[3] for c in foot):
        why.append("мягкий предмет под ним")
    if any(c in ht.reserved for c in foot):
        why.append("резерв (проём)")
    h = ht.hides(name, x, y) if _props.info(name)["block"] else None
    if h:
        why.append(f"заслоняет {h[0]} ({h[1]}, {h[2]})")
    why.append("земля: " + "".join(ht.ground[b][a] for a, b in foot))
    raise AssertionError(f"«Замок»: «{name}» не встал в ({x}, {y}): " + "; ".join(why))


def hwall(name, x, y, dx=0, dy=-40):
    """Настенное (окно, портрет, доска с ключами): клетка стены, картинка висит на ней."""
    assert ht.ground[y][x] in ht.walls, f"«Замок»: «{name}» в ({x}, {y}) — там нет стены"
    ht.props.append([name, x, y + 1, dx, dy])


def hon(name, x, y, dx=0, dy=-34):
    """Мелочь на столешнице: клетка мебели, поднята в глубину, рисуется сразу после неё."""
    assert (x, y) in ht.blocked, f"«Замок»: «{name}» в ({x}, {y}) — под ним нет стола"
    ht.props.append([name, x, y, dx, dy, 1 - dy])


def hflat(name, x, y, dx=0, dy=0):
    """Плоское поверх (дорожка, полотенце): не блокирует и ничего не сдвигает."""
    ht.props.append([name, x, y, dx, dy])


# ------------------------------------------------------------ коридор
# Ковровая дорожка по центру, плафоны на обеих стенах, консоль с пальмой между дверями 29 и 37,
# чемоданы брошены у двери номера 4, кадки в торцах.
hput(T_PLAIN, 32, 13)                                 # консольный столик у северной стены
hon(H_FLOWERS, 32, 13, dy=-34)                        # на нём — цветы
hput(H_SUITCASES, 27, 13)                             # чемоданы у двери номера 4
hput(PLANT, 4, 13)                                    # кадка у западного торца коридора
hput(PLANT, 38, 15)                                   # и у юго-восточного
# настенных плафонов в коридоре быть не может: движок снимает их из узкого прохода (vaultkit.tidy_lamps),
# поэтому коридор светит лампами на шнуре — как в мотеле
for _lx in (7, 15, 23, 31, 39):
    ht.ceiling(_lx, 14, r=150, color=(255, 196, 132), flick=0.03)

# ------------------------------------------------------------ номера
# У всех: кровать изголовьем к северной стене, тумбочка с лампой, шкаф, окно на фасаде, ковёр у ног
# кровати, письменный стол у восточной стены и стул в профиль лицом к столу. Дальше — своё у каждого.
# 1 — «гость с деньгами»: двуспальная, чемодан у двери, раковина в углу, бумаги на столе.
hput(BEDS_H[0], 2, 4)                                 # голубое покрывало
hput(NIGHT, 4, 4)
hon(H_CLOCK, 4, 4)                                    # будильник: торговец встаёт рано — к открытию рынка
hput(WARDROBE, 7, 4)
hwall(H_WINDOW, 5, 2)
hput(RUGS_H[2], 2, 6)
hput("w_desk", 7, 8)                               # письменный стол (hotel_1_086 — со своим офисным креслом)
hput(CHAIR_R, 6, 8)                                   # стул западнее стола — лицом вправо, к столу
hon(H_LEDGER, 7, 8, dx=-14, dy=-40)                        # счета: сколько бутылей «чудо-воды» везти в Нидлс
hon(H_TEA, 7, 8, dx=14, dy=-42)                       # недопитый чай
hput(SINK, 2, 10)
hput(H_RACK, 4, 6)                                    # чемодан на подставке у кровати, раскрыт
ht.ceiling(5, 8, r=165, color=(255, 198, 138), flick=0.03)

# 2 — «одинокий путник»: койка, ширма отгораживает умывальник, сумка у двери, столик вместо стола.
hput(BED_S, 10, 4)
hput(NIGHT, 11, 4)
hon(T_LAMP, 11, 4)
hput(WARDROBE, 15, 4)
hwall(H_WINDOW, 13, 2)
hput(SCREEN, 10, 8)                                   # ширма: за ней умывальник
hput(SINK, 10, 10)
hput(T_PLAIN, 15, 8)
hput(CHAIR_R, 14, 8)
hon(H_JUG, 15, 8, dx=-10, dy=-30)                     # кувшин с водой на столике
hput(H_RACK, 12, 6)                                   # сумка путника на подставке — так и не разобрана
ht.ceiling(13, 7, r=165, color=(255, 198, 138), flick=0.03)

# 3 — «приготовлен к гостю»: свежие полотенца стопкой на кровати, кувшин на тумбочке, ничего личного.
hput(BEDS_H[2], 18, 4)                                # бежевое покрывало, заправлено без складки
hput(NIGHT, 20, 4)
hon(H_VASE, 20, 4, dy=-30)                            # свежие цветы — номер ждёт гостя
hput(WARDROBE, 23, 4)
hwall(H_WINDOW, 22, 2)
hput(RUGS_H[1], 18, 6)
hput("w_desk", 23, 8)                               # письменный стол (hotel_1_086 — со своим офисным креслом)
hput(CHAIR_R, 22, 8)
hon(H_TOWELS, 23, 8, dx=-14, dy=-44)                  # стопка свежих полотенец на столе — для гостя
hon(H_JUG, 23, 8, dx=14, dy=-44)                       # кувшин «чудо-воды» на столе — входит в цену
ht.ceiling(21, 8, r=165, color=(255, 198, 138), flick=0.03)

# 4 — «лучший номер, гость на водах»: столик с цветами у окна, кресло с торшером, книга на столе.
hput(BEDS_H[3], 26, 4)                                # клетчатое шерстяное покрывало: гостю холодно и в пустыне
hput(NIGHT, 28, 4)
hon(T_LAMP, 28, 4)
hput(WARDROBE, 31, 4)
hwall(H_WINDOW, 30, 2)

hput(RUG, 26, 6)
hput("w_desk", 31, 8)                               # письменный стол (hotel_1_086 — со своим офисным креслом)
hput(CHAIR_R, 30, 8)
hon(H_LEDGER, 31, 8, dx=-14, dy=-40)                      # раскрытая книга
hon(H_VASE, 31, 8, dx=16, dy=-44)                     # вазочка с цветами на столе
hput(ARMCHAIR, 26, 10)
hput(LAMP, 27, 10)                                    # торшер у кресла
ht.ceiling(29, 7, r=165, color=(255, 198, 138), flick=0.03)

# 5 — «вдова Харпер»: двадцать лет в одной комнате. Кровать заправлена с одной стороны, на второй
# тумбочке фотография в рамке; у кровати колыбель, комод с детскими вещами «на потом», цветы и кувшины.
hput(BED, 35, 4)                                       # кровать сдвинута от стены: тумбочки — по обе стороны
hput(NIGHT, 34, 4)
hon(H_PHOTO, 34, 4, dy=-30)                           # фотография в рамке
hput(NIGHT, 37, 4)
hon(T_LAMP, 37, 4)
hput(WARDROBE, 39, 4)
hwall(H_WINDOW, 38, 2)
hput(RUG, 34, 6)
hput(CRADLE, 37, 6)                                   # кроватка вплотную к её кровати, у тумбочки — на виду
hput("w_dresser", 39, 9)                              # комод, где лежат детские вещи
hon(H_TOWELS, 39, 9, dx=-14, dy=-50)                  # сложенное детское одеяльце на комоде
hon(H_JUG, 39, 9, dx=16, dy=-52)                      # кувшин с водой Зайзикса
hput(T_PLAIN, 38, 8)                                  # столик у окна
hput(CHAIR_R, 37, 8)                                  # стул лицом к столику
hon(H_JUG, 38, 8, dx=-8, dy=-32)                      # второй кувшин — на столике
hput(JUGS[0], 34, 9)                                  # третий — амфора на полу у кровати
hput(H_FLOWERS, 40, 6)                                # цветы в горшке у шкафа
ht.ceiling(36, 7, r=170, color=(255, 196, 136), flick=0.03)
ht.npcs += [["guest_widow", 36, 8]]                   # у колыбели, не в проёме

# ------------------------------------------------------------ холл
# Стойка портье лицом ко входу: две секции по две клетки, на них касса и раскрытая книга гостей;
# за стойкой портье, за его спиной на стене — доска с ключами номеров. Правее, на стене, портрет.
hput(H_RECEPT, 14, 19)                                # стойка портье: звонок для гостей
hput(H_DESK_PH, 16, 19)                               # вторая секция: телефон и касса
hon(H_GUESTBOOK, 16, 19, dx=34, dy=-38)                     # книга гостей — двадцать лет одна и та же фамилия в 5-м
hwall(H_KEYBOX, 15, 16, dy=-30)                               # доска с ключами за спиной портье
hwall("w_painting", 18, 16, dy=-26)                   # портрет Спрингера в золочёной раме
# lounge-уголок в восточной половине: диван спинкой к стене, ковёр перед ним, кресла по сторонам,
# низкий столик у южного края ковра, торшер у дивана
hput(H_SOFA, 25, 18)
hput(RUG, 25, 19)
hput(ARMCHAIR, 24, 20)
hput(ARMCHAIR, 27, 20)
hput("stool_1", 25, 21)                               # низкий столик
hput(LAMP, 27, 18)
hput(PLANT, 13, 18)                                   # пальма в северо-западном углу
hput(PLANT, 29, 23)                                   # и в юго-восточном
hput(H_SUITCASES, 18, 22)                             # чемоданы у входа
LM.lamps(ht, "warm", [(23, 17), (29, 17)])
ht.ceiling(16, 20, r=180, color=(255, 198, 138), flick=0.03)
ht.ceiling(25, 19, r=175, color=(255, 198, 138), flick=0.03)
ht.ceiling(19, 21, r=175, color=(255, 198, 138), flick=0.03)

# ------------------------------------------------------------ столовая
# Кухня-раздача вдоль северной стены: шкаф с посудой, чугунная печка с трубой, разделочный стол и
# буфет со стеклом (в нём — обрывок карты). Тоня носит еду отсюда на хозяйственный двор.
hput("w_cupboard", 2, 18)
hput(STOVE, 4, 18)
hput(T_LONG, 6, 18)                                   # разделочный стол у стены
ht.box("w_glass_cabinet", 10, 18, "буфет",            # буфет со стеклом — в нём обрывок карты
       {"консервы": 2, "энергетический батончик": 1, "обрывок карты (север)": 1})
assert ht.props[ht.containers[-1]["prop"]][1:3] == [10, 18], "буфет встал не туда"
for _ty in (21, 23):                                  # столы на двоих: стулья в профиль лицом к столу
    hput(T_LONG, 3, _ty)
    hput(CHAIR_R, 2, _ty)
    hput(CHAIR_L, 5, _ty)
hput(T_PLAIN, 8, 21)
hput(CHAIR_R, 7, 21)
hput(CHAIR_L, 10, 21)
ht.ceiling(3, 22, r=170, color=(255, 198, 138), flick=0.03)
ht.ceiling(8, 21, r=165, color=(255, 198, 138), flick=0.03)
ht.ceiling(6, 19, r=160, color=(255, 198, 138), flick=0.03)      # над раздачей

# ------------------------------------------------------------ покои Спрингера
# Роскошнее номеров: широкая кровать с двумя тумбочками, бар с бутылками и книжный шкаф вдоль стены,
# стол с терминалом у восточной, ковёр у ног кровати, кресло, сейф в углу.
hput(BED, 33, 18)
hput(NIGHT, 32, 18)
hput(NIGHT, 35, 18)
hon(T_LAMP, 35, 18)
hput("w_liquor", 37, 18)                              # бар: шкаф с бутылками
hput("w_bookcase", 40, 18)                            # книжный шкаф
hput(RUG, 33, 20)
ht.terminal(42, 21, "zz_springer")
assert ht.props[-1][1:3] == [42, 21], "терминал zz_springer встал не туда"
hput(CHAIR_R, 41, 21)                                 # стул к столу с терминалом
hput(ARMCHAIR, 39, 23)                               # кресло для чтения — у книжного угла, не у двери
hput("stool_1", 40, 23)                               # столик у кресла
hput(PLANT, 36, 23)
ht.box(H_SAFE, 42, 18, "сейф Спрингера",                # в северо-восточном углу, у книжного шкафа
       {"крышки": 220, "стимулятор": 2, "ключ от насосной": 1},
       requires={"flag": "springer_safe", "msg": "Сейф с кодом. Код Спрингер держит в голове — или в терминале."})
ht.ceiling(34, 20, r=180, color=(255, 198, 138), flick=0.03)
ht.ceiling(40, 21, r=160, color=(255, 198, 138), flick=0.03)      # вторая лампа — у бара


# ================================================================ цистерна
# Узел Vault-Tec ZZ-4 под купальнями (docs/furnish/zzyzx.md §4): фильтр «Чистый лист» с 2076 года чистит воду
# от радиации и тайно дозирует агент CS-3 — здесь разгадка города. Пятьдесят лет сюда спускается только
# смотритель Гас: чинит трубы и не задаёт вопросов. Всё поштучно, автообстановки нет (furnish=False): прежде
# «ливнёвка» ставила в зал кучи хлама и лужи там, где должна идти вода, а «трубы» (zz_pipes) на деле были
# кучей камней (sewer_1_042), отстойники — двумя прудами 10×4.
# Вода одной цепочкой, у каждой трубы видно откуда и куда: приток из потолка (8,5) → приёмный лоток
# (8..9, y6..10) → два отстойника (10..20, y6..7 и y9..10) → сборный лоток (21..22) → слив под пол (23,10) →
# подъём в приёмный бак (23,6) → ступень 1 «Чистого листа» (колонны 27..28, y5) → баки чистой воды
# (29..32, y5) → стояк вниз (31,5) → под пол → вдоль южной стены (y20) → колено (7,20) → вверх по x=7 →
# насос (7,6) → стояк в потолок (7,4) → в насосную купален, где вода выходит из пола в (37,14).
cs = CityMap(city, "zzyzx_cistern", "Цистерна под купальнями", 34, 22, start=(4, 5), seed=84, interior=True,
             music="lab", night=[78, 92, 104], furnish=False)
cs.floor_code("M", *METAL)
cs.wall_code("K", "pk:nbunk/nbunk_w1_12")
cs.room(1, 1, 33, 21, "K", "M")

# ---- свои предметы цистерны (tools/make_cistern.py)
PUMP = P("zz_pump", "zz_pump", foot=[1, 1])                           # напорный насос в линии
RISER = P("zz_pipe_riser", "zz_pipe_riser", block=False, layer="floor")   # труба входит в потолок
DROP = P("zz_pipe_drop", "zz_pipe_drop", block=False, layer="floor")      # труба из потолка, слив в лоток
THIN = {a: P(f"zz_pipe_thin_{a}", f"zz_pipe_thin_{a}", block=False, layer="floor")
        for a in ("h", "v", "ne", "nw", "sw", "se")}                  # тонкая линия дозирования CS-3
MUG = P("zz_mug", "zz_mug", block=False)                              # кружка Гаса
ASHTRAY = P("zz_ashtray", "zz_ashtray", block=False)                  # пепельница с окурками
SIGN_CS3 = P("zz_sign_cs3", "zz_sign_cs3", block=False)               # знак опасности на стойке
PLAC_STEP2 = P("zz_sign_step2", "zz_sign_step2", block=False)         # «Ступень 2 — не отключать»
POSTER = P("zz_poster_safety", "zz_poster_safety", block=False)       # плакат техники безопасности Vault-Tec
SEAL = P("zz_seal", "zz_seal", block=False)                           # пломба на дверце шкафа
FUNGUS = [P(f"zz_fungus{i}", f"pk:sewer/sewer_1_{n:03d}", block=False)
          for i, n in enumerate((24, 50))]                            # грибы в сырости
VT_LOCKER = P("zz_vt_locker", "p2_013", scale=0.75, sight=True)             # опломбированный шкаф (без обыска)
SPARES = P("zz_spares", "p2_021", scale=0.75, foot=[2, 1])                  # стеллаж картриджей (без обыска)
CATWALK = P("zz_catwalk", "zz_catwalk", block=False, layer="floor")         # настил мостка
TALLY49 = P("zz_tally", "zz_tally", block=False)                            # засечки ремонтов Гаса
TOOLBOARD = P("zz_toolboard", "zz_toolboard", block=False)                  # доска с инструментом


def cwhy(name, x, y):
    """Почему предмет не встал — чтобы ошибка сборки говорила делом."""
    foot = cs.footprint(name, x, y)
    why = []
    if any(c in cs.blocked for c in foot):
        why.append("занято: " + str([c for c in foot if c in cs.blocked]))
    if any(c in cs.soft_obj for c in foot):
        why.append("мягкий предмет под ним")
    if any(c in cs.reserved for c in foot):
        why.append("резерв (проём, лестница)")
    if _props.info(name)["block"] and cs.hides(name, x, y):
        h = cs.hides(name, x, y)
        why.append(f"заслоняет {h[0]} ({h[1]}, {h[2]})")
    why.append("земля: " + "".join(cs.ground[b][a] for a, b in foot))
    return "; ".join(why)


def cput(name, x, y, **kw):
    """Явная постановка в цистерне: не встал — ошибка с причиной (как bput в купальнях)."""
    try:
        ok = cs.put(name, x, y, **kw)
    except AssertionError as e:
        raise AssertionError(f"цистерна: {e}") from None
    if ok and cs.props[-1][1:3] == [x, y]:
        return True
    raise AssertionError(f"цистерна: «{name}» не встал в ({x}, {y}): " + cwhy(name, x, y))


def cwall(name, x, y, dx=0, dy=-40):
    """Настенное (плакат, табличка, засечки): клетка стены, картинка висит над полом под ней."""
    assert cs.ground[y][x] in cs.walls, f"цистерна: «{name}» в ({x}, {y}) — там нет стены"
    cs.props.append([name, x, y + 1, dx, dy])


def con(name, x, y, dx=0, dy=-34):
    """Мелочь на столешнице: клетка мебели, поднята в глубину, рисуется сразу после неё."""
    assert (x, y) in cs.blocked, f"цистерна: «{name}» в ({x}, {y}) — под ним нет стола"
    cs.props.append([name, x, y, dx, dy, 1 - dy])


def cfp(name, x, y, dx=0, dy=0):
    """Плоское на полу и поверх мебели (труба, знак, пломба): не блокирует и ничего не двигает."""
    cs.props.append([name, x, y, dx, dy])

# ------------------------------------------------------------ лестница и ствол труб
cs.props.append(["x_ladder", 4, 4])
cs.reserve(2, 4, 5, 5)                                    # подход к лестнице и прибытие (4,5) — свободны
cs.portal([(4, 4)], "zzyzx_bath", (34, 13), "Наверх, в насосную")
cfp(RISER, 7, 4)                                          # напорная — в потолок, в двух шагах от лестницы
cfp(DROP, 8, 5)                                           # приток от источника — из потолка, слив в лоток
cfp(PIPE_V, 7, 5)                                         # от стояка вниз, в насос
cput(PUMP, 7, 6)                                          # насос в линии
for _y in range(7, 20):                                   # чистая вода поднимается с юга — к насосу
    cfp(PIPE_V, 7, _y)
cfp(PIPE_NE, 7, 20)                                       # колено: с востока пришла, на север — вверх
cfp(PIPE_TAP, 6, 6)                                       # сливной кран у насоса: из него Гас моет кружку
# угол Гаса: табурет с кружкой и пепельницей, открытый ящик, ключи на стойке, ведро с тряпкой
cput("stool_1", 5, 7)
cfp(MUG, 6, 7, dx=-6)                                     # кружка под краном: Гас моет её здесь
cfp(ASHTRAY, 5, 8, dx=4)                                  # пепельница у табурета, под ногами
cput("toolbox_open", 4, 8)
cput("bucket", 3, 8)
cfp("rag", 4, 7)
cwall(TALLY49, 14, 3)                                    # засечки ремонтов — сорок девять и одна свежая
cwall("x_vd_sheet", 12, 3)                               # довоенный плакат Vault-Tec «МЫ НЕ УШЛИ»
cwall(POSTER, 16, 3)                                      # плакат техники безопасности Vault-Tec
cwall(TOOLBOARD, 10, 3)                                   # доска с инструментом на стене, у воды

# ------------------------------------------------------------ отстойники
# Каналы — кодом «~»: в подземелье движок рисует ровную каменную кромку, без пены и песка (src/townmap.py
# _indoor_water), поэтому два узких канала с бетонной тумбой между ними читаются каналами, а не прудом.
cs.floor_code("~", "pk:mport/p1/8,4,1,1", "pk:mport/p1/9,4,1,1",
              "pk:mport/p1/10,4,1,1", "pk:mport/p1/11,4,1,1")
cs.water_codes = ("~",)
cs.paint("~", 8, 6, 8, 10)                                # приёмный лоток под сливом
cs.paint("~", 9, 6, 21, 7)                                # отстойник 1
cs.paint("~", 9, 9, 21, 10)                               # отстойник 2
cs.paint("~", 22, 6, 22, 10)                              # сборный лоток
for _x in range(9, 22):                                   # между отстойниками — бетонная стена-разделитель
    cs.ground[8][_x] = "K"
for _x in (13, 18):                                       # мостки: проход в разделителе, настил — поверх
    cs.paint("M", _x, 6, _x + 1, 8)
    cs.paint("M", _x, 9, _x + 1, 10)
for _y in range(cs.H):
    for _x in range(cs.W):
        if cs.ground[_y][_x] == "~":
            cs.blocked.add((_x, _y))                      # вода непроходима и при расстановке (в карту — из water_codes)
cs._reach = None
for _x in (13, 18):
    for _y in (6, 7, 8, 9, 10):
        cfp(CATWALK, _x, _y)                              # стальной настил мостка, 2 клетки в ширину
for _x, _y in ((12, 5), (15, 5), (17, 5), (20, 5), (12, 11), (15, 11), (17, 11), (20, 11)):
    cfp("x_vd_hz_h", _x, _y)                              # жёлто-чёрная разметка по кромкам у мостков
for _x, _y in ((10, 5), (17, 5), (11, 11), (18, 11), (23, 7)):
    cfp("x_vd_waterline", _x, _y)                         # след уровня на бетоне у лотков

# ------------------------------------------------------------ фильтр «Чистый лист»
cput("water_tank_a", 23, 5)                               # приёмный бак: 3×2, у северной стены
cfp(PIPE_FLOOR, 23, 10)                                   # слив лотка уходит под пол
for _y in (7, 8, 9):
    cfp(PIPE_V, 23, _y)                                   # и поднимается в днище бака
cfp(PIPE_V_UP, 23, 6)
cput(VATS, 27, 5)                                         # ступень 1 — колонны «Чистого листа»
cfp(PIPE_H, 26, 5)                                        # из бака в колонны
cput(TANKS_W, 29, 5)                                      # баки чистой воды, 4 клетки
cfp(PIPE_V_UP, 31, 5)                                     # стояк из баков вниз
for _y in range(6, 20):
    cfp(PIPE_V, 31, _y)                                   # под пол — и вдоль восточной стены на юг
cfp(PIPE_NW, 31, 20)                                      # колено: с севера — на запад, вдоль южной стены
for _x in range(8, 31):
    cfp(PIPE_H, _x, 20)                                   # чистая вода идёт по полу к насосу
cfp(PLAC_STEP2, 27, 6, dx=-14)                            # табличка на ступени 2 — у колонн
# пульт ZZ-4 и довоенный стол оператора: терминал лицом в зал, на столе — журнал, кружка, табличка
cs.terminal(26, 8, "zz_cistern")
cput("w_desk", 24, 8)
con("w_newspaper", 24, 8, dx=-10, dy=-36)                 # раскрытый журнал смен
con(MUG, 25, 8, dx=10, dy=-34)                            # кружка оператора
con("x_vd_plaque", 25, 8, dx=-12, dy=-42)                 # латунная табличка «ОПЕРАТОР»
cfp("chair_broken", 25, 9)                                # стул отодвинут и сломан

# ------------------------------------------------------------ ступень 2: агент CS-3
cput(TANK, 30, 13)                                        # бак агента у восточной стены
cfp(SIGN_CS3, 29, 13, dx=-10)                             # знак опасности рядом, на стойке
cput("barrel_0", 32, 14)                                  # бочка агента
cput("barrel_12", 32, 13)
cfp(THIN["v"], 30, 12)                                    # тонкая линия дозирования: бак → колонны фильтра
cfp(THIN["v"], 30, 11)
cfp(THIN["v"], 30, 10)
cfp(THIN["sw"], 30, 9)                                    # колено: с юга — на запад
cfp(THIN["h"], 29, 9)
cfp(THIN["ne"], 28, 9)                                    # колено: на север — в колонны
for _y in (6, 7, 8):
    cfp(THIN["v"], 28, _y)

# ------------------------------------------------------------ склад Vault-Tec
cput(VT_LOCKER, 32, 12)                                  # опломбированный шкаф
cfp(SEAL, 32, 12, dx=-8, dy=-56)
cs.box(SPARES, 27, 12, "стеллаж с картриджами",         # сменные картриджи фильтра
       {"батарейки": 2, "крышки": 25, "антирадин": 1})
cput("canister", 25, 12)
cput("cardboard", 29, 14)
cs.box("metal_chest", 25, 15, "сундук сменщика",       # довоенный сундук оператора: снаряжение караула
       {"патроны": 6, "батарейки": 2, "крышки": 15})
cput("crate_broken", 32, 16)
cfp("x_wire_coil", 28, 16)                                # бухта кабеля
cs.box(CRATE, 24, 13, "ящик Vault-Tec",
       {"антирадин": 2, "образец «Чистый лист»": 1, "батарейки": 2})

# ------------------------------------------------------------ мастерская-развязка
# Южнее каналов: верстак, где Гас разбирает задвижки; на стене — довоенная схема узла, на полу — запас труб.
cput("concrete_table_2", 14, 15)
con("toolbox_open", 14, 15, dx=-8, dy=-38)
con("canister", 14, 15, dx=14, dy=-36)
cput("barrel_1", 20, 15)
cwall("x_vd_map", 19, 3)                                  # схема узла ZZ-4 на стене (2 клетки)
cfp("x_vd_rust1", 18, 14)
cfp("bucket", 12, 16)
cfp("x_manhole", 10, 13)                                  # сток в полу у каналов
cfp("x_puddle", 10, 14)
# обрезков труб на полу нет: кусок трубы, лежащий отдельно, читается оборванной магистралью
cput("crate_broken", 12, 18)                              # ящик с задвижками, которые Гас снял в ремонт
cput("barrel_0", 11, 18)
cput("barrel_1", 10, 19)
cput("x_planks", 24, 19)                                  # доски для мостков — у южной стены, а не посреди прохода

# ------------------------------------------------------------ сырой угол (юго-запад)
cput("barrel_1", 4, 17)
cput("barrel_0", 3, 18)
cput("crate_broken", 2, 19)
cfp(FUNGUS[0], 5, 16)                                     # гниль и грибы у воды
cfp(FUNGUS[1], 4, 15)
cfp("x_puddle", 5, 15)
cfp("junk_small_1", 6, 19)                                # гнездо радтаканов в хламе
cfp("wood_debris", 7, 18)
cfp("rag", 5, 19)
cfp("x_vd_wet0", 4, 16)
cfp("x_vd_wet1", 6, 17)
cfp("x_vd_drip", 2, 12)
cfp("x_vd_rust0", 3, 20)

# ------------------------------------------------------------ люди, вода и свет
cs.enemies += [["radroach", 10, 11], ["radroach", 20, 12], ["radroach", 4, 16],
               ["rat", 2, 18], ["rat", 6, 15], ["robot_skel", 28, 10]]
for _x, _y in ((4, 3), (22, 3), (26, 3)):
    LM.lamp(cs, "cold", _x, _y)                           # холодные плафоны на северной стене
LM.lamp(cs, "green", 9, 3)                                # зелёный — у воды
for _k, _x, _y in (("green", 2, 11), ("green", 2, 16), ("red", 26, 6), ("red", 30, 12), ("red", 32, 15)):
    LM.lamp(cs, _k, _x, _y)                               # напольные стойки у лотков и у машин
cs.ceiling(14, 12, r=210, color=(150, 200, 225), flick=0.05)   # лампы на шнуре над залом
cs.ceiling(20, 16, r=190, color=(150, 200, 225), flick=0.08)
cs.ceiling(27, 11, r=200, color=(196, 210, 220), flick=0.03)   # над фильтром
LM.decals(cs, "x_vd_wet0", [(10, 12), (14, 13), (19, 5), (23, 11), (6, 7), (12, 12)])
LM.decals(cs, "x_vd_wet1", [(16, 12), (21, 12), (3, 10)])
LM.decals(cs, "x_vd_rust1", [(8, 5), (22, 11), (30, 6)])
LM.decals(cs, "x_vd_drip", [(9, 4), (21, 11), (32, 7)])
LM.decals(cs, "x_vd_waterline", [(10, 5), (20, 11), (23, 7)])
LM.decals(cs, "x_vd_rust0", [(3, 12), (30, 18)])
LM.decals(cs, "x_vd_hz_h", [(23, 9), (23, 10), (28, 14), (29, 14)])
LM.doors(cs)

city.save(gap_exempt=("springer", "nurse_ava", "gus", "bath_pilgrim", "bath_pilgrim_b"))
# на карте мира — «Зайзикс»; открывается, если пройти рядом, или после Бейкера (src/game/quests.py)
L = json.load(open("data/locations.json", encoding="utf-8"))
L["zzyzx"].update({"world_name": "Зайзикс", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
