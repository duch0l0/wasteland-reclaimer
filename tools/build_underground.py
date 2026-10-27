"""
Подземные карты Пятнадцатой: Убежище 57 (data/maps/vault57.json) и
ливнёвка (data/maps/drain.json). Вход — порталы на карте города
(tools/build_town.py), выход — порталы обратно.

Убежище 57 (48×44):
  шлюз с дверью-шестернёй → атриум (ярус А: склад города, жилые каюты,
  кабинет смотрителя) → гермодверь яруса Б (ключ-карта или терминал) →
  ярус Б: коридор с турелью, лаборатория «Проекта Панцирь», архив.
Ливнёвка (60×31):
  лестница из люка → тоннели с тиной и трубами → развилка, где культисты
  обронили сумку → логово крысолюдов с вожаком и кормушкой → решётка
  стока, через которую крысолюды лезут в город.

Склад «Бейкер-7» (44×30) — под бункером на окраине Бейкера (tools/build_baker.py):
  лестница со шлюзом и мешками у двери → коридор → караулка (пост охраны у входа) →
  главный зал со стеллажными рядами и клетка «партии 7» (десять контейнеров ВРЭ,
  пять опломбированных, пять пустых, турель) → южнее зала оружейка, пост связи с
  терминалом-журналом отгрузки (он и заканчивает главу, слайды baker_finale)
  и генераторная.

Запуск из папки game_project:  .venv/bin/python tools/build_underground.py
"""
from mapkit import MapKit, CRATES, BARRELS, LOCKERS, JUNK_PILES, CLOTH_PILES, RUBBLE
from src import props as props_info
from vaultkit import tidy_lamps
from citykit import City

city = City("underground", "Подземелья")     # реестр объектов из наборов: data/props/underground.json


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


STEEL = ["pk:nbunk/p2/4,8,1,1"]
GRILLE = ["pk:nbunk/p2/0,12,1,1"]
PLATES_UG = ["pk:fstation/fstation_f2_09"]
BUNK_U = P("ug_bunk", "pk:nbunk/nbunk_2_000", foot=[2, 1], sight=True)
LOCKER_U = [P("ug_locker_a", "pk:nbunk/nbunk_2_005", foot=[1, 1], search="locker", title="шкафчик"), P("ug_locker_b", "pk:nbunk/nbunk_2_006", foot=[1, 1], search="locker", title="шкафчик")]
GEN_U = P("ug_gen", "pk:nbunk/nbunk_2_028", foot=[2, 2], sight=True, light={"r": 100, "color": [255, 200, 120], "at": [0.5, 0.5], "flicker": 0.25})
WARN_U = P("ug_warn", "pk:npower/npower_1_069", foot=[1, 1])
CONSOLE_U = [P("ug_console_a", "pk:npower/npower_2_006", foot=[2, 1]), P("ug_console_b", "pk:npower/npower_2_013", foot=[2, 1])]
SERVER_U = P("ug_server", "pk:npower/npower_2_042", foot=[1, 1])
VRE_U = P("ug_vre", "pk:wlab/wlab_2_024", foot=[2, 1], sight=True)
BIOHAZ_U = P("ug_biohaz", "pk:hosp/hosp_1_012", foot=[1, 1])
TUBE_U = P("ug_tube", "pk:wlab/wlab_3_101", foot=[2, 1], sight=True, light={"r": 80, "color": [150, 255, 160], "at": [0.5, 0.5], "flicker": 0.3})
LAMP_U = P("ug_lamp", "pk:cmine/cmine_1_032", foot=[1, 1], block=False, light={"r": 120, "color": [255, 190, 110], "at": [0.5, 0.5], "flicker": 0.3})
CHAIR_U = P("ug_chair", "pk:aoffice/aoffice_1_002", foot=[1, 1])


def room(m, code, x0, y0, x1, y1):
    m.paint(code, x0, y0, x1, y1)


# ================================================================ Убежище 57
# Подземелье: ×1.56 из docs/furnish_guide.md к нему не относится, клетка та же, что у интерьеров.
# Планировка по назначению (logic.md §1), расстановка поштучная — автообстановки у MapKit нет.
# Было 40×34 (699 проходимых клеток, 76 объектов, плотность 10.9): комнаты большие и полые, мебель
# длинными рядами по стенам, коридор Б и тупик с турелью пустые, кабинет смотрителя 5×7 и каюта 6×7
# тесны для своего назначения, у яруса Б не было ни площадки, ни спуска. Стало 48×44; комнаты
# разобраны по смыслу (docs/furnish/fifteen.md §3.6), добавлены коридор жилого блока, вторая каюта,
# спуск с площадкой и кабинет Кросса отдельной комнатой.
# С севера на юг:
#   шлюз 12..29 × 2..9 → проход → атриум-склад 9..33 × 11..20;
#   западнее — кабинет смотрителя 2..7 × 12..18, восточнее — коридор жилого блока 35..36 × 11..23
#   с каютами 38..44 × 11..16 (семейная) и 38..44 × 18..23 (после крысолюдов);
#   южнее атриума — спуск 17..24 × 22..27, гермодверь (20..21, 27) → коридор Б 6..42 × 28..31;
#   под коридором — лаборатория «Панцирь» 4..19 × 33..41, тупик с турелью 22..27 × 33..37,
#   архив 30..38 × 33..40 и кабинет Кросса 40..46 × 33..38.
VW, VH = 48, 44
v = MapKit(VW, VH, start=(19, 5), seed=57, fill="x")
FLOOR, WALL = "m", "x"          # m — стальной пол убежища (src/townmap.py: _vault_floor), x — порода


# ------------------------------------------------------------ мебель убежища: наборы nbunk, npower, wlab
# Пятно задаётся явно: у большинства спрайтов картинка ~1.9 клетки в ширину и 1.8 в высоту, и с
# автоматическим пятном 2×2 мебель налезает друг на друга (logic.md §2а, «двойники стеллажей»).
V_BUNK = P("vb_bunk_bed", "pk:nbunk/nbunk_3_001", foot=[2, 1], sight=True)          # двухъярусная койка
V_BED = P("vb_bed", "pk:nbunk/nbunk_3_000", foot=[2, 1], sight=True)                # койка с одеялом
V_NIGHT = P("vb_nightstand", "pk:nbunk/nbunk_3_005", foot=[1, 1], sight=True, search="drawer", title="тумбочка")
V_LOCKERS = P("vb_lockers", "pk:nbunk/nbunk_3_003", foot=[2, 1], sight=True, search="locker", title="ряд шкафчиков")
V_LOCKER = P("vb_locker", "pk:nbunk/nbunk_3_008", foot=[1, 1], sight=True, search="locker", title="шкафчик")
V_WARDROBE = P("vb_wardrobe", "pk:nbunk/nbunk_3_007", foot=[1, 1], sight=True, search="drawer", title="шкаф")
V_RACK = P("vb_rack", "pk:nbunk/nbunk_3_004", foot=[2, 1], sight=True)              # пустой стеллаж
V_SHELF = P("vb_shelf", "pk:nbunk/nbunk_3_002", foot=[2, 1], sight=True, search="shelf", title="полка")
V_TABLE = P("vb_table", "pk:nbunk/nbunk_3_018", foot=[2, 1], sight=True)            # деревянный стол
V_DESK = P("vb_desk", "pk:nbunk/nbunk_3_019", foot=[2, 1], sight=True)              # стол с ящиком
V_BENCH = P("vb_workbench", "pk:nbunk/nbunk_3_006", foot=[2, 1], sight=True)        # верстак с тисками
V_SAFE = P("vb_safe", "pk:nbunk/nbunk_3_027", foot=[1, 1], sight=True)              # стальной сейф
V_PANEL = P("vb_panel", "pk:nbunk/nbunk_3_032", foot=[1, 1], sight=True)            # электрощит
V_SINK = P("vb_sink", "pk:nbunk/nbunk_3_035", foot=[1, 1], sight=True)              # раковина
V_GRILLE = P("vb_grille", "pk:nbunk/nbunk_3_036", foot=[2, 1], sight=True)          # вентиляционная решётка
V_TANKS = P("vb_tanks", "pk:nbunk/nbunk_2_021", foot=[3, 1], sight=True)            # баки с водой
V_CRATES = P("vb_crates", "pk:nbunk/nbunk_3_029", foot=[2, 1], sight=True, search="crate", title="штабель ящиков")
V_MILBOX = P("vb_milbox", "pk:nbunk/nbunk_3_030", foot=[2, 1], sight=True, search="military", title="армейский ящик")
V_PILE = P("vb_supply", "pk:nbunk/nbunk_3_020", foot=[2, 1], sight=True)            # штабель ящиков с консервами
V_CAN = P("vb_jerrycan", "pk:nbunk/nbunk_3_041", foot=[1, 1])                       # канистра
V_CONSOLE = P("vb_console", "pk:npower/npower_2_002", foot=[2, 1], sight=True,
              light={"r": 90, "color": [140, 220, 200], "at": [0.5, 0.3], "flicker": 0.12})
V_SERVER = P("vb_server", "pk:npower/npower_2_042", foot=[1, 1], sight=True)
V_SERVER_ROW = P("vb_server_row", "pk:npower/npower_2_073", foot=[2, 1], sight=True)
V_DESK_MON = P("vb_desk_mon", "pk:npower/npower_2_066", foot=[2, 1], sight=True)
V_DESK_PAPER = P("vb_desk_paper", "pk:npower/npower_2_067", foot=[2, 1], sight=True)
V_LAB = P("vb_lab_bench", "pk:wlab/wlab_3_054", foot=[2, 1], sight=True)            # лабораторный стол
V_LAB_B = P("vb_lab_bench_b", "pk:wlab/wlab_3_055", foot=[2, 1], sight=True)
V_MICRO = P("vb_microscope", "pk:wlab/wlab_3_059", foot=[1, 1], block=False)
V_CAPSULE = P("vb_capsule", "pk:wlab/wlab_3_101", foot=[2, 1], sight=True,
              light={"r": 70, "color": [150, 255, 160], "at": [0.5, 0.4], "flicker": 0.06})
