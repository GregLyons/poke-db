/*
TABLES FOR ENTITIES
*/

-- We will handle LGPE in an entirely separate table.
CREATE TABLE IF NOT EXISTS generation (
  generation_id TINYINT UNSIGNED NOT NULL UNIQUE,
  generation_code VARCHAR(4) NOT NULL UNIQUE,

  PRIMARY KEY (generation_id)
);

-- The combination (pdescription_index, pdescription_type, entity_name) gives a unique identifier which we use for inserting data, even though technically only pdescription_id and pdescription_text are necessary.
CREATE TABLE IF NOT EXISTS pdescription (
  pdescription_id MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,
  pdescription_text VARCHAR(255) NOT NULL,
  pdescription_index TINYINT UNSIGNED NOT NULL,
  pdescription_entity_class ENUM('ability', 'item', 'move') NOT NULL,
  pdescription_entity_name VARCHAR(255) NOT NULL,

  PRIMARY KEY (pdescription_id)
);

-- While sprite_path should be unique, combining it with entity_name to get another unique identifier makes for easier selection when inserting data.
CREATE TABLE IF NOT EXISTS sprite (
  sprite_id MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,
  sprite_path TINYTEXT NOT NULL,
  sprite_entity_name VARCHAR(255) NOT NULL,

  PRIMARY KEY (sprite_id)
);

