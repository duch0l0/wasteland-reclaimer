# Звуки и музыка: авторство и лицензии

Правило: в игру попадают только свободные файлы (CC0 / CC-BY). Звуки Fallout 2 в репозиторий и сборку
не входят: игра берёт их из копии игрока, если она установлена.

Все внешние файлы обрабатывают tools/prepare_packs.py и tools/prepare_selected.py (обрезка тишины,
нормализация громкости, моно, ogg; ambient — петля с кроссфейдом, стерео, −20 LUFS).
Лицензия каждой страницы проверена 2026-10-17 (ambient и новые эффекты — 2026-10-22) по полю «License(s)»
на самой странице.

Ключи с вариантами (по строке на каждый файл — ниже): shot_*, hit_bullet_*, melee_*, human_hurt_*,
human_death_*, human_death_female_*, amb_sewer_*, step_gravel_*, step_sand_*, step_metal_*, step_water_*.

## Свои (синтез кодом, tools/make_sfx.py)
Лицензия: проект Wasteland Reclaimer. Файлы: button, empty, geiger_*, terminal_key_*, terminal_ok, terminal_err,
combat_end, levelup, quest, pickup_*, putdown_*, close_*, heal_*, dialog.

## Kenney, CC0 1.0 — https://kenney.nl
| Файлы в assets/sounds | Пакет |
|---|---|
| step_dirt_*, door_open_*, door_close_*, gate_open_*, open_*, coins_*, combat_start_* (нож, ремень), miss | [RPG Audio](https://kenney.nl/assets/rpg-audio) |
| step_concrete_*, step_wood_*, combat_start_* (колокол) | [Impact Sounds](https://kenney.nl/assets/impact-sounds) |

## OpenGameArt, CC0
| Файлы | Пакет, автор |
|---|---|
| shot_1, shot_2, shot_pipe_*, shot_enemy_*, shot_turret_*, ar_shot_*, rifle_shot_* | [The Free Firearm Sound Library](https://opengameart.org/content/the-free-firearm-sound-library). shot_1, shot_2 — Master Tracks/1911/A_15.wav (Ben Jaszczak, Brian Nelson, Kevin Heras, Matthew Nanney) |
| ar_reload | [Gun reload sounds](https://opengameart.org/content/gun-reload-sounds), SpringySpringo |
| armor_hit_*, armor_ricochet_* | [Metal Impact Sounds](https://opengameart.org/content/metal-impact-sounds), BMacZero |
| dog_*, ghoul_* | [Monster Sound Effects Pack](https://opengameart.org/content/monster-sound-effects-pack), Ogrebane |
| rat_* | [Squeaky Rat](https://opengameart.org/content/squeaky-rat), qubodup |
| robot_* | [100 CC0 SFX](https://opengameart.org/content/100-cc0-sfx), rubberduck |
| crit, hit_bullet_1 | [Impacts/Gun/sfx](https://opengameart.org/content/impactsgunsfx), Eldritch Grim |
| door_break | [35 wooden cracks/hits/destructions](https://opengameart.org/content/35-wooden-crackshitsdestructions), Independent.nu / qubodup |
| beetle_*, roach_* | [Monster or beast sounds](https://opengameart.org/content/monster-or-beast-sounds), pauliuw |

## Freesound, CC0 — эффекты
| Файл | Звук, автор |
|---|---|
| explosion | [Explosion Test](https://freesound.org/people/Apenguin73/sounds/335152/), Apenguin73 |
| pistol_reload | [Pistol Cock](https://freesound.org/people/xfixy8/sounds/467300/), XfiXy8 |
| sg_reload | [Rem870 Slide Forward 1](https://freesound.org/people/pjkasinski3/sounds/171630/), Pjkasinski3 (8 повторов) |
| sg_shot | [20 gauge shotgun gunshot](https://freesound.org/people/michorvath/sounds/427595/), michorvath |
| human_hurt_1 | [Male Grunt 1](https://freesound.org/people/Kodack/sounds/256603/), Kodack |
| human_hurt_2 | [Grunt Pain 1](https://freesound.org/people/mf_gloom/sounds/517847/), mf_gloom |
| human_hurt_3 | [Pain Grunt 09](https://freesound.org/people/MrFossy/sounds/547209/), MrFossy |
| human_hurt_4, human_hurt_5 | [Pain Grunt A / B](https://freesound.org/people/unfa/sounds/610998/), unfa |
| human_death_1 | [Male Death](https://freesound.org/people/Blankened/sounds/554443/), Blankened |
| human_death_2 | [Male Scream Death](https://freesound.org/people/JD_Brick_Productions/sounds/745726/), JD_Brick_Productions |
| human_death_female_1 | [Human Male Scream 5](https://freesound.org/people/JohnsonBrandEditing/sounds/243382/), JohnsonBrandEditing |
| melee_1 | [Punch Hard 2](https://freesound.org/people/magnuswaker/sounds/524956/), magnuswaker — CC0 1.0 |
| melee_2 | [Major punch](https://freesound.org/people/janbezouska/sounds/399183/), janbezouska — CC0 1.0 |
| hit_1 | [thump.wav](https://freesound.org/people/Reitanna/sounds/252264/), Reitanna — CC0 1.0 |

hit — один файл (hit_1), вариантов нет; hit_bullet — отдельный ключ (см. OpenGameArt).

## Ambient-петли (Freesound)
| Файл | Автор, страница | Лицензия |
|---|---|---|
| amb_wind | szegvari, [dark sahara egypt](https://freesound.org/people/szegvari/sounds/557552/) | CC0 1.0 |
| amb_night | trp, [night tree crickets with airplanes, binaural Toronto](https://freesound.org/people/trp/sounds/616619/) | CC0 1.0 |
| amb_vault | kevp888, [LS 34819 FR VentilationSystem](https://freesound.org/people/kevp888/sounds/661007/) | CC BY 4.0 — указать автора в титрах |
| amb_cave | LittleRobotSoundFactory, [Ambience Cave 00](https://freesound.org/people/LittleRobotSoundFactory/sounds/270387/) | CC BY 4.0 — указать автора в титрах |
| amb_sewer_1 | thedapperdan, [sewer drain](https://freesound.org/people/thedapperdan/sounds/26910/) | CC0 1.0 |
| amb_sewer_2 | InspectorJ, [Sewer Soundscape A](https://freesound.org/people/InspectorJ/sounds/342566/) | CC BY 4.0 — указать автора в титрах |
| amb_town | soundandmelodies, [afternoon walla and footsteps, Cadiz](https://freesound.org/people/soundandmelodies/sounds/784415/) | CC0 1.0 |
| amb_neon | jameswrowles, [Hum1](https://freesound.org/people/jameswrowles/sounds/248217/) | CC BY 4.0 — указать автора в титрах |
| amb_campfire | Spandau, [campfire](https://freesound.org/people/Spandau/sounds/40699/) | CC0 1.0 |
| amb_machine | Garuda1982, [large diesel emergency generator](https://freesound.org/people/Garuda1982/sounds/606933/) | CC0 1.0 |

## Шаги по поверхностям (Freesound, CC0)
| Файлы | Автор, страница |
|---|---|
| step_gravel_1…4 | fission9, [hiking boot footsteps on gravel](https://freesound.org/people/fission9/sounds/521588/) |
| step_sand_1…4 | rnan_sounddesign, [sand footsteps](https://freesound.org/people/rnan_sounddesign/sounds/725875/) |
| step_metal_1…4 | sanderboah, [walking on metal](https://freesound.org/people/sanderboah/sounds/696374/) |
| step_water_1…3 | coffeemakessounds, [step water](https://freesound.org/people/coffeemakessounds/sounds/849638/) — один шаг, варианты по высоте |

## Музыка
Файлы — assets/music/<ключ>_N.ogg (ключ → варианты, у world три трека, world_1 — главный).
Выбор автора — incoming_audio/selection_music.json, обработка tools/prepare_music.py: срезана только тишина
в начале и конце, −16 LUFS, стерео, ogg q5. Фон локаций −20 LUFS, эффекты −18 → музыка громче фона,
тише эффектов. Громкости в игре: музыка 0.5, эффекты 0.8, фон 0.48 (src/audio.py → DEFAULTS).
«Утомлённое солнце» (utomlennoe-solncedzhazovyj-orkestr-acfasmana.ogg) пока остаётся запасным треком:
музыка для ключей title, reno, ending ещё не выбрана.

| Файл | Автор | Название | Ссылка | Лицензия |
|---|---|---|---|---|
| world_1 | Alexandr Zhelanov | Grey Land | [Post apocalypse — more music inside](https://opengameart.org/content/post-apocalypse-more-music-inside) | CC BY 3.0 — указать автора в титрах |
| world_2 | Kevin MacLeod | Penumbra | [incompetech: Penumbra](https://incompetech.com/music/royalty-free/mp3-royaltyfree/Penumbra.mp3) | CC BY 4.0 — строка атрибуции (ниже) |
| world_3 | Alexandr Zhelanov | Road | [Post apocalypse — more music inside](https://opengameart.org/content/post-apocalypse-more-music-inside) | CC BY 3.0 — указать автора в титрах |
| desert_1 | Alexandr Zhelanov | Myst | [Post apocalypse — more music inside](https://opengameart.org/content/post-apocalypse-more-music-inside) | CC BY 3.0 — указать автора в титрах |
| caves_1 | Kevin MacLeod | Lightless Dawn | [incompetech: Lightless Dawn](https://incompetech.com/music/royalty-free/mp3-royaltyfree/Lightless%20Dawn.mp3) | CC BY 4.0 — строка атрибуции (ниже) |
| lab_1 | Kevin MacLeod | Static Motion | [incompetech: Static Motion](https://incompetech.com/music/royalty-free/mp3-royaltyfree/Static%20Motion.mp3) | CC BY 4.0 — строка атрибуции (ниже) |
| raiders_1 | Kevin MacLeod | Interloper | [incompetech: Interloper](https://incompetech.com/music/royalty-free/mp3-royaltyfree/Interloper.mp3) | CC BY 4.0 — строка атрибуции (ниже) |
| hub_1 | Matthew Pablo | Desolate Part II | [Desolate](https://opengameart.org/content/desolate) | CC BY 3.0 — указать автора в титрах |
| junktown_1 | Kevin MacLeod | Mesmerize | [incompetech: Mesmerize](https://incompetech.com/music/royalty-free/mp3-royaltyfree/Mesmerize.mp3) | CC BY 4.0 — строка атрибуции (ниже) |
| vats_1 | Kevin MacLeod | Ossuary 1 - A Beginning | [incompetech: Ossuary 1](https://incompetech.com/music/royalty-free/mp3-royaltyfree/Ossuary%201%20-%20A%20Beginning.mp3) | CC BY 4.0 — строка атрибуции (ниже) |
| combat_1 | Alexandr Zhelanov | Alert | [Post apocalypse — more music inside](https://opengameart.org/content/post-apocalypse-more-music-inside) | CC BY 3.0 — указать автора в титрах |

Строки атрибуции для титров (формат Kevin MacLeod):

- world_2: "Penumbra" Kevin MacLeod (incompetech.com), Licensed under Creative Commons: By Attribution 4.0 License, http://creativecommons.org/licenses/by/4.0/
- caves_1: "Lightless Dawn" Kevin MacLeod (incompetech.com), Licensed under Creative Commons: By Attribution 4.0 License, http://creativecommons.org/licenses/by/4.0/
- lab_1: "Static Motion" Kevin MacLeod (incompetech.com), Licensed under Creative Commons: By Attribution 4.0 License, http://creativecommons.org/licenses/by/4.0/
- raiders_1: "Interloper" Kevin MacLeod (incompetech.com), Licensed under Creative Commons: By Attribution 4.0 License, http://creativecommons.org/licenses/by/4.0/
- junktown_1: "Mesmerize" Kevin MacLeod (incompetech.com), Licensed under Creative Commons: By Attribution 4.0 License, http://creativecommons.org/licenses/by/4.0/
- vats_1: "Ossuary 1 - A Beginning" Kevin MacLeod (incompetech.com), Licensed under Creative Commons: By Attribution 4.0 License, http://creativecommons.org/licenses/by/4.0/

CC BY 3.0 (world_1, world_3, desert_1, combat_1 — Alexandr Zhelanov; hub_1 — Matthew Pablo):
указать автора в титрах (строки атрибуции свести при финальной сборке титров).
