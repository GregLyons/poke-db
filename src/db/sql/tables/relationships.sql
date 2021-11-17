/*
1-to-n 
*/
/*
pmove
*/
CREATE TABLE IF NOT EXISTS pmove_requires_pmove (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  base_pmove_generation_id TINYINT UNSIGNED NOT NULL,
  base_pmove_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, base_pmove_generation_id, base_pmove_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (base_pmove_generation_id, base_pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
); 

CREATE TABLE IF NOT EXISTS pokemon_evolution (
  prevolution_generation_id TINYINT UNSIGNED NOT NULL,
  prevolution_id SMALLINT UNSIGNED NOT NULL,
  evolution_generation_id TINYINT UNSIGNED NOT NULL,
  evolution_id SMALLINT UNSIGNED NOT NULL,
  evolution_method VARCHAR(100) NOT NULL

  PRIMARY KEY(prevolution_generation_id, prevolution_id, evolution_generation_id, evolution_id),
  FOREIGN KEY (prevolution_generation_id, prevolution_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (evolution_generation_id, evolution_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_prevolution_evolution (evolution_generation_id, evolution_id, prevolution_generation_id, prevolution_id)
);

-- does not include cosmetic forms
CREATE TABLE IF NOT EXISTS pokemon_form (
  base_form_generation_id TINYINT UNSIGNED NOT NULL,
  base_form_id SMALLINT UNSIGNED NOT NULL,
  form_generation_id TINYINT UNSIGNED NOT NULL,
  form_id SMALLINT UNSIGNED NOT NULL,
  form_class ENUM('mega', 'alola', 'galar', 'gmax', 'other'),

  PRIMARY KEY (base_form_generation_id, base_form_id, form_generation_id, form_id),
  FOREIGN KEY (base_form_generation_id, base_form_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (form_generation_id, form_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- we don't store the base stats, typing, etc. of cosmetic forms since they only differ in appearance; to compute those properties for a given cosmetic form, just use the corresponding property of the base form
CREATE TABLE IF NOT EXISTS cosmetic_form (
  base_form_generation_id TINYINT UNSIGNED NOT NULL,
  base_form_id SMALLINT UNSIGNED NOT NULL,
  cosmetic_form_generation_id TINYINT UNSIGNED NOT NULL,
  cosmetic_form_id SMALLINT UNSIGNED NOT NULL

  PRIMARY KEY (base_form_generation_id, base_form_id, cosmetic_form_generation_id, cosmetic_form_id),
  FOREIGN KEY (base_form_generation_id, base_form_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- for Natural Gift
CREATE TABLE IF NOT EXISTS item_ptype (
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,
  ptype_generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id TINYINT UNSIGNED NOT NULL,
  item_power TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (item_generation_id, item_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
)

/*
m-to-n
*/

/*
pokemon
*/
CREATE TABLE IF NOT EXISTS pokemon_ptype (
  pokemon_generation_id TINYINT UNSIGNED NOT NULL,
  pokemon_id SMALLINT UNSIGNED NOT NULL,
  ptype_generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (pokemon_generation_id, pokemon_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (pokemon_generation_id, pokemon_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pokemon_ptype_generation_id (ptype_generation_idptype, _id, pokemon_generation_id, pokemon_id)
);

CREATE TABLE IF NOT EXISTS pokemon_pmove (
  pokemon_generation_id TINYINT UNSIGNED NOT NULL,
  pokemon_id SMALLINT UNSIGNED NOT NULL,
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  learn_method VARCHAR(4),

  PRIMARY KEY (pokemon_generation_id, pokemon_id, pmove_generation_id, pmove_id),
  FOREIGN KEY (pokemon_generation_id, pokemon_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  
 INDEX opposite_pokemon_pmove (pmove_generation_id, pmove_id, pokemon_generation_id, pokemon_id)
);

CREATE TABLE IF NOT EXISTS pokemon_ability (
  pokemon_generation_id TINYINT UNSIGNED NOT NULL,
  pokemon_id SMALLINT UNSIGNED NOT NULL,
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  ability_slot ENUM('1', '2', 'Hidden'),

  PRIMARY KEY (pokemon_generation_id, pokemon_id, ability_generation_id, ability_id), 
  FOREIGN KEY (pokemon_generation_id, pokemon_id) REFERENCES pokemon(generation_id, pokemon_id)
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
CREATE TABLE IF NOT EXISTS ptype_matchup (
  attacking_ptype_generation_id TINYINT UNSIGNED NOT NULL,
  attacking_ptype_id TINYINT UNSIGNED NOT NULL,
  defending_ptype_generation_id TINYINT UNSIGNED NOT NULL,
  defending_ptype_id TINYINT UNSIGNED NOT NULL,
  multiplier DECIMAL(3,2) UNSIGNED NOT NULL,

  PRIMARY KEY (attacking_ptype_generation_id, attacking_ptype_id, defending_ptype_generation_id, defending_ptype_id),
  FOREIGN KEY (attacking_ptype_generation_id, attacking_ptype_id) REFERENCES ptype(generation_id, ptype_id)
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
CREATE TABLE IF NOT EXISTS pmove_modifies_stat (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  stat_id TINYINT UNSIGNED NOT NULL,
  stage TINYINT NOT NULL, /* 0 for pmoves which modify stat but not the stage */
  multiplier DECIMAL(3,2) UNSIGNED NOT NULL, /* 0.0 for pmoves which modify stat but not via a multiplier */
  chance DECIMAL(5,2) UNSIGNED NOT NULL,
  recipient ENUM('target', 'user'),

  PRIMARY KEY (pmove_generation_id, pmove_id, stat_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (stat_id) REFERENCES stat(stat_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_stat (stat_id, pmove_generation_id, pmove_id)
);

CREATE TABLE IF NOT EXISTS pmove_effect (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  effect_id TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, effect_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (effect_id) REFERENCES effect(effect_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_effect (effect_id, pmove_generation_id, pmove_id)
);

CREATE TABLE IF NOT EXISTS pmove_causes_pstatus (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  pstatus_id TINYINT UNSIGNED NOT NULL,
  chance DECIMAL(5,2) UNSIGNED NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, pstatus_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pstatus_id) REFERENCES pstatus(pstatus_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_causes_pstatus (pstatus_id, pmove_generation_id, pmove_id)
);

CREATE TABLE IF NOT EXISTS pmove_resists_pstatus (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  pstatus_id TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, pstatus_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pstatus_id) REFERENCES pstatus(pstatus_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_resists_pstatus (pstatus_id, pmove_generation_id, pmove_id)
);

CREATE TABLE IF NOT EXISTS pmove_requires_pokemon (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  pokemon_generation_id TINYINT UNSIGNED NOT NULL,
  pokemon_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, pokemon_generation_id, pokemon_id), 
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pokemon_generation_id, pokemon_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_pokemon (pokemon_generation_id, pokemon_id, pmove_generation_id, pmove_id)
);

CREATE TABLE IF NOT EXISTS pmove_requires_pokemon (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, item_generation_id, item_id), 
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_item (item_generation_id, item_id, pmove_generation_id, pmove_id)
);

-- note that Aura Sphere is both a pulse and a ball pmove, so we need an m-to-n relationship
CREATE TABLE IF NOT EXISTS pmove_usage_method (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  usage_method_id TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, usage_method_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
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
CREATE TABLE IF NOT EXISTS ability_boosts_ptype (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  ptype_generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id TINYINT UNSIGNED NOT NULL,
  multiplier DECIMAL(4,3) UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_boosts_ptype (ptype_generation_id, ptype_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_resists_ptype (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  ptype_generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id TINYINT UNSIGNED NOT NULL,
  multiplier DECIMAL(4,3) UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_resists_ptype (ptype_generation_id, ptype_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_boosts_usage_method (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  usage_method_id TINYINT UNSIGNED NOT NULL,
  multiplier DECIMAL(4,3) UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, usage_method_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (usage_method_id) REFERENCES usage_method(usage_method_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_boosts_usage_method (usage_method_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_resists_usage_method (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  usage_method_id TINYINT UNSIGNED NOT NULL,
  multiplier DECIMAL(4,3) UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, usage_method_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (usage_method_id) REFERENCES usage_method(usage_method_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_resists_usage_method (usage_method_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_modifies_stat (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  stat_id TINYINT UNSIGNED NOT NULL,
  stage TINYINT NOT NULL, /* 0 for abilities which modify stat but not the stage */
  multiplier DECIMAL(3,2) UNSIGNED NOT NULL, /* 0.0 for abilities which modify stat but not via a multiplier */
  chance DECIMAL(5,2) UNSIGNED NOT NULL,
  recipient ENUM('target', 'user'),

  PRIMARY KEY (ability_generation_id, ability_id, stat_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (stat_id) REFERENCES stat(stat_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_stat (stat_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_effect (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  effect_id TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, effect_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (effect_id) REFERENCES effect(effect_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_effect (effect_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_causes_pstatus (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  pstatus_id TINYINT UNSIGNED NOT NULL,
  chance DECIMAL(5,2) UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, pstatus_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pstatus_id) REFERENCES pstatus(pstatus_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  
  INDEX opposite_ability_causes_pstatus (pstatus_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_resists_pstatus (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  pstatus_id TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, pstatus_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
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
CREATE TABLE IF NOT EXISTS item_boosts_ptype (
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,
  ptype_generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id TINYINT UNSIGNED NOT NULL,
  multiplier DECIMAL(4,3) UNSIGNED NOT NULL,

  PRIMARY KEY (item_generation_id, item_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_item_boosts_ptype (ptype_generation_id, ptype_id, item_generation_id, item_id)
);

CREATE TABLE IF NOT EXISTS item_resists_ptype (
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,
  ptype_generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id TINYINT UNSIGNED NOT NULL,
  multiplier DECIMAL(4,3) UNSIGNED NOT NULL,

  PRIMARY KEY (item_generation_id, item_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_item_resists_ptype (ptype_generation_id, ptype_id, item_generation_id, item_id)
);

CREATE TABLE IF NOT EXISTS item_boosts_usage_method (
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,
  usage_method_id TINYINT UNSIGNED NOT NULL,
  multiplier DECIMAL(4,3) UNSIGNED NOT NULL,

  PRIMARY KEY (item_generation_id, item_id, usage_method_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (usage_method_id) REFERENCES usage_method(usage_method_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_item_boosts_usage_method (usage_method_id, item_generation_id, item_id)
);

CREATE TABLE IF NOT EXISTS item_resists_usage_method (
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,
  usage_method_id TINYINT UNSIGNED NOT NULL,
  multiplier DECIMAL(4,3) UNSIGNED NOT NULL,

  PRIMARY KEY (item_generation_id, item_id, usage_method_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (usage_method_id) REFERENCES usage_method(usage_method_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_item_resists_usage_method (usage_method_id, item_generation_id, item_id)
);

CREATE TABLE IF NOT EXISTS item_modifies_stat (
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,
  stat_id TINYINT UNSIGNED NOT NULL,
  stage TINYINT NOT NULL, /* 0 for abilities which modify stat but not the stage */
  multiplier DECIMAL(3,2) UNSIGNED NOT NULL, /* 0.0 for abilities which modify stat but not via a multiplier */
  chance DECIMAL(5,2) UNSIGNED NOT NULL,
  recipient ENUM('target', 'user'),

  PRIMARY KEY (item_generation_id, item_id, stat_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (stat_id) REFERENCES stat(stat_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_item_stat (stat_id, item_generation_id, item_id)
);

CREATE TABLE IF NOT EXISTS item_effect (
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,
  effect_id TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (item_generation_id, item_id, effect_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (effect_id) REFERENCES effect(effect_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_item_effect (effect_id, item_generation_id, item_id)
);

CREATE TABLE IF NOT EXISTS item_causes_pstatus (
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,
  pstatus_id TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (item_generation_id, item_id, pstatus_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pstatus_id) REFERENCES pstatus(pstatus_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_item_causes_pstatus (pstatus_id, item_generation_id, item_id)
);

CREATE TABLE IF NOT EXISTS item_resists_pstatus (
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,
  pstatus_id TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (item_generation_id, item_id, pstatus_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
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
CREATE TABLE IF NOT EXISTS version_group_pdescription (
  version_group_generation_id TINYINT UNSIGNED NOT NULL,
  version_group_id TINYINT UNSIGNED NOT NULL,
  pdescription_id MEDIUMINT UNSIGNED NOT NULL,

  PRIMARY KEY (version_group_generation_id, version_group_id, pdescription_id),
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pdescription_id) REFERENCES pdescription(pdescription_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_version_group_pdescription (pdescription_id, version_group_generation_id, version_group_id),
);

CREATE TABLE IF NOT EXISTS version_group_sprite (
  version_group_generation_id TINYINT UNSIGNED NOT NULL,
  version_group_id TINYINT UNSIGNED NOT NULL,
  sprite_id MEDIUMINT UNSIGNED NOT NULL,

  PRIMARY KEY (version_group_generation_id, version_group_id, sprite_id),
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id)
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
CREATE TABLE IF NOT EXISTS pdescription_ability (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  version_group_generation_id TINYINT UNSIGNED NOT NULL,
  version_group_id TINYINT UNSIGNED NOT NULL,
  pdescription_id MEDIUMINT UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, version_group_generation_id, version_group_id, pdescription_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY pdescription_id REFERENCES pdescription(pdescription_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS pdescription_pmove (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  version_group_generation_id TINYINT UNSIGNED NOT NULL,
  version_group_id TINYINT UNSIGNED NOT NULL,
  pdescription_id MEDIUMINT UNSIGNED NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, version_group_generation_id, version_group_id, pdescription_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY pdescription_id REFERENCES pdescription(pdescription_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS pdescription_item (
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,
  version_group_generation_id TINYINT UNSIGNED NOT NULL,
  version_group_id TINYINT UNSIGNED NOT NULL,
  pdescription_id MEDIUMINT UNSIGNED NOT NULL,

  PRIMARY KEY (item_generation_id, item_id, version_group_generation_id, version_group_id, pdescription_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY pdescription_id REFERENCES pdescription(pdescription_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

/*
sprite
*/
CREATE TABLE IF NOT EXISTS sprite_pokemon (
  pokemon_generation_id TINYINT UNSIGNED NOT NULL,
  pokemon_id SMALLINT UNSIGNED NOT NULL,
  version_group_generation_id TINYINT UNSIGNED NOT NULL,
  version_group_id TINYINT UNSIGNED NOT NULL,
  sprite_id MEDIUMINT UNSIGNED NOT NULL,

  PRIMARY KEY (pokemon_generation_id, pokemon_id, version_group_generation_id, version_group_id, sprite_id),
  FOREIGN KEY (pokemon_generation_id, pokemon_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY sprite_id REFERENCES sprite(sprite_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS sprite_item (
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,
  version_group_generation_id TINYINT UNSIGNED NOT NULL,
  version_group_id TINYINT UNSIGNED NOT NULL,
  sprite_id MEDIUMINT UNSIGNED NOT NULL,

  PRIMARY KEY (item_generation_id, item_id, version_group_generation_id, version_group_id, sprite_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY sprite_id REFERENCES sprite(sprite_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);