"""
Генератор карты стартового города Пятнадцатая (data/maps/town.json).

Районы (96×64 клетки), подробно — docs/story.md, раздел «Стартовый город»:
  запад            — въезд с трассы, остановка; отсюда начинается игра;
  северо-запад     — жилой квартал: дом деда, дома жителей, дворы;
  север            — салун «Последний глоток», склад «Пасифик Фрейт»;
  центр-север      — рынок: лавка Гены, палатка проповедника «Детей Единства», доска объявлений;
  северо-восток    — водокачка за сеткой: баки, контора, светящиеся мутанты, Блонди;
  юг у дороги      — дом Черепана, пост шерифа, клиника, ратуша;
  юго-запад        — руины склада со спуском в ливнёвку (крысы), кладбище;
  юг-центр         — сквер (панцирный жук) и скала с дверью Убежища 57;
  юго-восток       — свалка: лагерь рейдеров, пёс на цепи, лачуга Панка-одиночки.
Через весь город — улица (трасса I-15) с выходами на запад и на юг.

Спуск в ливнёвку и дверь убежища — порталы в подземные карты
(tools/build_underground.py).

Запуск из папки game_project:  .venv/bin/python tools/build_town.py
"""
from mapkit import (MapKit, BARRELS, CRATES, GRASS, BUSHES, STONES, FLOOR_BITS, DIRT_DECALS, JUNK_PILES,
                    CLOTH_PILES, RUBBLE, FURNITURE, LOCKERS, POLES, SIGNS, SEATS, BENCHES)

W, H = 96, 64
m = MapKit(W, H, start=(3, 31), seed=7)
rnd = m.rnd
put, box, terminal, scatter = m.put, m.box, m.terminal, m.scatter
m.exits = [(0, y) for y in range(30, 34)] + [(x, H - 1) for x in range(44, 48)]


def place(name, x, y, **kw):
    """Явная расстановка: предмет обязан встать. put() возвращает False молча — из-за этого в интерьерах
    из десяти задуманных предметов оставалось по три (docs/furnish/fifteen.md §1.1)."""
    if put(name, x, y, **kw):
        return True
    foot = m.footprint(name, x, y)
    why = []
    if any(t in m.blocked for t in foot):
        why.append("блок: " + str([t for t in foot if t in m.blocked]))
    if any(t in m.soft for t in foot):
        why.append("мягкое: " + str([t for t in foot if t in m.soft]))
    if any(t in m.soft_obj for t in foot):
        why.append("мягкий предмет: " + str([t for t in foot if t in m.soft_obj]))
    if any(t in m.reserved for t in foot):
        why.append("резерв")
    if m.hides(name, x, y):
        b = m.hides(name, x, y)
        why.append(f"заслоняет {b[0]} ({b[1]}, {b[2]})")
    why.append("земля: " + "".join(m.ground[yy][xx] for xx, yy in foot))
    raise AssertionError(f"«{name}» не встал в ({x}, {y}): " + "; ".join(why))


# ------------------------------------------------------------ кто и что где (резервируется до расстановки)
m.pickups += [
    ["лом", 1, 9, 20],                  # в доме деда
    ["чей-то глаз", 1, 8, 18],          # в доме деда
    ["ткань", 1, 19, 10],
    ["химикаты", 1, 72, 13],
    ["химикаты", 1, 76, 58],
    ["лопата", 1, 24, 60],              # в сторожке кладбища
    ["ткань", 1, 30, 14],
]
m.npcs += [
    ["gena", 44, 22],
    ["silas", 52, 20],                  # проповедник «Детей Единства» у своей палатки
    ["blondie", 88, 4],
    ["mo", 21, 19],                     # за стойкой салуна
    ["lenny", 26, 23],                  # за столиком салуна
    ["marta", 9, 9],                    # во дворе своего дома
    ["turtle", 8, 40],                  # Черепан — в доме без крыши за дорогой
    ["sheriff", 19, 39],                # пост шерифа у въезда
    ["doc", 27, 40],                    # клиника
    ["ada", 38, 40],                    # ратуша
    ["dale", 52, 54],                   # помощник шерифа — часовой у двери убежища
    ["dex", 12, 25],                    # наёмник Дэкс у въезда — охрана застрявшего каравана Розы
    ["loner", 69, 60],
    ["dog", 90, 46],                    # пёс на цепи у ящика с патронами в лагере рейдеров
]
m.enemies += [
    ["rad_mutant", 68, 16], ["rad_mutant", 77, 19],     # водокачка
    ["rat", 5, 57], ["rat", 13, 58], ["rat", 10, 50],   # руины над ливнёвкой
    ["beetle", 56, 41],                                 # высохший сквер
    ["raider", 85, 45], ["raider", 87, 54],             # лагерь на свалке
]
for _, x, y in m.enemies + m.npcs:
    m.reserve(x, y, x, y)
for *_, x, y in m.pickups:
    m.reserve(x, y, x, y)


