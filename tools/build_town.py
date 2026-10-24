"""
Генератор карты стартового города Пятнадцатая (data/maps/town.json), 150×100.

Пересобран вручную 23.10.2026 (docs/furnish/logic.md — эталон ручной расстановки): здания по размеру
своего назначения, между ними проулки, дворы и площади — по городу интересно гулять, а не протискиваться.

Районы (подробно — docs/story.md, «Стартовый город»):
  запад            — въезд с трассы, остановка, КПП шерифа; отсюда начинается игра;
  северо-запад     — жилой квартал: три дома с дворами, дом деда у трассы, колодец и прачечная;
  север            — склад «Пасифик Фрейт» с грузовым двором, салун «Последний глоток» с крыльцом;
  центр-север      — рынок: два ряда лавок, палатка «Детей Единства», доска объявлений;
  северо-восток    — водокачка за сеткой: баки, насосная, контора; светящиеся мутанты, Блонди;
  юг у трассы      — дом Черепана, участок шерифа с камерами, клиника, ратуша;
  юго-запад        — руины склада со спуском в ливнёвку (крысы), кладбище со сторожкой;
  юг-центр         — сквер (панцирный жук) и скала с дверью Убежища 57;
  юго-восток       — свалка: лагерь рейдеров, пёс на цепи, лачуга Панка, контора, сторожка.
Через город — трасса I-15 (запад — въезд, восток — старая школа) и улица на юг.

Запуск из папки game_project:  .venv/bin/python tools/build_town.py
"""
from mapkit import (MapKit, BARRELS, CRATES, GRASS, STONES, FLOOR_BITS, JUNK_PILES, RUBBLE, POLES, SIGNS, BENCHES)

W, H = 150, 100
ROAD = 48                              # трасса: асфальт y 48..51, тротуары 47 и 52
SOUTH = 84                             # улица на юг: асфальт x 84..87, тротуары 83 и 88
m = MapKit(W, H, start=(3, ROAD + 1), seed=7)
rnd = m.rnd
m.rugs_under = True                    # стулья и лампы встают на ковёр (mapkit.put)
put, terminal, scatter = m.put, m.terminal, m.scatter
m.exits = [(0, y) for y in range(ROAD, ROAD + 4)] + [(x, H - 1) for x in range(SOUTH, SOUTH + 4)]


def why_not(name, x, y):
    foot = m.footprint(name, x, y)
    why = []
    if any(t in m.blocked for t in foot):
        why.append("блок: " + str([t for t in foot if t in m.blocked]))
    if any(t in m.soft_obj for t in foot):
        why.append("мягкий предмет: " + str([t for t in foot if t in m.soft_obj]))
    if any(t in m.reserved for t in foot):
        why.append("резерв")
    if m.hides(name, x, y):
        b = m.hides(name, x, y)
        why.append(f"заслоняет {b[0]} ({b[1]}, {b[2]})")
    why.append("земля: " + "".join(m.ground[yy][xx] for xx, yy in foot))
    return f"«{name}» не встал в ({x}, {y}): " + "; ".join(why)


def place(name, x, y, **kw):
    """Явная расстановка: предмет обязан встать — молча потерянная мебель и была дефектом старой карты."""
    if put(name, x, y, **kw):
        return True
    raise AssertionError(why_not(name, x, y))


def box(name, x, y, *a, **kw):
    """Ящик с добычей — как place(): не встал — объяснить почему."""
    try:
        return m.box(name, x, y, *a, **kw)
    except AssertionError:
        raise AssertionError(why_not(name, x, y)) from None


def wall_art(name, x, y0, dy=None, dx=0):
    """Настенное (картина, плакат, часы) — на целой северной стене здания (её ряд y0): ставится на первый
    ряд пола и поднимается на стену, чтобы рисоваться поверх неё; низ картинки — на 26 px выше пола, так что
    и высокий портрет, и низкий плакат висят на одной высоте. Где стены нет (проём) — нельзя."""
    assert (x, y0) in m.blocked, f"«{name}» в ({x}, {y0}): там нет стены"
    m.props.append([name, x, y0 + 1, dx, -26 if dy is None else dy])


def on_table(name, x, y, dx=0, dy=-32):
    """Мелочь на столешнице (лампа, кружка, радио): на клетке стола, приподнята на его высоту."""
    assert (x, y) in m.blocked, f"«{name}» в ({x}, {y}): под ним нет стола"
    m.props.append([name, x, y, dx, dy, 1 - dy])     # рисуется сразу после стола, а не за ним


class Shift:
    """Район, перенесённый со старой карты целиком: те же вызовы, координаты сдвинуты на (dx, dy)."""

    def __init__(self, dx, dy):
        self.dx, self.dy = dx, dy

    def xy(self, x, y):
        return x + self.dx, y + self.dy

    def put(self, name, x, y, **kw):
        return put(name, *self.xy(x, y), **kw)

    def place(self, name, x, y, **kw):
        return place(name, *self.xy(x, y), **kw)

    def box(self, name, x, y, *a, **kw):
        return box(name, *self.xy(x, y), *a, **kw)

    def terminal(self, x, y, tid):
        return terminal(*self.xy(x, y), tid)

    def building(self, x0, y0, *a, **kw):
        return m.building(*self.xy(x0, y0), *a, **kw)

    def rect(self, x0, y0, x1, y1):
        return (*self.xy(x0, y0), *self.xy(x1, y1))

    def paint(self, code, *r):
        m.paint(code, *self.rect(*r))

    def scatter(self, names, x0, y0, x1, y1, n):
        return scatter(names, *self.rect(x0, y0, x1, y1), n)

    def grow(self, x0, y0, x1, y1, n, names=None):
        return m.grow(*self.rect(x0, y0, x1, y1), n, names) if names else m.grow(*self.rect(x0, y0, x1, y1), n)

    def hwall(self, names, x0, x1, y, gaps=()):
        m.hwall(names, x0 + self.dx, x1 + self.dx, y + self.dy, gaps=tuple(g + self.dx for g in gaps))

    def side_wall(self, style, side, x, y0, y1, gaps=()):
        m.side_wall(style, side, x + self.dx, y0 + self.dy, y1 + self.dy, gaps=tuple(g + self.dy for g in gaps))

    def portal(self, tiles, to, at, label, **kw):
        m.portal([self.xy(*t) for t in tiles], to, at, label, **kw)


