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
TENT = P("zz_tent", "pk:destown/destown_3_015", foot=[2, 2], sight=True)
TENT_S = P("zz_tent_small", "pk:destown/destown_3_018", foot=[2, 1])
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
ADOBE_GATE = P("zz_gate_arch", "pk:destown/p3/12,10,4,2", foot=[4, 1], sight=True, keybg=True)     # арка: проход 2 клетки посередине
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
POT = P("zz_pot_palm", "pk:bazaar/bazaar_3_206", foot=[1, 1])        # пальма в кадке на бульваре
JUG = P("zz_jug", "pk:destown/p3/3,6,1,1")                           # глиняный кувшин
JARS = P("zz_jars", "pk:bazaar/bazaar_2_048", search="shelf", title="кувшины")
BASKET = P("zz_basket", "pk:fishv/p1/12,2,2,2", foot=[2, 1])
HAY = P("zz_hay", "pk:west/west_1_004", block=False)                 # тюк сена
HIDE = P("zz_hide", "pk:destown/destown_3_023", block=False, layer="floor")
HIDE_B = P("zz_hide_b", "pk:destown/destown_3_033", block=False, layer="floor")
STALL_C = P("zz_stall_c", "pk:destown/destown_4_012", foot=[2, 1], keybg=True)   # прилавок, полосатый навес
WAGON = P("zz_wagon", "pk:west/west_1_011", foot=[2, 1], sight=True)             # крытая повозка
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
FOUNTAIN = P("zz_fountain", "pk:bcyber/bcyber_2_013", keybg=True,                 # чаша фонтана
             light={"r": 80, "color": [150, 210, 255], "at": [0.5, 0.3]})
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
# не растянута, а перестроена по смыслу: с запада — старая дорога и въезд с караулом; через весь курорт
# Бульвар Мечты с пальмами, фонтаном и эстрадой — к озеру Туэнде (набережная, причал, лодки). Севернее
# бульвара — купальни, источник «Сладкая вода» и «Замок» Спрингера; южнее, за саманной стеной-фасадом, —
# рынок и лагерь паломников, где живут те, ради кого курорт и стоит; юго-восток — глинобитные дома
# целителей. Колодец — на торговой улице, где сходятся рынок и лагерь. Расстановка поштучная:
# place/pbox (не встал — ошибка с причиной), случайного рассева посреди площадок нет.
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


def pond(cx, cy, rx, ry, wobble=0.12):
    """Вода карты: непроходима, берег и пену движок рисует сам (src/townmap.py _shore)."""
    z.blob("~", cx, cy, rx, ry, wobble=wobble)
    for wy in range(max(0, int(cy - ry * 2)), min(H, int(cy + ry * 2) + 1)):
        for wx in range(max(0, int(cx - rx * 2)), min(W, int(cx + rx * 2) + 1)):
            if z.ground[wy][wx] == "~":
                z.blocked.add((wx, wy))


# ---- земля курорта: дорога, бульвар, дворы, лагерь, квартал целителей
z.paint("p", 0, 36, 12, 40)                       # въезд с запада — утоптанный гравий
z.paint("q", 13, 36, 84, 40)                      # Бульвар Мечты — каменные плиты, «как в лучших домах»
z.paint("q", 17, 22, 38, 35)                      # двор купален
z.paint("q", 57, 22, 82, 35)                      # двор «Замка»
z.paint("q", 42, 34, 50, 42)                      # площадь у фонтана посреди бульвара
z.paint("q", 80, 22, 86, 50)                      # набережная озера
z.paint_ragged("k", 39, 23, 57, 33, depth=2)      # рабочий двор источника — за фасадом бульвара
z.paint_ragged("k", 12, 44, 52, 54, depth=2)      # рынок
z.paint_ragged("k", 8, 54, 48, 72, depth=3)       # лагерь паломников
z.paint_ragged("k", 54, 44, 86, 68, depth=2)      # квартал целителей
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
# Дорога из пустоши упирается в курорт: два каменных столба, доска с названием, будка караула. У въезда
# Спрингер держит человека, который считает входящих (folk_spots: bronya).
place(PILLAR, 11, 35)
place(PILLAR, 11, 41)
place(SIGN_BOARD, 6, 34)                          # доска «ЗАЙЗИКС. ЦЕЛЕБНЫЕ ИСТОЧНИКИ» — у самой дороги
place(SIGN_ENTRY, 6, 42)                          # указатель со стрелкой на южной обочине
place(HOUSE_D, 4, 29)                             # будка караула у въезда
place("table_2", 8, 31)                           # стол, за которым записывают входящих
place("chair_0", 8, 32)
place(BENCH, 6, 31)                               # где ждать, пока запишут
place(FIRE_PIT, 10, 32)                           # огневая яма: ночи в пустыне холодные
place(BARREL, 13, 32)
place(SACK, 12, 33)
place(CRATE, 14, 33)

