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

## Скачано с zvukogram.com (ПРАВА НЕЯСНЫ, заменить до релиза)
hit — исходник в sounds/ (the-bullet-hit-the-human-body.wav). melee заменён на CC0 с Freesound (см. выше).
Сайт пишет «Бесплатно, MP3 и WAV» и «Все права защищены», лицензии на звуки не указывает (проверено 2026-10-17).
Для релиза нужно либо письменное разрешение сайта, либо замена на CC0-файлы. Рабочие замены: shot — Free Firearm
Library (уже стоит), hit — Eldritch Grim «Impact N».