# ------------------------------------------------------------ земля: пятна песка, утоптанной глины и сухой травы поверх основной
m.floors = {"s": ["pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1"],
            "t": ["pk:desnat/p1/4,4,1,1", "pk:desnat/p1/5,4,1,1", "pk:desnat/p1/6,4,1,1"],        # сухая растрескавшаяся глина
            "q": ["pk:desnat/p1/10,4,1,1"]}                                                         # щебень
m.paint("s", 0, 0, W - 1, H - 1)
m.patchwork("s", ["t"], 46, 3, 6, seed=2)
m.patchwork("s", ["q"], 26, 2, 3, seed=1)


# ------------------------------------------------------------ дороги
m.paint("a", 0, 30, W - 1, 33)                    # главная улица
for x in range(0, W, 4):
    m.ground[31][x] = m.ground[31][x + 1] = "h"  # прерывистая разметка
m.paint("g", 0, 29, W - 1, 29)                    # тротуары
m.paint("g", 0, 34, W - 1, 34)
m.paint("a", 44, 34, 47, H - 1)                   # улица на юг
for y in range(36, H, 4):
    m.ground[y][45] = m.ground[y + 1][45] = "v"
m.paint("g", 43, 35, 43, H - 1)
m.paint("g", 48, 35, 48, H - 1)
m.paint_ragged("g", 36, 14, 57, 28, depth=2)            # рыночная площадь — край рваный в песок, а не вырезанный прямоугольник
m.paint("a", 70, 22, 72, 28)                      # подъезд к водокачке
m.paint("g", 60, 35, 62, 40)                      # въезд на свалку
m.paint("g", 49, 51, 60, 57)                      # площадка перед убежищем
m.reserve(0, 29, W - 1, 34)
m.reserve(43, 34, 48, H - 1)
m.reserve(70, 22, 72, 28)
m.reserve(0, 26, 8, 36)                           # площадка у въезда — старт
m.reserve(20, 27, 24, 28)                         # у дверей салуна
m.reserve(49, 51, 60, 57)


# ------------------------------------------------------------ запад: въезд и остановка
put("bench_7", 3, 27, allow_reserved=True, check=False)
put("sign_stop", 6, 27, allow_reserved=True, check=False)
put("seat_22", 1, 27, allow_reserved=True, check=False)
put("sign_72", 2, 36, allow_reserved=True, check=False)
put("lamp_post", 9, 28, allow_reserved=True, check=False)
# у остановки: урна, доска с расписанием (x_board — у рынка своя) и указатели-столбы;
# у поста шерифа — мешки с песком и барьер поперёк подъезда, тачка дежурного: сценка «КПП на въезде»
place("r_trash_can", 7, 27, allow_reserved=True, check=False)
place("x_sandbags", 16, 35, allow_reserved=True, check=False)
place("x_sandbags", 18, 35, allow_reserved=True, check=False)
place("plank_block", 16, 36, allow_reserved=True, check=False)   # барьер поперёк подъезда
place("x_cart", 14, 36)                                          # тачка дежурного
place("pole_8", 12, 27, allow_reserved=True, check=False)         # столб с указателями у дороги
for x in range(18, W - 4, 12):                    # фонари вдоль улицы
    put("lamp_post", x, 28, allow_reserved=True)
    put("lamp_post", x + 6, 35, allow_reserved=True)


# ------------------------------------------------------------ северо-запад: жилой квартал
# дом деда Эймоса — первый у въезда: разгром, чужой глаз на полу, включённый терминал, сейф
m.building(3, 14, 10, 8, "brick", south=(4,), sign="РИД")
terminal(5, 15, "grandpa")
box("metal_chest", 10, 15, "сейф деда",
    {"10-мм пистолет": 1, "голозапись деда": 1, "медаль за Анкоридж": 1, "патроны": 12},
    requires={"flag": "safe_code", "msg": "Сейф с кодовым замком: три колёсика по две цифры. Код должен быть где-то у деда."})
for name, x, y in [("table_upside", 7, 16), ("chair_broken", 9, 17), ("bed_frame", 4, 19), ("bits", 6, 18),
                   ("plank_floor", 10, 19), ("rag", 5, 17), ("wardrobe_broken", 11, 17)]:
    put(name, x, y, check=False)

yard_fences = ["fence_picket", "fence_picket2", "fence_broken", "plank_fence_b", "post_fence_a"]
for name, hx, hy in [("house_a", 3, 2), ("house_b", 14, 2), ("ruin_facade_a", 24, 2)]:
    put(name, hx, hy, check=False)
    m.hwall(yard_fences, hx - 1, hx + 6, hy + 9, gaps=(hx + 2, hx + 3))
    m.grow(hx - 2, hy + 3, hx + 6, hy + 8, 1)
box("wardrobe", 4, 7, "шкаф Марты", {"ткань": 2, "бинт": 1, "крышки": 6}, owner="marta")
box("metal_box_open", 12, 7, "ящик с бельём", {"ткань": 1})