# ------------------------------------------------------------ Бульвар Мечты
# Пальмы в два ряда, фонари 1950-х через две, скамьи лицом на бульвар (с севера это правильно: скамья
# нарисована лицом к камере, то есть на юг, в бульвар). Южная обочина уже самого бульвара — там только
# пальмы и фонари. Пальма — высокая: в её тени ничего не ставим, всё за ней прячется.
place(PALMS[0], 19, 35)
place(BENCH, 22, 35)
place(PALMS[1], 25, 35)
place(PALMS[2], 31, 35)
place(BENCH, 34, 35)
place(PALMS[3], 37, 35)
for x in (16, 28, 40):
    place(LAMP50, x, 35)
for x, y in ((15, 42), (21, 42), (33, 42), (39, 42), (51, 42),
             (63, 42), (69, 42), (75, 42)):
    place(PALMS[(x + y) % 4], x, y)
for x in (18, 30, 36, 48, 54, 66, 72, 78):
    place(LAMP50, x, 41)

# фонтан посреди бульвара — главный знак «процветания»: вода, которая льётся просто так
z.stamp("zz_pool", "pk:pool/p1/4,4,4,2", 44, 36)  # чаша фонтана: кафельный бассейн на площади
place(FOUNTAIN, 43, 37)                           # насадка-«чаша» у бассейна — вода, которая льётся
place(BENCH, 44, 35)
place(BENCH, 48, 35)
for x, y in ((42, 34), (50, 34), (42, 42), (50, 42)):
    place(POT, x, y)
place(FIRE_PIT, 42, 40)                           # жаровня у фонтана: вечером тут свет и люди
place(BARREL, 50, 37)

# эстрада: по вечерам играет оркестр, с неё же Спрингер говорит проповедь о воде
place(GAZEBO, 58, 34)
place(BENCH, 61, 35)                              # где сидят те, кто слушает проповедь
place(POT, 63, 34)

# ------------------------------------------------------------ киоск «чудо-воды»
# Два прилавка лицом на бульвар, за ними — кувшины, ящик с бутылями и бочка. Очередь стоит на площади
# перед фонтаном; кто не дошёл — сидит на скамье у аллеи. Всё это стоит на трубе от пруда (см. ниже).
place(STALL_B, 51, 35)
place(STALL, 54, 35)
place(SIGN_BOARD, 56, 34)                         # доска над прилавком: «ЦЕЛЕБНАЯ ВОДА»
place(JARS, 52, 33)                               # кувшины на розлив — за прилавком, в тени навеса
place(JUG, 51, 33)
pbox(CRATE, 55, 33, "бутыли с «чудо-водой»", {"вода Зайзикса": 3}, owner="springer")
place(BARREL, 49, 32)
place(BENCH, 43, 41)                              # где ждут те, кому уже невмоготу стоять
place(LANTERN, 56, 36)


