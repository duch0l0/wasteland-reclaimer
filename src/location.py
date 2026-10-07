"""
Локация: карта + враги + NPC + контейнеры. Описания — в data/locations.json,
типы врагов — в data/enemies.json. Состояние локации (кто убит, что
подобрано и открыто) живёт в объекте, пока игра открыта.
"""
import json

import pygame

from . import settings as S
from . import loader
from .tilemap import TileMap, load_map_file
from .townmap import TownMap
from .entities import Enemy, NPC

NPC_NAMES = {"gena": "Ржавый Гена", "robot": "Почтальон-3000", "blondie": "Блонди", "loner": "Панк-одиночка",
             "turtle": "Черепан", "dog": "Рыжий пёс", "silas": "Брат Сайлас", "mo": "Мо «Ведро»", "lenny": "Лен",
             "marta": "Марта", "sheriff": "Шериф Брэддок", "doc": "Док Мира", "ada": "Смотрительница Ада",
             "dale": "Дейл", "rose": "Караванщица Роза", "dex": "Наёмник Дэкс",
             # Бейкер
             "anselm": "Брат Ансельм", "amos": "Дед Эймос", "amos_b7": "Дед Эймос", "iskra": "Искра",
             "iskra_out": "Искра", "nick": "Ник Грек", "tobias": "Брат Тобиас", "hattie": "Хэтти Мур",
             "hollis": "Холлис", "lira_baker": "Лира", "loner_baker": "Панк", "silas_baker": "Брат Сайлас",
             "scar_baker": "Шрам", "baker_folk_a": "Житель", "baker_folk_b": "Жительница",
             "baker_kid": "Мальчишка", "baker_folk_c": "Девушка", "baker_folk_d": "Старик",
             "baker_folk_e": "Караванщица",
             # случайные встречи
             "caravan_trader": "Бродячий торговец", "caravan_guard": "Охранник каравана",
             "farmer_miller": "Фермер Миллер",
             "walt": "Старик Уолт", "miss_lane": "Мисс Лейн", "ghoul_kid_a": "Томми", "ghoul_kid_b": "Сью",
             "ghoul_kid_c": "Маленький Джо", "tess": "Тесс",
             "oskar": "Брат Оскар", "motel_mom": "Женщина в номере 201", "motel_kid": "Мальчик",
             "springer": "Отец Кёртис Спрингер", "nurse_ava": "Сестра Ава", "gus": "Смотритель Гас",
             "pilgrim_hank": "Паломник Хэнк", "pilgrim_maria": "Мария", "pilgrim_timmy": "Тимми",
             "healer_girl": "Целительница Лоис", "merchant_zz": "Торговец Абдул", "bath_pilgrim": "Паломница",
             "bath_pilgrim_b": "Паломник", "guest_widow": "Вдова Харпер",
             "kate": "Мамаша Кейт", "captain_morrow": "Капитан Морроу", "river_guard": "Страж Билли",
             "fisher_joe": "Рыбак Джо", "fishmonger": "Торговка Пег", "preacher_eli": "Проповедник Эли",
             "needles_girl": "Лиззи", "drunk_vic": "Пьяница Вик", "morrow_scout": "Дозорный стражи",
             "barkeep_ned": "Бармен Нед", "gambler_lou": "Картёжник Лу", "river_guard_off": "Стражник",
             "shopkeeper_rosa": "Лавочница Роуз",
             "dolores": "Долорес Вега", "water_clerk": "Конторщик Пабло", "hub_guard": "Хабская стража",
             "hub_guard_b": "Хабская стража", "crimson_boss": "Маргарет Крэйн", "spice_seller": "Торговец пряностями",
             "arms_seller": "Оружейник Кирк", "cult_preacher": "Сестра Мирра", "bos_scout": "Разведчица Братства",
             "hub_kid": "Мальчишка", "hub_beggar": "Нищий", "hub_beggar_b": "Нищенка", "old_woman": "Старуха Нэн",
             "junkie": "Торчок", "street_kid": "Беспризорник", "decker": "Декер", "falcon_barkeep": "Бармен Винни",
             "falcon_drunk": "Пьяница", "falcon_singer": "Певица Лулу", "falcon_gambler": "Шулер Ленни",
             "slum_mother": "Мать с ребёнком", "slum_old": "Старик у костра", "slum_boy": "Мальчишка с рогаткой",
             "roy": "Рой", "marla": "Марла", "marla_home": "Марла", "acolyte_a": "Послушница",
             "acolyte_b": "Послушник", "baker_kid_b": "Девочка",
             "gate_guard": "Привратник Кэл", "jt_guard": "Стражник", "cult_recruiter": "Брат Офир", "water_seller": "Водовоз Сэл", "jt_tinker": "Механик Лу", "jt_kid": "Пип", "jt_woman": "Прачка Дина", "jt_old_scav": "Старик Барни", "jt_drunk": "Пьяница Морт", "spike": "Старьёвщик Спайк", "scrapper": "Старьёвщик Хэл", "scrapper_girl": "Старьёвщица Джин", "mayor_darkwater": "Мэр Дарквотер", "hall_guard": "Стражник ратуши", "gizmo": "Гизмо", "gizmo_thug": "Громила Изо", "croupier": "Крупье Вера", "cashier_jt": "Кассир Билл", "gambler_jt": "Игрок", "gambler_jt_b": "Игрок", "marsha": "Марша Дарквотер", "anna_shaw": "Доктор Анна Шоу", "orderly_tom": "Санитар Томми", "patient_hank": "Больной Хэнк", "patient_girl": "Девочка Мэйси", "neal": "Бармен Нил", "hunter_rourke": "Рурк", "skum_drunk": "Пьянчуга", "skum_girl": "Танцовщица Сью",
             "nc_guard": "Страж Сета", "nc_guard_b": "Страж Сета", "cult_envoy": "Сестра Эсфирь", "gravedigger": "Могильщик Ирвинг", "harry_mech": "Механик Гарри", "water_queue": "Гуль в очереди", "water_queue_b": "Гулька в очереди", "maud": "Торговка Мод", "ghoul_vendor": "Старьёвщик Пит", "nc_ghoul_kid": "Гулёнок", "nc_old": "Старый гуль", "set": "Сет", "nc_hall_guard": "Страж Сета", "nc_hall_guard_b": "Страж Сета", "lorraine": "Писарь Лоррейн", "cobbs": "Капрал Коббс", "zeke": "Оружейник Зик", "ghoul_healer": "Целитель Дейв", "under_barkeep": "Хозяйка Бетти", "under_ghoul": "Гуль", "under_ghoul_b": "Гуль", "under_ghoul_c": "Гуль у костра",
             "aradesh": "Арадеш", "aradesh_wife": "Лейла", "unity_sister": "Сестра Ноэми", "settler_kai": "Кай", "farmer_ruth": "Рут", "well_digger": "Колодезник Сэм", "mechanic_vic": "Механик Вик", "settler_kid": "Мальчишка", "settler_old": "Старый Иона", "settler_woman": "Переселенка Мара", "khan_chief": "Хан Тагар", "khan_a": "Хан", "khan_b": "Ханша",
             "adytum_guard": "Страж Адитума", "adytum_guard_b": "Страж Адитума", "adytum_farmer": "Огородник Пол", "blade_nika": "Ника", "blade_a": "«Лезвие»", "blade_b": "«Лезвие»", "cult_foreman": "Брат-прораб Ахав", "cult_worker": "Послушник", "cult_worker_b": "Послушница", "adytum_worker": "Рабочий из Адитума", "adytum_mayor": "Мэр Холстед", "adytum_trader": "Торговка Джейн", "adytum_mom": "Жительница Адитума", "adytum_kid": "Мальчишка", "adytum_doc": "Медик Ли", "morpheus": "Брат Морфей", "cult_listener": "Прихожанин", "cult_listener_b": "Прихожанка", "cooper": "Купер Говард",
             "jackal_boss": "Гриз", "captive_mira": "Мира", "jackal_a": "Шакал", "jackal_b": "Шакалка", "jackal_c": "Шакал", "beatrice": "Беатрис", "v15_sentry": "Часовой Тони", "v15_cook": "Повариха Грета", "v15_tech": "Техник Отис", "v15_old": "Старик Абрахам", "v15_girl": "Девочка Лу",
             "overseer_sim": "Смотрительница Сим", "v4_mutant": "Тихоня", "v4_greeter": "Встречающий Элай", "v4_teacher": "Учительница Норма", "v4_kid": "Мальчик", "v4_kid_b": "Девочка", "v4_gardener": "Садовник Бёрт", "v4_mutant_b": "Глазастик", "v4_resident": "Жилец",
             "deputy_baxter": "Помощник Бакстер", "pr_deputy": "Помощник Ли", "pr_undertaker": "Гробовщик Хэнк", "pr_kid": "Мальчишка", "pr_old": "Старик Абнер", "pr_mechanic": "Механик Дейл", "pr_trader": "Торговка Луиза", "pr_caravan_guard": "Охранник каравана", "pr_manager": "Управляющая Рита", "pr_guest": "Постоялец", "mae_reeves": "Мэй Ривз", "barkeep_slim": "Бармен Слим", "pr_croupier": "Крупье Дорис", "pr_gambler": "Игрок", "pr_drunk": "Пьяница Вик", "prisoner_jonah": "Послушник Иона", "brother_job": "Брат Иов", "cult_guard_pr": "Страж культа", "cult_guard_pr_b": "Страж культа", "tobi": "Тоби", "cult_sister_pr": "Сестра Руфь",
             "sunny": "Санни Смайлс", "chet": "Лавочник Чет", "mayor_pettit": "Староста Петтит", "gs_farmer": "Фермерша Эбби", "gs_kid": "Мальчишка", "gs_old": "Старик Изи", "gravedigger_gs": "Могильщик Джеб", "trudy": "Труди", "gs_drunk": "Пьяница Ринго", "gs_prospector": "Старатель Джо", "ezekiel": "Иезекииль", "doc_mitchell": "Док Митчелл", "cult_hunter": "Брат-ловчий",
             "hugo_lee": "Хьюго Ли", "sam_botanist": "Сэм", "overseer_keene": "Смотритель Кин", "v22_greeter": "Встречающий Отто", "v22_cook": "Повар Дэлия", "v22_kid": "Мальчик", "v22_farmer": "Фермер Оскар", "v22_scientist": "Учёный Финч", "v22_gardener_out": "Огородник Пит",
             "mayor_carroll": "Мэр Кэрролл", "grace_widow": "Вдова Грейс", "np_storekeeper": "Лавочница Пирс", "np_crier": "Глашатай Бенни", "np_old_mae": "Бабка Мэй", "np_farmer": "Фермер Хэнк", "np_kid": "Девочка Энни", "np_drunk": "Пьяница Тед", "np_clerk": "Секретарь Олив", "np_bride": "«Невеста» Лора", "np_bride_b": "«Невеста» Тесса", "groom_cal": "Кэл", "groom_a": "«Жених»", "groom_b": "«Жених»", "groom_c": "«Жениха»", "brother_t": "Брат Т.", "cult_guard_np": "Страж культа", "cult_guard_np_b": "Страж культа", "np_captive": "Пленник",
             "fire_chief_hope": "Брандмейстер Хоуп", "marta_kane": "Марта Кейн", "foreman_gus": "Старшина Гас", "father_clement": "Отец Клемент", "sl_trader": "Лавочница Дот", "sl_kid": "Мальчишка", "sl_miner": "Шахтёр Билл", "paladin_ross": "Паладин Росс", "bos_knight": "Рыцарь Братства", "sl_firefighter": "Пожарный Эрни", "robo_sgt": "Сержант-робот ТР-7", "robo_sentry": "Робот-часовой", "recruit_danny": "Новобранец Дэнни", "recruit_b": "Новобранец Нико", "recruit_c": "Новобранка Лиз", "recruit_d": "Новобранец Пак", "recruit_e": "Новобранец Том", "recruit_f": "Новобранец Сэмми",
             "judge_sol": "Судья Сол", "strip_trader": "Торговка Лулу", "strip_drunk": "Пьяница Фрэнки", "grey_buyer": "Человек в сером", "strip_kid": "Мальчишка Тим", "hank_spur": "Хэнк «Шпора»", "boots_engineer": "Механик Роза", "boots_rider": "Сапог Дасти", "boots_rider_b": "Сапог Ред", "boots_rider_c": "Сапожка Бетт", "snake_kid": "Воришка Пип", "snake_guard": "Страж люка", "snake_trader": "Торговец Сайрус", "snake_gambler": "Игрок Змей", "mother_snake": "Мать-Змея", "den_dealer": "Крупье Змей", "den_barkeep": "Бармен Змей", "palms_doorman": "Привратник Ладоней", "palms_doctor": "Доктор Ирен", "palms_gardener": "Садовник Ладоней", "palms_reader": "Читатель Ладоней", "palms_librarian": "Библиотекарь Ладоней", "mother_agatha": "Матушка Агата", "palms_cook": "Повар Ладоней", "cooper_zero": "Купер Говард",
             "enclave_gate": "Солдат у ворот", "enclave_officer": "Лейтенант Крейн", "hollis_p7": "Комендант Холлис", "darnell": "Паладин Дарнелл", "enclave_tech": "Связист Анклава", "enclave_scientist": "Доктор Вейл", "enclave_trooper": "Солдат Анклава",
             "cult_herald": "Глашатай Единства", "mp_acolyte": "Послушник", "mp_acolyte_b": "Послушница", "tobi_mp": "Тоби", "ezekiel_mp": "Иезекииль", "nipton_bride_mp": "«Невеста» из Ниптона", "brother_t_mp": "Брат Т.",
             "harbor_master": "Смотритель причала Оуэн", "quarantine_nurse": "Сестра Пэм", "fisher_ana": "Рыбачка Ана", "tiki_barkeep": "Бармен Коко", "island_kid": "Девочка Лили", "island_old": "Бабушка Ингрид", "sailor_finn": "Моряк Финн", "island_teacher": "Учитель Маркус", "elder_mora": "Старейшина Мора", "elder_bram": "Старейшина Брэм", "young_jude": "Джуд", "keeper_silas": "Смотритель маяка Сайлас",
             "purity_officer": "Инспектор Чистоты Лин", "purity_bot": "Робот-сканер", "councillor_vale": "Советник Вэйл", "nv_citizen": "Горожанка", "nv_citizen_b": "Горожанин", "nv_doctor": "Доктор Эрик Сун", "nv_child": "Мальчик", "raven_hacker": "Рэйвен", "noodle_cook": "Повар Мо Чен", "nv_dealer": "Торговец Шрапнель", "nv_outcast": "Отсеянный", "nv_outcast_b": "Отсеянная", "cleaner_bot": "Робот-уборщик",
             "sphinx": "Сфинкс, экскурсовод", "bridge_keeper": "Хранитель моста", "harold": "Гарольд",
             "lucky_bot": "Секьюритрон", "radio_bot": "Диктор-автомат", "deputy_abby": "Помощница шерифа Эбби",
             "luis_cards": "Картёжник Луис", "beth_waitress": "Официантка Бет", "hank_miner": "Старатель Хэнк",
             "repconn_ghoul": "Гуль-техник Чет", "rover_bot": "Марсоход «Спирит-II»", "cmdr_hale": "Командир Хейл", "eng_okoro": "Инженер Окоро", "botanist_yuki": "Ботаник Юки"}
