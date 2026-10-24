"""
Заправка «Последний шанс» (data/maps/station.json, 100×62) — последняя заправка перед дюнами, логово
Бензо-банды Шрама; сюда сбежал Дэкс с глазом деда (docs/story.md §6, квест «Шрам на заправке»).

Была 64×40: плотность 6.0, 11 пустырей 8×8, половина обстановки терялась в maybe(), пол магазина — лоскут
из чужих плиток. Уличная карта по решению автора выросла ×1.56 по каждой стороне
(docs/furnish_guide.md «Масштаб»): 64×40 → 100×62. Планировка не растянута, а перестроена по смыслу
(docs/furnish/fifteen.md §11), обстановка — поштучная: place / pbox / swall / ptable, автообстановка
выключена (CityMap(..., furnish=False)).

С севера на юг: полоса пустыни с задворками → магазин 22×10 и гараж 24×11 на северной стороне (между ними
служебный проход в 6 клеток) → площадка с колонками под навесами и двумя съездами с трассы → трасса
y=27..30 с выходами на карту мира с двух краёв → южнее баррикады из остовов и мешков, за ними лагерь банды
с костром, палатками и Шрамом.

Что требуют тесты (tests/test_story.py, test_dog.py, test_save.py, test_town.py): локация station, враги
gang×2 и boss (Шрам), терминал station, два сюжетных контейнера (сейф заправщика с requires «лом», тайник
Панка — владелец gang), выход с карты.

Запуск из папки game_project:  .venv/bin/python tools/build_station.py
"""
import json

from citykit import City, CityMap
from src import props as _props

city = City("station", "Заправка «Последний шанс»")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


# ------------------------------------------------------------ 1950-е: колонки, вывески, машины, будка
# Набор town50 — тот же, что у Бейкера и Примма: у заправки должна быть родная графика трассы, а не
# осколки трёх наборов, как в старой сборке.
PUMP_RED = P("st_pump_red", "pk:town50/town50_1_102", foot=[1, 1], sight=True)
PUMP_YEL = P("st_pump_yellow", "pk:town50/town50_1_103", foot=[1, 1], sight=True)
SIGN_GAS = P("st_sign_gas", "pk:town50/town50_1_115", foot=[1, 1], sight=True,
             light={"r": 120, "color": [255, 170, 80], "at": [0.5, 0.35], "flicker": 0.3})
COKE_BOX = P("st_coke_box", "pk:town50/town50_1_114", foot=[1, 1], sight=True)
PHONE = P("st_phone", "pk:town50/town50_1_100", foot=[1, 1], sight=True)
LAMP50 = P("st_lamp", "pk:town50/town50_1_120", foot=[1, 1],
           light={"r": 155, "color": [255, 210, 140], "at": [0.5, 0.08]})
BENCH50 = P("st_bench", "pk:town50/town50_1_130", foot=[1, 1], block=False)
MAILBOX = P("st_mailbox", "pk:town50/town50_1_118", foot=[1, 1])
HYDRANT = P("st_hydrant", "pk:town50/town50_1_109", foot=[1, 1], block=False)
CARS = [P(f"st_car{i}", f"pk:town50/town50_1_{n:03d}", foot=[2, 1], sight=True)
        for i, n in enumerate((29, 37, 45, 53, 41, 40))]
BILLBOARD = P("st_billboard", "pk:zcity/zcity_4_142", foot=[2, 1], sight=True)
ROAD_SIGN = P("st_road_sign", "pk:zcity/zcity_3_035", foot=[1, 1], keybg=True)      # указатель на Бейкер
SPIKES = P("st_spikes", "pk:gcave/p1/12,8,2,2", foot=[2, 1])                           # шипы банды

# ------------------------------------------------------------ магазин: набор store (прилавок, стеллажи, ларь)
SHELF_CEREAL = P("st_shelf_cereal", "pk:store/store_2_002", foot=[2, 1], sight=True, search="shelf", title="полка с товаром")
SHELF_CANS = P("st_shelf_cans", "pk:store/store_2_011", foot=[2, 1], sight=True, search="shelf", title="полка с товаром")
SHELF_MIX = P("st_shelf_mix", "pk:store/store_2_030", foot=[2, 1], sight=True, search="shelf", title="полка с товаром")
SHELF_DRINK = P("st_shelf_drink", "pk:store/store_2_032", foot=[2, 1], sight=True, search="shelf", title="полка с напитками")
COOLER = P("st_cooler", "pk:store/store_2_005", foot=[2, 1], sight=True, search="shelf", title="холодильник с напитками")
FREEZER = P("st_freezer", "pk:store/store_2_045", foot=[2, 1], sight=True, search="shelf", title="морозильный ларь")
COUNTER = P("st_counter", "pk:store/store_2_036", foot=[4, 1], sight=True)
BOARD_WALL = "board_wall"