# ------------------------------------------------------------ купальни
# Здание с крышей, вход с юга по центру; во дворе — очередь к кассе, скамьи у стены, кадки.
z.building(19, 10, 18, 12, "concrete", south=(8,), sign="КУПАЛЬНИ")
z.portal([(27, 21), (28, 21)], "zzyzx_bath", (19, 23), "Купальни")
place(BENCH, 21, 22)
place(BENCH, 24, 22)
place(BENCH, 31, 22)
place(BENCH, 34, 22)
place(POT, 18, 23)
place(POT, 36, 23)
place(LAMP50, 19, 25)
place(LAMP50, 36, 25)
place(CART, 22, 27)                               # тележка с бельём: купальни меняют простыни
place(AWNING, 20, 29)                             # навес от солнца для тех, кто ждёт очереди
place(BENCH, 20, 31)
place(BENCH, 22, 32)
place(SIGN_BOARD, 33, 27)                         # доска: часы купаний и цена
place(JUG, 31, 24)
place(JUG, 32, 24)
place(JUG, 25, 24)
place(BARREL, 35, 28)
place(CRATE, 18, 28)
# западный проулок купален — дровяной двор: печи греют воду, дрова завозят сюда
for i, (x, y) in enumerate(((13, 14), (15, 14), (13, 15), (15, 15))):
    place(LOGS[i % 2], x, y)
place(CART, 13, 17)
place(BARREL, 16, 17)
place(CRATE, 13, 19)
place(BARREL, 16, 19)
# внутри оболочки — вестибюль под крышей (в игре его закрывает крыша; в кадре с растаявшей крышей виден)
place(BENCH, 22, 13)
place(BENCH, 33, 13)
place(RUG, 27, 15)
place(LANTERN, 26, 18)
place(POT, 20, 19)
place(POT, 35, 19)

# ------------------------------------------------------------ источник «Сладкая вода»
# Пруд в пальмовой роще между купальнями и «Замком»: здесь молятся у воды и черпают её ковшом.
# Южный берег — каменная чаша, молитвенные коврики лицом к воде, доска с именами исцелённых.
place(BASIN, 48, 20)                              # каменная чаша источника
for x, y in ((41, 12), (43, 22), (50, 11), (54, 13), (55, 21), (45, 23), (52, 23)):
    place(PALMS[(x + y) % 4], x, y)
for x, y in ((43, 12), (53, 12), (46, 20), (50, 20), (41, 16), (55, 16)):
    place(REEDS[(x + y) % 4], x, y)
for _x in (43, 45, 51, 53):                       # коврики паломников лицом к воде
    place(PRAYER, _x, 21)
place(SIGN_BOARD, 52, 24)                         # доска исцелённых: имена, даты, благодарности
place(LANTERN, 47, 21)
place(LANTERN, 50, 21)
place(JUG, 47, 22)
place(JUG, 49, 22)
place(BARREL, 41, 24)
place(BENCH, 45, 24)

# ------------------------------------------------------------ рабочий двор источника
# То, чего с бульвара не видно: труба от пруда, бочки, ящики, тележка с бутылями, розлив под навесом.
# Тут Гас и его насос; отсюда «чудо-вода» идёт на прилавок в двадцати шагах от пальм.
place(PIPE, 47, 23)                               # стояк у самой чаши: отсюда воду и берут
place(PIPE, 47, 30)
place("zz_pipes", 50, 32)                         # лежак трубы к розливу
place(TANK_FILTER, 55, 27)                        # корпус фильтра под навесом
place(AWNING, 52, 25)                             # навес над розливом
place("table_2", 53, 27)
place(JUG, 51, 27)
place(JUG, 56, 28)
place(BARREL, 41, 26)
place(BARREL, 43, 26)
place(BARREL, 41, 28)
place(CRATE, 55, 30)
place(CRATE, 56, 31)
place(CART, 50, 30)
place(JARS, 44, 31)
place(SACK, 45, 25)
place(SACK, 56, 29)
place(LANTERN, 49, 27)
place(LOGS[0], 42, 31)
oskin("x_puddle", 48, 30)                           # пролитая вода под трубой
oskin("x_puddle", 44, 29)