# ------------------------------------------------------------ кто где (резервируется до расстановки)
WATER = Shift(54, 12)        # водокачка — старый северо-восток целиком
VAULT = Shift(49, 24)        # сквер и Убежище 57
JUNK = Shift(54, 17)         # свалка
m.pickups += [
    ["лом", 1, 12, 34],                 # в доме деда
    ["чей-то глаз", 1, 10, 32],         # в доме деда
    ["ткань", 1, 30, 39],               # у прачечной
    ["химикаты", 1, *WATER.xy(72, 13)],
    ["химикаты", 1, *JUNK.xy(76, 58)],
    ["лопата", 1, 35, 90],              # у сторожки кладбища
    ["ткань", 1, 62, 19],               # на грузовом дворе склада
]
m.npcs += [
    ["gena", 88, 23],                   # у прилавка своей лавки на рынке
    ["silas", 104, 25],                 # проповедник «Детей Единства» у палатки
    ["blondie", *WATER.xy(88, 4)],
    ["mo", 55, 28],                     # за стойкой салуна
    ["lenny", 64, 33],                  # за столиком салуна
    ["marta", 10, 10],                  # во дворе своего дома
    ["turtle", 11, 60],                 # Черепан — в доме без крыши
    ["sheriff", 28, 57],                # участок шерифа: за своим столом, стойка за спиной
    ["doc", 48, 57],                    # клиника: за столом приёма, аптека за спиной
    ["ada", 68, 57],                    # ратуша: во главе совета, перед своим креслом
    ["dale", *VAULT.xy(52, 54)],        # помощник шерифа — часовой у двери убежища
    ["dex", 20, 43],                    # наёмник Дэкс — охрана застрявшего фургона Розы у трассы
    ["loner", *JUNK.xy(69, 60)],
    ["dog", *JUNK.xy(90, 46)],          # пёс на цепи у ящика с патронами в лагере рейдеров
]
m.enemies += [
    ["rad_mutant", *WATER.xy(68, 16)], ["rad_mutant", *WATER.xy(77, 19)],
    ["rat", 7, 85], ["rat", 18, 86], ["rat", 14, 76],                    # руины над ливнёвкой
    ["beetle", *VAULT.xy(56, 41)],                                       # высохший сквер
    ["raider", *JUNK.xy(85, 45)], ["raider", *JUNK.xy(87, 54)],          # лагерь на свалке
]
for _, x, y in m.enemies + m.npcs:
    m.reserve(x, y, x, y)
for *_, x, y in m.pickups:
    m.reserve(x, y, x, y)


# ------------------------------------------------------------ земля: песок, пятна глины и щебня
m.floors = {"s": ["pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1"],
            "t": ["pk:desnat/p1/4,4,1,1", "pk:desnat/p1/5,4,1,1", "pk:desnat/p1/6,4,1,1"],        # утоптанная глина
            "q": ["pk:desnat/p1/10,4,1,1"]}                                                         # щебень
m.paint("s", 0, 0, W - 1, H - 1)
m.patchwork("s", ["t"], 80, 3, 6, seed=2)
m.patchwork("s", ["q"], 40, 2, 3, seed=1)


# ------------------------------------------------------------ дороги и тропы
m.paint("a", 0, ROAD, W - 1, ROAD + 3)              # трасса
for x in range(0, W - 1, 4):
    m.ground[ROAD + 1][x] = m.ground[ROAD + 1][x + 1] = "h"     # прерывистая разметка
m.paint("g", 0, ROAD - 1, W - 1, ROAD - 1)          # тротуары
m.paint("g", 0, ROAD + 4, W - 1, ROAD + 4)
m.paint("a", SOUTH, ROAD + 5, SOUTH + 3, H - 1)     # улица на юг
for y in range(ROAD + 7, H - 1, 4):
    m.ground[y][SOUTH + 1] = m.ground[y + 1][SOUTH + 1] = "v"
m.paint("g", SOUTH - 1, ROAD + 5, SOUTH - 1, H - 1)
m.paint("g", SOUTH + 4, ROAD + 5, SOUTH + 4, H - 1)
m.paint("t", 2, 15, 46, 16)                          # переулок за дворами жилого квартала
m.paint("t", 44, 2, 45, 46)                          # проезд между кварталом и складом
m.paint_ragged("g", 78, 15, 108, 41, depth=2)       # рыночная площадь — край рваный в песок
m.paint("a", *WATER.xy(70, 25), *WATER.xy(72, 34))  # подъезд к водокачке от трассы
m.paint("g", *JUNK.xy(60, 35), *JUNK.xy(62, 37))    # въезд на свалку
m.paint("g", *VAULT.xy(49, 51), *VAULT.xy(60, 57))  # площадка перед убежищем
m.reserve(0, ROAD - 1, W - 1, ROAD + 4)
m.reserve(SOUTH - 1, ROAD + 4, SOUTH + 4, H - 1)
m.reserve(*WATER.xy(70, 25), *WATER.xy(72, 34))
m.reserve(0, ROAD - 3, 8, ROAD + 6)                  # площадка у въезда — старт
m.reserve(*VAULT.xy(49, 51), *VAULT.xy(60, 57))
m.reserve(44, 2, 45, 46)


# ------------------------------------------------------------ запад: въезд, остановка, КПП
# Остановка у обочины: скамья под знаком, урна, расписание. КПП шерифа — по другую сторону трассы:
# мешки полукольцом, шлагбаум из досок у обочины, тачка дежурного. Проезжая часть свободна.
put("bench_7", 3, ROAD - 3, allow_reserved=True, check=False)
put("sign_stop", 6, ROAD - 3, allow_reserved=True, check=False)
put("seat_22", 1, ROAD - 3, allow_reserved=True, check=False)
place("r_trash_can", 7, ROAD - 3, allow_reserved=True, check=False)
put("lamp_post", 9, ROAD - 2, allow_reserved=True, check=False)
put("sign_72", 2, ROAD + 6, allow_reserved=True, check=False)
place("x_sandbags", 10, ROAD + 5, allow_reserved=True, check=False)      # КПП — у обочины, перед домами
place("x_sandbags", 12, ROAD + 5, allow_reserved=True, check=False)
place("plank_block", 14, ROAD + 5, allow_reserved=True, check=False)   # шлагбаум
place("x_cart", 17, ROAD + 5, allow_reserved=True, check=False)        # тачка дежурного
place("pole_8", 12, ROAD - 3, allow_reserved=True, check=False)         # столб с указателями
for x in range(20, W - 4, 14):                                           # фонари вдоль трассы
    put("lamp_post", x, ROAD - 2, allow_reserved=True)
    put("lamp_post", x + 7, ROAD + 5, allow_reserved=True)


