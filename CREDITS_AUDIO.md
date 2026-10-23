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
| step_sand_1…6 | rnan_sounddesign, [sand footsteps](https://freesound.org/people/rnan_sounddesign/sounds/725875/) — нарезано по одному шагу |
| step_metal_1…4 | sanderboah, [walking on metal](https://freesound.org/people/sanderboah/sounds/696374/) |
| step_water_1…3 | coffeemakessounds, [step water](https://freesound.org/people/coffeemakessounds/sounds/849638/) — один шаг, варианты по высоте |

## Музыка
Файлы — assets/music/<ключ>_N.ogg (ключ → варианты, у world три трека, world_1 — главный).
Выбор автора — incoming_audio/selection_music.json, обработка tools/prepare_music.py: срезана только тишина
в начале и конце, −16 LUFS, стерео, ogg q5. Фон локаций −20 LUFS, эффекты −18 → музыка громче фона,
тише эффектов. Громкости в игре: музыка 0.5, эффекты 0.8, фон 0.48 (src/audio.py → DEFAULTS).
Ретро-записи 1907–1922 (заставка title, казино reno, заведения saloon / hotel / home, концовка ending) —
реставрации с Wikimedia Commons, общественное достояние (кроме «Лебедя» — CC BY-SA 3.0). Заведения играют
внутри городов: ключ интерьера или музыкальная зона на городской карте (music_zones в data/locations.json).

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
| title_1 | Mischa Elman, Josef Bonime (1919) | Massenet — Méditation (Thaïs) | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AElman_74341_NR.ogg) | общественное достояние |
| title_2 | Enrico Caruso (1920) | Handel — Ombra mai fu | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AEnrico_Caruso%2C_George_Frideric_Handel%2C_Ombra_mai_fu_%28Serse%29.ogg) | общественное достояние |
| title_3 | John Michel, cello | Saint-Saëns — The Swan | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AJOHN_MICHEL_CELLO-SAINT_SAENS_CARNIVAL_OF_ANIMALS_THE_SWAN.ogg) | CC BY-SA 3.0 — указать автора в титрах, файл под той же лицензией |
| title_4 | Paul Whiteman and His Orchestra (1922) | Three O'Clock in the Morning | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AThree_O%27clock_In_The_Morning.ogg) | общественное достояние |
| reno_1 | Billy Jones (1921), restored by Adam Cuerden | Ain't We Got Fun | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AAin%27t_we_got_fun_-_Billy_Jones.ogg) | общественное достояние |
| reno_2 | Zez Confrey (1921) | Kitten on the Keys | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AZez_Confrey_-_Kitten_on_the_Keys.ogg) | общественное достояние |
| reno_3 | Eubie Blake (1922) | I'm Just Wild About Harry | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AEubie_Blake_-_Just_Wild_about_Harry.ogg) | общественное достояние |
| reno_4 | Al Jolson (1920) | Gershwin — Swanee | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AAl_Jolson%2C_George_Gershwin%2C_Irving_Caesar%2C_Swanee_1920.ogg) | общественное достояние |
| reno_5 | Imperial Marimba Band | Twelfth Street Rag | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3ATwelfth_Street_Rag.ogg) | общественное достояние |
| reno_6 | Original Dixieland Jass Band (1917) | Livery Stable Blues | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AOriginal_Dixieland_Jass_Band_-_Livery_Stable_Blues_%281917%29_alternate_edit.ogg) | общественное достояние |
| reno_7 | Warren Trachtman, piano | Bowman — 12th Street Rag | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AEuday_Louis_Bowman%27s_%2212th_Street_Rag%22%2C_performed_by_Warren_Trachtman.ogg) | общественное достояние |
| saloon_1 | Scott Joplin, piano roll (1916) | Maple Leaf Rag | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AMaple_Leaf_Rag_-_played_by_Scott_Joplin_1916_sample.ogg) | общественное достояние |
| saloon_2 | Scott Joplin, piano roll (1916) | Pleasant Moments | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3APleasant_Moments_Piano_Roll.ogg) | общественное достояние |
| saloon_3 | Victor Military Band (1914) | Handy — Memphis Blues | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AVictor_Military_Band-The_Memphis_Blues.ogg) | общественное достояние |
| saloon_4 | Mamie Smith (1920) | Crazy Blues | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AMamie_Smith%2C_Crazy_Blues.ogg) | общественное достояние |
| saloon_5 | (1922) | Save a Little Dram for Me | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3ASave_a_Little_Dram_for_Me.ogg) | общественное достояние |
| saloon_6 | (1908) | Florodora — Tell Me, Pretty Maiden | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AFlorodora_-_Tell_me_pretty_maiden.ogg) | общественное достояние |
| saloon_7 | Lillian Russell (1912) | Come Down Ma Evenin' Star | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3ALillian_Russell_-_Come_Down_Ma_Evenin%27_Star.ogg) | общественное достояние |
| saloon_8 | Pietro Frosini, accordion (1916) | New York Blues | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3APietro_Frosini_-_New_York_Blues_%281916%29_-_hiss_reduced.ogg) | общественное достояние |
| saloon_9 | (1914) | Berlin — I Want to Go Back to Michigan | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AI_Want_to_Go_Back_to_Michigan.ogg) | общественное достояние |
| saloon_10 | Arthur Fields (1918) | Berlin — Oh! How I Hate to Get Up in the Morning | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AIrving_Berlin_-_Arthur_Fields_-_Oh%21_How_I_Hate_To_Get_Up_In_The_Morning.ogg) | общественное достояние |
| saloon_11 | Edward Meeker (1908) | Take Me Out to the Ball Game | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AMeekerBallGame.ogg) | общественное достояние |
| hotel_1 | Enrico Caruso, Nellie Melba (1907) | Puccini — O soave fanciulla | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AEnrico_Caruso_-_Nellie_Melba_-_La_boh%C3%A8me_-_O_soave_fanciulla_%28restored%29.ogg) | общественное достояние |
| hotel_2 | Enrico Caruso, Geraldine Farrar (1912) | Massenet — Manon | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AEnrico_Caruso_-_Geraldine_Farrar_-_Jules_Massenet_-_Manon_-_On_L%27appelle_Manon.ogg) | общественное достояние |
| hotel_3 | Enrico Caruso, Marcel Journet (1910) | Gounod — Faust: O merveille! | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3ACaruso%2C_Journet%2C_Charles_Gounod%27s_Faust%2C_%27O_merveille%21_..._A_moi_les_plaisirs%27.ogg) | общественное достояние |
| hotel_4 | Enrico Caruso (1916) | Massenet — Le Cid: O Souverain | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AJules_Massenet%2C_Enrico_Caruso%2C_O_Souverain%2C_O_Juge%2C_O_Pere.ogg) | общественное достояние |
| hotel_5 | Marguerita Sylva (1910) | Massenet — Le Cid: Pleurez, mes yeux | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AMassenet_-_Le_Cid_-_Pleurez%2C_pleurez%2C_mes_yeux.ogg) | общественное достояние |
| hotel_6 | (1910) | Wagner — Preislied (Die Meistersinger) | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3ARichard_Wagner_-_Preisleid_from_Die_Meistersinger_von_N%C3%BCrnberg_sung_by_Leo_Slezak_3.ogg) | общественное достояние |
| hotel_7 | Hurtado Brothers Royal Marimba Band (1916) | Villoldo — El Choclo | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AEl_Choclo_%281916%29.mp3) | общественное достояние |
| home_1 | Frank C. Stanley (1910) | Auld Lang Syne | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AAuld_Lang_Syne.ogg) | общественное достояние |
| home_2 | Ada Jones, Billy Murray (1909) | Shine On, Harvest Moon | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AAda_Jones_and_Billy_Murray_-_Shine_On%2C_Harvest_Moon.ogg) | общественное достояние |
| home_3 | Edward M. Favor (1910) | How Can They Tell That I'm Irish? | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AHow_Can_They_Tell_That_I%27m_Irish.ogg) | общественное достояние |
| home_4 | Frank C. Stanley, Elise Stevenson (1908) | Battle Hymn of the Republic | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3ABattle_Hymn_of_the_Republic%2C_Frank_C._Stanley%2C_Elise_Stevenson.ogg) | общественное достояние |
| ending_1 | Frederick Wheeler (1914) | Keep the Home Fires Burning | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AKeep_the_Home_Fires_Burning_-_Frederick_Wheeler.ogg) | общественное достояние |
| ending_2 | Enrico Caruso, Giuseppe de Luca (1918) | Verdi — La forza del destino | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AEnrico_Caruso%2C_Giuseppe_de_Luca%2C_Giuseppe_Verdi%2C_N%C3%A8_gustare_m%27%C3%A8_dato_un%27ora_%28La_forza_del_destino%29.ogg) | общественное достояние |
| ending_3 | Reed Miller (1913) | Sullivan — The Lost Chord | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File%3AArthur_Sullivan%2C_The_Lost_Chord%2C_Reed_Miller_1913_%28restored_1%29.ogg) | общественное достояние |

