# Звуки и музыка: авторство и лицензии

Правило: в игру попадают только свободные файлы (CC0 / CC-BY). Звуки Fallout 2 в репозиторий и сборку
не входят: игра берёт их из копии игрока, если она установлена.

Все внешние файлы обрабатывает tools/prepare_packs.py (обрезка тишины, нормализация громкости, моно, ogg).
Лицензия каждой страницы проверена 2026-10-17 по полю «License(s)» на самой странице.

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
| shot_pipe_*, shot_enemy_*, shot_turret_*, ar_shot_*, rifle_shot_* | [The Free Firearm Sound Library](https://opengameart.org/content/the-free-firearm-sound-library) |
| ar_reload | [Gun reload sounds](https://opengameart.org/content/gun-reload-sounds), SpringySpringo |
| armor_hit_*, armor_ricochet_* | [Metal Impact Sounds](https://opengameart.org/content/metal-impact-sounds), BMacZero |
| dog_*, ghoul_* | [Monster Sound Effects Pack](https://opengameart.org/content/monster-sound-effects-pack), Ogrebane |
| rat_* | [Squeaky Rat](https://opengameart.org/content/squeaky-rat), qubodup |
| robot_* | [100 CC0 SFX](https://opengameart.org/content/100-cc0-sfx), rubberduck |
| crit | [Impacts/Gun/sfx](https://opengameart.org/content/impactsgunsfx), Eldritch Grim |
| door_break | [35 wooden cracks/hits/destructions](https://opengameart.org/content/35-wooden-crackshitsdestructions), Independent.nu / qubodup |
| human_hurt_*, human_death_* | [grunts of male death and pain](https://opengameart.org/content/grunts-male-death-and-pain), thebardofblasphemy. Проверить перед релизом: комментарий на странице намекает на GPL |
| beetle_*, roach_* | [Monster or beast sounds](https://opengameart.org/content/monster-or-beast-sounds), pauliuw |

## Freesound, CC0
| Файл | Звук, автор |
|---|---|
| explosion | [Explosion Test](https://freesound.org/people/Apenguin73/sounds/335152/), Apenguin73 |
| pistol_reload | [Pistol Cock](https://freesound.org/people/xfixy8/sounds/467300/), XfiXy8 |
| sg_reload | [Rem870 Slide Forward 1](https://freesound.org/people/pjkasinski3/sounds/171630/), Pjkasinski3 (8 повторов) |
| sg_shot | [20 gauge shotgun gunshot](https://freesound.org/people/michorvath/sounds/427595/), michorvath |

## Скачано с zvukogram.com (ПРАВА НЕЯСНЫ, заменить до релиза)
shot, melee, hit — исходники в sounds/ (gun-shot.wav, udar-po-zaschite--priglushnno.wav,
the-bullet-hit-the-human-body.wav). Сайт пишет «Бесплатно, MP3 и WAV» и
«Все права защищены», лицензии на звуки не указывает (проверено 2026-10-17). Для релиза нужно либо письменное
разрешение сайта, либо замена на CC0-файлы. Рабочие замены: shot — Free Firearm Library, melee — Kenney
impactPunch, hit — Eldritch Grim «Impact N».
