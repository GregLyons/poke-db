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