# ------------------------------------------------------------ гараж: набор nbunk (верстак, доска, шкафчики)
WORKBENCH = P("st_workbench", "pk:nbunk/nbunk_2_014", foot=[2, 1], sight=True)
TOOLBOARD = P("st_toolboard", "pk:nbunk/nbunk_2_007", foot=[2, 1], sight=True)
LOCKERS = P("st_lockers", "pk:nbunk/nbunk_2_006", foot=[2, 1], sight=True)
G_CRATES = P("st_g_crates", "pk:nbunk/nbunk_2_033", foot=[2, 1])
BAY_CAR = P("st_bay_car", "pk:town50/town50_1_046", foot=[2, 1], sight=True)

# ------------------------------------------------------------ сюжетные контейнеры и мелочь
# «сейф» в наборе west — это буфет с посудой (west_2_105), на заправке он читался как сервант.
SAFE = "x_safe"                                         # настоящий железный сейф (pk:west/west_3_132)
STASH = P("st_stash", "pk:ucamp/ucamp_2_030", search="crate", title="тайник Панка")
FUEL_SIGN = "x_sign_fuel"
CAMPFIRE = "campfire"

W, H = 100, 62
ROAD = (27, 30)                        # трасса I-15: асфальт, обочины y=26 и y=31
m = CityMap(city, "station", "Заправка «Последний шанс»", W, H, start=(2, 29), seed=77, music="raiders",
            world_pos=(1760, 900), night=[150, 136, 140], furnish=False)
rnd = m.rnd
SAND = ["pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1"]
DIRT = ["pk:desnat/p1/4,4,1,1", "pk:desnat/p1/5,4,1,1", "pk:desnat/p1/6,4,1,1"]
DRY = ["pk:desnat/p1/10,4,1,1"]
m.floor_code("s", *SAND)               # пустошь
m.floor_code("t", *DIRT)               # утоптанная земля лагеря и подъездов
m.floor_code("q", *DRY)                # сухая плешь


# ------------------------------------------------------------ помощники ручной расстановки (как в build_town)
def pwhy(name, x, y, blocked=None, soft=None, reserved=None):
    """Почему предмет не встал — как why_not() в build_town.py."""
    foot = m.footprint(name, x, y)
    blocked = m.blocked if blocked is None else blocked
    soft = m.soft_obj if soft is None else soft
    reserved = m.reserved if reserved is None else reserved
    why = []
    if any(t in blocked for t in foot):
        why.append("блок: " + str([t for t in foot if t in blocked]))
    if any(t in soft for t in foot):
        why.append("мягкий предмет: " + str([t for t in foot if t in soft]))
    if any(t in reserved for t in foot):
        why.append("резерв")
    h = m.hides(name, x, y)
    if h:
        why.append(f"заслоняет {h[0]} ({h[1]}, {h[2]})")
    why.append("земля: " + "".join(m.ground[yy][xx] for xx, yy in foot))
    return f"«{name}» не встал в ({x}, {y}): " + "; ".join(why)


def _undo(snap):
    """Неудачная попытка не оставляет следов: предмет, его клетки и контейнер убираются."""
    n_props, n_conts, blocked, soft_obj, reserved = snap
    del m.props[n_props:], m.containers[n_conts:]
    m.blocked, m.soft_obj, m.reserved = blocked, soft_obj, reserved
    m._reach = None


def place(name, x, y, **kw):
    """Явная расстановка: предмет обязан встать и остаться там, куда его поставили (logic.md §2)."""
    snap = (len(m.props), len(m.containers), set(m.blocked), set(m.soft_obj), set(m.reserved))
    ok = m.put(name, x, y, **kw)
    if ok and m.props[-1][1:3] == [x, y]:
        return True
    why = pwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
    _undo(snap)
    raise AssertionError(why)


def pbox(name, x, y, title, loot, **kw):
    """Сюжетный ящик — как place(): не встал, так с причиной."""
    snap = (len(m.props), len(m.containers), set(m.blocked), set(m.soft_obj), set(m.reserved))
    try:
        m.box(name, x, y, title, loot, **kw)
    except AssertionError:
        why = pwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
        _undo(snap)
        raise AssertionError(why) from None
    if m.props[-1][1:3] == [x, y]:
        return True
    moved = m.props[-1][1:3]
    _undo(snap)
    raise AssertionError(pwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
                         + f"; встал в ({moved[0]}, {moved[1]})")


def oskin(name, x, y):
    """Мелочь на полу (проволока, газета): не блокирует, но и на стену не лезет."""
    if not m.put(name, x, y, check=False) or m.props[-1][1:3] != [x, y]:
        raise AssertionError(pwhy(name, x, y))