# ------------------------------------------------------------ «Замок» Спрингера
# Кирпичный дом на северо-востоке; перед ним — парадный двор: аллея со столбами, кадки, скамьи,
# привезённая повозка. Номера и покои — внутри (zzyzx_hotel).
z.building(62, 9, 20, 13, "brick", south=(8,), sign="ЗАМОК")
z.portal([(70, 21), (71, 21)], "zzyzx_hotel", (21, 23), "«Замок» Спрингера")
for y in (25, 30):
    place(PILLAR, 67, y)
    place(PILLAR, 72, y)
for x in (60, 64, 75, 79):
    place(PALMS[(x + 24) % 4], x, 23)
for x, y in ((63, 24), (76, 24), (63, 31), (76, 31)):
    place(POT, x, y)
place(BENCH, 65, 22)
place(BENCH, 74, 22)
place(LAMP50, 69, 23)
place(LAMP50, 71, 28)
place(WAGON, 78, 28)                              # повозка гостей у парадного двора
place(CRATE, 79, 31)
place(SIGN_BOARD, 74, 34)
place(BARREL, 60, 34)
# внутри оболочки — холл «Замка» (виден в кадре с растаявшей крышей)
place(RUG_SHOW, 70, 14)
place(BENCH, 65, 13)
place(BENCH, 77, 13)
place(POT, 63, 18)
place(POT, 80, 18)
place(LANTERN, 70, 18)

# ------------------------------------------------------------ стена-фасад и ворота на юг
# Саманная стена вдоль южной обочины: с бульвара видно только её и пальмы. За стеной — рынок и лагерь.
# Две арки: торговая (к рынку) и восточная (к домам целителей, а дальше — к озеру).
z.hwall(ADOBE_WALL, 10, 76, 43, gaps=(26, 27, 28, 29, 57, 58, 59, 60))
place(ADOBE_GATE, 26, 43)
place(ADOBE_GATE, 57, 43)
place(LANTERN, 25, 42)
place(LANTERN, 30, 42)
place(LANTERN, 56, 42)
place(LANTERN, 61, 42)

# ------------------------------------------------------------ рынок
# Северный ряд — прилавки с навесами (кто может платить Спрингеру за место), южная сторона — товар
# прямо на коврах: паломники продают своё, чтобы дожить до следующей бутыли. Посреди — проход.
for name, x in ((STALL, 15), (STALL_B, 19), (STALL_C, 23), (STALL_B, 32), (STALL, 37), (STALL_C, 42)):
    place(name, x, 45)
place(SCALES, 30, 46)                             # весы на проходе: спорят о весе до хрипоты
for x, y in ((17, 45), (21, 45), (34, 45), (39, 45)):
    place(SACK, x, y)
for x, y in ((13, 46), (46, 46)):
    place(BARREL, x, y)
place(CRATE, 12, 47)
place(CRATE, 49, 46)
place(RUG, 20, 48)                                # южная сторона: товар на коврах
place(RUG_R, 24, 48)
place(RUG_B, 35, 48)
place(RUG, 39, 48)
for x, y in ((19, 49), (21, 49), (36, 49), (38, 49), (41, 49)):
    place(SACK, x, y)
for x, y in ((25, 49), (34, 49), (43, 48)):
    place(JUG, x, y)
place(JARS, 22, 50)
place(HIDE, 31, 49)                               # шкуры — товар лагеря
place(HIDE_B, 44, 49)
place(BASKET, 47, 51)
place(HAY, 47, 50)
place(SIGN_MARKET, 45, 44)                        # неоновая вывеска рынка на стене
place(LANTERN, 26, 51)
place(LANTERN, 45, 51)

# ------------------------------------------------------------ колодец
# Торговая улица идёт от арки на юг и вливается в лагерь: на этом стыке — колодец, общий на всех, кто
# живёт за стеной. Скамья, корыто, ведро и кувшины в очереди.
place(WELL, 33, 53)
place(BENCH, 36, 52)
place(TROUGH, 31, 53)
place(BUCKET, 30, 53)
place(JUG, 35, 53)
place(JUG, 35, 54)
place(LANTERN, 32, 52)