# Двор Марты (3..9,4..10): навес у стены дома, стол под ним, две скамьи, бочка дождевой воды,
# корыто, бельё на заборе. На песке перед домом — только камни и трава.
place("shelter_a", 4, 4)                          # навес-крыльцо у стены дома
place("table_1", 5, 5)
place("chair_wood", 4, 5)                         # стулья вокруг стола
place("chair_wood", 6, 5)
place("chair_wood", 5, 6)
place("bench_7", 4, 9)                            # скамья у забора, лицом во двор
place("barrel_wood", 9, 4)                        # бочка дождевой воды под водостоком
place("bucket", 8, 4)
place("sink", 8, 7)                               # корыто для стирки
place("clothes_73", 6, 8)                         # бельё, брошенное на забор
place("pants", 5, 8)
place("sock", 8, 9)

# Двор Нюры (24..30,4..10): огород — четыре грядки, вода в бочке, вёдра, мешок с семенами,
# лопата у грядки: она живёт с этого огорода (её грядки — сценка «Грядки Нюры»).
for gx, gy in ((25, 4), (27, 4), (25, 6), (27, 6)):
    place("x_garden", gx, gy)
place("barrel_wood", 30, 7)
place("bucket", 29, 8)
place("bucket", 24, 7)
place("sack", 24, 8)                              # мешок с семенами
place("shovel", 25, 9)                            # лопата у грядки
place("locker_2", 29, 3)                          # ящик с инструментом у стены развалины

# Двор третьего дома (14..20,4..10): поленница, козлы, таз, инструмент — здесь живёт работяга,
# который чинит всё в квартале.
place("plank_block", 15, 4)                       # козлы
place("log", 15, 6)
place("log", 16, 6)
place("pickaxe", 17, 5)
place("bucket", 19, 4)                            # таз
place("crate_broken", 19, 8)
place("metal_sheets", 17, 8)
place("sack", 18, 6)


# ------------------------------------------------------------ север: салун «Последний глоток»
ix0, iy0, ix1, iy1 = m.building(15, 16, 14, 11, "planks", south=(6,), sign="САЛУН")
# Стойка — цельная от западной стены до прохода у (26,20): за ней Мо, люк в подвал и полки с бутылками.
for x in (16, 18, 20, 22, 24):
    place("counter", x, 20, check=False)
# За стойкой: полки с товаром вдоль северной стены, открытый ящик с бутылками, тара у люка.
place("shelf_goods", 16, 17, check=False)
place("shelf_stuff_1", 18, 17, check=False)
place("shelf_goods", 21, 17, check=False)
place("barrel_wood", 24, 17, check=False)
place("barrel_wood", 26, 17, check=False)
box("cabinet_small", 27, 17, "шкафчик Мо", {"крышки": 30, "самогон": 2}, owner="mo")
place("crate_open", 16, 18)                       # ящик с бутылками
place("pile_bottles", 18, 18)                     # пустая тара
place("crate", 23, 18)
# Музыка в салуне: граммофон на полке за стойкой (набор 1920s Speakeasy, px SCKR) — к нему потом
# вешается музыкальная зона (docs/audio_plan.md). Стоит на стороне Мо, лицом в зал.
place("x_gramophone", 25, 19)
# Зал: два столика со стульями, «последний вечер» на троих у (23,23), столик Ленни у восточной стены.
place("round_table_45", 17, 23)
place("chair_wood", 16, 23)
place("chair_wood", 18, 23)
place("candles", 17, 22)
place("round_table_42", 23, 23)
place("chair_2", 22, 23)
place("chair_3", 24, 23)
place("plate", 23, 24)                            # тарелки у столика на троих
place("chair_broken", 22, 24)                     # опрокинутый табурет
place("round_table_60", 26, 24)
place("stool_round_41", 25, 23)
place("stool_round_55", 27, 24)
# Южная стена: пианино с табуретом, бочка-стол в углу, ведро у стойки, лампы на стенах.
place("x_piano", 16, 25)
place("stool_round_56", 19, 24)
place("barrel_wood", 27, 22)                      # бочка-стол у восточной стены
place("bucket", 24, 21)                           # ведро у стойки
place("lantern_lit", 27, 21)
place("lantern_lit", 16, 22)


# ------------------------------------------------------------ склад «Пасифик Фрейт»
ix0, iy0, ix1, iy1 = m.building(32, 1, 10, 9, "brick", south=(4,), sign="PACIFIC FREIGHT")
terminal(34, 2, "warehouse")
# Стеллажи вдоль обеих стен, штабель ящиков у восточной, весы и накладные у стола приёмщика;
# по центру — проход в две клетки от ворот (36..37,8) к терминалу.
place("filecab_1", 33, 2, check=False)
place("filecab_1", 35, 2, check=False)
place("filecab_3", 36, 2, check=False)
place("shelf_goods", 37, 2, check=False)
place("shelf_stuff_2", 39, 2)
place("table_2", 33, 3)                           # стол приёмщика рядом с терминалом
place("x_scales", 33, 4)                          # весы у стола
place("cardboard", 33, 5)                         # накладные
place("crate", 34, 5)
place("crate", 39, 4)                             # штабель у восточной стены
place("crate_b", 40, 4)
place("crate_small", 39, 5)
place("crate_open", 40, 5)
place("barrel_wood", 40, 6)                       # южная стена: груз в бочках, а не второй ряд стеллажей
place("crate_small", 33, 7)
place("crate_b", 40, 7)
place("barrel_small", 39, 7)