# у кого кадры лежат в чужой папке (жители из tools/make_variants.py)
NPC_SPRITES = {"marta": "folk_a", "dale": "folk_b", "rose": "folk_a", "dex": "merc",
               # Бейкер (листы из tools/import_sheets.py)
               "amos_b7": "amos", "iskra": "girl_hood", "iskra_out": "girl_hood", "nick": "barkeep",
               "tobias": "cultist", "hattie": "seer", "hollis": "detective", "lira_baker": "blondie",
               "loner_baker": "loner", "silas_baker": "silas", "scar_baker": "boss",
               "baker_folk_a": "folk_c", "baker_folk_b": "folk_d", "baker_kid": "kid", "baker_folk_c": "girl_pink",
               "baker_folk_d": "folk_g", "baker_folk_e": "folk_e",
               "caravan_trader": "healer", "caravan_guard": "desert_guard", "farmer_miller": "folk_i",
               "walt": "folk_g", "miss_lane": "ghoul_lady", "ghoul_kid_a": "ghoul_kid", "ghoul_kid_b": "ghoul_kid",
               "ghoul_kid_c": "ghoul_kid", "tess": "acolyte",
               "oskar": "folk_c", "motel_mom": "folk_f", "motel_kid": "kid",
               "springer": "detective", "nurse_ava": "seer", "gus": "folk_g", "pilgrim_hank": "feral",
               "pilgrim_maria": "folk_d", "pilgrim_timmy": "kid", "healer_girl": "acolyte", "merchant_zz": "healer",
               "bath_pilgrim": "folk_h", "bath_pilgrim_b": "folk_c", "guest_widow": "folk_f",
               "kate": "folk_d", "captain_morrow": "desert_guard", "river_guard": "soldier", "fisher_joe": "folk_e",
               "fishmonger": "folk_h", "preacher_eli": "monk", "needles_girl": "girl_pink", "drunk_vic": "folk_c",
               "morrow_scout": "scout", "barkeep_ned": "barkeep", "gambler_lou": "detective",
               "river_guard_off": "redarmor", "shopkeeper_rosa": "seer",
               "dolores": "folk_f", "water_clerk": "detective", "hub_guard": "soldier", "hub_guard_b": "soldier",
               "crimson_boss": "redarmor", "spice_seller": "healer", "arms_seller": "desert_guard",
               "cult_preacher": "cultist", "bos_scout": "blondie", "hub_kid": "kid", "hub_beggar": "folk_c",
               "hub_beggar_b": "folk_h", "old_woman": "folk_d", "junkie": "folk_e", "street_kid": "kid",
               "decker": "visor_punk", "falcon_barkeep": "barkeep", "falcon_drunk": "folk_g",
               "falcon_singer": "girl_pink", "falcon_gambler": "scout",
               "slum_mother": "folk_d", "slum_old": "folk_g", "slum_boy": "kid",
               "roy": "folk_f", "marla": "folk_h", "marla_home": "folk_h", "acolyte_a": "acolyte",
               "acolyte_b": "monk", "baker_kid_b": "folk_j",
               "gate_guard": "soldier", "jt_guard": "desert_guard", "cult_recruiter": "cultist", "water_seller": "healer", "jt_tinker": "folk_i", "jt_kid": "kid", "jt_woman": "folk_h", "jt_old_scav": "folk_g", "jt_drunk": "folk_c", "spike": "merc", "scrapper": "folk_e", "scrapper_girl": "girl_hood", "mayor_darkwater": "sheriff", "hall_guard": "soldier", "gizmo": "boss", "gizmo_thug": "gang", "croupier": "blondie", "cashier_jt": "detective", "gambler_jt": "folk_b", "gambler_jt_b": "folk_e", "marsha": "folk_d", "anna_shaw": "doc", "orderly_tom": "folk_j", "patient_hank": "folk_c", "patient_girl": "girl_pink", "neal": "barkeep", "hunter_rourke": "loner", "skum_drunk": "folk_g", "skum_girl": "girl_pink",
               "nc_guard": "ghoul_b", "nc_guard_b": "ghoul_e", "cult_envoy": "cultist", "gravedigger": "ghoul_c", "harry_mech": "ghoul_e", "water_queue": "ghoul_a", "water_queue_b": "ghoul_d", "maud": "ghoul_d", "ghoul_vendor": "ghoul_a", "nc_ghoul_kid": "ghoul_child", "nc_old": "ghoul_c", "set": "ghoul_set", "nc_hall_guard": "ghoul_b", "nc_hall_guard_b": "ghoul_e", "lorraine": "ghoul_lady", "cobbs": "ghoul_cobbs", "zeke": "ghoul_b", "ghoul_healer": "ghoul_c", "under_barkeep": "ghoul_d", "under_ghoul": "ghoul_a", "under_ghoul_b": "ghoul_e", "under_ghoul_c": "ghoul_c",
               "aradesh": "detective", "aradesh_wife": "folk_d", "unity_sister": "cultist", "settler_kai": "folk_b", "farmer_ruth": "folk_a", "well_digger": "folk_i", "mechanic_vic": "folk_e", "settler_kid": "kid", "settler_old": "folk_g", "settler_woman": "folk_h", "khan_chief": "boss", "khan_a": "raider", "khan_b": "visor_punk",
               "adytum_guard": "soldier", "adytum_guard_b": "desert_guard", "adytum_farmer": "folk_i", "blade_nika": "blondie", "blade_a": "gang", "blade_b": "raider", "cult_foreman": "monk", "cult_worker": "acolyte", "cult_worker_b": "cultist", "adytum_worker": "folk_e", "adytum_mayor": "detective", "adytum_trader": "folk_d", "adytum_mom": "folk_h", "adytum_kid": "kid", "adytum_doc": "healer", "morpheus": "silas", "cult_listener": "folk_c", "cult_listener_b": "folk_a", "cooper": "ghoul_cooper",
               "jackal_boss": "boss", "captive_mira": "ada", "jackal_a": "raider", "jackal_b": "visor_punk", "jackal_c": "gang", "beatrice": "folk_d", "v15_sentry": "merc", "v15_cook": "folk_h", "v15_tech": "folk_e", "v15_old": "folk_g", "v15_girl": "kid",
               "overseer_sim": "doc", "v4_mutant": "rad_mutant", "v4_greeter": "folk_b", "v4_teacher": "ada", "v4_kid": "kid", "v4_kid_b": "girl_pink", "v4_gardener": "ghoul_e", "v4_mutant_b": "ghoul_a", "v4_resident": "folk_c",
               "deputy_baxter": "sheriff", "pr_deputy": "soldier", "pr_undertaker": "folk_g", "pr_kid": "kid", "pr_old": "folk_c", "pr_mechanic": "folk_i", "pr_trader": "healer", "pr_caravan_guard": "desert_guard", "pr_manager": "detective", "pr_guest": "folk_a", "mae_reeves": "folk_f", "barkeep_slim": "barkeep", "pr_croupier": "blondie", "pr_gambler": "scout", "pr_drunk": "lenny", "prisoner_jonah": "acolyte", "brother_job": "silas", "cult_guard_pr": "cultist", "cult_guard_pr_b": "monk", "tobi": "kid", "cult_sister_pr": "acolyte",
               "sunny": "blondie", "chet": "folk_c", "mayor_pettit": "detective", "gs_farmer": "folk_h", "gs_kid": "kid", "gs_old": "folk_g", "gravedigger_gs": "folk_e", "trudy": "folk_d", "gs_drunk": "lenny", "gs_prospector": "folk_i", "ezekiel": "acolyte", "doc_mitchell": "doc", "cult_hunter": "cultist",
               "hugo_lee": "soldier", "sam_botanist": "folk_a", "overseer_keene": "doc", "v22_greeter": "folk_b", "v22_cook": "folk_h", "v22_kid": "kid", "v22_farmer": "folk_i", "v22_scientist": "detective", "v22_gardener_out": "folk_e",
               "mayor_carroll": "detective", "grace_widow": "folk_f", "np_storekeeper": "folk_d", "np_crier": "folk_b", "np_old_mae": "folk_h", "np_farmer": "folk_i", "np_kid": "girl_pink", "np_drunk": "lenny", "np_clerk": "folk_a", "np_bride": "girl_hood", "np_bride_b": "folk_h", "groom_cal": "boss", "groom_a": "raider", "groom_b": "gang", "groom_c": "visor_punk", "brother_t": "silas", "cult_guard_np": "cultist", "cult_guard_np_b": "monk", "np_captive": "folk_c",
               "fire_chief_hope": "folk_d", "marta_kane": "folk_f", "foreman_gus": "folk_i", "father_clement": "monk", "sl_trader": "folk_h", "sl_kid": "kid", "sl_miner": "folk_e", "paladin_ross": "redarmor", "bos_knight": "soldier", "sl_firefighter": "folk_c", "robo_sgt": "robot_guard", "robo_sentry": "robot_guard", "recruit_danny": "merc", "recruit_b": "merc", "recruit_c": "girl_hood", "recruit_d": "merc", "recruit_e": "merc", "recruit_f": "merc",
               "judge_sol": "folk_g", "strip_trader": "folk_h", "strip_drunk": "lenny", "grey_buyer": "detective", "strip_kid": "kid", "hank_spur": "sheriff", "boots_engineer": "girl_hood", "boots_rider": "desert_guard", "boots_rider_b": "merc", "boots_rider_c": "blondie", "snake_kid": "kid", "snake_guard": "gang", "snake_trader": "visor_punk", "snake_gambler": "scout", "mother_snake": "seer", "den_dealer": "folk_b", "den_barkeep": "barkeep", "palms_doorman": "folk_c", "palms_doctor": "doc", "palms_gardener": "folk_i", "palms_reader": "folk_e", "palms_librarian": "ada", "mother_agatha": "folk_d", "palms_cook": "folk_g", "cooper_zero": "ghoul_cooper",
               "enclave_gate": "soldier", "enclave_officer": "soldier", "hollis_p7": "detective", "darnell": "folk_b", "enclave_tech": "soldier", "enclave_scientist": "doc", "enclave_trooper": "soldier",
               "cult_herald": "silas", "mp_acolyte": "acolyte", "mp_acolyte_b": "cultist", "tobi_mp": "kid", "ezekiel_mp": "ghoul_child", "nipton_bride_mp": "girl_hood", "brother_t_mp": "silas",
               "harbor_master": "folk_g", "quarantine_nurse": "healer", "fisher_ana": "folk_h", "tiki_barkeep": "barkeep", "island_kid": "girl_pink", "island_old": "folk_d", "sailor_finn": "folk_e", "island_teacher": "folk_b", "elder_mora": "seer", "elder_bram": "folk_c", "young_jude": "loner", "keeper_silas": "folk_i",
               "purity_officer": "ada", "purity_bot": "robot_guard", "councillor_vale": "detective", "nv_citizen": "blondie", "nv_citizen_b": "folk_b", "nv_doctor": "doc", "nv_child": "kid", "raven_hacker": "visor_punk", "noodle_cook": "barkeep", "nv_dealer": "gang", "nv_outcast": "ghoul_a", "nv_outcast_b": "ghoul_d", "cleaner_bot": "robot_skel",
               "sphinx": "robot_guard", "bridge_keeper": "seer", "harold": "ghoul_c", "lucky_bot": "robot_guard", "radio_bot": "robot_guard", "deputy_abby": "sheriff", "luis_cards": "folk_b",
               "beth_waitress": "girl_pink", "hank_miner": "folk_i",
               "repconn_ghoul": "ghoul_e", "rover_bot": "robot_skel", "cmdr_hale": "soldier", "eng_okoro": "folk_i", "botanist_yuki": "folk_a"}

