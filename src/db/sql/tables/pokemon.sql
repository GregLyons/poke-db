CREATE TABLE IF NOT EXISTS pokemon_evolution (
  prevolution_generation_id TINYINT UNSIGNED NOT NULL,
  prevolution_id SMALLINT UNSIGNED NOT NULL,
  evolution_generation_id TINYINT UNSIGNED NOT NULL,
  evolution_id SMALLINT UNSIGNED NOT NULL,
  evolution_method VARCHAR(255) NOT NULL,

  PRIMARY KEY (prevolution_generation_id, prevolution_id, evolution_generation_id, evolution_id),
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
  form_class ENUM('mega', 'alola', 'galar', 'gmax', 'other', 'base', 'cosmetic', 'type'),

  PRIMARY KEY (base_form_generation_id, base_form_id, form_generation_id, form_id),
  FOREIGN KEY (base_form_generation_id, base_form_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (form_generation_id, form_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS pokemon_ptype (
  pokemon_generation_id TINYINT UNSIGNED NOT NULL,
  pokemon_id SMALLINT UNSIGNED NOT NULL,
  ptype_generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (pokemon_generation_id, pokemon_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (pokemon_generation_id, pokemon_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pokemon_ptype_generation_id (ptype_generation_id, ptype_id, pokemon_generation_id, pokemon_id)
);

CREATE TABLE IF NOT EXISTS pokemon_pmove (
  pokemon_generation_id TINYINT UNSIGNED NOT NULL,
  pokemon_id SMALLINT UNSIGNED NOT NULL,
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  learn_method VARCHAR(4) NOT NULL,

  PRIMARY KEY (pokemon_generation_id, pokemon_id, pmove_generation_id, pmove_id, learn_method),
  FOREIGN KEY (pokemon_generation_id, pokemon_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  
 INDEX opposite_pokemon_pmove (pmove_generation_id, pmove_id, pokemon_generation_id, pokemon_id, learn_method)
);

CREATE TABLE IF NOT EXISTS pokemon_ability (
  pokemon_generation_id TINYINT UNSIGNED NOT NULL,
  pokemon_id SMALLINT UNSIGNED NOT NULL,
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  ability_slot ENUM('1', '2', 'hidden'),

  PRIMARY KEY (pokemon_generation_id, pokemon_id, ability_generation_id, ability_id), 
  FOREIGN KEY (pokemon_generation_id, pokemon_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  
  INDEX opposite_pokemon_ability (ability_generation_id, ability_id, pokemon_generation_id, pokemon_id)
);

CREATE TABLE IF NOT EXISTS pokemon_requires_item (
  pokemon_generation_id TINYINT UNSIGNED NOT NULL,
  pokemon_id SMALLINT UNSIGNED NOT NULL,
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (pokemon_generation_id, pokemon_id, item_generation_id, item_id), 
  FOREIGN KEY (pokemon_generation_id, pokemon_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pokemon_item (item_generation_id, item_id, pokemon_generation_id, pokemon_id)
);