def swall(name, x, y0, dx=0, dy=-40):
    """Настенное — только на целой стене: ставится на ряд стены-пропа и поднимается так, чтобы висеть на
    фасаде (logic.md §2а). Где стены нет (проём ворот) — падает со счётом."""
    fw, fh = _props.info(name)["foot"]
    cells = [(x + i, y0 + j) for i in range(fw) for j in range(fh)]
    assert all(c in m.blocked for c in cells), f"«{name}» в ({x}, {y0}): там нет целой стены"
    m.props.append([name, x, y0 + 1, dx, dy])
    m.soft_obj.add((x, y0 + 1))      # на клетке под настенным ничего не ставим
    m._reach = None


def ptable(name, x, y, dx=0, dy=-34):
    """Мелочь на столешнице: на клетке мебели, поднята на её высоту и в глубину — не у переднего края
    (замечание автора 24.10), рисуется сразу после стола (6-й элемент — порядок отрисовки)."""
    assert (x, y) in m.blocked, f"«{name}» в ({x}, {y}): под ним нет стола"
    m.props.append([name, x, y, dx, dy, 1 - dy])


# ================================================================ земля
# Пустошь вокруг, площадка заправки, западная парковка, подъезды; никаких случайных пятен посреди
# площадки (замечание автора 4): где земля истоптана, она истоптана по делу — у колонок и в лагере.
m.paint("s", 0, 0, W - 1, H - 1)
m.paint("c", 8, 15, 62, 24)                     # бетон заправки: от фасадов до съездов
m.paint("g", 1, 15, 7, 24)                      # западная парковка — гравий
m.paint("g", 0, 25, W - 1, 25)                  # полоса перед трассой
m.paint("c", 12, 25, 21, 26)                    # съезд против магазина
m.paint("c", 40, 25, 49, 26)                    # съезд против ворот гаража
m.paint("g", 0, 26, W - 1, 26)                  # северная обочина
m.paint("a", 0, ROAD[0], W - 1, ROAD[1])        # трасса
for x in range(0, W, 6):                        # прерывистая разметка по оси
    m.ground[28][x] = m.ground[28][x + 1] = "h"
m.paint("g", 0, 31, W - 1, 31)                  # южная обочина
m.paint("t", 46, 31, 50, 36)                    # накатанный съезд с обочины к воротам лагеря
m.paint_ragged("t", 14, 36, 86, 58, depth=2)    # лагерь банды — утоптанная земля с рваным краем
m.exits = [(0, y) for y in range(ROAD[0], ROAD[1] + 1)] + [(W - 1, y) for y in range(ROAD[0], ROAD[1] + 1)]
m.reserve(0, ROAD[0], W - 1, ROAD[1])           # по трассе ничего не ставим


# ================================================================ здания
# Магазин (север, запад) и гараж (север, восток) — лицом к площадке и трассе, дверь и ворота против
# съездов; между ними 6 клеток служебного прохода, за ними — задворки.
SHOP_IN = m.building(8, 4, 22, 10, "brick", south=(10,), sign="ЗАПРАВКА", worn=False)
GARAGE_IN = m.building(35, 3, 24, 11, "metal", south=(6, 8), sign="ГАРАЖ", worn=False)
assert SHOP_IN == (9, 5, 28, 12) and GARAGE_IN == (36, 4, 57, 12)
# Бетон площадки подходит к самим фасадам: полоса песка в клетку между стеной и заливкой читалась
# как «площадка не достроена» (замечание «участок закрыт целиком»).
m.paint("c", 8, 14, 62, 24)
m.paint("g", 1, 14, 7, 24)


# ================================================================ площадка с колонками
# Два островка по две колонки под навесами: навес не блокирует — под ним ходят и ездят, свет — от
# потолочных ламп под навесом (радиус и мерцание, а не плоская плашка).
# Навеса над колонками нет: довоенный навес сгнил, и заправка стоит открыто — как сельская 1950-х.
# Прежний `st_awning` (палатка-рынок с прилавком) читался как торговый лоток, а не как навес (logic.md §2:
# «спрайт — по месту»). Свет над островками дают столбы-фонари между колонками.
for px, pump in ((16, PUMP_RED), (20, PUMP_YEL), (46, PUMP_RED), (50, PUMP_YEL)):
    place(pump, px, 19)
for lx in (18, 48):
    place(LAMP50, lx, 17)
oskin("x_vd_oil1", 17, 21)                      # лужа топлива у колонки
oskin("x_vd_oil0", 51, 21)
place("bucket", 21, 20)                         # ведро с песком: колонки тушили песком, не пеной
place(FUEL_SIGN, 32, 16)                        # «НЕТ БЕНЗИНА» — посередине площадки, читается с трассы
place("r_dumpster", 11, 16)                     # баки у магазина
place("crate", 30, 22)                          # ящик на площадке (обыскивается)
place("barrel_wood", 33, 23)                    # бочка под дождь