V_CAPSULE_B = P("vb_capsule_b", "pk:wlab/wlab_3_103", foot=[2, 1], sight=True)
V_GLASS = P("vb_glass_cab", "pk:wlab/wlab_2_012", foot=[2, 1], sight=True, search="shelf", title="стеклянный шкаф")
V_BOTTLES = P("vb_bottle_shelf", "pk:wlab/wlab_2_061", foot=[2, 1], sight=True, search="shelf", title="полка с реактивами")
V_DOCS = P("vb_docs_table", "pk:wlab/wlab_2_027", foot=[2, 1], sight=True)          # стол с бумагами
V_CHAIR = P("vb_chair", "pk:wlab/wlab_3_041", foot=[1, 1])                          # офисный стул
V_VIAL = P("vb_vial", "pk:wlab/wlab_3_084", foot=[1, 1], block=False)              # склянка
V_FLASK = P("vb_flask", "pk:wlab/wlab_3_090", foot=[1, 1], block=False)            # банка с осадком

# Высоты спрайтов (px): до 96 мебель встаёт вплотную к северной стене, выше — на клетку от неё,
# иначе картинка залезает на стену (правило 1 мира: «ничего высокого вплотную под стеной снизу»).

# ------------------------------------------------------------ планировка: пол «m», вокруг — порода
for x0, y0, x1, y1 in (
        (12, 2, 29, 9),        # шлюз
        (20, 10, 21, 10),      # дверной проём шлюз → атриум
        (9, 11, 33, 20),       # атриум-склад
        (2, 12, 7, 18),        # кабинет смотрителя
        (8, 15, 8, 16),        # дверь кабинета
        (35, 11, 36, 23),      # коридор жилого блока
        (34, 15, 34, 16),      # дверь в коридор из атриума
        (38, 11, 44, 16),      # каюта семьи
        (37, 13, 37, 14),      # дверь каюты семьи
        (38, 18, 44, 23),      # каюта после крысолюдов
        (37, 20, 37, 21),      # дверь второй каюты
        (20, 21, 21, 21),      # проём атриум → спуск
        (19, 22, 22, 26),      # спуск к ярусу Б — лестница в две клетки
        (20, 27, 21, 27),      # створ гермодвери — единственный проход в коридор Б
        (6, 28, 42, 31),       # коридор Б
        (4, 33, 19, 41),       # лаборатория «Панцирь»
        (11, 32, 12, 32),      # дверь лаборатории
        (22, 33, 27, 37),      # тупик с турелью
        (24, 32, 25, 32),      # дверь тупика
        (30, 33, 38, 40),      # архив
        (33, 32, 34, 32),      # дверь архива
        (40, 33, 46, 38),      # кабинет Кросса
        (41, 32, 42, 32),      # дверь кабинета Кросса
):
    v.paint(FLOOR, x0, y0, x1, y1)


# ------------------------------------------------------------ помощники ручной расстановки
def vwhy(name, x, y, blocked=None, soft=None, reserved=None):
    """Почему предмет не встал — как why_not() в build_town.py."""
    foot = v.footprint(name, x, y)
    blocked = v.blocked if blocked is None else blocked
    soft = v.soft_obj if soft is None else soft
    reserved = v.reserved if reserved is None else reserved
    why = []
    if any(t in blocked for t in foot):
        why.append("блок: " + str([t for t in foot if t in blocked]))
    if any(t in soft for t in foot):
        why.append("мягкий предмет: " + str([t for t in foot if t in soft]))
    if any(t in reserved for t in foot):
        why.append("резерв")
    h = v.hides(name, x, y)
    if h:
        why.append(f"заслоняет {h[0]} ({h[1]}, {h[2]})")
    why.append("пол: " + "".join(v.ground[yy][xx] for xx, yy in foot))
    return f"«{name}» не встал в ({x}, {y}): " + "; ".join(why)


WALL_ART = []                     # что повесили на стену: tidy_lamps() молча снимает настенное у проёма


def _undone(snap):
    n_props, n_conts, blocked, soft_obj, reserved = snap
    del v.props[n_props:], v.containers[n_conts:]
    v.blocked, v.soft_obj, v.reserved = blocked, soft_obj, reserved
    v._reach = None


def vplace(name, x, y, **kw):
    """Явная расстановка: мебель — только на полу комнаты, встать обязана ровно туда, куда ставили."""
    foot = v.footprint(name, x, y)
    if any(v.ground[yy][xx] != FLOOR for xx, yy in foot):
        raise AssertionError(f"«{name}» в ({x}, {y}): не на полу — "
                             + " ".join(v.ground[yy][xx] for xx, yy in foot))
    snap = (len(v.props), len(v.containers), set(v.blocked), set(v.soft_obj), set(v.reserved))
    ok = v.put(name, x, y, **kw)
    if ok and v.props[-1][1:3] == [x, y]:
        return True
    why = vwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
    if v._reach is not None:
        lost = sorted(v.reachable() - v.reachable(v.footprint(name, x, y)))[:8]
        nears = sorted(t for t in lost for dx, dy in ((0, 0), (0, -1), (0, 1), (-1, 0), (1, 0))
                       if (t[0] + dx, t[1] + dy) in v.blocked)
        why += f"; проход: отрезало {lost}; блок рядом: {sorted(set(nears))}"
        why += "; " + str({p[0]: (p[1], p[2]) for p in v.props if p[1] >= 38 and p[2] >= 17 and p[1] <= 45 and p[2] <= 24})
    _undone(snap)
    raise AssertionError(why)


def vbox(name, x, y, title, loot, **kw):
    """Сюжетный ящик/сейф — как vplace(): не встал, так с причиной."""
    foot = v.footprint(name, x, y)
    if any(v.ground[yy][xx] != FLOOR for xx, yy in foot):
        raise AssertionError(f"«{name}» в ({x}, {y}): не на полу")
    snap = (len(v.props), len(v.containers), set(v.blocked), set(v.soft_obj), set(v.reserved))
    try:
        v.box(name, x, y, title, loot, **kw)
    except AssertionError:
        why = vwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
        _undone(snap)
        raise AssertionError(why) from None
    if v.props[-1][1:3] != [x, y]:
        moved = v.props[-1][1:3]
        _undone(snap)
        raise AssertionError(f"«{name}» уехал в {moved}")
    return True


def vskin(name, x, y):
    """Мелочь на полу (сумка, бумаги, носок): не блокирует, но и на стену не лезет."""
    if not v.put(name, x, y, check=False) or v.props[-1][1:3] != [x, y]:
        raise AssertionError(vwhy(name, x, y))


def vdecal(name, x, y):
    """Пятно, кабель, ступень — слой пола: никого не блокирует, под мебель не лезет."""
    if not v.put(name, x, y, check=False, allow_reserved=True) or v.props[-1][1:3] != [x, y]:
        raise AssertionError(vwhy(name, x, y))


def vwall(name, x, y, dx=0, dy=0):
    """Настенное — только на целой стене: клетка породы, под ней пол (это лицевая сторона стены).
    Над проёмом и над выработкой, где стены нет, — падает со счётом (logic.md §2)."""
    fw, fh = props_info.info(name)["foot"]
    cells = [(x + i, y + j) for i in range(fw) for j in range(fh)]
    for cx, cy in cells:
        assert v.ground[cy][cx] == WALL, f"«{name}» в ({x}, {y}): там не порода"
        assert v.ground[cy + 1][cx] == FLOOR, f"«{name}» в ({x}, {y}): под клеткой не пол — это не стена"
    rec = [name, x, y, dx, dy]
    v.props.append(rec)
    WALL_ART.append(rec)
    v.soft_obj.update(cells)          # на клетке стены ничего не ставим: лампа-плафон не ляжет на карту


def vtable(name, x, y, dx=0, dy=-34):
    """Мелочь на столешнице: на клетке мебели, поднята на её высоту и в глубину — не у переднего края
    (замечание автора 24.10), рисуется сразу после стола (6-й элемент — порядок отрисовки)."""
    assert (x, y) in v.blocked, f"«{name}» в ({x}, {y}): под ним нет стола"
    v.props.append([name, x, y, dx, dy, 1 - dy])


def vlamp(kind, x, y):
    """Лампа-торшер у стены: свет живёт в предмете (набор x_vd_stand_*), а не плоской плашкой на полу."""
    vplace(f"x_vd_stand_{kind}", x, y, check=False, allow_reserved=True)


# ================================================================ шлюз
# Дверь-шестерня в город, пост дежурной смены у западной стены, скамья ожидания у восточной, мешки с
# песком по сторонам двери: вход держали, пока не стало ясно, что держать нечего.
v.put("x_vault_gear", 19, 1, force=True)                       # дверь-шестерня изнутри
v.portal([(19, 2), (20, 2)], "ruins", (104, 77), "Пятнадцатая")
v.reserve(18, 3, 22, 6)                                        # площадка прибытия из города — свободна
vwall("x_vd_num57", 14, 1)                                     # трафарет «57» на стене
vwall("x_vault_sign", 22, 1)                                   # табличка Vault-Tec у самой двери
vwall("x_vd_map", 26, 1)                                       # схема убежища на стене
vplace("x_sandbags", 16, 3)                                    # мешки по сторонам двери
vplace("x_sandbags", 23, 3)
v.terminal(16, 2, "vault_door")                                # пульт двери у поста
vplace(V_LOCKERS, 12, 3)                                       # шкафчики дежурной смены
vplace(V_LOCKER, 12, 5)
vplace("x_fireext", 12, 7)
vplace(V_DESK, 14, 6)                                          # стол дежурного
vtable("x_radio", 14, 6)                                       # рация на столе
vplace("ws_chair_down", 14, 7)                                 # табурет опрокинут: уходили второпях
vskin("ws_papers", 15, 8)
vplace("bench_16", 27, 3)                                      # скамья ожидания у восточной стены
vskin("bag", 26, 5)                                            # брошенная сумка
vskin("sock", 26, 6)
vskin("pants", 27, 7)
for _y in (6, 7, 8):
    vdecal("x_vd_dragv", 21, _y)                               # следы волочения — внутрь, не к двери