# ------------------------------------------------------------ рынок
# Площадь 36..57 × 14..28. Два ряда лавок вокруг прохода: северный ряд — навес y=18, прилавок y=19
# лицом на юг; южный ряд — навес y=26, прилавок y=25 лицом на север. За прилавком (в глубине навеса) —
# товар в ящиках и бочках, на прилавке — витрина. Центр площади (y=20..23) остаётся свободным: по нему ходят.
place("shelter_b", 37, 18)                        # северный ряд, лоток 1
place("counter", 37, 19)                          # 2×1: прилавок с товаром
place("display_case_a", 39, 19)                   # витрина рядом с прилавком
place("crate_open", 38, 15)                       # товар за прилавком, в тени навеса
place("barrel_wood", 40, 15)
place("shelter_a", 43, 18)                        # лавка Гены — постоянная, с вывеской
place("counter", 43, 19)
place("display_case_b", 45, 19)
place("crate_small", 44, 15)
place("barrel_wood", 42, 15)
place("lantern_lit", 46, 22)
place("x_scales", 41, 20)                         # весы: здесь взвешивают товар
# южный ряд — лицом на север, к проходу
place("shelter_b", 37, 24)
place("counter", 37, 25)
place("display_case_c", 39, 25)
place("crate", 40, 26)                            # ящики рядом с прилавком
place("shelter_a", 43, 24)
place("counter", 43, 25)
place("crate_b", 46, 25)
place("barrel_wood", 45, 25)
# палатка «Детей Единства»: бочка со «святой водой», кружки, свечи, коврик для молитвы
put("tent_round_tan", 50, 15, check=False)
box("barrel_wood", 54, 18, "бочка «святой воды»", {"святая вода": 3}, owner="silas")
place("candles", 49, 19)
place("round_table_60", 50, 21)
place("stool_round_55", 49, 21)
place("canteen", 51, 21)                          # кружки на столе
place("x_carpet", 47, 22)                         # коврик перед палаткой
place("x_cart", 46, 24)                           # тележка Гоши с товаром
put("tent_green", 36, 13)
put("tent_blue", 55, 13)
place("r_trash_can", 41, 23)
place("r_trash_can", 52, 24)
place("backpack", 40, 22)
put("x_board", 40, 27, allow_reserved=True, check=False)  # доска объявлений у улицы
m.terminals.append({"prop": len(m.props) - 1, "id": "doc:doc_board_market"})
put("shack_a", 56, 20, check=False)               # лачуга, за ней — заначка Гены
box("metal_chest", 57, 18, "заначка Гены", {"крышки": 45, "тоник": 1, "патроны": 8}, owner="gena")
# привоз товара к северной кромке площади: бочки и ящики, ещё не разобранные
for name, x, y in (("barrel_10", 46, 15), ("barrel_11", 47, 15), ("crate_b", 41, 15),
                   ("barrel_18", 53, 17), ("crate", 54, 17)):
    place(name, x, y)


# ------------------------------------------------------------ северо-восток: водокачка
m.hwall(["chain_a", "chain_b", "chain_c", "chain_d", "chain_e", "chain_broken_a", "chain_broken_d"],
        60, 94, 24, gaps=(70, 71, 72))
m.side_wall("metal", "e", 59, 2, 23, gaps=(11, 12))
put("water_tank_a", 64, 5, check=False)
put("water_tank_b", 74, 5, check=False)
put("water_tank_a", 86, 7, check=False)           # за этим баком прячется Блонди
ix0, iy0, ix1, iy1 = m.building(81, 13, 12, 8, "metal", south=(4,), west=(4,), sign="ВОДА")  # контора водокачки
terminal(83, 14, "pump")
box("locker_1", 88, 14, "шкафчик Уоллеса", {"записка техника": 1, "бинт": 1})
# Картотека и шкафчики вдоль северной стены, стол сменщика у восточной, у западной — канистра,
# термос и инструмент. Проход от двери (85..86,19) и от западного проёма (81,17) свободен.
place("filecab_3", 85, 14, check=False)
place("filecab_4", 87, 14, check=False)
place("filecab_4", 90, 14, check=False)
place("locker_3", 91, 14, check=False)
place("locker_2", 91, 15)
place("table_2", 82, 16)                          # рабочий стол у западной стены
place("canteen", 83, 16)                          # термос
place("table_6", 89, 16)                          # стол сменщика
place("chair_wood", 89, 17)
place("lantern_lit", 91, 16)
place("canister", 82, 17)
place("tool_rack", 82, 18)
place("cardboard", 87, 18)                        # папка с планом водопровода
place("bucket", 91, 18)
place("chair_wood", 88, 17)
place("x_pipe", 91, 17)                           # труба, принесённая из колодца
# Водокачка (60..94 × 2..24). Шкафчики дежурных — вдоль западной металлической стены, а не посреди песка:
# от баков к сетке идут трубы, к каждому баку — лестница, у основания — канистры; насосная (68..70,9) со
# верстаком и инструментом, штабель труб у южной сетки, мешки с цементом — там же, где чинят трубы.
put("shelter_b", 61, 14)
for name, y in (("locker_2", 4), ("locker_3", 5), ("locker_2", 6), ("locker_3", 7)):
    place(name, 60, y)