# ================================================================= СЕВЕР ТРАССЫ
# ------------------------------------------------------------ жилой квартал: три дома с дворами
# Дома стоят фасадом на юг, перед каждым — двор за забором с калиткой; за заборами — переулок (y 15..16).
yard_fences = ["fence_picket", "fence_picket2", "fence_broken", "plank_fence_b", "post_fence_a"]
for name, hx, hy in [("house_a", 4, 3), ("house_b", 19, 3), ("ruin_facade_a", 34, 3)]:
    put(name, hx, hy, check=False)
    m.hwall(yard_fences, hx - 1, hx + 7, hy + 10, gaps=(hx + 3, hx + 4))
    m.grow(hx - 2, hy + 3, hx + 7, hy + 9, 1)

# Двор Марты (3..11, 5..12): навес у стены, стол со стульями под ним, скамья у забора, бочка
# дождевой воды под водостоком, корыто для стирки, бельё на заборе; её шкаф — у стены дома.
place("shelter_a", 5, 5)
place("table_1", 6, 6)
place("chair_wood", 5, 6)
place("chair_wood", 7, 6)
place("chair_wood", 6, 7)
place("bench_7", 5, 11)
place("barrel_wood", 10, 5)
place("bucket", 9, 5)
place("sink", 9, 8)
place("clothes_73", 7, 9)
place("pants", 6, 9)
place("sock", 9, 11)
box("wardrobe", 3, 6, "шкаф Марты", {"ткань": 2, "бинт": 1, "крышки": 6}, owner="marta")
box("metal_box_open", 11, 9, "ящик с бельём", {"ткань": 1})

# Двор работяги (18..26, 5..12): козлы, поленница, кирка, таз, обрезки жести — он чинит квартал.
place("plank_block", 20, 6)
place("log", 20, 8)
place("log", 21, 8)
place("pickaxe", 22, 7)
place("bucket", 24, 6)
place("crate_broken", 24, 10)
place("metal_sheets", 22, 10)
place("sack", 23, 8)

# Двор Нюры (33..41, 5..12): четыре грядки, бочка с водой, вёдра, мешок семян, лопата у грядки.
for gx, gy in ((35, 6), (37, 6), (35, 8), (37, 8)):
    place("x_garden", gx, gy)
place("barrel_wood", 40, 9)
place("bucket", 39, 10)
place("bucket", 34, 10)
place("sack", 40, 6)
place("shovel", 36, 11)
place("locker_2", 39, 5)

# ------------------------------------------------------------ дом деда Эймоса — первый у въезда
# Кирпичный дом 14×11 фасадом на трассу. Разгром: стол перевёрнут, шкаф выломан, на полу — чужой глаз.
# Терминал у северной стены, сейф в углу; люк в подвал — под половицами у кровати.
ix0, iy0, ix1, iy1 = m.building(4, 27, 14, 11, "brick", south=(4,), sign="РИД")
terminal(6, 28, "grandpa")
box("metal_chest", 15, 28, "сейф деда",
    {"10-мм пистолет": 1, "голозапись деда": 1, "медаль за Анкоридж": 1, "патроны": 12},
    requires={"flag": "safe_code", "msg": "Сейф с кодовым замком: три колёсика по две цифры. Код должен быть где-то у деда."})
place("w_bookcase", 8, 28)                          # книги деда — у северной стены
place("w_armchair", 11, 28)                         # его кресло
place("w_wardrobe", 13, 28)                         # выломанный шкаф: дверцы на полу
place("rag", 13, 30)
place("table_upside", 9, 31)                        # стол перевёрнут посреди комнаты
place("chair_broken", 11, 30)
place("bits", 8, 33)
place("bed_frame", 5, 33)                           # кровать у западной стены (сломана)
place("w_rug_quilt", 5, 35)                         # лоскутный коврик у кровати
place("w_cookstove", 14, 35)                        # кухонный угол: плита, буфет, табурет
place("w_cupboard", 12, 35)
place("stool_round_55", 11, 34)
wall_art("w_painting", 5, 27, dy=-44)               # картина над терминалом — Анкоридж в снегу
wall_art("w_wall_clock", 16, 27)                    # часы — над сейфом
place("w_newspaper", 7, 30)                         # бумаги сброшены со стола
place("plank_floor", 15, 33)
place("wardrobe_broken", 16, 31)

# ------------------------------------------------------------ колодец и прачечная тёти Зины
# Двор у колодца (20..42, 19..33): общий колодец с воротом, колонка с корытом, скамьи вокруг,
# верёвки с бельём от прачечной. Сюда ходят за водой и новостями.
m.paint_ragged("t", 21, 19, 41, 32, depth=2)
place("w_well", 30, 24)
place("w_pump", 36, 23)
place("sink", 37, 24)                               # корыто у колонки
place("bench_16", 26, 26)
place("bench_7", 33, 27)
place("bucket", 31, 26)
place("bucket", 29, 26)
place("w_barrels", 23, 21)
put("dead_tree", 25, 23)                             # сухое дерево у колодца — в его тени скамья
place("bench_7", 23, 25)
# прачечная: чаны вдоль стен, корыта, гладильный стол, мешки с бельём; Мила живёт здесь с тётей
ix0, iy0, ix1, iy1 = m.building(24, 34, 12, 9, "planks", south=(4,), sign="ПРАЧЕЧНАЯ")
place("w_bathtub", 25, 35)                          # чаны — у северной стены
place("w_bathtub", 28, 35)
place("w_stove", 34, 35)                            # печь — греть воду
place("bucket", 32, 35)
place("table_2", 25, 39)                            # гладильный стол
place("sack", 33, 39)                               # мешки с бельём
place("sack", 34, 39)
place("w_crate_sacks", 33, 37)
place("w_barrels", 31, 37)                          # вода в бочках — у печи
place("bucket", 27, 35)                             # вёдра между чанами
place("bucket", 30, 35)
place("w_cabinet", 25, 37)                          # шкаф с мылом и щёлоком — у западной стены


# фургон Розы у трассы: застрял — колесо снято; Дэкс охраняет
place("w_wagon", 18, 40)
place("w_crates", 22, 41)
place("crate", 17, 43)

