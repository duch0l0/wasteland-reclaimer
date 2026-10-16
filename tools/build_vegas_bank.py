"""
«Последний банк Вегаса» — подвал Первого банка Мохаве под Стрипом. Отсюда Змеи таскают «новенькие» довоенные
крышки. Квест-ограбление: пройти охрану (взлом пульта, команда из двух специалистов или динамит) и решить,
что делать с хранилищем, — крышки обеспечены водой Хаба, и мешки из банка обесценят их по всей пустоши.

  vegas_bank   холл с пультом охраны (турель, роботы-охранники), бронедверь, хранилище с мешками крышек.

Запуск из папки game_project:  .venv/bin/python tools/build_vegas_bank.py
"""
import json

from citykit import City, CityMap

city = City("vegas_bank", "Последний банк Вегаса")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


GRILLE_B = cells("nbunk/p2", [(0, 12)])
COUNTER_B = P("bk_counter", "pk:lhotel/lhotel_1_012", foot=[4, 1])
PLANT_B = P("bk_plant", "pk:aoffice/aoffice_3_025")
CHAIR_W = P("bk_wait_chair", "pk:aoffice/aoffice_1_002")
SAFEBOX = P("bk_safebox", "pk:nbunk/nbunk_2_005", search="locker", title="депозитная ячейка")
SAFEBOX_B = P("bk_safebox_b", "pk:nbunk/nbunk_2_006", search="locker", title="депозитная ячейка")
CARPET_B = "pk:lhotel/p2/10,12,2,2"
VENT_B = P("bk_vent", "pk:nbunk/nbunk_2_021", foot=[1, 1], block=False)
SAFE = P("bk_safe", "pk:west/west_2_105")
DESK = P("bk_desk", "pk:lrest/lrest_1_061", foot=[2, 1])
CHAIR = P("bk_chair", "pk:west/west_2_001")
SERVER = P("bk_server", "pk:npower/npower_2_042")
CRATES = P("bk_crates", "pk:nbunk/nbunk_2_021", foot=[3, 1], sight=True)
BONES = P("bk_bones", "pk:grave/grave_2_022", block=False)
MARBLE = ["pk:lrest/p1/0,12,1,1"]
PLATES = cells("nbunk/p2", [(4, 8), (5, 9), (6, 10), (4, 10)])
VWALL = "pk:nbunk/nbunk_w3_17"

W, H = 40, 28
bk = CityMap(city, "vegas_bank", "Первый банк Мохаве: подвал", W, H, start=(6, 5), seed=231, interior=True, music="vats",
             night=[100, 100, 130])
bk.floor_code("M", *MARBLE)
bk.floor_code("F", *PLATES)
bk.floor_code("G", *GRILLE_B)
bk.wall_code("W", VWALL)
bk.room(1, 1, 26, 27, "W", "M")                       # холл: стойки кассиров, пульт охраны
bk.room(26, 1, 39, 27, "W", "F")                      # хранилище за бронедверью
bk.props.append(["x_ladder", 6, 4])
bk.portal([(6, 4)], "vegas_strip", (22, 37), "Наверх, на Стрип")
bk.reserve(4, 4, 9, 7)
for x in (8, 12, 16, 20):
    bk.put(DESK, x, 10)
    bk.put(CHAIR, x, 12)
bk.terminal(13, 18, "bank_security")
# операционный зал: красная дорожка от входа к стойкам, стойки кассиров с решётками, зона ожидания, колонны из шкафов
bk.stamp("bk_rug_a", CARPET_B, 10, 6, water=False)
bk.stamp("bk_rug_b", CARPET_B, 14, 14, water=False)
bk.stamp("bk_rug_c", CARPET_B, 6, 22, water=False)
bk.stamp("bk_rug_d", CARPET_B, 20, 20, water=False)
for x in (9, 13, 17, 21):
    bk.maybe(COUNTER_B, x - 2, 8)
for x, y in ((3, 14), (3, 18), (22, 14), (22, 18), (3, 24), (22, 24), (13, 22), (17, 22)):
    bk.maybe(CHAIR_W, x, y)
for x, y in ((3, 8), (24, 8), (3, 26), (24, 26), (12, 3), (18, 3)):
    bk.maybe(PLANT_B, x, y)
for x in range(4, 25, 4):
    bk.maybe(SAFEBOX if (x // 4) % 2 else SAFEBOX_B, x, 3)
bk.paint("G", 4, 24, 24, 24)                             # решётчатый стык в южной части зала — вентиляция подвала
for x, y in ((5, 20), (19, 22), (11, 25)):
    bk.put(BONES, x, y)
# бронедверь: открывается флагом (пульт охраны, команда или динамит)
bk.opening(26, 13, 26, 13, "F")
bk.gate("x_vault_gear0", 26, 13, "bank_vault_open", "Бронедверь хранилища. Замок — на пульте охраны. Или динамит.")
bk.reserve(25, 12, 28, 15)
for x, y in ((31, 4), (35, 4), (31, 22), (35, 22)):
    bk.put(CRATES, x, y)
bk.terminal(34, 13, "bank_vault")
# хранилище: ряды депозитных ячеек вдоль стен, стальные ящики, весы слитков, огнетушители
for y in (3, 6, 9, 17, 20, 23, 26):
    bk.maybe(SAFEBOX if y % 2 else SAFEBOX_B, 28, y)
    bk.maybe(SAFEBOX_B if y % 2 else SAFEBOX, 38, y)
for x, y in ((31, 9), (35, 9), (31, 17), (35, 17)):
    bk.maybe(CRATES, x, y)
for x, y in ((31, 26), (35, 26)):
    bk.maybe(SERVER, x, y)
# хранилище живёт: кабели, разметка к весам, разлитое масло, сброшенные слитки и бумаги, красная лампа над дверью, холодные плафоны
for x, y in ((29, 12), (30, 12), (31, 12)):
    bk.maybe("x_vd_hz_h", x, y, check=False)
for x in range(29, 38):
    bk.maybe("x_vd_cab_h", x, 15, check=False)
for x, y in ((33, 6), (36, 19), (30, 24), (34, 20)):
    bk.maybe("x_vd_oil0", x, y, check=False)
for x, y in ((32, 5), (36, 11), (31, 21)):
    bk.maybe("x_vd_blood0", x, y, check=False)
for x, y in ((33, 3), (37, 3), (30, 11), (35, 24), (36, 7)):
    bk.maybe("crate_broken" if x % 2 else "pile_scrap", x, y)
for x, y in ((29, 5), (37, 13), (29, 20)):
    bk.maybe("x_vd_stand_cold", x, y, check=False, allow_reserved=True)
bk.maybe("x_vd_stand_red", 27, 11, check=False, allow_reserved=True)
bk.maybe("x_vd_stand_red", 27, 15, check=False, allow_reserved=True)
bk.enemies += [["turret", 22, 6], ["robot_guard", 18, 16], ["robot_guard", 10, 22]]

city.save()
L = json.load(open("data/locations.json", encoding="utf-8"))
L["vegas_bank"].update({"name": "Первый банк Мохаве: подвал"})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
