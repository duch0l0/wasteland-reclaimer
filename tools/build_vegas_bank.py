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
             night=[60, 60, 80])
bk.floor_code("M", *MARBLE)
bk.floor_code("F", *PLATES)
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
for x, y in ((5, 20), (19, 22), (11, 25)):
    bk.put(BONES, x, y)
# бронедверь: открывается флагом (пульт охраны, команда или динамит)
bk.opening(26, 13, 26, 13, "F")
bk.gate("x_vault_gear0", 26, 13, "bank_vault_open", "Бронедверь хранилища. Замок — на пульте охраны. Или динамит.")
bk.reserve(25, 12, 28, 15)
for x, y in ((31, 4), (35, 4), (31, 22), (35, 22)):
    bk.put(CRATES, x, y)
bk.terminal(34, 13, "bank_vault")
bk.enemies += [["turret", 22, 6], ["robot_guard", 18, 16], ["robot_guard", 10, 22]]

city.save()
L = json.load(open("data/locations.json", encoding="utf-8"))
L["vegas_bank"].update({"name": "Первый банк Мохаве: подвал"})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