for x, y in ((64, 12), (70, 12), (76, 12)):     # трубы выходят из земли у баков: по одной на бак
    place("x_pipe", x, y)
place("x_ladder", 65, 7)                          # лестницы к бакам
place("x_ladder", 75, 7)
place("x_ladder", 87, 9)
place("canister", 63, 7)
place("canister", 75, 8)
place("table_2", 68, 9)                           # насосная: верстак под навесом
place("tool_rack", 70, 9)
place("canister", 70, 10)
place("x_puddle", 72, 11)                         # прорвало стык: лужа и брошенный инструмент
place("canister", 72, 14)
for x in (77, 78, 79, 80):                        # штабель труб у сетки
    place("x_pipe", x, 20)
for x in (66, 67, 68):
    place("sack", x, 23)                          # цемент у сетки
put("x_barrel_boom", 66, 18)
put("x_barrel_boom", 75, 15)
# укрытия светящихся мутантов: бочки и ящики в двух клетках — есть выбор позиции, но не лабиринт
place("barrel_wood", 67, 17)
place("crate", 69, 17)
place("barrel_wood", 76, 20)
place("crate_b", 78, 18)


# ------------------------------------------------------------ юг у дороги: Черепан, шериф, клиника, ратуша
# дом Черепана без крыши: разгром собран в углы — верстак у северной стены, хлам у южной, балки по полу
ix0, iy0, ix1, iy1 = m.building(2, 37, 14, 8, "brick", north=(4,), roof=False)
place("table_chair", 3, 38)                       # верстак с инструментом
place("toolbox_red", 5, 38)
place("chair_wood", 4, 39)
place("wardrobe_broken", 11, 38)
place("wardrobe", 14, 38, check=False)            # шкафы — по углам, не в ряд посреди комнаты
place("armchair", 12, 39)
place("nightstand", 14, 40)
place("table_1", 9, 41)
place("plank_block", 9, 42)                       # балки с рухнувшей крыши
place("log", 12, 40)
place("metal_sheets", 6, 42)
place("crate_broken", 7, 41)
place("pile_scrap", 11, 42)                       # куча хлама
put("x_puddle", 4, 42)
put("bucket", 3, 41)
put("pile_rags", 13, 42)

# пост шерифа: стол в углу, за ним стул, радио и кружка; оружейный шкаф — у южной стены
ix0, iy0, ix1, iy1 = m.building(17, 37, 6, 6, "planks", north=(2,), sign="★ШЕРИФ")
place("table_2", 20, 38, check=False)             # стол дежурного у северной стены
place("chair_wood", 21, 39, check=False)
place("x_radio", 21, 38, check=False)             # радио на столе
place("filecab_2", 18, 38, check=False)           # картотека с делами
place("canteen", 18, 39)                          # кофе дежурного
place("plate", 19, 40)
box("locker_double", 18, 41, "оружейный шкаф шерифа", {"патроны": 6}, owner="sheriff")
put("x_board", 23, 35, allow_reserved=True, check=False)
m.terminals.append({"prop": len(m.props) - 1, "id": "doc:doc_board_sheriff"})

# клиника: две койки за ширмой, стол Дока, раковина у южной стены, полка с бинтами у восточной
ix0, iy0, ix1, iy1 = m.building(24, 37, 8, 8, "concrete", north=(2,), sign="+КЛИНИКА")
place("bed", 29, 39, check=False)
place("bed", 29, 42, check=False)
place("x_screen", 29, 40)                         # ширма между койками
place("sink", 25, 43, check=False)
box("glass_cabinet", 25, 38, "аптечный шкаф Дока", {"бинт": 2, "антирадин": 1, "химикаты": 1}, owner="doc")
place("table_3", 26, 39, check=False)             # стол Дока
place("chair_wood", 27, 39, check=False)
place("lantern_lit", 25, 39)                      # лампа у койки
place("shelf_stuff_2", 30, 38)                    # полка с бинтами
place("table_3", 27, 43, check=False)             # смотровой стол у южной стены
place("bucket", 25, 42)                           # таз