# ================================================================ атриум-склад
# Город держит здесь воду и припасы: стеллажи вдоль северной стены, бочки и баки у западной, штабеля
# ящиков у восточной и южной, стол выдачи с журналом посередине западной половины, тележка с ящиками.
# Верстаков у южной стены нет: верстак с доской стоит спиной к стене, а у южной он смотрел бы в стену (замечание автора).
vwall("x_vd_plaque", 12, 10)                                   # сводка выдачи на простенке
vwall("x_vd_tally", 18, 10)                                    # меловые счёты дней на стене
vplace(V_RACK, 10, 11)
vplace(V_SHELF, 13, 11)
vplace(V_CRATES, 16, 11)
vplace(V_MILBOX, 24, 11)
vplace(V_SHELF, 27, 11)
vplace(V_RACK, 30, 11)
for _y, _b in ((13, "barrel_0"), (14, "barrel_5")):            # паллета бочек с водой у западной стены
    vplace(_b, 9, _y)
    vplace("barrel_12", 10, _y)
vplace("crate", 9, 18)
vplace("crate_open", 10, 18)
vplace("crate_b", 9, 19)
vplace(V_CRATES, 32, 13)                                       # штабеля у восточной стены
vplace(V_CRATES, 32, 14)
vplace(V_MILBOX, 32, 18)
vplace(V_CRATES, 32, 19)
vplace(V_TANKS, 14, 20)                                        # баки с водой
vplace(V_PILE, 17, 20)
vplace(V_CRATES, 28, 20)
vbox("locker_double", 33, 17, "шкафчик кладовой", {"бинт": 1, "антирадин": 1, "крышки": 12})
vplace(V_DESK, 16, 13)                                         # стол выдачи
vtable("ws_book_open", 16, 13, dx=2)                           # журнал выдачи
vtable("w_table_lamp", 17, 13, dx=-16)                         # лампа в глубине столешницы
vplace("chair_2", 16, 14)                                      # двое в очереди
vplace("chair_1", 17, 14)
vplace("x_cart", 25, 18)                                       # тележка с ящиками
# Середина склада не пустует: две паллеты под стенами проходов — западная (штабель ящиков и бочки) и
# восточная (штабель с консервами и армейский ящик). Проходы x=19..22 (на север и на юг) и y=15..16
# (к двери жилого блока) остаются свободными.
vplace(V_CRATES, 12, 17)                                       # штабель у западной паллеты
vplace(V_CRATES, 12, 18)
vplace(V_PILE, 28, 13)                                         # штабель с консервами на востоке
vplace(V_CRATES, 28, 14)
vplace(V_MILBOX, 28, 17)

# ================================================================ кабинет смотрителя
# Кросс сидит спиной к северной стене, лицом к двери из атриума: терминал перед ним, стул посетителя
# напротив, сейф за спиной в углу, картотеки и шкаф с папками у стен.
vwall("x_vd_plaque", 5, 11)                                    # портрет смотрителя на стене
vplace("filecab_2", 2, 12)                                     # картотеки у северной стены
vplace("filecab_3", 3, 12)
v.terminal(4, 13, "vault_upper")
vplace("ws_chair", 4, 14)                                      # стул посетителя перед терминалом
vplace(V_WARDROBE, 7, 13)                                      # шкаф с папками у восточной стены
vplace("chair_broken", 5, 17)                                  # второй стул опрокинут (стоячий спрайт читался «стул посреди комнаты»)
vskin("ws_papers", 3, 15)
vbox(V_SAFE, 2, 18, "сейф смотрителя", {"крышки": 35, "стимулятор": 1},
     requires={"flag": "vault_safe_open", "msg": "Сейф Кросса. Замок электронный — открывается с его терминала."})

# ================================================================ коридор жилого блока
# Две каюты напротив друг друга: семейная и та, из которой ушли. Коридор в две клетки — сам по себе
# проход (аудит считает такой коридор «проёмом»), поэтому мебели в нём нет: объявление на стене у входа
# и следы волочения на полу.
vwall("x_vd_sheet", 33, 10)                                    # сорванное объявление у входа в блок
vdecal("x_vd_dragh", 35, 19)                                   # что-то тащили к дальней каюте

# ================================================================ каюта семьи
# Жили семьями: двухъярусная койка у северной стены, вторая койка в углу, стол с лампой и котелком,
# детский рисунок кнопками на стене, мелки на полу.
vwall("x_vd_drawing", 40, 10)                                  # детский рисунок: «все дома»
vplace(V_BUNK, 38, 11)
vplace(V_WARDROBE, 42, 11)
vplace(V_LOCKER, 44, 11)
vplace("w_rug_quilt", 38, 12)                                  # лоскутный коврик перед койкой
vplace(V_TABLE, 41, 13)
vtable("w_table_lamp", 41, 13, dx=2)
vtable("canteen", 42, 13, dx=-12)
vplace("stool_1", 41, 14)
vplace("stool_2", 42, 14)
vplace(V_BED, 38, 15)
vskin("ws_crayons", 40, 16)
vskin("sock", 43, 16)

# ================================================================ каюта после крысолюдов
# Матрас утащили, стол перевернули, шкафчик вскрыт; в углу южной стены — вентиляционная решётка, из
# которой в убежище и лезут радтараканы.
vplace("bed_frame", 38, 19)
vplace(V_LOCKER, 44, 19)
vplace("table_upside", 41, 21)
vplace(V_GRILLE, 43, 23)
vplace("crate_open", 44, 21)
vplace("pile_rags", 40, 22)
vskin("rag", 42, 22)
vskin("cloth_bit", 43, 21)
vskin("sock", 39, 21)
vdecal("x_vd_blood0", 41, 20)

# ================================================================ спуск к ярусу Б
# Лестница в две клетки вниз, по её сторонам — стояки-перила; знак напряжения на входе, электрощит у
# створа. Гермодверь стоит в стене (прорублена только створ 20..21) — обойти её нельзя, это единственный
# проход в коридор Б. Свет красный: нижний ярус на аварийном питании.
for _y in (23, 24, 25, 26):
    for _x in (20, 21):
        vdecal("x_vd_steps", _x, _y)                           # ступени: 2 в ширину, 4 вниз
for _x, _y in ((19, 24), (19, 25), (22, 24), (22, 25)):
    vplace("x_pipe", _x, _y)                                   # стояки по сторонам лестницы
vplace(WARN_U, 19, 22)                                         # знак напряжения на входе на спуск
vplace(V_PANEL, 19, 26)                                        # электрощит у гермодвери
vplace("x_vault_gear", 20, 27, check=False)                    # гермодверь яруса Б: закрыта, пока не откроют
# Пропуск прохода проверяется ниже через v.check(passable=...) — на сборке створ ещё «стена».
# Ссылку на гермодверь держим объектом, а не индексом: tidy_lamps() убирает лампы из props, и индексы
# сдвигаются — с «len(props)-1» гермодверью в JSON оказывался пульт (падал tests/test_quests.py).
GATE = v.props[-1]
v.terminal(22, 26, "vault_gate")                               # пульт гермодвери рядом
v.pickups.append(["патроны", 4, 20, 23])

# ================================================================ коридор Б
# Длинный коридор нижнего яруса: шкафчики и штабеля у северной стены, тележка посреди, кровь ведёт к
# лаборатории, гильзы — к тупику с турелью.
vwall("x_vd_plaque", 14, 27)                                   # указатель яруса на стене
vwall("x_vd_sheet", 32, 27)                                    # сорванное объявление
vwall("x_vd_exit", 23, 27)                                     # «ВЫХОД» над гермодверью, со стороны коридора
vplace(V_LOCKERS, 9, 28)
vplace(V_LOCKER, 12, 28)
vplace(V_LOCKERS, 24, 28)
vplace(V_CRATES, 27, 28)
vplace(V_SHELF, 31, 28)
vplace(V_MILBOX, 35, 28)
vplace("crate", 7, 31)
vplace(V_PILE, 16, 31)
vplace(V_MILBOX, 29, 31)                                       # армейский ящик — не вторая такая же гора консервов
vplace(V_CRATES, 37, 31)
vplace("x_cart", 14, 29)                                       # тележка с ящиками
vdecal("x_vd_blood0", 11, 30)                                  # кровь у тележки — и след волоком к лаборатории,
vdecal("x_vd_dragh", 12, 30)                                   # а не три одинаковых пятна в ряд
vdecal("x_vd_caps", 23, 30)                                    # гильзы у двери тупика — россыпью, не по углам квадрата
vdecal("x_vd_caps", 24, 32)
for _x in (23, 24, 25):
    vdecal("x_vd_cab_h", _x, 31)                               # кабель по южной стене
vdecal("x_vd_sparks", 40, 28)                                  # сорванная лампа искрит
vdecal("x_vd_blood0", 34, 29)