-- E.g. Red/Blue (RB) belongs to one version group
CREATE TABLE IF NOT EXISTS version_group (
  version_group_id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
  version_group_code VARCHAR(5) NOT NULL UNIQUE,
  version_group_name VARCHAR(45) NOT NULL UNIQUE,
  version_group_formatted_name VARCHAR(45) NOT NULL UNIQUE,
  introduced TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (version_group_id),
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS ability (
  generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  ability_name VARCHAR(45) NOT NULL,
  ability_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT UNSIGNED NOT NULL,
  ability_ps_id VARCHAR(45) NOT NULL,

  PRIMARY KEY (generation_id, ability_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX (ability_id),
  INDEX gen_alpha (generation_id, ability_name),
  INDEX gen_ps_id (generation_id, ability_ps_id),
  INDEX intro (introduced)
);

CREATE TABLE IF NOT EXISTS item (
  generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  item_name VARCHAR(45) NOT NULL,
  item_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT UNSIGNED NOT NULL,
  item_class ENUM('berry','choice', 'drive', 'gem', 'incense', 'mega_stone', 'memory', 'other', 'plate', 'power', 'stat_enhancer', 'type_enhancer', 'z_crystal'),
  item_ps_id VARCHAR(45) NOT NULL,

  PRIMARY KEY (generation_id, item_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX (item_id),
  INDEX gen_alpha (generation_id, item_name),
  INDEX gen_ps_id (generation_id, item_ps_id),
  INDEX intro (introduced),
  INDEX by_class (generation_id, item_class)
);

CREATE TABLE IF NOT EXISTS effect (
  generation_id TINYINT UNSIGNED NOT NULL,
  effect_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  effect_name VARCHAR(45) NOT NULL,
  effect_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT UNSIGNED NOT NULL,
  effect_description VARCHAR(400) NOT NULL,
  effect_unformatted_name VARCHAR(45) NOT NULL,
  effect_class ENUM('crit', 'misc', 'restore', 'cost', 'ability', 'type', 'stat', 'switch', 'accuracy', 'power', 'size', 'contact', 'speed', 'ground'),

  PRIMARY KEY (generation_id, effect_id),
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX (effect_id),
  INDEX gen_unformatted_name (generation_id, effect_unformatted_name)
);

CREATE TABLE IF NOT EXISTS field_state (
  generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  field_state_name VARCHAR(45) NOT NULL,
  field_state_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT UNSIGNED NOT NULL,
  field_state_damage_percent DECIMAL(5, 2),
  field_state_max_layers TINYINT UNSIGNED NOT NULL,
  field_state_only_grounded TINYINT UNSIGNED NOT NULL,
  field_state_class ENUM('entry_hazard', 'other', 'pledge', 'room', 'screen', 'terrain', 'weather'),
  field_state_target ENUM('all', 'all_allies', 'all_foes'),
  field_state_description VARCHAR(255) NOT NULL,
  field_state_unformatted_name VARCHAR(45) NOT NULL,

  PRIMARY KEY (generation_id, field_state_id),
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX (field_state_id),
  INDEX gen_unformatted_name (generation_id, field_state_unformatted_name)
);

CREATE TABLE IF NOT EXISTS nature (
  generation_id TINYINT UNSIGNED NOT NULL,
  nature_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  nature_name VARCHAR(45) NOT NULL,
  nature_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT UNSIGNED NOT NULL,
  nature_favorite_flavor VARCHAR(45) NOT NULL,
  nature_disliked_flavor VARCHAR(45) NOT NULL,

  PRIMARY KEY (generation_id, nature_id),
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  INDEX (nature_id)
);

CREATE TABLE IF NOT EXISTS usage_method (
  generation_id TINYINT UNSIGNED NOT NULL,
  usage_method_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  usage_method_name VARCHAR(45) NOT NULL,
  usage_method_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT UNSIGNED NOT NULL,
  usage_method_description VARCHAR(255) NOT NULL,
  usage_method_unformatted_name VARCHAR(45) NOT NULL,

  PRIMARY KEY (generation_id, usage_method_id),
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX (usage_method_id),
  INDEX gen_unformatted_name (generation_id, usage_method_unformatted_name)
);

CREATE TABLE IF NOT EXISTS pstatus (
  generation_id TINYINT UNSIGNED NOT NULL,
  pstatus_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  pstatus_name VARCHAR(45) NOT NULL,
  pstatus_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT UNSIGNED NOT NULL,
  pstatus_description VARCHAR(400) NOT NULL,
  pstatus_volatile TINYINT UNSIGNED NOT NULL,
  pstatus_unformatted_name VARCHAR(45) NOT NULL,

  PRIMARY KEY (generation_id, pstatus_id),

  INDEX (pstatus_id),
  INDEX gen_unformatted_name (generation_id, pstatus_unformatted_name)
);

CREATE TABLE IF NOT EXISTS ptype (
  generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  ptype_name VARCHAR(45) NOT NULL,
  ptype_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (generation_id, ptype_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX (ptype_id)
);

CREATE TABLE IF NOT EXISTS pmove (
  generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  pmove_name VARCHAR(45) NOT NULL,
  pmove_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT UNSIGNED NOT NULL,
  pmove_power SMALLINT UNSIGNED, /* Non-damaging pmoves, fixed damage pmoves, and variable damage pmoves can have NULL */
  pmove_pp TINYINT UNSIGNED NOT NULL,
  pmove_accuracy TINYINT UNSIGNED, /* pmoves which bypass accuracy checks can have NULL */
  pmove_category ENUM('physical', 'special', 'status', 'varies'),
  pmove_priority TINYINT NOT NULL,
  pmove_contact TINYINT UNSIGNED NOT NULL,
  pmove_target ENUM('adjacent_ally', 'adjacent_foe', 'all_adjacent','all_adjacent_foes', 'all', 'all_allies', 'all_foes', 'any', 'any_adjacent', 'user', 'user_and_all_allies', 'user_or_adjacent_ally'),
  pmove_removed_from_swsh TINYINT UNSIGNED NOT NULL,
  pmove_removed_from_bdsp TINYINT UNSIGNED NOT NULL,
  pmove_ptype_name VARCHAR(45) NOT NULL,
  pmove_ps_id VARCHAR(45) NOT NULL,

  PRIMARY KEY (generation_id, pmove_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  
  INDEX (pmove_id),
  INDEX gen_alpha (generation_id, pmove_name),
  INDEX gen_ps_id (generation_id, pmove_ps_id),
  INDEX intro (introduced),
  INDEX by_power (generation_id, pmove_power),
  INDEX by_category (generation_id, pmove_category),
  INDEX by_ptype (pmove_ptype_name)
);

-- stats in battle, i.e. attack, defense, evasion, accuracy, critical hit ratio, but not HP
CREATE TABLE IF NOT EXISTS stat (
  generation_id TINYINT UNSIGNED NOT NULL,
  stat_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  stat_name VARCHAR(45) NOT NULL,
  stat_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT UNSIGNED NOT NULL,
  stat_description VARCHAR(255) NOT NULL,
  stat_unformatted_name VARCHAR(45) NOT NULL,

  PRIMARY KEY (generation_id, stat_id),
  INDEX (stat_id),
  INDEX gen_unformatted_name (generation_id, stat_unformatted_name)
);

-- does not include cosmetic forms
CREATE TABLE IF NOT EXISTS pokemon (
  generation_id TINYINT UNSIGNED NOT NULL,
  pokemon_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  pokemon_name VARCHAR(45) NOT NULL,
  pokemon_formatted_name VARCHAR(45) NOT NULL,
  pokemon_species VARCHAR(45) NOT NULL,
  pokemon_dex SMALLINT UNSIGNED NOT NULL, /* national dex number */
  pokemon_height DECIMAL(4,1) UNSIGNED NOT NULL, /* meters */
  pokemon_weight DECIMAL(4,1) UNSIGNED NOT NULL, /* kilograms */
  introduced TINYINT UNSIGNED NOT NULL,
  pokemon_hp TINYINT UNSIGNED NOT NULL,
  pokemon_attack TINYINT UNSIGNED NOT NULL,
  pokemon_defense TINYINT UNSIGNED NOT NULL,
  pokemon_special_attack TINYINT UNSIGNED NOT NULL,
  pokemon_special_defense TINYINT UNSIGNED NOT NULL,
  pokemon_speed TINYINT UNSIGNED NOT NULL,
  pokemon_base_stat_total SMALLINT UNSIGNED NOT NULL,
  pokemon_form_class ENUM('gmax', 'mega', 'alola', 'galar', 'hisui', 'other', 'base', 'cosmetic', 'type', 'battle'),
  pokemon_ps_id VARCHAR(45) NOT NULL,
  pokemon_pokeapi_name VARCHAR(45) NOT NULL,
  pokemon_pokeapi_id VARCHAR(45) NOT NULL,
  pokemon_ptype_name_1 VARCHAR(45) NOT NULL,
  pokemon_ptype_name_2 VARCHAR(45) NOT NULL,
  pokemon_removed_from_swsh TINYINT UNSIGNED NOT NULL,
  pokemon_removed_from_bdsp TINYINT UNSIGNED NOT NULL,
  pokemon_male_rate DECIMAL(4, 1) UNSIGNED NOT NULL,
  pokemon_female_rate DECIMAL(4, 1) UNSIGNED NOT NULL,
  pokemon_genderless TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (generation_id, pokemon_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX (pokemon_id),
  INDEX gen_alpha (generation_id, pokemon_name),
  INDEX gen_ps_id (generation_id, pokemon_ps_id),
  INDEX by_species (generation_id, pokemon_species),
  INDEX intro (introduced),
  INDEX dex_sort (generation_id, pokemon_dex, introduced),
  INDEX speed_tier (generation_id, pokemon_speed),
  INDEX base_stat_total (generation_id, pokemon_base_stat_total),
  INDEX survive_physical (generation_id, pokemon_hp, pokemon_defense),
  INDEX survive_special (generation_id, pokemon_hp, pokemon_special_defense),
  INDEX damage_physical (generation_id, pokemon_attack),
  INDEX damage_special (generation_id, pokemon_special_attack),
  INDEX by_ptype (generation_id, pokemon_ptype_name_1, pokemon_ptype_name_2),
  INDEX by_form (generation_id, pokemon_form_class)
);