# ратуша: стол заседаний на четыре места, скамья для просителей, архив у восточной стены,
# портрет смотрителя над терминалом, флаг города в юго-восточном углу
ix0, iy0, ix1, iy1 = m.building(33, 36, 10, 9, "brick", north=(4,), sign="СОВЕТ")
terminal(35, 37, "council")
box("filecab_2", 40, 37, "стол Смотрительницы", {"ключ-карта Б": 1, "крышки": 20}, owner="ada")
place("filecab_1", 41, 37, check=False)
place("x_vault_sign", 34, 37)                     # знак убежища у входа в зал
place("x_portrait", 36, 37)                       # портрет смотрителя у северной стены
place("filecab_3", 34, 39)                        # архив
place("filecab_4", 41, 39)
place("cardboard", 34, 40)                        # папки
place("table_b", 36, 41, check=False)             # стол заседаний
place("table_b", 38, 41, check=False)

place("chair_wood", 40, 41, check=False)
place("chair_2", 36, 42, check=False)
place("chair_3", 39, 42, check=False)
place("bench_16", 34, 41, check=False)            # скамья для просителей
place("x_flag", 40, 42, check=False)
place("shelf_wood", 41, 42, check=False)


# ------------------------------------------------------------ юго-запад: руины над ливнёвкой и кладбище
ix0, iy0, ix1, iy1 = m.building(2, 48, 16, 13, "concrete", north=(6,), east=(6,), roof=False)  # руины — крыши нет
m.paint("c", 3, 49, 16, 59)
put("x_manhole", 9, 54)
m.portal([(9, 54)], "drain", (3, 3), "Ливнёвка")
# Обвал у восточной стены (13..16,52..56): балки, плиты, битый кирпич. Тропа от входа (5..9,52..54)
# к люку остаётся чистой — по ней ходят в ливнёвку. У люка — ящик с инструментом, у трубы — мох и лужа.
place("plank_block", 14, 52)
place("metal_sheets", 15, 53)
place("brick_pile_a", 14, 55)
place("concrete_block", 16, 54)
place("rubble_heap", 13, 56)
place("x_puddle", 11, 50)
place("toolbox_red", 10, 55)                      # ящик с инструментом у люка
for name, x, y in [("bed_frame", 4, 50), ("pile_rags", 14, 50), ("clothes_74", 5, 58), ("pile_bags", 15, 57)]:
    put(name, x, y)
scatter(RUBBLE + JUNK_PILES[:4], ix0, iy0, ix1, iy1, 5)
put("x_pipe", 12, 49)

m.paint("d", 20, 48, 41, 62)
m.hwall(["post_fence_a", "post_fence_b", "plank_fence_a", "plank_fence_b", "fence_broken"],
        20, 41, 47, gaps=(30, 31))
m.side_wall("planks", "w", 20, 48, 61)
m.hwall(["post_fence_a", "post_fence_b", "plank_fence_a", "fence_broken"], 20, 41, 62)
graves = []
for gy in (50, 53, 56):
    for gx in range(23, 40, 3):
        if (gx, gy) == (38, 56):
            continue
        graves.append((gx, gy))
for i, (gx, gy) in enumerate(graves):
    put("x_cross" if i % 3 else "x_tombstone", gx, gy - 1, check=False)
    put("x_grave", gx, gy, check=False)
    m.containers[-1]["requires"] = {"item": "лопата", "msg": "Могила. Голыми руками не раскопать — нужна лопата."}
    m.containers[-1]["name"] = "могила"
# могила пса деда: надгробие «КОЛБАСА», внутри — жетон Эймоса со Списком Марипозы
put("x_tombstone", 38, 55, check=False)
box("x_grave", 38, 56, "могила «Колбаса»", {"жетон Эймоса": 1, "патроны": 6},
    requires={"item": "лопата", "msg": "На камне выцарапано: «КОЛБАСА. Лучший пёс. Э.Р.». Без лопаты не раскопать."})
put("shack_b", 22, 58, check=False)                # сторожка кладбища (лопата — рядом)
# дорожки между рядами могил — гравий: ровные полосы по y=51 и y=54, от ограды до ограды,
# и короткий вход от ворот (30..31,47) к первому ряду. По дорожкам ходят, могилы не топчут.
m.paint("g", 21, 51, 40, 51)
m.paint("g", 21, 54, 40, 54)
m.paint("g", 30, 48, 31, 49)
place("bench_16", 25, 59)                         # скамья у сторожки
place("bucket", 27, 59)                           # лейка и вёдра для полива
place("bucket", 26, 58)
place("shovel", 27, 57)
place("x_petunia", 24, 50)                        # цветы на трёх могилах
place("x_petunia", 27, 53)
place("x_petunia", 30, 56)
place("lantern_lit", 37, 57)                      # лампада у «Колбасы»
place("candles", 39, 57)
for x, y in ((34, 60), (26, 49)):
    put("dead_tree", x, y)
m.grow(21, 48, 40, 61, 4, GRASS)


# ------------------------------------------------------------ юг-центр: сквер и Убежище 57
for x, y in [(50, 37), (55, 37), (58, 41)]:
    put("dead_tree", x, y)
for x, y in [(49, 39), (52, 41)]:
    put(rnd.choice(BENCHES), x, y)