# ================================================================ лаборатория «Проекта Панцирь»
# Холодильник с сывороткой и полка реактивов у северной стены, два стола с приборами (по одному прибору —
# раковина за столом и три вещи на столешнице читались кашей, замечание автора), терминал
# смотрителя яруса, койки вдоль западной стены, капсулы с сывороткой — вдоль южной.
# Капсулы — самое высокое на карте (142 px), поэтому стоят у южной стены: у северной они залезли бы
# на стену и в коридор над лабораторией (правило 1).
vbox(V_GLASS, 4, 33, "холодильник с сывороткой", {"сыворотка «Панцирь»": 2, "антирадин": 1})
vplace(V_BOTTLES, 7, 34)                                       # полка реактивов — сама по себе, без пробирок сверху
vplace(V_LAB, 10, 34)
vtable(V_MICRO, 10, 34, dx=10, dy=-40)                        # на первом столе — только микроскоп
vplace(V_LAB_B, 13, 34)
vtable(V_VIAL, 13, 34, dx=14, dy=-40)                         # на втором — штатив с пробирками
vplace(V_DOCS, 16, 34)
v.terminal(4, 35, "vault_lab")
vplace(V_CHAIR, 4, 36)
vplace(V_RACK, 18, 37)                                         # стеллаж к восточной стене
vplace(V_BED, 4, 38)
vplace(V_NIGHT, 4, 39)
vtable("cl_medbox", 4, 39, dy=-36)                             # аптечка на тумбочке
vplace(V_BED, 4, 40)
vplace(V_CAPSULE, 7, 41)
vplace(V_CAPSULE_B, 11, 41)
vplace(V_CAPSULE, 15, 41)
vplace("x_barrel_boom", 18, 41)                                # взрывная бочка у южной стены
vplace(V_CAN, 17, 35)                                          # канистра у стеллажа, не за ним
vskin("ws_papers", 6, 36)
vskin("ws_papers", 12, 39)
vdecal("x_vd_blood0", 8, 37)                                   # пятна у коек
vdecal("x_vd_wet0", 13, 40)

# ================================================================ тупик с турелью
# Турель смотрит в дверь из коридора: мешки с песком полукругом, ящик с патронами за спиной, гильзы.
vplace(WARN_U, 27, 33)                                         # знак у входа
vbox("ammo_box", 22, 33, "ящик с патронами", {"патроны": 12, "граната": 1})
vplace("x_sandbags", 22, 36)
vplace("x_sandbags", 25, 36)
vdecal("x_vd_caps", 24, 33)
vdecal("x_vd_caps", 26, 35)
vdecal("x_vd_blood0", 23, 37)

# ================================================================ архив
# Картотеки у северной стены, стеллаж папок у восточной, стол для чтения, коробки с документами.
vwall("x_vd_nine", 31, 32)                                     # «доска девяти» над терминалом
v.terminal(31, 34, "vault_overseer")                           # терминал смотрителя
vbox("filecab_4", 34, 34, "шкаф с журналами", {"журнал «Проект Панцирь»": 1, "крышки": 15})
vplace("filecab_3", 35, 34)
vplace("filecab_2", 36, 34)
vplace("filecab_1", 37, 34)
vplace(V_RACK, 37, 36)
vplace(V_TABLE, 32, 37)
vtable("ws_book_open", 32, 37, dx=-4)
vtable("w_table_lamp", 33, 37, dy=-40)                        # лампа над книгой, на второй половине стола — не на мониторе терминала
vplace("chair_2", 32, 38)
vplace("cardboard", 30, 40)
vplace("crate_b", 31, 40)
vplace("pile_electronics", 30, 38)
vskin("ws_papers", 34, 38)
vskin("ws_papers", 35, 39)

# ================================================================ кабинет Кросса
# Стол с мониторами, стул смотрителя, пульт у стены, ряд серверных стоек и шкафчик охраны. Кросс
# закрыл ворота 23.10.2077 и остался на своём ярусе: кровь у стула — всё, что от него осталось.
# «Доска девяти» — в архиве, над терминалом: на стене кабинета её закрывал пульт (картинка пульта
# 76 px — это два ряда, она заслоняла доску).
vplace(V_CONSOLE, 44, 33)                                      # пульт яруса
vplace(V_DESK_MON, 42, 34)                                     # стол с мониторами
vtable("w_table_lamp", 42, 34, dx=2)
vtable("canteen", 43, 34, dx=-16)                              # графин
vplace(V_CHAIR, 42, 35)
vplace(V_SERVER_ROW, 44, 36)
vplace(V_SERVER, 46, 35)
vbox("locker_4", 46, 33, "шкафчик охраны", {"стимулятор": 1, "патроны": 8, "граната": 1})
vplace("filecab_2", 40, 33)                                    # картотека у северной стены
vplace("pile_scrap", 40, 38)                                   # у Кросса — металлолом, не копия кучи из архива
vskin("ws_papers", 41, 37)
vdecal("x_vd_blood0", 41, 36)

# ================================================================ враги
# Ярус — на 2–3 уровне: тараканы в каютах и коридоре, гуль в лаборатории, бегун в архиве, турель
# в тупике (её обходят или снимают из-за угла).
v.enemies += [["radroach", 40, 21], ["radroach", 43, 22], ["radroach", 16, 29],
              ["turret", 24, 35], ["feral", 8, 38], ["ghoul_runner", 34, 37]]

# ================================================================ атмосфера
# Ярус А — тусклый жёлтый (аварийное питание города), ярус Б — красный и мёртвая зелень лаборатории.
for _x, _y in ((13, 9), (28, 8), (12, 16), (24, 16), (31, 16), (6, 16), (36, 13), (36, 20), (44, 14)):
    vlamp("amber", _x, _y)
for _x, _y in ((22, 23), (8, 29), (18, 29), (33, 29), (41, 29), (6, 39), (9, 36)):
    vlamp("red", _x, _y)
for _x, _y in ((15, 38), (30, 36)):
    vlamp("green", _x, _y)

v.check(npc_enemy_gap=0, passable=v.footprint(*GATE))
tidy_lamps(v)
gate_prop = next(i for i, q in enumerate(v.props) if q is GATE)   # после tidy_lamps: индексы могли сдвинуться
assert v.props[gate_prop][0] == "x_vault_gear", v.props[gate_prop]
lost = [r for r in WALL_ART if r not in v.props]                  # настенное у проёма tidy_lamps снимает молча
assert not lost, "снято настенное: " + str([(r[0], r[1], r[2]) for r in lost])
v.save("data/maps/vault57.json", style="vault", dark=140, night=[96, 92, 88], lights=getattr(v, "lights", []),   # верхний ярус город освещает
       gates=[{"prop": gate_prop, "flag": "vault_b_open", "key": "ключ-карта Б",
               "msg": "Гермодверь яруса Б. Табло: «ДОПУСК: СМОТРИТЕЛЬ». Нужна ключ-карта — или терминал рядом."}])
print(f"Убежище 57: объектов {len(v.props)}, врагов {len(v.enemies)}, контейнеров {len(v.containers)}")


# ================================================================ Ливнёвка
# Тоннели под Пятнадцатой (docs/furnish/fifteen.md §13). Подземелье: ×1.56 из docs/furnish_guide.md к нему
# не применяется, клетка та же, что у интерьеров. Было 50×28 (440 проходимых клеток, 51 объект, плотность
# 11.6): в главном тоннеле 4 предмета, отвод и решётка пустые, логово — 187 клеток с 11 предметами без
# смысла, затопленная камера — 70 клеток с ящиком и лужами. Стало 60×31; зоны разобраны по назначению:
# колодец → главный коллектор (два ходовых ряда, средний — вода) → спуск ступенями → нижний тоннель →
# логово; добавлены дежурка ремонтников и устье с решёткой, отвод закрыт завалом. Всё поштучно
# (dplace, dbox, dskin, ddecal, dwall, dtable, dlamp) — автообстановки у MapKit нет.
DW, DH = 60, 31
d = MapKit(DW, DH, start=(3, 4), seed=15, fill="x")
FLOOR_D, WALL_D = "w", "x"        # w — мокрый бетон ливнёвки (src/townmap.py: _drain_floor), x — порода

for x0, y0, x1, y1 in (
        (2, 2, 8, 8),        # колодец под люком: площадка под лестницей
        (9, 4, 46, 6),       # главный коллектор
        (12, 7, 15, 11),     # боковой рукав культистов (тупик в четыре клетки)
        (22, 7, 24, 13),     # спуск к нижнему тоннелю — ступени
        (32, 8, 40, 12),     # дежурка ремонтников
        (36, 7, 37, 7),      # дверь дежурки
        (10, 14, 40, 16),    # нижний тоннель
        (8, 13, 11, 17),     # отвод: камера, заваленная с запада
        (15, 17, 16, 18),    # проход в затопленную камеру
        (12, 19, 20, 26),    # затопленная камера с насосом
        (42, 3, 46, 7),      # восточный конец коллектора: обвал в широкой камере
        (36, 17, 40, 17),    # брешь из тоннеля в логово
        (36, 18, 54, 29),    # логово крысолюдов
        (55, 22, 57, 24),    # устье с решёткой: отсюда лезут в город
):
    room(d, FLOOR_D, x0, y0, x1, y1)


# ------------------------------------------------------------ помощники ручной расстановки
def dwhy(name, x, y, blocked=None, soft=None, reserved=None):
    """Почему предмет не встал — как why_not() в build_town.py."""
    foot = d.footprint(name, x, y)
    blocked = d.blocked if blocked is None else blocked
    soft = d.soft_obj if soft is None else soft
    reserved = d.reserved if reserved is None else reserved
    why = []
    if any(t in blocked for t in foot):
        why.append("блок: " + str([t for t in foot if t in blocked]))
    if any(t in soft for t in foot):
        why.append("мягкий предмет: " + str([t for t in foot if t in soft]))
    if any(t in reserved for t in foot):
        why.append("резерв")
    h = d.hides(name, x, y)
    if h:
        why.append(f"заслоняет {h[0]} ({h[1]}, {h[2]})")
    why.append("пол: " + "".join(d.ground[yy][xx] for xx, yy in foot))
    return f"«{name}» не встал в ({x}, {y}): " + "; ".join(why)