# ---------------------------------------------------------------- площадка: от колонок до фасадов
# Заправка работала до весны, поэтому между колонками и магазином осталось то, что не успели убрать:
# тележка у двери, ящик кока-колы, не разгруженный товар, урны, пустые канистры, шины на продажу и
# брошенный пикап клиента. Всё — по краям заливки, середина проезда между колонками свободна.
place("st_coke_box", 15, 15)                    # ящик кока-колы у витрины, сбоку от двери — на шаг от фасада:
                                                # высокий спрайт вплотную под стеной залезает на неё
place("st_bench", 13, 14)                       # скамья у витрины, где ждали машину
place("pr_trash_a", 26, 14)
place("w_crate_sacks", 28, 15)                  # товар не разгрузили
place("crate_b", 28, 16)
place("canister", 8, 22)
place("pile_tires", 9, 23)                      # шины «на продажу» у западного края
place("pile_tires", 59, 22)
place("w_oil_drum", 60, 15)                     # бочка масла у угла гаража
place("barrel_lying_a", 61, 16)
place("bucket", 47, 20)                         # второе ведро с песком — у второй пары колонок
place("pr_trash_a", 44, 22)
place("r_pickup", 38, 21)                       # брошенный пикап клиента посреди заливки
place("pile_cans", 23, 23)
place("pile_bottles", 27, 22)
place("junk_small_2", 18, 21)
place("junk_small_3", 48, 22)
place("x_vd_caps", 30, 20)                      # гильзы на бетоне: тут стреляли до банды
place(CARS[3], 13, 20)                          # машина клиента у колонки: заправиться уже нечем
place(CARS[4], 52, 19)                          # и вторая — у восточной пары
place("canister", 17, 22)                       # канистры: бензин из колонок слили
place("x_board", 12, 24)                        # щит с ценами у съезда, уже без цен
place("pile_tires", 57, 15)
place("junk_small_2", 45, 15)
place("canister", 10, 20)
place("crate_small", 31, 16)

# ================================================================ трасса и обочины
# Фонари 1950-х по обеим обочинам (у них свой свет), знак на въезде, остов на обочине, будка, почта,
# гидрант — трасса жила до войны и читается до сих пор.
for x in (10, 30, 60, 82):
    place(LAMP50, x, 26)
for x in (20, 36, 64, 88):
    place(LAMP50, x, 31)
place(SIGN_GAS, 9, 25)                          # «GAS» на столбе у съезда
place(ROAD_SIGN, 90, 31)                        # указатель «Бейкер →» на южной обочине
place("r_car_wreck", 58, 32)                    # остов на обочине
place(HYDRANT, 22, 25)
place(MAILBOX, 55, 25)
place(PHONE, 2, 25)                             # телефонная будка на западном краю
place(BENCH50, 12, 25)
# Столбы связи вдоль северной обочины и знаки, которые видит всякий, кто едет в Бейкер: трасса без них
# читалась как пустая полоса асфальта. Мусор на обочинах — кучками, не в линию.
place("r_pole_wire", 44, 26)                    # единственный завалившийся столб — след войны, не забор
place("sign_50", 70, 26)                        # ограничение 50 перед заправкой
place("sign_43", 34, 31)                        # «поворот» на южной обочине
place("r_trash", 16, 32)
place("r_trash", 72, 32)
place("pile_cans", 30, 32)
place("junk_small_3", 48, 32)
place("r_bones", 26, 32)                        # сбитое зверем зверьё — обочина
place("pile_tires", 40, 32)
place("r_bones", 84, 32)

# ================================================================ западный двор: парковка
# Три машины клиентов у магазина, канистры и бак в углу, доска объявлений на столбе у дороги.
place(CARS[0], 2, 18)
place(CARS[1], 5, 21)
place(CARS[2], 2, 21)
place("canister", 7, 18)
place("canister", 7, 19)
place("r_dumpster", 2, 23)
place("x_board", 4, 16)
place("barrel_wood", 3, 15)
place("pile_tires", 6, 23)
place("pr_trash_a", 1, 17)
place("junk_small_2", 5, 19)
place("pile_cans", 1, 15)
place("canister", 1, 22)