scatter(["round_table_45", "stool_round_55", "stone_table", "rock_grass", "rock_grass_b"], 49, 36, 58, 42, 3)
m.grow(49, 36, 58, 42, 2)
# столовая гора, в южном склоне — дверь-шестерня; перед ней площадка с часовым
put("x_mesa_vault", 49, 48, check=False, allow_reserved=True)
m.portal([(55, 51), (56, 51)], "vault57", (19, 5), "Убежище 57")
put("x_vault_sign", 59, 52, allow_reserved=True, check=False)
# КПП у двери убежища: мешки полукольцом, прожектор, стол с журналом для Дейла, ящик с патронами.
# Перед дверью (54..57,52) пусто — проход к гермодвери не заставлен.
put("x_sandbags", 50, 53, allow_reserved=True, check=False)
put("x_sandbags", 53, 54, allow_reserved=True, check=False)
put("x_sandbags", 57, 54, allow_reserved=True, check=False)
put("x_sandbags", 58, 55, allow_reserved=True, check=False)
put("lamp_post", 53, 52, allow_reserved=True, check=False)      # прожектор на штативе
put("lamp_post", 58, 52, allow_reserved=True, check=False)
place("table_2", 52, 57, allow_reserved=True, check=False)      # стол с журналом дежурного
place("cardboard", 53, 57, allow_reserved=True, check=False)    # журнал
place("chair_wood", 52, 58, allow_reserved=True, check=False)
place("ammo_box", 58, 57, allow_reserved=True, check=False)
place("r_trash_can", 60, 57, allow_reserved=True, check=False)
place("bench_16", 50, 59, allow_reserved=True, check=False)     # скамьи лицом к месе
place("bench_7", 56, 59, allow_reserved=True, check=False)
place("x_petunia", 50, 56, allow_reserved=True, check=False)    # клумба у площадки
scatter(CRATES + BARRELS, 60, 56, 62, 62, 4)


# ------------------------------------------------------------ юго-восток: свалка
m.hwall(["wall_corrugated", "wall_corrugated2", "wall_metal", "wall_metal2", "wall_corrugated_rust",
         "corrugated_panel", "corrugated_b"], 60, 94, 37, gaps=(60, 61, 62))
m.side_wall("metal", "e", 64, 38, 62, gaps=(45, 46, 58))
put("shack_b", 66, 56, check=False)               # лачуга Панка
ix0, iy0, ix1, iy1 = m.building(68, 40, 12, 8, "metal", south=(4,), west=(3,), sign="КОНТОРА")  # контора свалки
terminal(70, 41, "junk")
box("metal_chest", 77, 41, "сейф конторы", {"крышки": 60, "патроны": 10, "тоник": 1},
    requires={"flag": "junk_safe_open", "msg": "Сейф конторы. Электронный замок — открывается с терминала."})
# Приёмка металлолома: весы у входа с запада, стол приёмщика с журналом, ящики с сортировкой у южной
# стены. Проход от западного проёма (68,43) и от двери (72..73,46) свободен.
place("shelf_rust", 69, 41)
place("locker_4", 71, 41, check=False)
place("cardboard", 72, 41)                        # журнал приёмки
place("filecab_1", 73, 41, check=False)
place("crate_small", 75, 41)
place("locker_double", 76, 41, check=False)
place("barrel_small", 69, 42)
place("pile_tech_tire", 76, 42)
place("table_5", 76, 43, check=False)             # стол приёмщика
place("chair_wood", 77, 43)
place("chair_2", 77, 44, check=False)
place("barrel_wood", 69, 44)
place("x_wire_coil", 78, 44)                      # моток проволоки из мастерской
place("x_scales", 70, 45)                         # весы для металлолома
place("crate", 74, 45)                            # ящики с сортировкой
place("crate_b", 75, 45)
place("pile_scrap", 76, 45)
place("table_5", 69, 46, check=False)
place("sofa", 70, 46, check=False)
ix0, iy0, ix1, iy1 = m.building(80, 55, 10, 6, "planks", south=(4,))     # сторожка свалки
# Сторожка: койка у северной стены, шкафчик в углу, стол со стульями, фонарь — светит на дверь.
place("bed", 81, 56, check=False)
place("locker_3", 88, 56)
place("table_4", 85, 57)
place("chair_3", 84, 57)
place("chair_3", 86, 57)
place("plate", 86, 58)
place("lantern_lit", 87, 58)
place("crate_broken", 83, 58)
place("crate_small", 88, 58)
place("bucket", 81, 58)
for name, x, y in [("tent_green", 84, 41), ("tent_tan", 88, 49), ("firewood", 86, 46), ("ammo_box", 90, 45),
                   ("crate", 83, 46), ("crate_b", 91, 53), ("x_barrel_boom", 82, 50), ("x_sandbags", 83, 44)]:
    put(name, x, y)