def _dundone(snap):
    n_props, n_conts, blocked, soft_obj, reserved = snap
    del d.props[n_props:], d.containers[n_conts:]
    d.blocked, d.soft_obj, d.reserved = blocked, soft_obj, reserved
    d._reach = None


DRAIN_WALL_ART = []


def dplace(name, x, y, **kw):
    """Явная расстановка: мебель — только на полу ливнёвки, встать обязана ровно туда, куда ставили."""
    foot = d.footprint(name, x, y)
    if any(d.ground[yy][xx] != FLOOR_D for xx, yy in foot):
        raise AssertionError(f"«{name}» в ({x}, {y}): не на полу — "
                             + " ".join(d.ground[yy][xx] for xx, yy in foot))
    snap = (len(d.props), len(d.containers), set(d.blocked), set(d.soft_obj), set(d.reserved))
    ok = d.put(name, x, y, **kw)
    if ok and d.props[-1][1:3] == [x, y]:
        return True
    why = dwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
    if d._reach is not None:
        lost = sorted(d.reachable() - d.reachable(d.footprint(name, x, y)))[:8]
        why += f"; проход: отрезало {lost}"
    _dundone(snap)
    raise AssertionError(why)


def dbox(name, x, y, title, loot, **kw):
    """Сюжетный ящик/сумка — как dplace(): не встал, так с причиной."""
    foot = d.footprint(name, x, y)
    if any(d.ground[yy][xx] != FLOOR_D for xx, yy in foot):
        raise AssertionError(f"«{name}» в ({x}, {y}): не на полу")
    snap = (len(d.props), len(d.containers), set(d.blocked), set(d.soft_obj), set(d.reserved))
    try:
        d.box(name, x, y, title, loot, **kw)
    except AssertionError:
        why = dwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
        _dundone(snap)
        raise AssertionError(why) from None
    if d.props[-1][1:3] != [x, y]:
        moved = d.props[-1][1:3]
        _dundone(snap)
        raise AssertionError(f"«{name}» уехал в {moved}")
    return True


def dskin(name, x, y):
    """Мелочь на полу (тряпка, кость, фонарь): не блокирует, но и на стену не лезет."""
    if not d.put(name, x, y, check=False) or d.props[-1][1:3] != [x, y]:
        raise AssertionError(dwhy(name, x, y))


def ddecal(name, x, y):
    """Слой пола: ступени, лужа, кабель — никого не блокирует, под мебель не лезет."""
    if not d.put(name, x, y, check=False, allow_reserved=True) or d.props[-1][1:3] != [x, y]:
        raise AssertionError(dwhy(name, x, y))


def dwall(name, x, y, dx=0, dy=0):
    """Настенное — только на целой стене: клетка породы, под ней пол. Под проёмом падает со счётом."""
    fw, fh = props_info.info(name)["foot"]
    cells = [(x + i, y + j) for i in range(fw) for j in range(fh)]
    for cx, cy in cells:
        assert d.ground[cy][cx] == WALL_D, f"«{name}» в ({x}, {y}): там не порода"
        assert d.ground[cy + 1][cx] == FLOOR_D, f"«{name}» в ({x}, {y}): под клеткой не пол — это не стена"
    rec = [name, x, y, dx, dy]
    d.props.append(rec)
    DRAIN_WALL_ART.append(rec)
    d.soft_obj.update(cells)


def dtable(name, x, y, dx=0, dy=-40):
    """Мелочь на столешнице: на клетке мебели, поднята на её высоту, в глубину — не у переднего края."""
    assert (x, y) in d.blocked, f"«{name}» в ({x}, {y}): под ним нет стола"
    d.props.append([name, x, y, dx, dy, 1 - dy])


def dlamp(kind, x, y):
    """Свет в ливнёвке — то, что сюда принесли: фонари бригады в коллекторе и тоннелях, костры в бочках у
    крысолюдов. Торшеры из убежища здесь были бы абсурдом (замечание автора 24.10)."""
    name = {"amber": "lantern_lit", "green": "lantern_lit", "red": "x_fire_barrel"}[kind]
    dplace(name, x, y, allow_reserved=True)


# ------------------------------------------------------------ колодец под люком
# Лестница к люку во всю стену (dy=-18), площадка под ней пустая: вылез — и сразу видно коллектор.
# Ведро, брошенный ящик с инструментом и фонарь: сюда спускалась бригада, а уходила уже не она.
d.props.append(["x_ladder_wall", 3, 2, 0, -18])
d.portal([(3, 2)], "ruins", (13, 78), "Пятнадцатая")
d.reserve(2, 3, 5, 6)                                  # площадка прибытия из города — свободна
dwall("x_vd_waterline", 7, 1)                          # отметка уровня воды на стене колодца
dwall("x_vd_tally", 5, 1)                              # меловые счёты дней: бригада ждала, пока вода сойдёт
dplace("bucket", 7, 2)
dplace("toolbox_red", 7, 6)                            # ящик с инструментом брошен у стены
dplace("sack", 2, 7)                                   # мешок песка против воды
dskin("lantern_lit", 4, 7)                             # единственный свет: фонарь забыли
dskin("rag", 6, 7)
dskin("cloth_bit", 5, 8)
ddecal("x_puddle", 6, 4)
ddecal("x_vd_drip", 4, 2)

# ------------------------------------------------------------ главный коллектор
# Три ряда: два ходовых вдоль стен, средний — вода. Трубы вдоль северной стены, мусор, принесённый водой,
# у обеих стен; восточный конец — широкая камера, где рухнул свод: дальше хода нет, вода уходит вниз
# по ступеням (x=22..24).
for _x in (10, 30, 39):
    dplace("x_pipe", _x, 4)                            # трубы вдоль северной стены
dplace("planks", 12, 4)                                # доски, принесённые водой
dplace("pile_scrap", 15, 4)
dplace("barrel_lying_a", 18, 4)
dskin("log", 21, 4)
dplace("metal_sheets", 24, 4)
dskin("x_wire_coil", 27, 4)
dplace("metal_sheets_b", 32, 4)
dplace("planks", 35, 4)
dplace("rubble_a", 41, 4)
dplace("pile_bottles", 10, 6)                          # мусор у южной стены
dplace("sack", 14, 6)
dplace("cardboard", 16, 6)
dplace("firewood", 19, 6)
dplace("crate", 28, 6)
dplace("barrel_wood", 40, 6)
dplace("pile_cans", 42, 6)
dplace("barrel_0", 44, 4)                              # камера обвала: бочка, ящик, плиты
dplace("crate_broken", 44, 6)
dplace("rubble_a", 45, 3)                              # свод рухнул: дальше хода нет
dplace("concrete_block", 45, 4)
dplace("rubble_b", 45, 5, check=False)                 # завал ставится целиком: промежуточный расчёт
dplace("metal_sheets", 45, 6, check=False)             # «отрезал проход» не должен срабатывать на половине
dplace("planks", 45, 7, check=False)                   # стены завала — к концу они закрыты все
ddecal("x_vd_wet0", 11, 5)                             # вода в среднем ряду
ddecal("x_puddle", 17, 5)
ddecal("x_puddle", 26, 5)
ddecal("x_vd_cab_h", 19, 4)                            # кабель по стене
ddecal("x_vd_cab_h", 20, 4)
ddecal("x_vd_drip", 12, 5)

# ------------------------------------------------------------ боковой рукав: следы культистов
# Тупик в четыре клетки: сумку обронили, таща деда; рядом листовка, огарок свечи и отпечатки сапог на иле.
dbox("bag", 14, 10, "сумка культиста", {"листовка Единства": 1, "крышки": 12})
dskin("w_newspaper", 12, 10)                           # брошенная листовка
dskin("candles", 14, 11)                               # огарок: здесь стояли
dskin("cloth_bit_b", 15, 10)
ddecal("x_vd_steps", 12, 8)                            # отпечатки сапог ведут вглубь
ddecal("x_vd_steps", 14, 8)
ddecal("x_vd_steps", 13, 9)

# ------------------------------------------------------------ спуск к нижнему тоннелю
# Ступени в три клетки шириной, на верхней кромке — жёлто-чёрная разметка: тут можно оступиться.
for _y in range(8, 14):
    for _x in (22, 23, 24):
        ddecal("x_vd_steps", _x, _y)
for _x in (22, 23, 24):
    ddecal("x_vd_hz_h", _x, 7)

# ------------------------------------------------------------ дежурка ремонтников
# Маленькая камера обслуживания: верстак с доской инструмента, шкафчики, стол с лампой, раковина.
# Дежурный не вышел: меловые счёты дней — на стене колодца (на северной стене дежурки вешать нечего,
# ряд под ней считается проёмом), его кости в углу, кровь на полу, стул опрокинут, ящик открыт.
dplace(V_BENCH, 32, 8)                                 # верстак у северной стены
dplace(V_LOCKERS, 39, 8)                               # шкафчики смены
dplace(V_SINK, 40, 9)
dplace(V_TABLE, 34, 10)                                # стол дежурного
dtable("w_table_lamp", 34, 10, dx=2)                   # лампа в глубине столешницы
dtable("canteen", 35, 10, dx=-10)                      # кружка
dplace("w_chair_r", 33, 10)                            # стул с торца, лицом к столу
dplace("chair_broken", 36, 11)                         # опрокинутый стул
dplace("toolbox_open", 32, 11)                         # ящик открыт, инструмент разбросан
dplace("bucket", 38, 10)
dskin("rag", 37, 9)
dskin("r_bones", 37, 11)                               # то, что осталось от дежурного
ddecal("x_vd_blood0", 37, 10)
ddecal("x_vd_caps", 32, 10)                            # гильза: он стрелял

