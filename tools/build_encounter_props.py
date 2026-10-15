"""
Свои объекты для случайных встреч и придорожных мест (src/encounters.py): дюны, гряды валунов, пятна горелой земли.
Регистрируются в data/props/encounters.json. Дюны и скалы — куски страницы desert-natural (песок под ними убирается).

Запуск из папки game_project:  .venv/bin/python tools/build_encounter_props.py
"""
import json
import os

from citykit import City

city = City("encounters", "Встречи")
for i, (x, y) in enumerate(((4, 0), (6, 0), (8, 0), (4, 2), (6, 2))):
    city.prop(f"enc_dune{i}", f"pk:desnat/p1/{x},{y},2,2", foot=[2, 1], keybg=True)
os.makedirs("data/props", exist_ok=True)
with open("data/props/encounters.json", "w", encoding="utf-8") as f:
    json.dump({"props": city.props}, f, ensure_ascii=False, indent=0)
print("зарегистрировано:", len(city.props))