# ================================================================ восточный двор: свалка заправки
# Штабель шин, три остова в ряд, сортир-кабинка, бочки и канистры, билборд у дороги — у заправки всегда
# свалка за углом, но не ровной сеткой: кучами. Сарай-шиномонтаж и куча хлама — чтобы двор был двором,
# а не песком с тремя машинами.
place("pile_tires", 66, 16)
place("pile_tires", 68, 19)
place("r_car_wreck", 72, 20)
place("r_pickup", 80, 22)
place("r_car_a", 88, 18)
place("x_outhouse", 94, 16)
place("r_dumpster", 76, 15)
place("pile_junk", 84, 16)
place("pile_scrap", 92, 21)
place("barrel_wood", 96, 19)
place("bucket", 95, 20)
place(BILLBOARD, 64, 25)
place("r_shack", 86, 20)                        # сарай, где держали шины
place("r_junk_mound", 70, 22)                   # куча хлама под стеной сарая
place("jt_tire_stack", 64, 17)
place("ar_tires", 67, 22)
place("pile_tires", 78, 17)
place("ar_tires", 91, 16)
place("pile_tires", 97, 22)
place("r_barrels", 98, 14)
place("crate_broken", 74, 14)
place("r_bones", 90, 22)
place("canister", 82, 15)
place("junk_small_2", 93, 19)
place("jt_tire_stack", 90, 15)
place("crate", 88, 22)

# ================================================================ задворки за зданиями
# Товар не разгрузили: поддоны, ящики, бочки, сухие деревья вдоль северного края.
place("crate", 12, 1)
place("crate_b", 13, 1)
place("crate", 14, 1)
place("barrel_wood", 16, 1)
place("barrel_wood", 17, 1)
place("pile_scrap", 25, 1)
place("pile_junk", 40, 1)
place("metal_sheets", 43, 1)
place("crate", 47, 1)
place("barrel_wood", 50, 1)
place("pile_tires", 54, 1)
place("crate", 31, 2)                          # в служебном проходе между зданиями
place("barrel_wood", 32, 1)
for x, y in ((4, 2), (22, 1), (66, 1), (78, 1), (91, 1), (98, 2)):
    place("r_dtree_a", x, y)
place("r_dry_bush", 7, 2)
place("r_dry_bush", 33, 2)
place("r_rocks", 60, 1)
place("r_bones", 70, 1)
place("crate_open", 24, 1)
place("crate_small", 26, 2)
place("w_sacks", 34, 1)
place("by_pallet", 19, 1)
place("pr_trash_a", 45, 1)
place("crate_broken", 52, 1)

# ================================================================ магазин внутри
# Придорожный магазин: у северной стены — стеллажи, холодильник с напитками, ларь-морозилка; островной ряд
# стеллажей через проход; прилавок с кассой южнее, лицом к двери; за прилавком — подсобка с терминалом и
# сейфом; у двери огнетушитель. Дверь `18..19` на южном фасаде, от неё свободный проход на север.
place(SHELF_CEREAL, 10, 5)
place(SHELF_CANS, 12, 5)
place(SHELF_MIX, 14, 5)
place(SHELF_DRINK, 16, 5)
swall(BOARD_WALL, 19, 4, dy=-44)                # доска с ценами над проходом от двери
place(COOLER, 22, 5)
place(FREEZER, 24, 5)
place(SHELF_CANS, 11, 7)                        # островной ряд стеллажей
place(SHELF_CEREAL, 13, 7)
place(SHELF_DRINK, 15, 7)
place(SHELF_CEREAL, 10, 11)                     # ряд у южной стены (ряд выше фасада — не под ним)
place(SHELF_MIX, 12, 11)
place(SHELF_CANS, 14, 11)
place(COUNTER, 22, 9)                           # прилавок 4 клетки, лицом к двери
ptable("x_register", 22, 9, dx=14, dy=-48)      # касса — на западной половине прилавка, в глубине, не свисает с края
place("x_fireext", 9, 11)                       # огнетушитель у стены, в конце ряда, а не посреди зала
place("crate", 28, 8)                           # ящики в подсобке
place("crate_b", 27, 9)
place("canister", 28, 11)
oskin("w_newspaper", 17, 10)                    # газета на полу у прилавка
m.terminal(24, 6, "station")                    # терминал заправщика — в подсобке за прилавком
pbox(SAFE, 26, 7, "сейф заправщика", {"крышки": 70, "бронежилет из дорожных знаков": 1, "тоник": 1},
     owner="gang", requires={"item": "лом", "msg": "Сейф заправщика. Замок не открыть — разве что вскрыть ломом."})
m.ceiling(18, 9, r=170, color=(255, 195, 120), flick=0.02)   # лампы под потолком магазина
m.ceiling(24, 7, r=150, color=(255, 195, 120), flick=0.02)

