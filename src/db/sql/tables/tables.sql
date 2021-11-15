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

/*
TABLES FOR RELATIONSHIPS
*/

/*
1-to-1
*/

/*
pmove
*/ 
CREATE TABLE pmove_requires_ptype (
  pmove_generation_id TINYINT NOT NULL UNSIGNED,
  pmove_id SMALLINT NOT NULL UNSIGNED,
  ptype_generation_id TINYINT NOT NULL UNSIGNED,
  ptype_id TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (pmove_generation_id, pmove_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

/*
1-to-n 
*/
/*
pmove
*/
CREATE TABLE pmove_requires_pmove (
  pmove_generation_id TINYINT NOT NULL UNSIGNED,
  pmove_id SMALLINT NOT NULL UNSIGNED,
  base_pmove_generation_id TINYINT NOT NULL UNSIGNED,
  base_pmove_id SMALLINT NOT NULL UNSIGNED,

  PRIMARY KEY (pmove_generation_id, pmove_id, base_pmove_generation_id, base_pmove_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (base_pmove_generation_id, base_pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
); 

CREATE TABLE pokemon_evolution (
  prevolution_generation_id TINYINT NOT NULL UNSIGNED,
  prevolution_id SMALLINT NOT NULL UNSIGNED,
  evolution_generation_id TINYINT NOT NULL UNSIGNED,
  evolution_id SMALLINT NOT NULL UNSIGNED,
  evolution_method VARCHAR(100) NOT NULL

  PRIMARY KEY(prevolution_generation_id, prevolution_id, evolution_generation_id, evolution_id),
  FOREIGN KEY (prevolution_generation_id, prevolution_id) REFERENCES pokemon(generation_id, pokemon_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (evolution_generation_id, evolution_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_prevolution_evolution (evolution_generation_id, evolution_id, prevolution_generation_id, prevolution_id)
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
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (form_generation_id, form_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- we don't store the base stats, typing, etc. of cosmetic forms since they only differ in appearance; to compute those properties for a given cosmetic form, just use the corresponding property of the base form
CREATE TABLE cosmetic_form (
  base_form_generation_id TINYINT NOT NULL UNSIGNED,
  base_form_id SMALLINT NOT NULL UNSIGNED,
  cosmetic_form_generation_id TINYINT NOT NULL UNSIGNED,
  cosmetic_form_id SMALLINT NOT NULL UNSIGNED

  PRIMARY KEY (base_form_generation_id, base_form_id, cosmetic_form_generation_id, cosmetic_form_id),
  FOREIGN KEY (base_form_generation_id, base_form_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- for Natural Gift
CREATE TABLE item_ptype (
  item_generation_id TINYINT NOT NULL UNSIGNED,
  item_id SMALLINT NOT NULL UNSIGNED,
  ptype_generation_id TINYINT NOT NULL UNSIGNED,
  ptype_id TINYINT NOT NULL UNSIGNED,
  item_power TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (item_generation_id, item_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

/*
m-to-n
*/

/*
pokemon
*/
CREATE TABLE pokemon_ptype (
  pokemon_generation_id TINYINT NOT NULL UNSIGNED,
  pokemon_id SMALLINT NOT NULL UNSIGNED,
  ptype_generation_id TINYINT NOT NULL UNSIGNED,
  ptype_id TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (pokemon_generation_id, pokemon_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (pokemon_generation_id, pokemon_id) REFERENCES pokemon(generation_id, pokemon_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pokemon_ptype_generation_id (ptype_generation_idptype, _id, pokemon_generation_id, pokemon_id)
);

CREATE TABLE pokemon_pmove (
  pokemon_generation_id TINYINT NOT NULL UNSIGNED,
  pokemon_id SMALLINT NOT NULL UNSIGNED,
  pmove_generation_id TINYINT NOT NULL UNSIGNED,
  pmove_id SMALLINT NOT NULL UNSIGNED,
  learn_method VARCHAR(4),

  PRIMARY KEY (pokemon_generation_id, pokemon_id, pmove_generation_id, pmove_id),
  FOREIGN KEY (pokemon_generation_id, pokemon_id) REFERENCES pokemon(generation_id, pokemon_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
  
  INDEX opposite_pokemon_pmove (pmove_generation_id, pmove_id, pokemon_generation_id, pokemon_id)
);

CREATE TABLE pokemon_ability (
  pokemon_generation_id TINYINT NOT NULL UNSIGNED,
  pokemon_id SMALLINT NOT NULL UNSIGNED,
  ability_generation_id TINYINT NOT NULL UNSIGNED,
  ability_id SMALLINT NOT NULL UNSIGNED,
  ability_slot ENUM('1', '2', 'Hidden'),

  PRIMARY KEY (pokemon_generation_id, pokemon_id, ability_generation_id, ability_id), 
  FOREIGN KEY (pokemon_generation_id, pokemon_id) REFERENCES pokemon(generation_id, pokemon_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES (generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  
  INDEX opposite_pokemon_ability (ability_generation_id, ability_id, pokemon_generation_id, pokemon_id)
);

/*
ptype
*/
CREATE TABLE ptype_matchup (
  attacking_ptype_generation_id TINYINT NOT NULL UNSIGNED,
  attacking_ptype_id TINYINT NOT NULL UNSIGNED,
  defending_ptype_generation_id TINYINT NOT NULL UNSIGNED,
  defending_ptype_id TINYINT NOT NULL UNSIGNED,
  multiplier DECIMAL(3,2) NOT NULL UNSIGNED,

  PRIMARY KEY (attacking_ptype_generation_id, attacking_ptype_id, defending_ptype_generation_id, defending_ptype_id),
  FOREIGN KEY (attacking_ptype_generation_id, attacking_ptype_id) REFERENCES ptype(generation_id, ptype_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (defending_ptype_generation_id, defending_ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  
  INDEX opposite_attacking_ptype_defending_ptype (defending_ptype_generation_id, defending_ptype_id, attacking_ptype_generation_id, attacking_ptype_id)
);

/*
pmove
*/
CREATE TABLE pmove_modifies_stat (
  pmove_generation_id TINYINT NOT NULL UNSIGNED,
  pmove_id SMALLINT NOT NULL UNSIGNED,
  stat_id TINYINT NOT NULL UNSIGNED,
  stage TINYINT NOT NULL, /* 0 for pmoves which modify stat but not the stage */
  multiplier DECIMAL(3,2) NOT NULL UNSIGNED, /* 0.0 for pmoves which modify stat but not via a multiplier */
  chance DECIMAL(5,2) NOT NULL UNSIGNED,
  recipient ENUM('target', 'user'),

  PRIMARY KEY (pmove_generation_id, pmove_id, stat_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (stat_id) REFERENCES (stat_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_stat (stat_id, pmove_generation_id, pmove_id)
);

CREATE TABLE pmove_effect (
  pmove_generation_id TINYINT NOT NULL UNSIGNED,
  pmove_id SMALLINT NOT NULL UNSIGNED,
  effect_id TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (pmove_generation_id, pmove_id, effect_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (effect_id) REFERENCES effect(effect_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE

  INDEX opposite_pmove_effect (effect_id, pmove_generation_id, pmove_id)
);

CREATE TABLE pmove_causes_pstatus (
  pmove_generation_id TINYINT NOT NULL UNSIGNED,
  pmove_id SMALLINT NOT NULL UNSIGNED,
  pstatus_id TINYINT NOT NULL UNSIGNED,
  chance DECIMAL(5,2) NOT NULL UNSIGNED,

  PRIMARY KEY (pmove_generation_id, pmove_id, pstatus_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pstatus_id) REFERENCES pstatus(pstatus_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE

  INDEX opposite_pmove_causes_pstatus (pstatus_id, pmove_generation_id, pmove_id)
);

CREATE TABLE pmove_resists_pstatus (
  pmove_generation_id TINYINT NOT NULL UNSIGNED,
  pmove_id SMALLINT NOT NULL UNSIGNED,
  pstatus_id TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (pmove_generation_id, pmove_id, pstatus_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pstatus_id) REFERENCES pstatus(pstatus_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_resists_pstatus (pstatus_id, pmove_generation_id, pmove_id)
);

CREATE TABLE pmove_requires_pokemon (
  pmove_generation_id TINYINT NOT NULL UNSIGNED,
  pmove_id SMALLINT NOT NULL UNSIGNED,
  pokemon_generation_id TINYINT NOT NULL UNSIGNED,
  pokemon_id SMALLINT NOT NULL UNSIGNED,

  PRIMARY KEY (pmove_generation_id, pmove_id, pokemon_generation_id, pokemon_id), 
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pokemon_generation_id, pokemon_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_pokemon (pokemon_generation_id, pokemon_id, pmove_generation_id, pmove_id)
);

CREATE TABLE pmove_requires_pokemon (
  pmove_generation_id TINYINT NOT NULL UNSIGNED,
  pmove_id SMALLINT NOT NULL UNSIGNED,
  item_generation_id TINYINT NOT NULL UNSIGNED,
  item_id SMALLINT NOT NULL UNSIGNED,

  PRIMARY KEY (pmove_generation_id, pmove_id, item_generation_id, item_id), 
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_item (item_generation_id, item_id, pmove_generation_id, pmove_id)
);

-- note that Aura Sphere is both a pulse and a ball pmove, so we need an m-to-n relationship
CREATE TABLE pmove_usage_method (
  pmove_generation_id TINYINT NOT NULL UNSIGNED,
  pmove_id SMALLINT NOT NULL UNSIGNED,
  usage_method_id TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (pmove_generation_id, pmove_id, usage_method_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (usage_method_id) REFERENCES usage_method(usage_method_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_usage_method (usage_method_id, pmove_generation_id, pmove_id)
);

/*
ability
*/
CREATE TABLE ability_boosts_ptype (
  ability_generation_id TINYINT NOT NULL UNSIGNED,
  ability_id SMALLINT NOT NULL UNSIGNED,
  ptype_generation_id TINYINT NOT NULL UNSIGNED,
  ptype_id TINYINT NOT NULL UNSIGNED,
  multiplier DECIMAL(4,3) NOT NULL UNSIGNED,

  PRIMARY KEY (ability_generation_id, ability_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_boosts_ptype (ptype_generation_id, ptype_id, ability_generation_id, ability_id)
);

CREATE TABLE ability_resists_ptype (
  ability_generation_id TINYINT NOT NULL UNSIGNED,
  ability_id SMALLINT NOT NULL UNSIGNED,
  ptype_generation_id TINYINT NOT NULL UNSIGNED,
  ptype_id TINYINT NOT NULL UNSIGNED,
  multiplier DECIMAL(4,3) NOT NULL UNSIGNED,

  PRIMARY KEY (ability_generation_id, ability_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_resists_ptype (ptype_generation_id, ptype_id, ability_generation_id, ability_id)
);

CREATE TABLE ability_boosts_usage_method (
  ability_generation_id TINYINT NOT NULL UNSIGNED,
  ability_id SMALLINT NOT NULL UNSIGNED,
  usage_method_id TINYINT NOT NULL UNSIGNED,
  multiplier DECIMAL(4,3) NOT NULL UNSIGNED,

  PRIMARY KEY (ability_generation_id, ability_id, usage_method_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (usage_method_id) REFERENCES usage_method(usage_method_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_boosts_usage_method (usage_method_id, ability_generation_id, ability_id)
);

CREATE TABLE ability_resists_usage_method (
  ability_generation_id TINYINT NOT NULL UNSIGNED,
  ability_id SMALLINT NOT NULL UNSIGNED,
  usage_method_id TINYINT NOT NULL UNSIGNED,
  multiplier DECIMAL(4,3) NOT NULL UNSIGNED,

  PRIMARY KEY (ability_generation_id, ability_id, usage_method_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (usage_method_id) REFERENCES usage_method(usage_method_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_resists_usage_method (usage_method_id, ability_generation_id, ability_id)
);

CREATE TABLE ability_modifies_stat (
  ability_generation_id TINYINT NOT NULL UNSIGNED,
  ability_id SMALLINT NOT NULL UNSIGNED,
  stat_id TINYINT NOT NULL UNSIGNED,
  stage TINYINT NOT NULL, /* 0 for abilities which modify stat but not the stage */
  multiplier DECIMAL(3,2) NOT NULL UNSIGNED, /* 0.0 for abilities which modify stat but not via a multiplier */
  chance DECIMAL(5,2) NOT NULL UNSIGNED,
  recipient ENUM('target', 'user'),

  PRIMARY KEY (ability_generation_id, ability_id, stat_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (stat_id) REFERENCES (stat_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_stat (stat_id, ability_generation_id, ability_id)
);

CREATE TABLE ability_effect (
  ability_generation_id TINYINT NOT NULL UNSIGNED,
  ability_id SMALLINT NOT NULL UNSIGNED,
  effect_id TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (ability_generation_id, ability_id, effect_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (effect_id) REFERENCES effect(effect_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_effect (effect_id, ability_generation_id, ability_id)
);

CREATE TABLE ability_causes_pstatus (
  ability_generation_id TINYINT NOT NULL UNSIGNED,
  ability_id SMALLINT NOT NULL UNSIGNED,
  pstatus_id TINYINT NOT NULL UNSIGNED,
  chance DECIMAL(5,2) NOT NULL UNSIGNED,

  PRIMARY KEY (ability_generation_id, ability_id, pstatus_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pstatus_id) REFERENCES pstatus(pstatus_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  
  INDEX opposite_ability_causes_pstatus (pstatus_id, ability_generation_id, ability_id)
);

CREATE TABLE ability_resists_pstatus (
  ability_generation_id TINYINT NOT NULL UNSIGNED,
  ability_id SMALLINT NOT NULL UNSIGNED,
  pstatus_id TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (ability_generation_id, ability_id, pstatus_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pstatus_id) REFERENCES pstatus(pstatus_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_resists_pstatus (pstatus_id, ability_generation_id, ability_id)
);

/*
item
*/
CREATE TABLE item_boosts_ptype (
  item_generation_id TINYINT NOT NULL UNSIGNED,
  item_id SMALLINT NOT NULL UNSIGNED,
  ptype_generation_id TINYINT NOT NULL UNSIGNED,
  ptype_id TINYINT NOT NULL UNSIGNED,
  multiplier DECIMAL(4,3) NOT NULL UNSIGNED,

  PRIMARY KEY (item_generation_id, item_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_item_boosts_ptype (ptype_generation_id, ptype_id, item_generation_id, item_id)
);

CREATE TABLE item_resists_ptype (
  item_generation_id TINYINT NOT NULL UNSIGNED,
  item_id SMALLINT NOT NULL UNSIGNED,
  ptype_generation_id TINYINT NOT NULL UNSIGNED,
  ptype_id TINYINT NOT NULL UNSIGNED,
  multiplier DECIMAL(4,3) NOT NULL UNSIGNED,

  PRIMARY KEY (item_generation_id, item_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_item_resists_ptype (ptype_generation_id, ptype_id, item_generation_id, item_id)
);

CREATE TABLE item_boosts_usage_method (
  item_generation_id TINYINT NOT NULL UNSIGNED,
  item_id SMALLINT NOT NULL UNSIGNED,
  usage_method_id TINYINT NOT NULL UNSIGNED,
  multiplier DECIMAL(4,3) NOT NULL UNSIGNED,

  PRIMARY KEY (item_generation_id, item_id, usage_method_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (usage_method_id) REFERENCES usage_method(usage_method_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_item_boosts_usage_method (usage_method_id, item_generation_id, item_id)
);

CREATE TABLE item_resists_usage_method (
  item_generation_id TINYINT NOT NULL UNSIGNED,
  item_id SMALLINT NOT NULL UNSIGNED,
  usage_method_id TINYINT NOT NULL UNSIGNED,
  multiplier DECIMAL(4,3) NOT NULL UNSIGNED,

  PRIMARY KEY (item_generation_id, item_id, usage_method_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (usage_method_id) REFERENCES usage_method(usage_method_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_item_resists_usage_method (usage_method_id, item_generation_id, item_id)
);

CREATE TABLE item_modifies_stat (
  item_generation_id TINYINT NOT NULL UNSIGNED,
  item_id SMALLINT NOT NULL UNSIGNED,
  stat_id TINYINT NOT NULL UNSIGNED,
  stage TINYINT NOT NULL, /* 0 for abilities which modify stat but not the stage */
  multiplier DECIMAL(3,2) NOT NULL UNSIGNED, /* 0.0 for abilities which modify stat but not via a multiplier */
  chance DECIMAL(5,2) NOT NULL UNSIGNED,
  recipient ENUM('target', 'user'),

  PRIMARY KEY (item_generation_id, item_id, stat_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (stat_id) REFERENCES (stat_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_item_stat (stat_id, item_generation_id, item_id)
);

CREATE TABLE item_effect (
  item_generation_id TINYINT NOT NULL UNSIGNED,
  item_id SMALLINT NOT NULL UNSIGNED,
  effect_id TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (item_generation_id, item_id, effect_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (effect_id) REFERENCES effect(effect_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_item_effect (effect_id, item_generation_id, item_id)
);

CREATE TABLE item_causes_pstatus (
  item_generation_id TINYINT NOT NULL UNSIGNED,
  item_id SMALLINT NOT NULL UNSIGNED,
  pstatus_id TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (item_generation_id, item_id, pstatus_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pstatus_id) REFERENCES pstatus(pstatus_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_item_causes_pstatus (pstatus_id, item_generation_id, item_id)
);

CREATE TABLE item_resists_pstatus (
  item_generation_id TINYINT NOT NULL UNSIGNED,
  item_id SMALLINT NOT NULL UNSIGNED,
  pstatus_id TINYINT NOT NULL UNSIGNED,

  PRIMARY KEY (item_generation_id, item_id, pstatus_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pstatus_id) REFERENCES pstatus(pstatus_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_item_resists_pstatus (pstatus_id, item_generation_id, item_id)
);

/*
version_group
*/
CREATE TABLE version_group_pdescription (
  version_group_generation_id TINYINT NOT NULL UNSIGNED,
  version_group_id TINYINT NOT NULL UNSIGNED,
  pdescription_id MEDIUMINT NOT NULL UNSIGNED,

  PRIMARY KEY (version_group_generation_id, version_group_id, pdescription_id),
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pdescription_id) REFERENCES pdescription(pdescription_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_version_group_pdescription (pdescription_id, version_group_generation_id, version_group_id),
);

CREATE TABLE version_group_sprite (
  version_group_generation_id TINYINT NOT NULL UNSIGNED,
  version_group_id TINYINT NOT NULL UNSIGNED,
  sprite_id MEDIUMINT NOT NULL UNSIGNED,

  PRIMARY KEY (version_group_generation_id, version_group_id, sprite_id),
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (sprite_id) REFERENCES sprite(sprite_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_version_group_sprite (sprite_id, version_group_generation_id, version_group_id),
);

/*
Threefold relationships
*/

/*
pdescription
*/
CREATE TABLE pdescription_ability (
  ability_generation_id TINYINT NOT NULL UNSIGNED,
  ability_id SMALLINT NOT NULL UNSIGNED,
  version_group_generation_id TINYINT NOT NULL UNSIGNED,
  version_group_id TINYINT NOT NULL UNSIGNED,
  pdescription_id MEDIUMINT NOT NULL UNSIGNED,

  PRIMARY KEY (ability_generation_id, ability_id, version_group_generation_id, version_group_id, pdescription_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY pdescription_id REFERENCES pdescription(pdescription_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE pdescription_pmove (
  pmove_generation_id TINYINT NOT NULL UNSIGNED,
  pmove_id SMALLINT NOT NULL UNSIGNED,
  version_group_generation_id TINYINT NOT NULL UNSIGNED,
  version_group_id TINYINT NOT NULL UNSIGNED,
  pdescription_id MEDIUMINT NOT NULL UNSIGNED,

  PRIMARY KEY (pmove_generation_id, pmove_id, version_group_generation_id, version_group_id, pdescription_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY pdescription_id REFERENCES pdescription(pdescription_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE pdescription_item (
  item_generation_id TINYINT NOT NULL UNSIGNED,
  item_id SMALLINT NOT NULL UNSIGNED,
  version_group_generation_id TINYINT NOT NULL UNSIGNED,
  version_group_id TINYINT NOT NULL UNSIGNED,
  pdescription_id MEDIUMINT NOT NULL UNSIGNED,

  PRIMARY KEY (item_generation_id, item_id, version_group_generation_id, version_group_id, pdescription_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY pdescription_id REFERENCES pdescription(pdescription_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

/*
sprite
*/
CREATE TABLE sprite_pokemon (
  pokemon_generation_id TINYINT NOT NULL UNSIGNED,
  pokemon_id SMALLINT NOT NULL UNSIGNED,
  version_group_generation_id TINYINT NOT NULL UNSIGNED,
  version_group_id TINYINT NOT NULL UNSIGNED,
  sprite_id MEDIUMINT NOT NULL UNSIGNED,

  PRIMARY KEY (pokemon_generation_id, pokemon_id, version_group_generation_id, version_group_id, sprite_id),
  FOREIGN KEY (pokemon_generation_id, pokemon_id) REFERENCES pokemon(generation_id, pokemon_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY sprite_id REFERENCES sprite(sprite_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE sprite_item (
  item_generation_id TINYINT NOT NULL UNSIGNED,
  item_id SMALLINT NOT NULL UNSIGNED,
  version_group_generation_id TINYINT NOT NULL UNSIGNED,
  version_group_id TINYINT NOT NULL UNSIGNED,
  sprite_id MEDIUMINT NOT NULL UNSIGNED,

  PRIMARY KEY (item_generation_id, item_id, version_group_generation_id, version_group_id, sprite_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY sprite_id REFERENCES sprite(sprite_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);