# ------------------------------------------------------------ склад «Пасифик Фрейт» и грузовой двор
# 20×12, ворота в середине южной стены (56..57). Северо-западный угол — контора приёмщика: терминал,
# стол с весами и накладными. Вдоль северной стены — сплошной ряд стеллажей; посередине — ещё два ряда
# стеллажей лицом на юг, между рядами проходы, через склад от ворот — центральный проезд (x 56..57).
# У ворот — разгрузка: плотные штабели ящиков, бочки, мешки.
ix0, iy0, ix1, iy1 = m.building(48, 3, 20, 12, "brick", south=(8,), sign="PACIFIC FREIGHT")
terminal(50, 4, "warehouse")
place("w_desk_b", 49, 6)                             # стол приёмщика
on_table("cardboard", 49, 6)                         # накладные
place("x_scales", 51, 6)                             # весы
place("filecab_1", 49, 4)
for x, name in zip(range(53, 66, 2), ("rack_goods", "rack_stuff", "rack_tools", "rack_goods", "rack_parts",
                                      "rack_stuff", "rack_metal")):
    place(name, x, 4)                                # ряд вдоль северной стены
for y in (8, 11):                                    # два ряда посередине, проезд 56..57 свободен
    for x, name in ((52, "rack_goods"), (54, "rack_metal"), (58, "rack_stuff"), (60, "rack_tools"),
                    (62, "rack_goods"), (64, "rack_parts")):
        place(name, x, y)
place("w_crates", 49, 9)                             # разгрузка у ворот: штабели, бочки, мешки
place("w_crates", 50, 9)
place("w_crate_sacks", 49, 12)
place("w_barrels", 51, 12)
# двор: грузовик у ворот, поддоны с ящиками, бочки — разгрузка
place("r_army_truck", 50, 18)
place("w_crates", 61, 17)
place("w_crates", 64, 17)
place("crate_b", 62, 20)
place("w_barrels", 65, 20)

# ------------------------------------------------------------ салун «Последний глоток»
# 22×15. Северная стена: за стойкой полки с бутылками, люк в подвал Мо. Стойка — через весь запад
# зала; зал — столы со стульями, покерный стол, бильярд; у восточной стены — пианино и граммофон
# (музыкальная зона saloon, data/locations.json). На крыльце — коновязи и скамьи.
ix0, iy0, ix1, iy1 = m.building(48, 24, 22, 15, "planks", south=(10,), sign="САЛУН")
place("w_liquor", 50, 25, check=False)               # шкафы с бутылками за стойкой
place("w_shelf", 53, 25, check=False)
place("w_liquor", 55, 25, check=False)
box("cabinet_small", 58, 25, "шкафчик Мо", {"крышки": 30, "самогон": 2}, owner="mo")
place("w_bar", 50, 29, check=False)                  # стойка — Мо за ней (55,28)
place("w_bar_b", 54, 29, check=False)
for x in (51, 53, 55, 57):
    place("w_stool_red", x, 30)
place("w_wine_rack", 60, 25)
place("x_gramophone", 63, 25)                        # граммофон на тумбе у пианино
place("x_piano", 65, 25)
place("w_stool_grey", 66, 26)
place("w_table_set", 51, 34)                         # стол с лавками
on_table("w_table_lamp", 52, 34, dx=-24, dy=-40)    # посреди стола
place("w_round_table", 56, 33)                       # круглый стол — стулья в профиль, лицом к столу
place("w_chair_r", 55, 33)
place("w_chair_l", 58, 33)
on_table("w_table_lamp", 56, 33, dx=20)
place("w_round_table", 64, 32)                       # столик Ленни — он сидит перед ним (64,33)
place("w_chair_r", 63, 32)
place("w_chair_l", 66, 32)
place("w_poker", 60, 30)                             # покер посередине зала
place("w_chair_r", 59, 30)
place("w_chair_l", 62, 30)
place("w_pool", 66, 29)                              # бильярд у восточной стены
place("w_candelabra", 49, 32)                        # канделябры у стен
place("w_candelabra", 68, 32)
place("barrel_wood", 68, 36)
place("w_plant_b", 49, 36)
place("w_table_set", 60, 35)                         # ещё стол с лавками в южной части зала
on_table("w_table_lamp", 61, 35, dx=-24, dy=-40)
# крыльцо
place("w_hitch", 50, 41)
place("w_hitch_b", 64, 41)
place("w_bench", 54, 40)
place("barrel_wood", 62, 40)


# ------------------------------------------------------------ рынок
# Площадь 77..111 × 13..45. Северный ряд лавок — навесы y 21, прилавки y 22 лицом на юг; южный ряд —
# навесы y 35, прилавки y 34 лицом на север. Между рядами — проход в 10 клеток: по нему ходят.
# Лавка Гены — постоянная, с вывеской и весами; у восточного края — палатка «Детей Единства».
for sx, kind, case in ((80, "shelter_b", "display_case_a"), (87, "shelter_a", "display_case_b"),
                       (94, "shelter_b", "display_case_c")):
    place(kind, sx, 21)
    place("counter", sx, 22)
    place(case, sx + 2, 22)
    place(rnd.choice(["crate_open", "crate", "crate_b"]), sx, 18)
    place("barrel_wood", sx + 2, 18)
for sx, kind in ((80, "shelter_a"), (87, "shelter_b"), (94, "shelter_a")):
    place(kind, sx, 34)
    place("counter", sx, 35)
    place(rnd.choice(["crate", "crate_b", "crate_small"]), sx + 3, 36)
place("x_scales", 91, 23)                            # весы — у прилавка Гены, сам Гена перед ним (88,23)
on_table("table_lantern", 87, 22)                      # фонарь на прилавке
# посреди площади — где едят: котёл с похлёбкой над огнём, скамьи вокруг, миски
place("x_cauldron", 95, 28)
place("bench_7", 93, 30)
place("bench_16", 96, 30)
place("stool_round_55", 94, 27)
place("plate", 97, 28)
place("x_cart", 98, 29)                              # тележка Гоши
place("r_trash_can", 84, 30)
place("r_trash_can", 99, 37)
place("backpack", 83, 27)
# палатка «Детей Единства»: бочка «святой воды», стол с кружками, свечи, коврик для молитвы
put("tent_round_tan", 102, 17, check=False)
box("barrel_wood", 107, 21, "бочка «святой воды»", {"святая вода": 3}, owner="silas")
place("candles", 101, 22)
place("round_table_60", 103, 27)
place("stool_round_55", 102, 27)
place("canteen", 104, 28)
place("x_carpet", 100, 24)
put("tent_green", 79, 14)
put("tent_blue", 96, 14)
put("x_board", 90, 43, allow_reserved=True, check=False)    # доска объявлений — у трассы, на краю рынка
m.terminals.append({"prop": len(m.props) - 1, "id": "doc:doc_board_market"})
put("shack_a", 108, 30, check=False)                 # лачуга, за ней — заначка Гены
box("metal_chest", 109, 28, "заначка Гены", {"крышки": 45, "тоник": 1, "патроны": 8}, owner="gena")
place("w_barrels", 78, 39)                           # привоз у края площади
place("crate_b", 81, 40)