# ------------------------------------------------------------ нижний тоннель
# Три ряда под дежуркой: канистры и ящики у стен, кровь и следы волочения ведут к бреши в логово.
for _x, _y in ((12, 14), (26, 14)):
    dplace("x_pipe", _x, _y)
dplace("barrel_0", 15, 14)
dplace("crate", 18, 14)
dplace("pile_scrap", 27, 14)
dplace("sack", 31, 14)
dplace("planks", 34, 14)
dplace("barrel_wood", 38, 14)
dplace("pile_bottles", 11, 16)
dplace("cardboard", 18, 16)
dplace("crate_small", 21, 16)
dplace("firewood", 28, 16)
dplace("junk_small_1", 34, 16)
ddecal("x_puddle", 13, 15)
ddecal("x_puddle", 29, 15)
for _x in (35, 36):
    ddecal("x_vd_dragh", _x, 16)                       # что-то тащили в логово
ddecal("x_vd_dragh", 39, 17)
ddecal("x_vd_blood0", 34, 15)
ddecal("x_vd_cab_h", 17, 14)

# ------------------------------------------------------------ отвод: обвал
# Западная камера завалена досками, арматурой и плитами: дальше хода нет — только щель, куда не пролезть.
dplace("rubble_a", 8, 13)
dplace("planks", 8, 14)
dplace("rebar_fence", 8, 15)
dplace("metal_sheets", 8, 16)
dplace("rubble_b", 8, 17)
ddecal("x_puddle", 10, 15)

# ------------------------------------------------------------ затопленная камера
# Низкая точка ливнёвки: сюда стекает вода, здесь стоят ручной насос и баки, доски брошены мостками.
# В углу — ржавый ящик ремонтников: то, за чем сюда лезут.
dwall("x_vd_waterline", 13, 18)
dwall("x_vd_waterline", 19, 18)
dplace("w_pump", 13, 19)                               # насос у северной стены
dplace(V_TANKS, 17, 19)                                # баки: сюда качали воду
dplace("x_sandbags", 12, 22)                           # мешки, чтобы отвести поток
dplace("x_planks", 14, 23)                             # мостки из досок
dbox("metal_chest", 12, 25, "ржавый ящик", {"патроны": 6, "химикаты": 1, "коктейль Молотова": 1})
dplace("toolbox_open", 16, 25)
dplace("bucket", 19, 25)
dplace("planks", 16, 21)                               # доски, принесённые водой
dskin("rag", 18, 26)
ddecal("x_puddle", 14, 21)
ddecal("x_puddle", 17, 23)
ddecal("x_vd_wet1", 12, 21)
ddecal("x_vd_wet0", 17, 25)
ddecal("x_vd_drip", 16, 20)

# ------------------------------------------------------------ логово крысолюдов
# Гнёзда из тряпья и каркасов по стенам — по два-три предмета вместе, как их и натаскали; в середине
# кости и объедки у котла; у восточной стены — куча награбленного, в юго-восточном углу «трон» вожака:
# кресло, притащенное из города.
dplace("bed_frame", 37, 19)                            # гнездо в северо-западном углу
dplace("clothes_74", 39, 19)
dskin("cloth_bit", 38, 20)
dplace("pile_rags", 45, 18)                            # гнездо у северной стены
dplace("clothes_76", 47, 19)
dskin("cloth_bit_b", 46, 20)
dplace("pile_bags", 52, 18)                            # гнездо в северо-восточном углу
dplace("clothes_77", 53, 21)
dplace("clothes_75", 36, 23)                           # гнездо у западной стены
dplace("sofa_frame", 36, 26)
dplace("pile_cloth", 42, 28)                           # гнездо у южной стены
dskin("pants", 41, 27)
dskin("sock", 44, 27)
dbox("crate_open", 42, 19, "кормушка крысолюдов", {"ткань": 2, "лом": 1})   # у входа: сюда тащат объедки
d.containers[-1]["on_put"] = {"item": "отравленная приманка", "effects": [   # квест шерифа: отрава губит всю стаю
    {"type": "set_flag", "flag": "rats_poisoned"}, {"type": "kill_pack", "pack": "ratmen"}]}
dplace("r_bones", 45, 24)                              # кости и черепа у котла
dplace("r_bones", 40, 25)
dplace("x_cauldron", 47, 26)                           # украденный котёл
dskin("junk_small_2", 44, 26)
dplace("w_junk_pile", 50, 22)                          # куча награбленного у восточной стены
dplace("pile_junk", 52, 23)
dplace("backpack", 49, 23)                             # чей-то рюкзак
dskin("canteen", 49, 21)
dskin("plate", 51, 24)
dplace("w_armchair", 52, 27)                           # «трон» вожака
dplace("pile_scrap", 50, 28)
dskin("candles", 53, 26)                               # свечи, украденные из города
ddecal("x_puddle", 39, 23)
ddecal("x_vd_wet1", 46, 21)
ddecal("x_vd_blood0", 50, 26)
ddecal("x_vd_blood0", 41, 26)
ddecal("x_vd_dragh", 40, 18)                           # добычу тащили через брешь внутрь

# ------------------------------------------------------------ устье с решёткой
# Решётку не заварили: прутья выгнуты, за ними темнота — оттуда они и лезут в город. Лом брошен рядом.
for _y in (22, 23, 24):
    dplace("bar_fence_a", 57, _y)                      # три прута поперёк канала
d.pickups.append(["лом", 1, 56, 23])
ddecal("x_puddle", 56, 22)

# ------------------------------------------------------------ враги
# Разведчик у бреши, крысолюд у кормушки, пара у «трона» с вожаком; крыса — в затопленной камере.
# Первый крысолюд — в засаде (data/squads.json): он сидит за гнездом у входа и выходит, когда герой
# проходит мимо. Бой идёт по частям: вход, середина зала, угол вожака.
d.enemies += [["ratman", 39, 22], ["ratman", 44, 21], ["ratman", 48, 27],
              ["ratman_boss", 51, 26], ["rat", 14, 22]]

# ------------------------------------------------------------ атмосфера
# Янтарные лампы в коллекторе и тоннеле, зелёная тина в затопленной камере, красный свет у логова.
dlamp("amber", 13, 6)
dlamp("amber", 37, 4)
dlamp("amber", 41, 6)
dlamp("amber", 13, 14)
dlamp("amber", 30, 16)
dlamp("green", 15, 19)
dlamp("green", 18, 23)
dlamp("red", 46, 27)
dlamp("red", 46, 22)                                  # костёр посреди логова, у куч — не на троне
dlamp("red", 36, 21)

# ------------------------------------------------------------ свет без предмета
# Ступени спуска, рукав культистов и устье — там лампу-торшер поставить некуда (это проход), а чёрные
# провалы вместо комнат на тёмной карте читаются как дыры. Пятно света без плашки: источник за кадром —
# лампа в своде, свет из люка наверху, отблеск улицы за решёткой.
DRAIN_LIGHTS = []


def dceil(x, y, r=150, color=(255, 190, 110), flick=0.03):
    DRAIN_LIGHTS.append([x * 48 + 24, y * 48 + 24, r, [int(c) for c in color], flick, "nh"])


dceil(23, 9, 150)                                     # свет из люка на верх ступеней
dceil(23, 12, 130, (255, 176, 96))
dceil(13, 10, 110, (255, 176, 96), 0.2)               # рукав: отсвет огарка на иле
dceil(56, 23, 130)                                    # устье: сюда пробивается улица

d.check(npc_enemy_gap=0)
tidy_lamps(d)
lost_wall = [r for r in DRAIN_WALL_ART if r not in d.props]     # настенное у проёма tidy_lamps снимает молча
assert not lost_wall, "снято настенное: " + str([(r[0], r[1], r[2]) for r in lost_wall])
d.save("data/maps/drain.json", style="drain", dark=195, night=[142, 152, 138],
       lights=DRAIN_LIGHTS + getattr(d, "lights", []))
print(f"Ливнёвка: объектов {len(d.props)}, врагов {len(d.enemies)}, контейнеров {len(d.containers)}")


# ================================================================ Склад «Бейкер-7»
# Военный склад Ф.Б. Марипоза под бункером на окраине Бейкера — финал главы: журнал отгрузки на
# посту связи открывает слайды baker_finale. Интерьер: ×1.56 из docs/furnish_guide.md к нему не
# относится, клетка та же, что у интерьеров; размеры комнат — по назначению, не по масштабу города.
#
# Было 36×26 (349 клеток пола, 54 объекта, плотность 0.155 на клетку, 15 контейнеров, ни одной
# лампы): площадка под лестницей 6×6 стояла пустой, коридор 18×2 — без единого предмета, караулка —
# три койки и шкафчики в ряд, «хранилище» — зал 16×14, в котором десять контейнеров лежали двумя
# линиями по пять, турель — на пустом полу, терминал — в углу между серверными стойками. Шлюза с
# постом охраны, оружейки, генераторной не было вовсе, а «следов» — ни одного пятна: склад выглядел
# как чистая коробка.
#
# Стало 44×30. Склад разобран по назначению, как он и был устроен:
#   шлюз 2..8 × 16..22 — площадка под лестницей с окраины (портал — сама лестница), мешки у двери;
#   коридор 9..16 × 19..20 — кабельный лоток, гильзы, следы волочения к лестнице;
#   караулка 10..16 × 12..17 — пост охраны у входа: стол дежурного, шкафчики, койка, схема складов;
#   главный зал 18..41 × 3..20 — стеллажные ряды y 3, 6, 9, 12, 15, сквозные проезды x 22..23 и 28..29;
#   «партия 7» — обнесённая решёткой клетка 30..41 × 3..9: десять контейнеров ВРЭ в два ряда, турель;
#   южнее зала, за глухой стеной: оружейка 19..26 × 22..27, пост связи 29..35 × 22..27,
#   генераторная 38..42 × 22..27.
# Враги те же (два охранных робота и турель), сюжетные контейнеры, терминал baker7_log и портал —
# на месте.
BW, BH = 44, 30
b = MapKit(BW, BH, start=(4, 18), seed=7, fill="x")
FLOOR_B, WALL_B = "m", "x"
FLOORS_B = ("m", "G")                    # стальной пол комнат и решётка в полу генераторной