# ================================================================ гараж внутри
# Мастерская: бокс с машиной на домкратах и масляными пятнами, верстак с инструментом у северной стены,
# стеллаж с запчастями у восточной, шины столбиками и ящики по углам; тайник Панка — за шинами в углу.
place(WORKBENCH, 36, 5)                         # верстак 2 клетки
ptable("w_lantern", 36, 5, dx=-6, dy=-40)       # фонарь на верстаке — свет над работой
place("toolbox_red", 36, 6)                      # ящик с инструментом под верстаком
swall(TOOLBOARD, 38, 3, dy=-44)                 # доска с инструментом на целой северной стене
place(BAY_CAR, 45, 8)                           # машина в боксе
oskin("x_vd_oil0", 44, 9)
oskin("x_vd_oil1", 46, 10)
place("toolbox_red", 47, 9)                     # ящик у машины
place("rack_parts", 48, 5)                      # стеллаж с запчастями у северной стены, у бокса
place(LOCKERS, 52, 4)                           # шкафчики в северо-восточном углу
place("ar_tires", 55, 4)                        # шины у стены — за ними тайник (не обыскиваются: иначе
#                                                E у тайника открывал шины, а не тайник)
place("barrel_wood", 57, 8)                     # бочка у восточной стены
place("w_oil_drum", 57, 10)                     # бочка масла
place("pile_tires", 39, 11)                     # шины столбиком у южной стены
place(G_CRATES, 52, 11)                         # ящики с крепежом
place("canister", 49, 11)
place("bucket", 36, 7)                          # ведро под верстаком
place("x_fireext", 37, 7)                       # огнетушитель в боксе, у верстака (не в проходе к ящику)
place("crate", 37, 10)                          # ящик у южной стены
place("canister", 54, 8)
place("stool_1", 52, 7)                          # табурет у стеллажа с запчастями
oskin("x_wire_coil", 50, 10)                    # моток проволоки на полу
pbox(STASH, 56, 5, "тайник Панка", {"доля Панка": 1, "крышки": 15}, owner="gang")
m.ceiling(44, 7, r=160, color=(255, 190, 110), flick=0.03)   # лампы под потолком гаража
m.ceiling(52, 6, r=150, color=(255, 190, 110), flick=0.03)

# ================================================================ баррикады и ворота лагеря
# Банда перекрыла подъезд к себе остовами, мешками и шипами, оставив одни ворота против съезда — с трассы
# видно, что просто так не заедешь (logic.md §6: вход читается).
for name, x, y in (("r_car_wreck", 30, 34), ("r_pickup", 36, 35), ("r_car_a", 54, 34), ("r_car_red", 60, 35),
                   ("r_taxi", 66, 34)):
    place(name, x, y)
for x, y in ((34, 34), (40, 35), (44, 34), (52, 34), (58, 35), (64, 34)):
    place("x_sandbags", x, y)
for x, y in ((38, 34), (42, 35), (56, 35), (62, 34)):
    place(SPIKES, x, y)
place("x_board", 52, 37)                        # доска банды у ворот («проверяем всех»)
place("barrel_wood", 51, 35)
place("ar_skull_pole", 44, 37)                  # трофейный столб у ворот: банда метит свою землю
place("ar_skull_pole", 53, 38)
place("ammo_box", 49, 37)
place("jt_tire_stack", 43, 36)
place("r_barrels", 55, 37)

# ================================================================ лагерь банды
# Костёр в середине, вокруг — брёвна, котелок и стол с добычей; пять палаток по кругу, огневые бочки,
# шины и тряпки у палаток: тут живут, а не просто стоят. Между палатками — кухня с ручным насосом,
# ящики с крупой и бочки с водой; на востоке — загон, где разбирают машину; у ворот — пост с ящиком
# патронов. Пустая утоптанная земля читалась как «сцена без обстановки».
place(CAMPFIRE, 50, 46)                         # костёр (свой свет и огонь)
place("r_logs", 49, 45)
place("r_logs", 51, 45)
place("r_logs", 50, 48)
place("x_cauldron", 52, 47)                     # котелок над огнём
place("w_table_plain", 46, 44)                  # стол с добычей у костра
ptable("junk_small_1", 46, 44, dx=-8, dy=-38)   # трофеи на столе
ptable("w_newspaper", 47, 44, dx=6, dy=-34)
ptable("canteen", 46, 44, dx=10, dy=-36)        # фляга хозяина стола
ptable("plate", 47, 44, dx=-10, dy=-38)         # тарелка с объедками
place("stool_1", 47, 45)
place("stool_1", 45, 45)
place("pile_bottles", 54, 45)                   # бутылки с вечера
place("pile_rags", 47, 50)
for name, x, y in (("r_tent_big", 36, 42), ("r_tent_yellow", 63, 41), ("r_tent_green", 38, 53),
                   ("r_tent_orange", 62, 53), ("r_tent_beige", 49, 57)):
    place(name, x, y)
for x, y in ((42, 39), (57, 44), (41, 51), (60, 57), (46, 55)):
    place("x_fire_barrel", x, y)