# ------------------------------------------------------------ северо-восток: водокачка (сдвиг старой)
WATER.hwall(["chain_a", "chain_b", "chain_c", "chain_d", "chain_e", "chain_broken_a", "chain_broken_d"],
            60, 94, 24, gaps=(70, 71, 72))
WATER.side_wall("metal", "e", 59, 2, 23, gaps=(11, 12))
WATER.put("water_tank_a", 64, 5, check=False)
WATER.put("water_tank_b", 74, 5, check=False)
WATER.put("water_tank_a", 86, 7, check=False)        # за этим баком прячется Блонди
WATER.building(81, 13, 12, 8, "metal", south=(4,), west=(4,), sign="ВОДА")   # контора водокачки
WATER.terminal(83, 14, "pump")
WATER.box("locker_1", 88, 14, "шкафчик Уоллеса", {"записка техника": 1, "бинт": 1})
for name, x, y in (("filecab_3", 85, 14), ("filecab_4", 90, 14), ("locker_3", 91, 14)):
    WATER.place(name, x, y, check=False)
WATER.place("w_desk_b", 82, 16)                       # рабочий стол у западной стены (без ящиков: E у терминала — терминал)
WATER.place("canteen", 83, 18)
WATER.place("w_table_plain", 89, 16)                  # стол сменщика, он сидит за ним (стул позади)
WATER.place("w_chair", 90, 15)
on_table("table_lantern", *WATER.xy(89, 16))
on_table("cardboard", *WATER.xy(90, 16), dx=6)        # план водопровода
WATER.place("canister", 82, 18)
WATER.place("bucket", 91, 18)
WATER.put("shelter_b", 61, 14)
for name, y in (("locker_2", 4), ("locker_3", 5), ("locker_2", 6), ("locker_3", 7)):
    WATER.place(name, 60, y)
for x, y in ((64, 12), (70, 12), (76, 12)):          # трубы из земли у баков
    WATER.place("x_pipe", x, y)
WATER.place("x_ladder", 65, 7)
WATER.place("x_ladder", 75, 7)
WATER.place("x_ladder", 87, 9)
WATER.place("canister", 63, 7)
WATER.place("canister", 75, 8)
WATER.place("table_2", 68, 9)                         # насосная: верстак под навесом
WATER.place("tool_rack", 70, 9)
WATER.place("canister", 70, 10)
WATER.place("x_puddle", 72, 11)
for x in (77, 78, 79, 80):
    WATER.place("x_pipe", x, 20)                      # штабель труб у сетки
for x in (66, 67, 68):
    WATER.place("sack", x, 23)                        # цемент у сетки
WATER.put("x_barrel_boom", 66, 18)
WATER.put("x_barrel_boom", 75, 15)
WATER.place("barrel_wood", 67, 17)                    # укрытия мутантов
WATER.place("crate", 69, 17)
WATER.place("barrel_wood", 76, 20)
WATER.place("crate_b", 78, 18)


# ================================================================= ЮГ ТРАССЫ
# ------------------------------------------------------------ дом Черепана — без крыши
# 14×11, вход с трассы. Крыша рухнула: балки и листы — у южной стены, верстак и шкафы — у северной.
ix0, iy0, ix1, iy1 = m.building(3, 55, 14, 11, "brick", north=(4,), roof=False)
place("w_desk_c", 4, 56)                              # верстак Черепана у северной стены — он мастерит
on_table("toolbox_red", 4, 56)
place("tool_rack", 7, 56)                             # инструмент на стене-стойке
place("w_crates", 9, 56)                              # заготовки в ящиках
place("w_cabinet", 12, 56)
place("w_armchair", 15, 59)
place("w_bed", 4, 62)
place("w_nightstand", 6, 62)                           # тумба рядом с кроватью
place("plank_block", 9, 63)                           # балки с крыши
place("metal_sheets", 12, 63)
place("pile_scrap", 14, 63)
place("crate_broken", 7, 63)
put("x_puddle", 10, 62)
place("bucket", 14, 61)

# ------------------------------------------------------------ участок шерифа
# 18×13, вход в северо-западном углу (24..25). Классика участка: шериф сидит за столом лицом в комнату,
# за его спиной на стене — оружейная стойка; перед столом коврик, туда подходят. Ожидающие — на стульях
# в профиль у западной стены, лицом к столу. Вдоль северной стены справа — шкафчик с оружием и картотеки;
# в глубине — стол помощника. Вдоль южной стены — три камеры. Юго-западный угол — уголок дежурного:
# койка, тумбочка с фонарём, плита с кофейником. На стене — картина у входа, «Разыскиваются», часы.
ix0, iy0, ix1, iy1 = m.building(20, 55, 18, 13, "planks", north=(4,), sign="★ШЕРИФ")
place("w_gun_rack", 27, 56)                           # стойка за спиной шерифа
place("w_rug_green", 27, 59)                          # коврик перед столом — сюда подходят
place("w_desk", 27, 58)                               # стол шерифа лицом в комнату
on_table("w_table_lamp", 27, 58)
on_table("canteen", 28, 58, dx=6)
box("w_locker", 32, 56, "оружейный шкаф шерифа", {"патроны": 6}, owner="sheriff")
place("w_locker", 33, 56)
place("filecab_2", 35, 56)                            # дела
place("filecab_1", 36, 56)
for y in (58, 60):                                    # ожидающие — лицом к столу
    place("w_chair_r", 21, y)
place("w_chair", 33, 60)                              # помощник — за своим столом
place("w_desk_b", 32, 61)
on_table("cardboard", 32, 61)
for x in (27, 30, 33):                                # камеры вдоль южной стены
    place("x_jail_cell", x, 65)
place("w_bed", 21, 65)                                # уголок дежурного
place("w_nightstand", 23, 65)
on_table("w_table_lantern", 23, 65)
place("w_cookstove", 21, 62)
on_table("canteen", 22, 62)
wall_art("w_painting", 21, 55)                        # картина у входа
wall_art("w_wanted", 29, 55, dx=4)                    # на свободной стене между стойкой и шкафчиками
wall_art("w_wanted", 30, 55, dx=22)
wall_art("w_wall_clock", 34, 55)
put("x_board", 30, 53, allow_reserved=True, check=False)    # доска объявлений шерифа — у входа, на улице
m.terminals.append({"prop": len(m.props) - 1, "id": "doc:doc_board_sheriff"})