# жители, которые есть на карте только при условии (как у реплик): кого не спасли — тот в Марипозе
NPC_IF = {"tobi_mp": {"not_flag": "tobi_home"},
          "ezekiel_mp": {"flag": "ezekiel_to_cult"},
          "nipton_bride_mp": {"not_flag": "nipton_decided"},
          "brother_t_mp": {"not_flags": ["killed_brother_t", "killed_brother_t_mp"]}}

with open("data/enemies.json", "r", encoding="utf-8") as f:
    ENEMY_DEFS = json.load(f)
with open("data/locations.json", "r", encoding="utf-8") as f:
    LOCATION_DEFS = json.load(f)

_ANIM_CACHE = {}


def enemy_animations(type_id):
    if type_id not in _ANIM_CACHE:
        d = ENEMY_DEFS[type_id]
        art = d["art"]
        # мутант исторически лежит в assets/sprites/enemy, остальные — в папке своего типа
        folder = f"{S.ASSET_ROOT}/sprites/{d.get('sprite_dir', type_id)}"
        _ANIM_CACHE[type_id] = loader.load_creature_animations(
            folder, tuple(art["size"]), tuple(art["base"]), tuple(art["accent"]), kind=art["kind"])
    return _ANIM_CACHE[type_id]


def make_enemy(pos, type_id, iso=False):
    """iso — на изометрической карте: кадры из iso_sprite (data/enemies.json), если есть."""
    sprite = ENEMY_DEFS[type_id].get("iso_sprite") if iso else None
    if sprite:
        from .iso import char_animator
        e = Enemy(pos, {"idle": [pygame.Surface((1, 1))]}, type_id, ENEMY_DEFS[type_id])
        e.anim = char_animator(sprite)
        return e
    return Enemy(pos, enemy_animations(type_id), type_id, ENEMY_DEFS[type_id])