for _x0, _y0, _x1, _y1 in (
        (2, 16, 8, 22),        # шлюз под лестницей
        (9, 19, 16, 20),       # коридор к залу
        (10, 12, 16, 17),      # караулка
        (13, 18, 14, 18),      # дверь караулки
        (17, 19, 17, 20),      # дверь в зал
        (18, 3, 41, 20),       # главный зал
        (19, 22, 26, 27),      # оружейка
        (22, 21, 23, 21),      # дверь оружейки
        (29, 22, 35, 27),      # пост связи
        (31, 21, 32, 21),      # дверь поста связи
        (38, 22, 42, 27),      # генераторная
        (40, 21, 41, 21),      # дверь генераторной
):
    b.paint(FLOOR_B, _x0, _y0, _x1, _y1)
b.paint("G", 39, 24, 41, 26)            # под генераторами — решётка, чтобы топливо уходило в поддон


# ------------------------------------------------------------ помощники ручной расстановки
def bwhy(name, x, y, blocked=None, soft=None, reserved=None):
    """Почему предмет не встал — как vwhy() для Убежища 57."""
    foot = b.footprint(name, x, y)
    blocked = b.blocked if blocked is None else blocked
    soft = b.soft_obj if soft is None else soft
    reserved = b.reserved if reserved is None else reserved
    why = []
    if any(t in blocked for t in foot):
        why.append("блок: " + str([t for t in foot if t in blocked]))
    if any(t in soft for t in foot):
        why.append("мягкий предмет: " + str([t for t in foot if t in soft]))
    if any(t in reserved for t in foot):
        why.append("резерв")
    h = b.hides(name, x, y)
    if h:
        why.append(f"заслоняет {h[0]} ({h[1]}, {h[2]})")
    why.append("пол: " + "".join(b.ground[yy][xx] for xx, yy in foot))
    return f"«{name}» не встал в ({x}, {y}): " + "; ".join(why)


def _bundone(snap):
    n_props, n_conts, blocked, soft_obj, reserved = snap
    del b.props[n_props:], b.containers[n_conts:]
    b.blocked, b.soft_obj, b.reserved = blocked, soft_obj, reserved
    b._reach = None


B_WALL_ART = []


def bplace(name, x, y, **kw):
    """Явная расстановка: мебель — только на полу склада, встать обязана ровно туда, куда ставили."""
    foot = b.footprint(name, x, y)
    if any(b.ground[yy][xx] not in FLOORS_B for xx, yy in foot):
        raise AssertionError(f"«{name}» в ({x}, {y}): не на полу — "
                             + " ".join(b.ground[yy][xx] for xx, yy in foot))
    snap = (len(b.props), len(b.containers), set(b.blocked), set(b.soft_obj), set(b.reserved))
    ok = b.put(name, x, y, **kw)
    if ok and b.props[-1][1:3] == [x, y]:
        return True
    why = bwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
    if b._reach is not None:
        lost = sorted(b.reachable() - b.reachable(b.footprint(name, x, y)))[:8]
        why += f"; проход: отрезало {lost}"
    _bundone(snap)
    raise AssertionError(why)


def bbox(name, x, y, title, loot, **kw):
    """Сюжетный ящик/контейнер — как bplace(): не встал, так с причиной."""
    foot = b.footprint(name, x, y)
    if any(b.ground[yy][xx] not in FLOORS_B for xx, yy in foot):
        raise AssertionError(f"«{name}» в ({x}, {y}): не на полу")
    snap = (len(b.props), len(b.containers), set(b.blocked), set(b.soft_obj), set(b.reserved))
    try:
        b.box(name, x, y, title, loot, **kw)
    except AssertionError:
        why = bwhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
        _bundone(snap)
        raise AssertionError(why) from None
    if b.props[-1][1:3] != [x, y]:
        moved = b.props[-1][1:3]
        _bundone(snap)
        raise AssertionError(f"«{name}» уехал в {moved}")
    return True


def bskin(name, x, y):
    """Мелочь на полу (сумка, бумаги, гильза): не блокирует, но и на стену не лезет."""
    if not b.put(name, x, y, check=False) or b.props[-1][1:3] != [x, y]:
        raise AssertionError(bwhy(name, x, y))


def bdecal(name, x, y):
    """Слой пола: кабель, лужа, след волочения — никого не блокирует, под мебель не лезет."""
    if not b.put(name, x, y, check=False, allow_reserved=True) or b.props[-1][1:3] != [x, y]:
        raise AssertionError(bwhy(name, x, y))


def bwall(name, x, y):
    """Настенное — только на целой стене: клетка породы, под ней пол (лицевая сторона стены)."""
    fw, fh = props_info.info(name)["foot"]
    cells = [(x + i, y + j) for i in range(fw) for j in range(fh)]
    for cx, cy in cells:
        assert b.ground[cy][cx] == WALL_B, f"«{name}» в ({x}, {y}): там не порода"
        assert b.ground[cy + 1][cx] in FLOORS_B, f"«{name}» в ({x}, {y}): под клеткой не пол — это не стена"
    rec = [name, x, y, 0, 0]
    b.props.append(rec)
    B_WALL_ART.append(rec)
    b.soft_obj.update(cells)


def btable(name, x, y, dx=0, dy=-34):
    """Мелочь на столешнице: на клетке мебели, поднята на её высоту и в глубину — не у переднего края."""
    assert (x, y) in b.blocked, f"«{name}» в ({x}, {y}): под ним нет стола"
    b.props.append([name, x, y, dx, dy, 1 - dy])


def blamp(kind, x, y):
    """Лампа-торшер у стены: свет живёт в предмете (x_vd_stand_*), а не плоской плашкой на полу."""
    bplace(f"x_vd_stand_{kind}", x, y, check=False, allow_reserved=True)


B_LIGHTS = []


def blight(x, y, r=180, color=(150, 190, 225), flick=0.04):
    """Потолочный светильник: пятно света, над ним движок повесит лампу на шнуре (src/townmap.py)."""
    B_LIGHTS.append([x * 48 + 24, y * 48 + 24, r, [int(c) for c in color], flick])


# ================================================================ шлюз
# Лестница с окраины (портал — её клетка, стрелка встаёт под ногами), на стене трафарет «7» и «ВЫХОД»,
# у двери в зал — мешки, которые ставили, когда казалось, что склад ещё можно держать. Стол приёмки
# брошен: журнал раскрыт, кружка, табурет отставлен. От двери к лестнице тянули тело — след волоком
# и кровь.
b.put("x_ladder", 4, 16, check=False)                            # лестница наверх, к бронедвери
b.portal([(4, 16)], "baker_outskirts", (97, 12), "Бейкер: окраина")
b.reserve(3, 17, 6, 20)                                          # площадка прибытия — свободна
bwall("x_vd_num7", 2, 15)                                        # трафарет «7» на бетоне
bwall("x_vd_exit", 6, 15)                                        # «ВЫХОД» над лестницей
bplace("vb_table", 2, 16)                                        # стол приёмки
btable("ws_book_open", 2, 16, dx=6)                              # раскрытый журнал посещений
bplace("stool_1", 2, 17)
bplace("crate_b", 7, 16)                                         # чей-то ящик, так и не поднятый наверх
bplace("r_sandbag_row", 7, 18)                                   # мешки у двери в зал
bplace("r_sandbag_row", 7, 21)
bplace("bench_16", 3, 22)                                        # лавка ожидания у южной стены
bplace("ar_water_barrel", 8, 22)                                 # бочка с водой у двери
bplace("x_fireext", 2, 22)
bskin("bag", 5, 21)                                              # брошенная сумка
bdecal("x_vd_dragh", 6, 19)                                      # тащили от двери к лестнице
bdecal("x_vd_dragh", 8, 19)
bdecal("x_vd_blood0", 7, 20)

# ================================================================ коридор
# Два метра в ширину, кабельный лоток по южной стене, на северной — меловые счёты смен: столько дней
# здесь ещё кто-то считал. Гильзы и кровь — у самой двери в зал.
for _x in (10, 11, 12):
    bdecal("x_vd_cab_h", _x, 20)                                 # лоток с кабелем
bdecal("x_vd_dragh", 10, 19)
bdecal("x_vd_dragh", 12, 19)
bdecal("x_vd_caps", 14, 20)
bdecal("x_vd_blood0", 15, 19)