for name, x, y in (("pile_tires", 32, 44), ("pile_tires", 70, 47), ("pile_junk", 30, 50),
                   ("pile_junk", 72, 42), ("pile_scrap", 66, 52), ("pile_bottles", 44, 57),
                   ("barrel_wood", 43, 41), ("barrel_wood", 58, 50), ("crate", 56, 52)):
    place(name, x, y)
place("r_car_wreck", 74, 48)                    # загон: разобранная машина на востоке лагеря
place("metal_sheets", 78, 50)
place("r_pickup", 80, 46)
place("r_bones", 44, 48)
pbox("crate", 40, 52, "ящик банды", {"крышки": 35, "патроны": 6, "стимулятор": 1, "виски": 1}, owner="gang")
# кухня лагеря: ручной насос, крупа в ящиках, бочки с водой, стол под навесом
place("w_pump", 55, 50)
place("w_crate_sacks", 44, 42)
place("w_crate_sacks", 46, 42)
place("r_barrels", 39, 47)
place("r_barrels", 62, 44)
place("canteen", 53, 43)
place("bucket", 54, 49)
# спят в поле: ещё две малые палатки и тряпьё вместо постели
place("tent_low", 33, 56)
place("r_tent_low", 70, 54)
place("ar_tarp", 34, 46)
place("pile_cloth_scrap", 68, 44)
# загон: разбирают машину — инструмент, канистры, масло, проволока
place("toolbox_red", 72, 47)
place("x_wire_coil", 75, 50)
place("w_oil_drum", 78, 48)
place("canister", 73, 53)
place("pile_tires", 76, 52)
place("crate_b", 68, 49)
# пост у ворот и мусор по лагерю
place("stool_1", 48, 39)
place("ammo_box", 47, 39)
place("x_fire_barrel", 45, 40)
place("r_junk_mound", 28, 44)
place("w_junk_pile", 76, 44)
place("pr_trash_a", 52, 42)
place("pile_cans", 59, 39)
place("r_bones", 40, 44)
place("pile_bottles", 57, 53)
place("w_table_plain", 42, 46)                  # второй стол — где едят
place("stool_2", 41, 46)
place("stool_2", 44, 46)
place("crate", 36, 48)
place("crate_b", 37, 48)
place("barrel_wood", 31, 53)
place("r_logs", 56, 46)
place("junk_small_3", 46, 52)
place("ar_tarp", 35, 51)
place("pile_bottles", 41, 49)
place("tent_small", 66, 38)
place("r_bones", 60, 52)
place("pile_junk", 33, 40)
place("barrel_wood", 64, 47)
place("jt_tire_stack", 79, 20)
place("r_trash", 95, 22)
place("pile_cans", 74, 19)
place("barrel_wood", 90, 20)
place("junk_small_2", 46, 25)

# ================================================================ пустыня по краям
# Сухие деревья, кусты, камни и кости — кучками у дорог, заборов и лагеря, а не ровной сеткой
# (замечание автора 4). Пустырей не оставляем: у каждого края что-то есть.
#
# ВАЖНО: только на улице. Прежний `m.scatter` по прямоугольнику 1,1..98,24 сыпал камни и кости внутрь
# магазина и гаража (пол там — тот же код «c», что и заливка) — в двух снимках подряд в магазине лежали
# камни, а в гараже рос куст. Рассев идёт по коду земли, как scatter_out в build_town.py (logic.md §2а).
OUTSIDE = ("s", "t", "q", "g")


def scatter_out(names, n, x0=1, y0=1, x1=W - 2, y1=H - 2, tries=80):
    """Рассев по коду земли: только улица, без полов зданий (logic.md §2а)."""
    placed = 0
    for _ in range(n * tries):
        if placed >= n:
            break
        x, y = rnd.randint(x0, x1), rnd.randint(y0, y1)
        if m.ground[y][x] not in OUTSIDE:
            continue
        try:                                  # put отказывает — просто пробуем другое место
            if m.put(rnd.choice(names), x, y):
                placed += 1
        except AssertionError:
            continue
    return placed


for x, y in ((2, 8), (3, 13), (1, 20), (5, 6), (62, 6), (70, 8), (80, 6), (90, 8), (97, 12)):
    place("r_dtree_a", x, y)
# (55, 8) вынесен наружу: после перепланировки эта клетка — пол гаража, и куст рос из пола.
for x, y in ((4, 10), (6, 12), (63, 12), (75, 10), (88, 12), (96, 6), (30, 5), (61, 9)):
    place("r_dry_bush", x, y)