# ------------------------------------------------------------ клиника Дока
# 16×12, вход в северо-западном углу (43..44). Док — за столом приёма лицом в комнату, за спиной у него
# на северной стене — аптека: шкаф со стеклом (его лекарства), шкаф с ящиками, полки с бинтами. Ожидающие
# — на стульях в профиль у западной стены, лицом к Доку. Палата — вдоль восточной стены: три койки с
# тумбочками, ширма отделяет её от приёмной. Юго-запад — процедурная: ванна, смотровой стол с лампой, ведро.
ix0, iy0, ix1, iy1 = m.building(41, 55, 16, 12, "concrete", north=(2,), sign="+КЛИНИКА")
box("w_glass_cabinet", 46, 56, "аптечный шкаф Дока", {"бинт": 2, "антирадин": 1, "химикаты": 1}, owner="doc")
place("w_cabinet", 48, 56)                            # аптека — за спиной Дока
place("w_shelf", 50, 56)
place("w_desk_b", 47, 58)                             # стол приёма
on_table("w_table_lantern", 47, 58)
on_table("cardboard", 48, 58)
place("w_rug_green", 47, 59)                          # перед столом — сюда подходят
for y in (58, 60):                                    # ожидающие — лицом к Доку
    place("w_chair_r", 42, y)
for y in (57, 60, 63):                                # палата: койки с тумбочками у восточной стены
    place("bed", 54, y)
    place("w_nightstand", 53, y)
on_table("bucket", 53, 63, dy=-18)
place("x_screen", 51, 61)                             # ширма между приёмной и палатой
place("w_bathtub", 42, 64)                            # процедурная
place("w_desk_b", 45, 64)                             # смотровой стол
on_table("w_table_lamp", 46, 64)
place("bucket", 44, 63)
wall_art("w_wall_clock", 45, 55)
wall_art("w_mirror", 52, 55)


# ------------------------------------------------------------ ратуша
# 20×13. Вход — в западном углу северной стены (62..63), не за спинами совета. Совет сидит за прямыми
# столами в северной части лицом на юг, к залу: Ада — в центре перед креслом, по сторонам — стулья
# советников; под столами ковёр, у торцов канделябры. На северной стене — портрет первого смотрителя,
# флаг города, знак убежища; у стены — книжный шкаф, напольные часы, стол с терминалом. Просители —
# на стульях в профиль вдоль западной и восточной стен, лицом к проходу; середина зала свободна —
# здесь стоят перед советом. Архив — картотеки вдоль восточной стены.
ix0, iy0, ix1, iy1 = m.building(60, 54, 20, 13, "brick", north=(2,), sign="СОВЕТ")
terminal(77, 55, "council")
place("w_bookcase", 72, 55)                           # книги города и протоколы
place("w_grand_clock", 75, 55)
wall_art("w_portrait", 66, 54)                        # первый смотритель — над местом Ады
wall_art("x_flag", 65, 54)
wall_art("x_vault_sign", 69, 54)
for x in (64, 66, 68, 70):                            # ковёр под столом совета
    place("w_rug_red", x, 57)
place("w_armchair", 68, 56)                           # кресло Ады — она стоит перед ним (68,57)
for x in (65, 66, 70, 71):                            # советники — за столом лицом к залу
    place("w_chair", x, 57)
for x in (65, 67, 69):                                # прямые столы в ряд
    place("w_table_long", x, 58)
on_table("cardboard", 66, 58)                         # протоколы
on_table("w_table_lamp", 69, 58)
place("w_candelabra", 64, 58)
place("w_candelabra", 71, 58)
place("w_rug_red", 67, 60)                            # ковёр перед советом — здесь стоит проситель
for y in (60, 62, 64):                                # просители — вдоль стен, лицом к проходу
    place("w_chair_r", 61, y)
    place("w_chair_l", 76, y)
box("filecab_2", 78, 58, "стол Смотрительницы", {"ключ-карта Б": 1, "крышки": 20}, owner="ada")
for y in (60, 62, 64):                                # архив вдоль восточной стены
    place("filecab_1" if y != 62 else "filecab_3", 78, y)
place("w_plant", 61, 56)


# ------------------------------------------------------------ юго-запад: руины над ливнёвкой
ix0, iy0, ix1, iy1 = m.building(3, 73, 22, 16, "concrete", north=(8,), east=(6,), roof=False)
m.paint("c", 4, 74, 23, 87)
put("x_manhole", 13, 80)
m.portal([(13, 80)], "drain", (3, 3), "Ливнёвка")
# обвал у восточной стены: балки, плиты, кирпич; тропа от входа к люку свободна
place("plank_block", 19, 78)
place("metal_sheets", 21, 79)
place("brick_pile_a", 20, 82)
place("concrete_block", 22, 81)
place("rubble_heap", 18, 84)
place("x_puddle", 15, 76)
place("toolbox_red", 14, 82)
for name, x, y in [("bed_frame", 5, 76), ("pile_rags", 21, 75), ("clothes_74", 6, 86), ("pile_bags", 22, 86)]:
    place(name, x, y)
scatter(RUBBLE + JUNK_PILES[:4], ix0, iy0, ix1, iy1, 5)
put("x_pipe", 16, 74)

# ------------------------------------------------------------ кладбище
CX0, CY0, CX1, CY1 = 30, 73, 66, 94
m.paint("d", CX0, CY0, CX1, CY1)
m.hwall(["post_fence_a", "post_fence_b", "plank_fence_a", "plank_fence_b", "fence_broken"], CX0, CX1, CY0 - 1,
        gaps=(47, 48))
m.side_wall("planks", "w", CX0, CY0, CY1 - 1)
m.side_wall("planks", "e", CX1, CY0, CY1 - 1)
m.hwall(["post_fence_a", "post_fence_b", "plank_fence_a", "fence_broken"], CX0, CX1, CY1)
graves = [(gx, gy) for gy in (77, 81, 85) for gx in range(34, 63, 4) if (gx, gy) != (62, 85)]
for i, (gx, gy) in enumerate(graves):
    put("x_cross" if i % 3 else "x_tombstone", gx, gy - 1, check=False)
    put("x_grave", gx, gy, check=False)
    m.containers[-1]["requires"] = {"item": "лопата", "msg": "Могила. Голыми руками не раскопать — нужна лопата."}
    m.containers[-1]["name"] = "могила"
