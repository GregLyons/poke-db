/*
CREATE TABLES FOR ENTITIES
*/

-- LGPE counts as its own generation; we use it for entities which are LGPE-exclusive
CREATE TABLE generation (
  generation_id TINYINT NOT NULL UNSIGNED UNIQUE, /* 100 refers to LGPE, otherwise matches generation number */
  generation_code VARCHAR(4) NOT NULL UNIQUE,

  PRIMARY KEY (gen_id)
);

CREATE TABLE description (
  description_id MEDIUMINT NOT NULL UNSIGNED AUTO_INCREMENT,
  description_text TINYTEXT NOT NULL UNIQUE,

  PRIMARY KEY (description_id)
);

CREATE TABLE sprite (
  sprite_id MEDIUMINT NOT NULL UNSIGNED AUTO_INCREMENT,
  sprite_url TINYTEXT NOT NULL UNIQUE,

  PRIMARY KEY (sprite_id)
);

-- E.g. Red/Blue (RB) belongs to one version group
CREATE TABLE version_group (
  generation_id TINYINT NOT NULL UNSIGHNED,
  version_group_id TINYINT NOT NULL UNSIGNED AUTO_INCREMENT,
  version_group_code VARCHAR(5) NOT NULL UNIQUE,

  PRIMARY KEY (generation_id, version_group_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id)
);

CREATE TABLE ability (
  generation_id TINYINT NOT NULL UNSIGHNED,
  ability_id SMALLINT NOT NULL UNSIGNED AUTO_INCREMENT
  ability_name VARCHAR(45) NOT NULL,
  ability_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT NOT NULL UNSIGNED,
  affects_item TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (generation_id, ability_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id),
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
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
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
);

CREATE TABLE effect (
  effect_id TINYINT NOT NULL UNSIGNED AUTO_INCREMENT,
  effect_name VARCHAR(45) NOT NULL UNIQUE,
  effect_formatted_name VARCHAR(45) NOT NULL UNIQUE,
  introduced TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (effect_id),
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
);

CREATE TABLE usage_method (
  usage_method_id TINYINT NOT NULL AUTO_INCREMENT,
  usage_method_name VARCHAR(45) NOT NULL UNIQUE,
  usage_method_formatted_name VARCHAR(45) NOT NULL UNIQUE,
  introduced TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (usage_method_id),
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
);

CREATE TABLE status_ailment (
  status_ailment_id TINYINT NOT NULL AUTO_INCREMENT,
  status_ailment_name VARCHAR(45) NOT NULL UNIQUE,
  status_ailment_formatted_name VARCHAR(45) NOT NULL UNIQUE,

  PRIMARY KEY (status_ailment_id)
);

CREATE TABLE ptype (
  generation_id TINYINT NOT NULL UNSIGNED,
  ptype_id SMALLINT NOT NULL AUTO_INCREMENT,
  ptype_name VARCHAR(45) NOT NULL,
  ptype_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (generation_id, ptype_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id),
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
);

CREATE TABLE move (
  generation_id TINYINT NOT NULL UNSIGNED,
  move_id SMALLINT NOT NULL AUTO_INCREMENT,
  move_name VARCHAR(45) NOT NULL,
  move_formatted_name VARCHAR(45) NOT NULL,
  introduced TINYINT NOT NULL UNSIGNED,
  move_ptype TINYINT NOT NULL UNSIGNED,
  move_power SMALLINT UNSIGNED /* Non-damaging moves, fixed damage moves, and variable damage moves can have NULL */,
  move_pp TINYINT NOT NULL UNSIGNED,
  move_accuracy TINYINT UNSIGNED /* moves which bypass accuracy checks can have NULL */
  move_category ENUM('physical', 'special', 'status', 'varies'),
  move_priority TINYINT NOT NULL,
  move_contact TINYINT NOT NULL UNSIGNED,
  move_target ENUM('adjacent_ally', 'adjacent_foe', 'all_adjacent','all_adjacent_foes', 'all', 'all_allies', 'all_foes', 'any', 'any_adjacent', 'user', 'user_and_all_allies', 'user_or_adjacent_ally')

  PRIMARY KEY (generation_id, move_id),
  FOREIGN KEY (generation_id) REFERENCES generation(generation_id),
  FOREIGN KEY (introduced) REFERENCES generation(generation_id),
  FOREIGN KEY (ptype) REFERENCES ptype(generation_id, ptype_id)
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
  FOREIGN KEY (introduced) REFERENCES generation(generation_id)
);