# Куртины по краям карты — там, где никто не ходит по делу: у северного среза, за зданиями, вдоль
# западного и восточного краёв, южнее лагеря. Плотность доведена до 9 на 100 проходимых клеток
# (docs/furnish/fifteen.md §11.5), но не свалкой: 3–5 предметов на пятно.
for rect, cnt_ in (((1, 1, 99, 3), 10), ((1, 3, 7, 13), 6), ((30, 1, 34, 13), 3),
                   ((59, 1, 99, 13), 14), ((1, 33, 13, 61), 10), ((87, 33, 99, 61), 9),
                   ((24, 50, 34, 58), 5), ((2, 59, 97, 61), 8)):
    scatter_out(["r_dry_bush", "r_rocks", "r_bones"], cnt_, *rect)
scatter_out(["r_dtree_a", "r_dtree_b", "r_dry_bush"], 8)
scatter_out(["pile_junk", "r_trash", "r_bones"], 10)      # мусор кучками, не сеткой
# Одинокие пустыри обживаем сценками (как в build_town.py): стоянка у костра, разбитая машина, билборд,
# лачуга — маленькое цельное место вместо песка с кустом посередине.
# Здания в резерв: dress_empty проверяет землю по участку 8×8, и сценка, зацепившая угол дома, ставила
# куст на бетонный пол гаража (в снимке он рос из пола).
m.reserve(8, 2, 29, 14)
m.reserve(35, 2, 58, 14)
print("обжито:", m.dress_empty([
    [("r_tent_beige", 0, 0), ("campfire", 3, 2), ("r_logs", 2, 3), ("barrel_wood", 0, 3), ("pile_rags", 4, 0)],
    [("r_car_wreck", 0, 0), ("pile_tires", 3, 2), ("r_trash", 0, 3), ("barrel_wood", 4, 1)],
    [("r_pickup", 0, 0), ("r_barrels", 3, 0), ("pile_scrap", 2, 3), ("crate_broken", 4, 2)],
    [("r_camper", 0, 0), ("r_awning", 0, 2), ("crate", 3, 2), ("bucket", 5, 1)],
    [("r_billboard", 0, 0), ("r_dtree_a", 2, 1), ("r_bones", 3, 2), ("r_rocks", 4, 2)],
    [("r_shack", 0, 0), ("pile_junk", 5, 1), ("barrel_wood", 0, 3), ("x_fire_barrel", 3, 3)],
], ground=("s", "t", "q", "g"), block=8, margin=2, chance=0.9, max_uses=2))


# ================================================================ кто где
# Трое: один держит кассу и сейф в магазине (за прилавком), второй — ворота лагеря, Шрам — у костра лицом
# к воротам. Подборы — по местам: лом в гараже, химикаты у огневых бочек, ткань в палатке, патроны на
# баррикаде.
m.enemies += [["gang", 24, 8], ["gang", 46, 38], ["boss", 52, 49]]
m.pickups += [["лом", 1, 50, 8], ["химикаты", 1, 58, 45], ["ткань", 1, 64, 42], ["патроны", 3, 37, 33]]
for _, x, y in m.enemies:
    m.reserve(x, y, x, y)

# ---------------------------------------------------------------- пустырей не остаётся
# dress_empty обходит участки, выровненные по 8 клеток, а `city_tour.py` считает их окном 8×8 с шагом 4 —
# часть окон попадает между сценками и снова считается пустырём. Здесь добиваем ровно те окна, которые
# видит tour: по одному кусту/камню/кости в каждое, только на улице, и только если окно правда пустое.
def empty_plots(block=8, step=4):
    walk = {(x, y) for y in range(H) for x in range(W)
            if m.ground[y][x] not in ("x", "_") and (x, y) not in m.blocked}
    things = set()
    for e in m.props:
        things.update(m.footprint(e[0], e[1], e[2]))
        things.update((e[1] + dx, e[2] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    things.update((e[1], e[2]) for e in m.enemies)
    out = []
    for by in range(0, H - block + 1, step):
        for bx in range(0, W - block + 1, step):
            win = {(bx + i, by + j) for i in range(block) for j in range(block)}
            if len(win & walk) >= 56 and not win & things:
                out.append((bx, by))
    return out


left = empty_plots()
for _ in range(6):
    if not left:
        break
    for bx, by in left:
        cells = [(bx + i, by + j) for i in range(8) for j in range(8)
                 if m.ground[by + j][bx + i] in OUTSIDE and (bx + i, by + j) not in m.blocked
                 and (bx + i, by + j) not in m.reserved]
        rnd.shuffle(cells)
        for cx, cy in cells:
            try:
                if m.put(rnd.choice(["r_dry_bush", "r_rocks", "r_bones"]), cx, cy):
                    break
            except AssertionError:
                continue
    left = empty_plots()
print("пустырей:", len(left))


city.save(gap_exempt=("boss",))
L = json.load(open("data/locations.json", encoding="utf-8"))
for k in ("containers", "terminals", "entry", "npcs"):
    L["station"].pop(k, None)
L["station"].update({"name": "Заправка «Последний шанс»", "known": False})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