# могила пса деда «Колбаса»: жетон Эймоса со Списком Марипозы
put("x_tombstone", 62, 84, check=False)
box("x_grave", 62, 85, "могила «Колбаса»", {"жетон Эймоса": 1, "патроны": 6},
    requires={"item": "лопата", "msg": "На камне выцарапано: «КОЛБАСА. Лучший пёс. Э.Р.». Без лопаты не раскопать."})
put("shack_b", 32, 88, check=False)                   # сторожка (лопата — рядом)
m.paint("g", CX0 + 1, 79, CX1 - 1, 79)               # дорожки между рядами
m.paint("g", CX0 + 1, 83, CX1 - 1, 83)
m.paint("g", 47, CY0, 48, 78)
place("bench_16", 38, 91)
place("bucket", 41, 91)
place("shovel", 42, 90)
place("x_petunia", 36, 78)
place("x_petunia", 46, 82)
place("x_petunia", 54, 86)
place("lantern_lit", 61, 86)
place("candles", 63, 86)
for x, y in ((52, 91), (34, 75), (64, 76)):
    put("dead_tree", x, y)
m.grow(CX0 + 1, CY0, CX1 - 1, CY1 - 1, 6, GRASS)


# ------------------------------------------------------------ юг-центр: сквер и Убежище 57 (сдвиг старого)
for x, y in [(50, 37), (55, 37), (58, 41)]:
    VAULT.put("dead_tree", x, y)
for x, y in [(49, 39), (52, 41)]:
    VAULT.put(rnd.choice(BENCHES), x, y)
VAULT.scatter(["round_table_45", "stool_round_55", "stone_table", "rock_grass", "rock_grass_b"], 49, 36, 58, 42, 3)
VAULT.grow(49, 36, 58, 42, 2)
VAULT.put("x_mesa_vault", 49, 48, check=False, allow_reserved=True)
VAULT.portal([(55, 51), (56, 51)], "vault57", (19, 5), "Убежище 57")
VAULT.put("x_vault_sign", 59, 52, allow_reserved=True, check=False)
for x, y in ((50, 53), (53, 54), (57, 54), (58, 55)):
    VAULT.put("x_sandbags", x, y, allow_reserved=True, check=False)
VAULT.put("lamp_post", 53, 52, allow_reserved=True, check=False)
VAULT.put("lamp_post", 58, 52, allow_reserved=True, check=False)
VAULT.place("table_2", 52, 57, allow_reserved=True, check=False)
VAULT.place("cardboard", 53, 57, allow_reserved=True, check=False)
VAULT.place("chair_wood", 52, 58, allow_reserved=True, check=False)
VAULT.place("ammo_box", 58, 57, allow_reserved=True, check=False)
VAULT.place("r_trash_can", 60, 57, allow_reserved=True, check=False)
VAULT.place("bench_16", 50, 59, allow_reserved=True, check=False)
VAULT.place("bench_7", 56, 59, allow_reserved=True, check=False)
VAULT.place("x_petunia", 50, 56, allow_reserved=True, check=False)
VAULT.scatter(CRATES + BARRELS, 60, 56, 62, 62, 4)


# ------------------------------------------------------------ юго-восток: свалка (сдвиг старой)
JUNK.hwall(["wall_corrugated", "wall_corrugated2", "wall_metal", "wall_metal2", "wall_corrugated_rust",
            "corrugated_panel", "corrugated_b"], 60, 94, 37, gaps=(60, 61, 62))
JUNK.side_wall("metal", "e", 64, 38, 62, gaps=(45, 46, 58))
JUNK.put("shack_b", 66, 56, check=False)              # лачуга Панка
JUNK.building(68, 40, 12, 8, "metal", south=(4,), west=(3,), sign="КОНТОРА")
JUNK.terminal(70, 41, "junk")
JUNK.box("metal_chest", 77, 41, "сейф конторы", {"крышки": 60, "патроны": 10, "тоник": 1},
         requires={"flag": "junk_safe_open", "msg": "Сейф конторы. Электронный замок — открывается с терминала."})
# приёмка металлолома: стеллаж и шкафчики у северной стены, стол приёмщика у восточной, весы у входа,
# ящики сортировки у южной; от западного проёма и южной двери — проход
JUNK.place("locker_4", 72, 41, check=False)
JUNK.place("filecab_1", 74, 41, check=False)
JUNK.place("w_desk_c", 76, 43)                        # стол приёмщика у восточной стены, стул — за ним
JUNK.place("w_chair", 77, 42)
on_table("cardboard", *JUNK.xy(76, 43))
JUNK.place("x_scales", 70, 45)                        # весы — у западного входа
JUNK.place("crate", 74, 45)                           # ящики сортировки — в стороне от двери
JUNK.place("crate_b", 75, 45)
JUNK.place("x_wire_coil", 78, 45)
JUNK.building(80, 55, 10, 6, "planks", south=(4,))   # сторожка свалки
JUNK.place("w_bed", 81, 56)
JUNK.place("w_locker", 88, 56)
JUNK.place("w_table_plain", 85, 57)                   # стол сторожей, стулья в профиль — лицом друг к другу
JUNK.place("w_chair_r", 84, 57)
JUNK.place("w_chair_l", 87, 57)
on_table("candles", *JUNK.xy(85, 57), dx=10)          # свеча и миска на столе
on_table("plate", *JUNK.xy(86, 57))
JUNK.place("bucket", 81, 58)
# лагерь рейдеров: костёр, круг из бочек, палатки, трофейный стол; места рейдеров не заняты
for name, x, y in [("tent_green", 84, 41), ("tent_tan", 88, 49), ("firewood", 86, 46), ("ammo_box", 90, 45),
                   ("crate", 83, 46), ("crate_b", 91, 53), ("x_barrel_boom", 82, 50), ("x_sandbags", 83, 44)]:
    JUNK.put(name, x, y)
for x, y in ((84, 46), (88, 46), (86, 44), (86, 48)):
    JUNK.place("barrel_wood", x, y)
JUNK.place("table_5", 85, 47)
JUNK.place("plate", 84, 48)
JUNK.place("pile_bottles", 88, 44)
JUNK.place("pile_tires", 89, 42)
JUNK.place("sack", 83, 48)
JUNK.place("metal_sheets", 91, 45)                    # навес-будка пса
JUNK.place("bucket", 90, 47)
JUNK.place("r_bones", 89, 48)
JUNK.place("r_bones", 79, 38)
JUNK.scatter(JUNK_PILES, 66, 39, 93, 62, 14)
# за оградой свалки к югу — поле битых машин
for x, y in ((122, 84), (132, 88), (141, 82), (127, 93)):
    put(rnd.choice(["r_car_wreck", "r_car_a", "r_car_c", "r_car_d"]), x, y, check=False)
