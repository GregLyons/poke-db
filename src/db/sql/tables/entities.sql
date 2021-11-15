/*
TABLES FOR ENTITIES
*/

-- LGPE counts as its own generation; we use it for entities which are LGPE-exclusive
CREATE TABLE generation (
  generation_id TINYINT NOT NULL UNSIGNED UNIQUE, /* 100 refers to LGPE, otherwise matches generation number */
  generation_code VARCHAR(4) NOT NULL UNIQUE,

  PRIMARY KEY (gen_id)
);

CREATE TABLE pdescription (
  pdescription_id MEDIUMINT NOT NULL UNSIGNED AUTO_INCREMENT,
  pdescription_text TINYTEXT NOT NULL UNIQUE,

  PRIMARY KEY (pdescription_id)
);

CREATE TABLE sprite (
  sprite_id MEDIUMINT NOT NULL UNSIGNED AUTO_INCREMENT,
  sprite_url TINYTEXT NOT NULL UNIQUE,

  PRIMARY KEY (sprite_id)
);

-- E.g. Red/Blue (RB) belongs to one version group
CREATE TABLE version_group (
  generation_id TINYINT NOT NULL UNSIGNED,
  version_group_id TINYINT NOT NULL UNSIGNED AUTO_INCREMENT,
  version_group_code VARCHAR(5) NOT NULL UNIQUE,

  PRIMARY KEY (generation_id, version_group_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE ability (
  generation_id TINYINT NOT NULL UNSIGNED,
  ability_id SMALLINT NOT NULL UNSIGNED AUTO_INCREMENT
  ability_name VARCHAR(45) NOT NULL,
  ability_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT NOT NULL UNSIGNED,
  affects_item TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (generation_id, ability_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX gen_alpha (generation_id, ability_formatted_name),
  INDEX intro (introduced)
);

CREATE TABLE item (
  generation_id TINYINT NOT NULL UNSIGNED,
  item_id SMALLINT NOT NULL UNSIGNED AUTO_INCREMENT,
  item_name VARCHAR(45) NOT NULL,
  item_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT NOT NULL UNSIGNED,
  item_class VARCHAR(45),

  PRIMARY KEY (generation_id, ability_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX gen_alpha (generation_id, item_formatted_name),
  INDEX intro (introduced),
  INDEX by_class (generation_id, item_class)
);

CREATE TABLE effect (
  effect_id TINYINT NOT NULL UNSIGNED AUTO_INCREMENT,
  effect_name VARCHAR(45) NOT NULL UNIQUE,
  effect_formatted_name VARCHAR(45) NOT NULL UNIQUE,
  introduced TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (effect_id),
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE usage_method (
  usage_method_id TINYINT NOT NULL AUTO_INCREMENT,
  usage_method_name VARCHAR(45) NOT NULL UNIQUE,
  usage_method_formatted_name VARCHAR(45) NOT NULL UNIQUE,
  introduced TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (usage_method_id),
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE pstatus (
  pstatus_id TINYINT NOT NULL AUTO_INCREMENT,
  pstatus_name VARCHAR(45) NOT NULL UNIQUE,
  pstatus_formatted_name VARCHAR(45) NOT NULL UNIQUE,

  PRIMARY KEY (pstatus_id)
);

CREATE TABLE ptype (
  generation_id TINYINT NOT NULL UNSIGNED,
  ptype_id SMALLINT NOT NULL AUTO_INCREMENT,
  ptype_name VARCHAR(45) NOT NULL,
  ptype_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (generation_id, ptype_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE pmove (
  generation_id TINYINT NOT NULL UNSIGNED,
  pmove_id SMALLINT NOT NULL AUTO_INCREMENT,
  pmove_name VARCHAR(45) NOT NULL,
  pmove_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT NOT NULL UNSIGNED,
  ptype_generation_id TINYINT NOT NULL UNSIGNED,
  ptype_id TINYINT NOT NULL UNSIGNED,
  pmove_power SMALLINT UNSIGNED /* Non-damaging pmoves, fixed damage pmoves, and variable damage pmoves can have NULL */,
  pmove_pp TINYINT NOT NULL UNSIGNED,
  pmove_accuracy TINYINT UNSIGNED /* pmoves which bypass accuracy checks can have NULL */
  pmove_category ENUM('physical', 'special', 'status', 'varies'),
  pmove_priority TINYINT NOT NULL,
  pmove_contact TINYINT NOT NULL UNSIGNED,
  pmove_target ENUM('adjacent_ally', 'adjacent_foe', 'all_adjacent','all_adjacent_foes', 'all', 'all_allies', 'all_foes', 'any', 'any_adjacent', 'user', 'user_and_all_allies', 'user_or_adjacent_ally')

  PRIMARY KEY (generation_id, pmove_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (introduced) REFERENCES generation(generation_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (usage_method) 
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  
  INDEX gen_alpha (generation_id, pmove_formatted_name),
  INDEX intro (introduced),
  INDEX by_ptype (generation_id, ptype_generation_id, ptype_id),
  INDEX by_power (generation_id, move_power),
  INDEX by_category (generation_id, move_category)
);

-- stats in battle, i.e. attack, defense, evasion, accuracy, critical hit ratio, but not HP
CREATE TABLE stat (
  stat_id TINYINT NOT NULL AUTO_INCREMENT,
  stat_name VARCHAR(45) NOT NULL UNIQUE,
  stat_formatted_name VARCHAR(45) NOT NULL UNIQUE,

  PRIMARY KEY (stat_id)
);

-- does not include cosmetic forms
CREATE TABLE pokemon (
  generation_id TINYINT NOT NULL UNSIGNED,
  pokemon_id SMALLINT NOT NULL UNSIGNED AUTO_INCREMENT,
  pokemon_name VARCHAR(45) NOT NULL,
  pokemon_formatted_name VARCHAR(45) NOT NULL,
  pokemon_species VARCHAR(45) NOT NULL,
  pokemon_dex SMALLINT NOT NULL UNSIGNED, /* national dex number */
  pokemon_height DECIMAL(4,1) NOT NULL UNSIGNED, /* meters */
  pokemon_weight DECIMAL(4,1) NOT NULL UNSIGNED, /* kilograms */
  introduced TINYINT NOT NULL UNSIGNED,
  pokemon_hp TINYINT NOT NULL UNSIGNED,
  pokemon_attack TINYINT NOT NULL UNSIGNED,
  pokemon_defense TINYINT NOT NULL UNSIGNED,
  pokemon_special_defense TINYINT NOT NULL UNSIGNED,
  pokemon_special_attack TINYINT NOT NULL UNSIGNED,
  pokemon_speed TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (generation_id, pokemon_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (introduced) REFERENCES generation(generation_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX gen_alpha (generation_id, pokemon_formatted_name),
  INDEX intro (introduced),
  INDEX dex_sort (generation_id, pokemon_dex, introduced),
  INDEX speed_tier (generation_id, speed),
  INDEX survive_physical (generation_id, hp, defense),
  INDEX survive_special (generation_id, hp, special_defense),
  INDEX damage_physical (generation_id, attack),
  INDEX damage_special (generation_id, special_attack),
);