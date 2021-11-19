/*
TABLES FOR ENTITIES
*/

-- LGPE counts as its own generation. we use it for entities which are LGPE-exclusive
CREATE TABLE IF NOT EXISTS generation (
  generation_id TINYINT UNSIGNED NOT NULL UNIQUE,
  generation_code VARCHAR(4) NOT NULL UNIQUE,

  PRIMARY KEY (generation_id)
);

CREATE TABLE IF NOT EXISTS pdescription (
  pdescription_id MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,
  pdescription_text VARCHAR(255) NOT NULL,
  pdescription_index TINYINT UNSIGNED NOT NULL,
  pdescription_type ENUM('ability', 'item', 'move') NOT NULL,
  entity_name VARCHAR(255) NOT NULL,

  PRIMARY KEY (pdescription_id)
);

CREATE TABLE IF NOT EXISTS sprite (
  sprite_id MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,
  sprite_path TINYTEXT NOT NULL,

  PRIMARY KEY (sprite_id)
);

-- E.g. Red/Blue (RB) belongs to one version group
CREATE TABLE IF NOT EXISTS version_group (
  generation_id TINYINT UNSIGNED NOT NULL,
  version_group_id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
  version_group_code VARCHAR(5) NOT NULL UNIQUE,
  version_group_formatted_name VARCHAR(45) NOT NULL UNIQUE,

  PRIMARY KEY (generation_id, version_group_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  
  INDEX (version_group_id)
);

CREATE TABLE IF NOT EXISTS ability (
  generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  ability_name VARCHAR(45) NOT NULL,
  ability_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (generation_id, ability_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX (ability_id),
  INDEX gen_alpha (generation_id, ability_formatted_name),
  INDEX intro (introduced)
);

CREATE TABLE IF NOT EXISTS item (
  generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  item_name VARCHAR(45) NOT NULL,
  item_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT UNSIGNED NOT NULL,
  item_class VARCHAR(45),

  PRIMARY KEY (generation_id, item_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX (item_id),
  INDEX gen_alpha (generation_id, item_formatted_name),
  INDEX intro (introduced),
  INDEX by_class (generation_id, item_class)
);

CREATE TABLE IF NOT EXISTS effect (
  effect_id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
  effect_name VARCHAR(45) NOT NULL UNIQUE,
  effect_formatted_name VARCHAR(45) NOT NULL UNIQUE,
  introduced TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (effect_id),
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX (effect_id)
);

CREATE TABLE IF NOT EXISTS usage_method (
  usage_method_id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
  usage_method_name VARCHAR(45) NOT NULL UNIQUE,
  usage_method_formatted_name VARCHAR(45) NOT NULL UNIQUE,
  introduced TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (usage_method_id),
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS pstatus (
  pstatus_id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
  pstatus_name VARCHAR(45) NOT NULL UNIQUE,
  pstatus_formatted_name VARCHAR(45) NOT NULL UNIQUE,

  PRIMARY KEY (pstatus_id)
);

CREATE TABLE IF NOT EXISTS ptype (
  generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
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

  PRIMARY KEY (generation_id, pmove_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  
  INDEX (pmove_id),
  INDEX gen_alpha (generation_id, pmove_formatted_name),
  INDEX intro (introduced),
  INDEX by_power (generation_id, pmove_power),
  INDEX by_category (generation_id, pmove_category)
);

-- stats in battle, i.e. attack, defense, evasion, accuracy, critical hit ratio, but not HP
CREATE TABLE IF NOT EXISTS stat (
  stat_id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
  stat_name VARCHAR(45) NOT NULL UNIQUE,
  stat_formatted_name VARCHAR(45) NOT NULL UNIQUE,

  PRIMARY KEY (stat_id)
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
  pokemon_special_defense TINYINT UNSIGNED NOT NULL,
  pokemon_special_attack TINYINT UNSIGNED NOT NULL,
  pokemon_speed TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (generation_id, pokemon_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX (pokemon_id),
  INDEX gen_alpha (generation_id, pokemon_formatted_name),
  INDEX intro (introduced),
  INDEX dex_sort (generation_id, pokemon_dex, introduced),
  INDEX speed_tier (generation_id, pokemon_speed),
  INDEX survive_physical (generation_id, pokemon_hp, pokemon_defense),
  INDEX survive_special (generation_id, pokemon_hp, pokemon_special_defense),
  INDEX damage_physical (generation_id, pokemon_attack),
  INDEX damage_special (generation_id, pokemon_special_attack)
);