/*
CREATE TABLES FOR RELATIONSHIPS
*/

CREATE TABLE move_requires_ptype (
  move_generation_id TINYINT NOT NULL UNSIGNED,
  move_id SMALLINT NOT NULL UNSIGNED,
  ptype_generation_id TINYINT NOT NULL UNSIGNED,
  ptype_id TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (move_generation_id, move_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (move_generation_id, move_id) REFERENCES move(generation_id, move_id),
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
);

CREATE TABLE move_requires_ptype (
  move_generation_id TINYINT NOT NULL UNSIGNED,
  move_id SMALLINT NOT NULL UNSIGNED,
  base_move_generation_id TINYINT NOT NULL UNSIGNED,
  base_move_id SMALLINT NOT NULL UNSIGNED,

  PRIMARY KEY (move_generation_id, move_id, base_move_generation_id, base_move_id),
  FOREIGN KEY (move_generation_id, move_id) REFERENCES move(generation_id, move_id),
  FOREIGN KEY (base_move_generation_id, base_move_id) REFERENCES move(generation_id, move_id)
); 

CREATE TABLE pokemon_evolution (
  prevolution_generation_id TINYINT NOT NULL UNSIGNED,
  prevolution_id SMALLINT NOT NULL UNSIGNED,
  evolution_generation_id TINYINT NOT NULL UNSIGNED,
  evolution_id SMALLINT NOT NULL UNSIGNED,
  evolution_method VARCHAR(100) NOT NULL

  PRIMARY KEY(prevolution_generation_id, prevolution_id, evolution_generation_id, evolution_id),
  FOREIGN KEY (prevolution_generation_id, prevolution_id) REFERENCES pokemon(generation_id, pokemon_id),
  FOREIGN KEY (evolution_generation_id, evolution_id) REFERENCES pokemon(generation_id, pokemon_id)
);

-- does not include cosmetic forms
CREATE TABLE pokemon_form (
  base_form_generation_id TINYINT NOT NULL UNSIGNED,
  base_form_id SMALLINT NOT NULL UNSIGNED,
  form_generation_id TINYINT NOT NULL UNSIGNED,
  form_id SMALLINT NOT NULL UNSIGNED,
  form_class ENUM('mega', 'alola', 'galar', 'gmax', 'other'),

  PRIMARY KEY (base_form_generation_id, base_form_id, form_generation_id, form_id),
  FOREIGN KEY (base_form_generation_id, base_form_id) REFERENCES pokemon(generation_id, pokemon_id),
  FOREIGN KEY (form_generation_id, form_id) REFERENCES pokemon(generation_id, pokemon_id)
);

-- we don't store the base stats, typing, etc. of cosmetic forms since they only differ in appearance; to compute those properties for a given cosmetic form, just use the corresponding property of the base form
CREATE TABLE cosmetic_form (
  base_form_generation_id TINYINT NOT NULL UNSIGNED,
  base_form_id SMALLINT NOT NULL UNSIGNED,
  cosmetic_form_generation_id TINYINT NOT NULL UNSIGNED,
  cosmetic_form_id SMALLINT NOT NULL UNSIGNED

  PRIMARY KEY (base_form_generation_id, base_form_id, cosmetic_form_generation_id, cosmetic_form_id),
  FOREIGN KEY (base_form_generation_id, base_form_id) REFERENCES pokemon(generation_id, pokemon_id)
);

-- E.g. Flamethrower is a Fire-type move
CREATE TABLE move_ptype (
  move_generation_id TINYINT NOT NULL UNSIGNED,
  move_id SMALLINT NOT NULL UNSIGNED,
  ptype_generation_id TINYINT NOT NULL UNSIGNED,
  ptype_id TINYINT NOT NULL UNSIGNED,
)