scatter(JUNK_PILES[:6] + RUBBLE[:4], 116, 81, 147, 97, 10)


# ------------------------------------------------------------ по всему городу — только на улице
# Камни, обломки, трава и столбы — на песке, глине и щебне; на пол домов и на асфальт не сыплются.
OUTSIDE = ("s", "t", "q")


def scatter_out(names, n, tries=60):
    placed = 0
    for _ in range(n * tries):
        if placed >= n:
            break
        x, y = rnd.randint(1, W - 2), rnd.randint(1, H - 2)
        if m.ground[y][x] in OUTSIDE and put(rnd.choice(names), x, y):
            placed += 1
    return placed


m.grow(1, 1, W - 2, H - 2, 70)
m.grow(1, 1, W - 2, H - 2, 18, GRASS)
scatter_out(POLES + SIGNS, 8)
scatter_out(STONES + FLOOR_BITS[:5], 50)


# ------------------------------------------------------------ переходы
m.portal([(W - 1, y) for y in range(ROAD, ROAD + 4)], "fifteen_school", (2, 46), "Старая школа")


def hatch(cands, to, at, label, requires):
    """Люк в подвал: первая свободная клетка из списка; выходят из подвала на соседнюю (at)."""
    for x, y in cands:
        if (x, y) not in m.blocked and (x, y) not in m.soft and m.ground[y][x] == "c":
            m.props.append(["x_manhole", x, y])
            m.portal([(x, y)], to, at, label, requires=requires)
            return (x, y)
    raise AssertionError(f"негде поставить люк в {to}")


print("люк деда:", hatch([(7, 33), (8, 34), (6, 34)], "fifteen_cellar", (3, 5), "Подвал деда",
      {"flag": "cellar_found",
       "msg": "Половицы здесь звучат гулко. Под ними люк — без ручки и без замка. Как открыть — знает только дед."}))
print("люк салуна:", hatch([(52, 27), (53, 27), (56, 26)], "fifteen_saloon_cellar", (3, 5), "Подвал салуна",
      {"flag": "mo_cellar", "msg": "Люк за стойкой. Мо, не оборачиваясь: «Это мой подвал. Даже не думай»."}))

# ------------------------------------------------------------ пустыри — сценками (только снаружи)
print("обжито:", m.dress_empty([
    [("r_tent_beige", 0, 0), ("campfire", 3, 2), ("r_logs", 2, 3), ("barrel_wood", 0, 3), ("pile_rags", 4, 0)],
    [("r_car_wreck", 0, 0), ("pile_tires", 3, 2), ("r_trash", 0, 3), ("barrel_wood", 4, 1)],
    [("r_pickup", 0, 0), ("r_barrels", 3, 0), ("pile_scrap", 2, 3), ("crate_broken", 4, 2)],
    [("r_camper", 0, 0), ("r_awning", 0, 2), ("crate", 3, 2), ("sack", 4, 2), ("bucket", 5, 1)],
    [("r_billboard", 0, 0), ("r_dtree_a", 2, 1), ("r_bones", 3, 2), ("r_rocks", 4, 2)],
    [("r_water_tower_b", 3, 0), ("barrel_wood", 4, 1), ("bucket", 2, 1), ("r_barrels", 5, 1)],
    [("r_shack", 0, 0), ("pile_junk", 5, 1), ("barrel_wood", 0, 3), ("x_fire_barrel", 3, 3)],
], ground=("s", "t", "q"), block=9, margin=2, chance=0.8, max_uses=2))


# ------------------------------------------------------------ места жителей массовки (src/ambient.py)
# Каждый — у своего дела (tools/folks_01_fifteen.py): огородница — на огороде, певица — у пианино,
# выпивоха — у стойки, прачка с племянницей — у прачечной, караульный — на КПП, повариха — у котла.
FOLK_SPOTS = {
    "nyura": (34, 7),        # огород во дворе Нюры
    "gosha": (100, 29),      # у своей тележки на рынке
    "lyokha": (14, 71),      # у входа в руины над ливнёвкой — лазит туда
    "mila": (31, 44),        # двор прачечной
    "boris": (27, 27),       # на скамье у колодца
    "fedya": (53, 31),       # у стойки салуна
    "zina": (29, 38),        # в прачечной
    "pashka": (13, 44),      # бегунок — у трассы, ждёт поручений
    "tikhon": (82, 24),      # охотник со шкурами — у первой лавки рынка
    "glasha": (64, 27),      # у пианино
    "ignat": (16, 54),       # караульный на КПП у въезда
    "shura": (53, 21),       # механичка — чинит грузовик у склада
    "tasya": (96, 27),       # повариха — у котла посреди рынка
    "critter:chicken": [(40, 11)],                   # куры — у огорода Нюры
    "critter:brahmin": [(16, 42)],                   # брамин — у фургона Розы
    "critter:cat": [(50, 35), (27, 40), (10, 34)],   # кошки — в салуне, у прачечной, у деда
    "critter:dog": [(86, 38), (9, 54)],              # собаки — у рынка и у КПП
}


# ------------------------------------------------------------ проверки и запись
reach = m.check(gap_exempt=("dog",))
for key, t in FOLK_SPOTS.items():
    for tt in (t if key.startswith("critter:") else [t]):
        assert tuple(tt) in reach and tuple(tt) not in m.blocked, f"место жителя {key} {tt} занято или недоступно"
# рабочие зоны: ходят, но по своему месту (src/wander.py) — x0, y0, x1, y1
WALK_ZONES = {
    "sheriff": (26, 57, 34, 59),      # между своим столом, стойкой и шкафчиками
    "doc": (45, 57, 52, 62),          # стол приёма, аптека, палата
    "ada": (64, 56, 77, 57),          # за столом совета и у своего терминала
    "mo": (49, 26, 58, 28),           # вдоль стойки
    "lenny": (61, 31, 66, 34),        # у своего столика
    "gena": (85, 23, 92, 24),         # у своей лавки
}
m.save("data/maps/town.json", floors=m.floors, walk_zones={k: list(v) for k, v in WALK_ZONES.items()},
       folk_spots={k: ([list(t) for t in v] if k.startswith("critter:") else list(v)) for k, v in FOLK_SPOTS.items()})
print(f"город {W}×{H}: объектов {len(m.props)}, пятен {len(m.decals)}, обыскиваемых {len(m.containers)}, "
      f"врагов {len(m.enemies)}, NPC {len(m.npcs)}, предметов {len(m.pickups)}; доступно клеток {len(reach)}")