def npc_animations(npc_id):
    """Кадры NPC — assets/sprites/<npc_id>/ (см. tools/slice_sprites.py), иначе плейсхолдер."""
    key = f"npc:{npc_id}"
    if key not in _ANIM_CACHE:
        folder = f"{S.ASSET_ROOT}/sprites/{NPC_SPRITES.get(npc_id, npc_id)}"
        if npc_id == "robot":
            _ANIM_CACHE[key] = loader.load_creature_animations(
                folder, (44, 56), (120, 125, 135), (230, 190, 60), kind="humanoid")
        else:
            _ANIM_CACHE[key] = loader.load_humanoid_animations(
                folder, loader.FRAME_SIZE, base_color=(70, 90, 110), accent_color=(190, 180, 150))
    return _ANIM_CACHE[key]


class Location:
    def __init__(self, loc_id, d=None, rows=None, hero=False):
        d = d if d is not None else LOCATION_DEFS.get(loc_id, {})
        self.id = loc_id
        self.name = d.get("name", loc_id)
        self.world_pos = d.get("world_pos")
        self.is_encounter = d.get("encounter", False)
        if rows is None and d.get("scene"):   # придорожное место: сцена из src/encounters.py, всегда одна и та же
            from .encounters import spot_map
            self.level = TownMap(spot_map(loc_id, d["scene"]))
        elif rows is None and isinstance(d.get("map"), dict):   # сцена случайной встречи, собранная на лету
            self.level = TownMap(d["map"])
        elif rows is None and d["map"].endswith(".json"):
            with open(d["map"], "r", encoding="utf-8") as f:
                is_iso = '"iso":true' in f.read(200).replace(" ", "")
            if is_iso:
                from .isomap import IsoMap
                self.level = IsoMap(d["map"])   # изометрия (tools/build_iso_town.py)
            else:
                self.level = TownMap(d["map"])  # карта из объектов (tools/build_town.py)
        else:
            self.level = TileMap(rows or load_map_file(d["map"]), npc_ids=d.get("npcs"),
                                 containers=d.get("containers"), terminals=d.get("terminals"))
        entry = d.get("entry")
        self.entry = (entry[0] * S.TILE, entry[1] * S.TILE) if entry else self.level.player_spawn
        iso = getattr(self.level, "iso", False)
        self.enemies = [make_enemy(pos, t, iso) for pos, t in self.level.enemy_spawns]
        if not self.is_encounter and not d.get("action"):   # мир растёт вместе с героем (src/balance.py)
            from .balance import act_of, scale_enemy, scale_loot
            act = act_of(loc_id)
            for e in self.enemies:
                scale_enemy(e, act)
            for box in getattr(self.level, "containers", []):
                box["loot"] = scale_loot(box["loot"], act)
        if d.get("action") and hero:   # Барстоу без Дэкса: пошаговый бой, орда для аркады героя бы смяла —
            ghouls = [e for e in self.enemies if e.type_id in ("feral", "ghoul_runner")]   # остаётся каждый третий гуль
            self.enemies = [e for e in self.enemies if e not in ghouls] + ghouls[::3]
            for h in getattr(self.level, "hordes", []):   # толпы из домов — только в аркаде Дэкса
                h["done"] = True
        elif d.get("action"):   # экшен (Барстоу): здоровье гулей — ровно в пулях
            from .action import set_action_hp
            for e in self.enemies:
                set_action_hp(e)
        self.hero = hero                        # Барстоу: создана героем (поредевшая орда) или Дэксом (аркада)
        self.enemies_all = list(self.enemies)  # исходный порядок — для сохранений (ушедшие исчезают из enemies)
        self.npcs = [NPC(pos, npc_animations(nid), npc_id=nid, name=NPC_NAMES.get(nid, nid))
                     for pos, nid in self.level.npc_spawns]
        self.npcs_all = list(self.npcs)   # все жители карты — тот, кто ушёл со спутником и вернулся, снова здесь

    def faction_members(self, faction):
        return [e for e in self.enemies if e.alive and e.faction == faction]