# Лагерь рейдеров: круг из бочек у костра (86,46), трофейный стол с добычей, мешки и шины.
# Места самих рейдеров (85,45 и 87,54) не занимаем.
place("barrel_wood", 84, 46)
place("barrel_wood", 88, 46)
place("barrel_wood", 86, 44)
place("barrel_wood", 86, 48)
place("table_5", 85, 47)                          # стол с добычей
place("plate", 84, 48)
place("pile_bottles", 88, 44)
place("pile_tires", 89, 42)
place("sack", 83, 48)
place("metal_sheets", 82, 53)
# у пса (90,46): навес-будка из листов, миска, кости — он на цепи у склада патронов
place("metal_sheets", 91, 45)
place("bucket", 90, 47)
place("r_bones", 89, 48)
place("r_bones", 79, 38)                          # «трофеи» на ограде у входа
scatter(JUNK_PILES, 66, 39, 93, 62, 16)           # хлам — уже вокруг лагеря, а не под ногами
# между оградой свалки и сквером — пустырь с хламом
scatter(JUNK_PILES[:6] + RUBBLE[:4], 59, 38, 63, 62, 5)


# ------------------------------------------------------------ по всему городу
m.grow(1, 1, W - 2, H - 2, 38)                                         # трава и кусты — куртинами
m.grow(1, 1, W - 2, H - 2, 10, GRASS)                                  # и небольшие пучки у стен
scatter(POLES + SIGNS, 1, 1, W - 2, H - 2, 5)
scatter(STONES + FLOOR_BITS[:5], 1, 1, W - 2, H - 2, 30)
# пятен земли (dirt_patch) на карте нет: у них квадратные края, а земля и так пятнистая
scatter(RUBBLE, 1, 1, W - 2, 3, 2)


# ------------------------------------------------------------ новые районы (tools/build_fifteen.py)
# ставится в самом конце, чтобы не сдвигать случайную расстановку выше
m.portal([(W - 1, y) for y in range(30, 34)], "fifteen_school", (2, 30), "Старая школа")


def hatch(cands, to, at, label, requires):
    """Люк в подвал: первая свободная клетка из списка; выходят из подвала на соседнюю (at)."""
    for x, y in cands:
        if (x, y) not in m.blocked and (x, y) not in m.soft and m.ground[y][x] == "c":
            m.props.append(["x_manhole", x, y])
            m.portal([(x, y)], to, at, label, requires=requires)
            return (x, y)
    raise AssertionError(f"негде поставить люк в {to}")


hatch([(9, 19), (8, 19), (6, 20), (9, 20)], "fifteen_cellar", (3, 5), "Подвал деда",
      {"flag": "cellar_found",
       "msg": "Половицы здесь звучат гулко. Под ними люк — без ручки и без замка. Как открыть — знает только дед."})
hatch([(20, 18), (22, 18), (25, 19), (19, 19)], "fifteen_saloon_cellar", (3, 5), "Подвал салуна",
      {"flag": "mo_cellar", "msg": "Люк за стойкой. Мо, не оборачиваясь: «Это мой подвал. Даже не думай»."})

# ------------------------------------------------------------ пустыри обживаются сценками (экскурсия по городам)
print("обжито:", m.dress_empty([
    [("r_tent_beige", 0, 0), ("campfire", 3, 2), ("r_logs", 2, 3), ("barrel_wood", 0, 3), ("pile_rags", 4, 0)],
    [("r_car_wreck", 0, 0), ("pile_tires", 3, 2), ("r_trash", 0, 3), ("barrel_wood", 4, 1)],
    [("r_pickup", 0, 0), ("r_barrels", 3, 0), ("pile_scrap", 2, 3), ("crate_broken", 4, 2)],
    [("r_camper", 0, 0), ("r_awning", 0, 2), ("crate", 3, 2), ("sack", 4, 2), ("bucket", 5, 1)],
    [("r_dumpster", 0, 0), ("pile_cans", 2, 0), ("r_trash", 0, 2), ("crate_broken", 3, 2)],
    [("x_cross", 0, 0), ("x_grave", 0, 1), ("x_cross", 2, 0), ("x_grave", 2, 1), ("r_dtree_a", 4, 1)],
    [("r_billboard", 0, 0), ("r_dtree_a", 2, 1), ("r_bones", 3, 2), ("r_rocks", 4, 2)],
    [("r_water_tower_b", 3, 0), ("barrel_wood", 4, 1), ("bucket", 2, 1), ("r_barrels", 5, 1)],
    [("r_shack", 0, 0), ("pile_junk", 5, 1), ("barrel_wood", 0, 3), ("x_fire_barrel", 3, 3)],
], ground=("s", "t", "q", "d"), block=7, margin=1, chance=0.9, max_uses=2))


# ------------------------------------------------------------ проверки и запись
reach = m.check(gap_exempt=("dog",))
m.save("data/maps/town.json", floors=m.floors)
print(f"город {W}×{H}: объектов {len(m.props)}, пятен {len(m.decals)}, обыскиваемых {len(m.containers)}, "
      f"врагов {len(m.enemies)}, NPC {len(m.npcs)}, предметов {len(m.pickups)}; доступно клеток {len(reach)}")