# ================================================================ караулка
# Пост охраны у входа: стол дежурного лицом к двери, рация и раскрытый журнал на столе, шкафчики
# дежурного и смены у северной стены, койка у западной, схема складов и счёты — на стене.
# Уходили второпях: стул опрокинут, бумаги на полу, шкафчик дежурного распахнут.
bwall("x_vd_map", 12, 11)                                        # схема складов Б-7 на стене
bwall("x_vd_tally", 16, 11)                                      # счёты смен у шкафчиков
bbox("ar2_locker", 10, 12, "шкафчик охраны", {"стимулятор": 1, "патроны": 10, "граната": 1})
bbox(V_LOCKERS, 15, 12, "шкафчик сержанта", {"бинт": 2, "антирадин": 1, "автомат": 1, "патроны": 30})
bplace("ar2_desk", 11, 14)                                       # стол дежурного лицом к двери
btable("x_radio", 11, 14, dx=8)                                  # рация на столе
btable("ws_book_open", 13, 14, dx=-18)                           # журнал поста
bplace("chair_2", 11, 15)                                        # стулья дежурных — лицом к столу
bplace("chair_2", 13, 15)
bplace("chair_broken", 15, 16)                                  # третий опрокинут: уходили второпях
bplace(BUNK_U, 10, 17)                                           # койка дежурного у южной стены
bskin("ws_papers", 15, 13)

blamp("amber", 16, 17)                                           # тёплая лампа у койки

# ================================================================ главный зал
# Стеллажи рядами: пять рядов по y 3, 6, 9, 12, 15, между ними проходы в две клетки, сквозные
# проезды x 22..23 и x 28..29 — по ним возили ящики с приёмки. Ближе к северной стене — то, что
# осталось: ящики с патронами, армейские короба, пустые стеллажи (партию вывезли в марте 2077).
# У северной стены — только невысокое: стеллаж 111 px у стены залез бы картинкой на бетон.
for _x, _name in ((18, V_SHELF), (20, "cl_milbox"), (24, V_SHELF), (26, "mp_ammo")):
    bplace(_name, _x, 3)
for _x, _name in ((18, "cl_rack"), (20, V_RACK), (24, "ct_navy_crate"), (26, "cl_rack")):
    bplace(_name, _x, 6)
for _x, _name in ((18, V_SHELF), (20, "vb_milbox"), (24, "cl_rack"), (26, "sl_ammo")):
    bplace(_name, _x, 9)
for _x, _name in ((18, "cl_rack"), (20, V_SHELF), (24, V_RACK), (26, "cl_rack"),
                  (31, V_SHELF), (33, "cl_rack"), (35, V_RACK), (37, "cl_rack")):
    bplace(_name, _x, 12)
for _x, _name in ((18, V_RACK), (20, "cl_rack"), (24, "mp_ammo"), (26, V_SHELF),
                  (31, V_RACK), (33, V_SHELF), (35, "cl_rack"), (37, "cl_crates")):
    bplace(_name, _x, 15)
# приёмка в южном проезде: верстак у западной стены, тележка, ящики, поддон — то, что не успели разобрать
bplace(V_BENCH, 18, 17)
bplace("cl_crates", 24, 18)                                      # штабель ящиков, не дошедший до стеллажа (тележка с овощами — не армейский склад)
bplace("cl_crates", 26, 17)
bplace("crate_broken", 30, 18)                                   # разбитый ящик
bplace("by_pallet", 39, 18)
bdecal("x_vd_oil0", 34, 19)                                      # масло из тележки
bdecal("x_vd_rust0", 21, 18)

# ------------------------------------------------------------ «партия 7»
SEALED = {"flag": "never", "msg": "Пломба армии США: «ВРЭ. ПАРТИЯ 7». Вскрывать голыми руками — безумие."}
# Десять контейнеров ВРЭ в два ряда за решёткой: дальний ряд опломбирован, ближний вскрыт и пуст.
# Клетку обнесли ещё тогда, когда здесь стояли: решётка, красные лампы над рядами, турель в углу.
for _y in (3, 4, 7, 8, 9):
    bplace("bar_fence_a", 30, _y, check=False)                   # решётка поперёк проезда
for _x in range(31, 42):
    bplace("bar_fence_a", _x, 9, check=False)                    # южная сторона клетки
for _x in (31, 33, 35, 37, 39):
    bbox(VRE_U, _x, 3, "контейнер ВРЭ", {}, requires=SEALED)     # пломбы целы (SEALED — ниже)
for _x in (31, 33, 35, 37, 39):
    bbox(VRE_U, _x, 8, "пустой контейнер", {})                   # вскрыт и выпотрошен
bwall("x_vd_tally", 35, 2)                                       # счёты партии на бетоне
bwall("x_vd_sheet", 32, 2)                                       # сорванная опись у клетки
bplace(WARN_U, 29, 4)                                            # знак у калитки клетки
b.pickups.append(["лом", 1, 34, 7])                              # чем вскрывали ближний ряд — бросили тут же

# ================================================================ оружейка
# Пирамиды с оружием у северной стены — одна уже пустая, замки сняты; стол для чистки, патронные
# ящики, сейф в углу. Гильзы на полу: оружие здесь не только хранили.
bplace("w_gun_rack", 19, 22)                                     # пустая пирамида: оружие вынесли
bplace("by_gun_table", 23, 22)                                   # пирамида с винтовками (стойки с мечами — не армейский склад)
bplace("by_gun_table", 19, 24)                                   # уцелевшая пирамида у западной стены
bplace("by_gun_table", 24, 24)                                   # стол для чистки
bplace("chair_2", 24, 25)
bplace("sl_ammo", 19, 26)                                         # патронный ящик в юго-западном углу
bplace("mp_ammo", 23, 26)
bbox(V_SAFE, 26, 22, "сейф оружейки", {"патроны": 20, "стимулятор": 1, "граната": 1})   # сейф в углу
bskin("ws_papers", 22, 26)
bdecal("x_vd_caps", 22, 23)
bdecal("x_vd_caps", 23, 25)
bdecal("x_vd_blood0", 21, 25)
blamp("amber", 26, 27)

# ================================================================ пост связи
# Терминал с журналом отгрузки — то, за чем сюда пришли. Пульт яруса и серверная стойка у стены,
# стол с рацией, стул оператора опрокинут, кровь у стула: смену здесь и застали.
bwall("x_vd_map", 29, 21)
bplace(V_CONSOLE, 29, 22)                                        # пульт связи — у западной стены, с зазором до терминала
b.terminal(33, 22, "baker7_log")                                 # журнал отгрузки склада Б-7
bplace(SERVER_U, 35, 22)
bplace(V_DESK, 31, 24)                                           # стол оператора
btable("x_radio", 31, 24, dx=8)
btable("ws_book_open", 32, 24, dx=-20)
bplace("chair_2", 31, 25)
bplace("chair_broken", 33, 24)
bplace(V_SERVER_ROW, 34, 25)                                     # серверная стойка у восточной стены
bskin("ws_papers", 30, 26)
bskin("ws_papers", 33, 27)
bdecal("x_vd_blood0", 33, 23)
bdecal("x_vd_cab_h", 29, 27)
bdecal("x_vd_cab_h", 30, 27)

# ================================================================ генераторная
# Два дизель-генератора (основной и резервный) у северной стены, доска инструмента, щит, канистры и
# бочки с топливом, решётка в полу под поддон. Кабель сорван, искрит; масло растеклось к двери.
bplace("cl_generator", 38, 22)
bplace("by_generator", 41, 22)
bplace(V_BENCH, 38, 24)                                          # верстак механика у западной стены
bplace(V_PANEL, 42, 24)                                          # щит на восточной стене
bplace("barrel_0", 40, 26)
bplace(V_CAN, 39, 26)
bplace("x_fireext", 42, 27)
bplace(WARN_U, 38, 26)
bdecal("x_vd_oil0", 39, 25)
bdecal("x_vd_oil1", 41, 26)
bdecal("x_vd_sparks", 40, 23)                                    # сорванный кабель искрит
bdecal("x_vd_cab_h", 38, 25)

# ================================================================ враги
# Охранные роботы ещё держат склад: один ходит между стеллажами, второй — у поста связи, турель
# стоит в клетке «партии 7» и простреливает калитку.
b.enemies += [["robot_guard", 25, 10], ["robot_guard", 33, 17], ["turret", 41, 5]]

# ================================================================ свет
# Зал — холодный аварийный свет над проездами; «партия 7» — красный; оружейка и койка дежурного —
# тёплая лампа; генераторная — красная, с мерцанием. Пятен без источника нет.
blight(6, 19, 200, (150, 190, 225))                              # шлюз
blight(11, 19, 150, (150, 190, 225))
blight(15, 20, 140, (150, 190, 225))                             # коридор
blight(20, 10, 190, (150, 190, 225))                             # ряды, западная половина
blight(26, 13, 190, (150, 190, 225))
blight(23, 18, 200, (150, 190, 225))                             # южный проезд
blight(33, 10, 180, (150, 190, 225))                             # восточная половина
blight(36, 13, 180, (150, 190, 225))
blight(39, 17, 170, (150, 190, 225))
blight(34, 5, 170, (255, 90, 60), 0.12)                          # «партия 7», красный
blight(38, 6, 160, (255, 90, 60), 0.2)
blight(22, 24, 170, (255, 180, 90))                              # оружейка
blight(32, 23, 170, (170, 200, 230))                             # пост связи
blight(40, 24, 170, (255, 110, 60), 0.25)                        # генераторная

reached = b.check(npc_enemy_gap=0)
tidy_lamps(b)
lost = [r for r in B_WALL_ART if r not in b.props]                # настенное у проёма tidy_lamps снимает молча
assert not lost, "снято настенное: " + str([(r[0], r[1], r[2]) for r in lost])
b.save("data/maps/baker7.json", style="vault", dark=170, night=[76, 84, 96],
       floors={"m": STEEL, "G": GRILLE}, lights=B_LIGHTS + getattr(b, "lights", []))
print(f"Бейкер-7: {BW}×{BH}, объектов {len(b.props)}, обыскиваемых {len(b.containers)}, "
      f"врагов {len(b.enemies)}, проходимых {len(reached)}")
city.save()
city.save()