# ------------------------------------------------------------ лагерь паломников
# Шатры двумя станами по сторонам торговой улицы, общий котёл, костры, бельё на верёвке, шкуры, кувшины.
# Западный стан — те, кто пришёл давно; восточный — пришлые. Лазарет — в шатре с коврами.
for name, x, y in ((TENT_BIG, 8, 55), (TENT_AWN, 13, 55),
                   (TENT, 8, 59), (TENT_S, 13, 59), (TENT, 17, 59), (TENT_S, 21, 59),
                   (TENT_BIG, 13, 64), (TENT, 17, 64), (TENT_BIG, 21, 64),
                   (TENT, 8, 67), (TENT_BIG, 13, 69)):
    place(name, x, y)
for name, x, y in ((TENT, 31, 55), (TENT_AWN, 36, 55), (TENT_BIG, 42, 55),
                   (TENT, 31, 60), (TENT_S, 36, 60), (TENT, 42, 59),
                   (TENT_S, 45, 63), (TENT_BIG, 32, 65), (TENT, 37, 65), (TENT, 42, 66)):
    place(name, x, y)
# костры, ковры, бельё, посуда — в промежутках между шатрами, а не под ними
place(FIRE_PIT, 11, 57)                          # костёр западного стана
place(RUG, 9, 57)
place(RUG_R, 11, 62)
place(FIRE_PIT, 22, 58)                          # общий котёл: навес, костёр, стол, лавки
place(AWNING, 21, 56)
place("table_2", 23, 58)
place(BENCH, 9, 63)
place(BENCH, 25, 58)
place(JUG, 25, 59)
place(LAUNDRY, 17, 57)                            # бельё поперёк двора
place(LAUNDRY, 39, 69)
place(RUG, 24, 64)                                # молятся и в лагере, лицом к северу, к воде
place(RUG_R, 27, 64)
place(FIRE_PIT, 40, 58)                          # костёр восточного стана
place(RUG_B, 40, 62)
place(BENCH, 33, 58)
place(BENCH, 36, 63)
place("table_2", 35, 58)
for x, y in ((11, 63), (11, 58), (25, 57), (35, 64), (41, 63), (45, 66)):
    place(SACK, x, y)
for x, y in ((12, 66), (20, 67), (33, 63), (46, 60)):
    place(BARREL, x, y)
for x, y in ((15, 67), (20, 65), (28, 63), (38, 64), (46, 69)):
    place(JUG, x, y)
place(HIDE, 12, 63)
place(HIDE_B, 46, 67)
place(HAY, 29, 69)
place(CRATE, 47, 61)
place(FIRE_PIT, 19, 68)                          # очаг: воду греют круглые сутки
# лазарет: шатёр с коврами, кувшин с водой, фонарь — сюда кладут тех, кому совсем плохо
place(RUG, 16, 71)
place(JUG, 12, 69)
place(LANTERN, 12, 70)
# отхожее место — на отшибе, за станом
place(OUTHOUSE, 24, 71)
oskin("x_puddle", 23, 70)

# ------------------------------------------------------------ квартал целителей
# Глинобитные дома вдоль улицы от восточной арки: здесь живут те, кто лечит травами и водой, когда
# вода не помогает. При каждом доме — двор, кадка, скамья для больных, сушёные травы.
for name, x, y in ((HOUSE_A, 63, 46), (HOUSE_B, 69, 46), (HOUSE_C, 75, 46), (HOUSE_BIG, 63, 54),
                   (HOUSE_A, 70, 56), (HOUSE_B, 78, 52), (HOUSE_C, 79, 61), (HOUSE_D, 65, 62)):
    place(name, x, y)