Строки атрибуции для титров (формат Kevin MacLeod):

- world_2: "Penumbra" Kevin MacLeod (incompetech.com), Licensed under Creative Commons: By Attribution 4.0 License, http://creativecommons.org/licenses/by/4.0/
- caves_1: "Lightless Dawn" Kevin MacLeod (incompetech.com), Licensed under Creative Commons: By Attribution 4.0 License, http://creativecommons.org/licenses/by/4.0/
- lab_1: "Static Motion" Kevin MacLeod (incompetech.com), Licensed under Creative Commons: By Attribution 4.0 License, http://creativecommons.org/licenses/by/4.0/
- raiders_1: "Interloper" Kevin MacLeod (incompetech.com), Licensed under Creative Commons: By Attribution 4.0 License, http://creativecommons.org/licenses/by/4.0/
- junktown_1: "Mesmerize" Kevin MacLeod (incompetech.com), Licensed under Creative Commons: By Attribution 4.0 License, http://creativecommons.org/licenses/by/4.0/
- vats_1: "Ossuary 1 - A Beginning" Kevin MacLeod (incompetech.com), Licensed under Creative Commons: By Attribution 4.0 License, http://creativecommons.org/licenses/by/4.0/

CC BY 3.0 (world_1, world_3, desert_1, combat_1 — Alexandr Zhelanov; hub_1 — Matthew Pablo):
указать автора в титрах (строки атрибуции свести при финальной сборке титров).
