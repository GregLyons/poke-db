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