place(BENCH, 66, 48)
place(BENCH, 72, 48)
place(POT, 62, 49)
place(POT, 74, 49)
place(POT, 62, 57)
place(POT, 77, 55)
place(JUG, 68, 49)
place(JUG, 71, 58)
place(BARREL, 81, 56)
place(CRATE, 84, 58)
place(FIRE_PIT, 68, 64)                          # очаг, на котором вываривают травы
place(JUG, 69, 65)
place(LAUNDRY, 74, 60)                            # травы и бинты сушат на верёвке
place(SIGN_BOARD, 60, 45)                         # доска целителей у входа в квартал
place(AWNING, 66, 51)                             # общий навес: под ним принимают больных
place(BENCH, 66, 53)
place(BENCH, 69, 53)
place(CART, 73, 52)
place(HERB, 83, 60)
place(HERB, 85, 60)
place(HERB, 83, 62)
place(HERB, 85, 62)
place(LANTERN, 68, 47)
place(LANTERN, 76, 49)
place(LANTERN, 66, 59)
# огородик с травами за домами
for x, y in ((83, 64), (85, 64), (83, 66), (85, 66)):
    place(HERB, x, y)
place(BUCKET, 82, 66)
place(SACK, 72, 66)

# ------------------------------------------------------------ озеро Туэнде
# Набережная, причал на сваях, лодки у мостков, лодочный сарай, сети и вёсла на просушке. Пальмы по
# берегу, камыш у воды.
z.paint("q", 82, 36, 86, 44)
z.paint("w", 83, 40, 88, 41)                      # доски причала: вода под ними вырезана
for wy in (40, 41):
    for wx in range(83, 89):
        z.blocked.discard((wx, wy))
place(ROWBOAT, 90, 39, force=True)
place(BOAT, 89, 43, force=True)
place(BOAT_B, 87, 35, force=True)
place(SHED_BOAT, 84, 47)
place(NET, 81, 48)
place(OARS, 86, 44)
place(NET_RACK, 81, 44)
place(BARREL, 84, 50)
place(CRATE, 82, 49)
place(JUG, 83, 44)
for x, y in ((86, 30), (87, 36), (85, 26), (87, 52), (84, 33)):
    place(PALMS[(x + y) % 4], x, y)
for x, y in ((89, 26), (90, 55), (88, 47), (89, 52)):
    place(REEDS[(x + y) % 4], x, y)
place(LANTERN, 84, 38)
place(BENCH, 86, 37)

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
# Жители — у своего дела, не в проёмах: Спрингер на площади у фонтана, где его видят все; Гас — у
# фильтра в рабочем дворе; Абдул — за прилавком; Мария с Тимми — в очереди за водой; Лоис — у себя в
# квартале; Хэнк — у костра в лагере.
npc("springer", 52, 37)
npc("gus", 54, 29)
npc("merchant_zz", 25, 45)
npc("pilgrim_maria", 51, 36)
npc("pilgrim_timmy", 52, 36)
npc("healer_girl", 67, 57)
npc("pilgrim_hank", 13, 63)
z.walk_zones["springer"] = [43, 36, 56, 40]        # прохаживается по площади у фонтана
z.walk_zones["merchant_zz"] = [24, 45, 26, 47]     # у прилавка и перед ним
z.walk_zones["healer_girl"] = [63, 56, 72, 62]     # между домами квартала
z.walk_zones["pilgrim_hank"] = [10, 61, 18, 66]    # у костра западного стана
# у авторов есть свои анкеты жителей (data/folks.json) — ставим их туда, где они и работают
z.folk_spots.update({
    "bronya": [10, 37],                            # часовой — у въезда, на дороге
    "mirra": [28, 24],                             # банщица — у входа в купальни, с полотенцем
    "zakhar": [74, 23],                            # управляющий — в парадном дворе «Замка»
    "kord": [53, 25],                              # фильтровщик — у насадки фильтра
    "tonya": [31, 34],                             # подавальщица — у стола с лепёшками
    "esfir": [72, 60],                             # знахарка — у своего огородика
    "stepan": [27, 47],                            # старик торгует на рынке
    "pasha": [84, 46],                             # рыбак — у сетей
    "gerda": [84, 39],                             # смотрительница причала
    "dina": [86, 42],                              # девочка у лодок
    "critter:cat": [[17, 59], [38, 62], [23, 71]],
    "critter:dog": [[15, 64]],
    "critter:chicken": [[30, 70], [31, 70], [32, 71]],
})
if place.fails:
    print("ОТКАЗОВ:", len(place.fails))
    for w in place.fails:
        print("  ", w)
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
