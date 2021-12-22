CREATE TABLE IF NOT EXISTS pmove_ptype (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  ptype_generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_ptype (ptype_generation_id, ptype_id, pmove_generation_id, pmove_id)
);

CREATE TABLE IF NOT EXISTS pmove_requires_ptype (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  ptype_generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  INDEX opposite_pmove_requires_ptype (ptype_generation_id, ptype_id, pmove_generation_id, pmove_id)
);

CREATE TABLE IF NOT EXISTS pmove_requires_pmove (
  requiring_pmove_generation_id TINYINT UNSIGNED NOT NULL,
  requiring_pmove_id SMALLINT UNSIGNED NOT NULL,
  required_pmove_generation_id TINYINT UNSIGNED NOT NULL,
  required_pmove_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (requiring_pmove_generation_id, requiring_pmove_id, required_pmove_generation_id, required_pmove_id),
  FOREIGN KEY (requiring_pmove_generation_id, requiring_pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (required_pmove_generation_id, required_pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  INDEX opposite_pmove_requires_pmove (required_pmove_generation_id, required_pmove_id, requiring_pmove_generation_id, requiring_pmove_id)
);

-- 'assist' can call 'surf', so 'surf' is the interacting move, and 'assist' is the recipient move (the move being interacted with)
CREATE TABLE IF NOT EXISTS pmove_interacts_pmove (
  interacting_pmove_generation_id TINYINT UNSIGNED NOT NULL,
  interacting_pmove_id SMALLINT UNSIGNED NOT NULL,
  recipient_pmove_generation_id TINYINT UNSIGNED NOT NULL,
  recipient_pmove_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (interacting_pmove_generation_id, interacting_pmove_id, recipient_pmove_generation_id, recipient_pmove_id),
  FOREIGN KEY (interacting_pmove_generation_id, interacting_pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (recipient_pmove_generation_id, recipient_pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  INDEX opposite_pmove_interacts_pmove (recipient_pmove_generation_id, recipient_pmove_id, interacting_pmove_generation_id, interacting_pmove_id)
); 

CREATE TABLE IF NOT EXISTS pmove_modifies_stat (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  stat_generation_id TINYINT UNSIGNED NOT NULL,
  stat_id SMALLINT UNSIGNED NOT NULL,
  stage TINYINT NOT NULL, /* 0 for pmoves which modify stat but not the stage */
  multiplier DECIMAL(3,2) UNSIGNED NOT NULL, /* 0.0 for pmoves which modify stat but not via a multiplier */
  chance DECIMAL(5,2) UNSIGNED NOT NULL,
  recipient ENUM('target', 'user'),

  PRIMARY KEY (pmove_generation_id, pmove_id, stat_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (stat_generation_id, stat_id) REFERENCES stat(generation_id, stat_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_stat (stat_generation_id, stat_id, pmove_generation_id, pmove_id)
);

CREATE TABLE IF NOT EXISTS pmove_effect (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  effect_generation_id TINYINT UNSIGNED NOT NULL,
  effect_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, effect_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (effect_generation_id, effect_id) REFERENCES effect(generation_id, effect_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_effect (effect_generation_id, effect_id, pmove_generation_id, pmove_id)
);

CREATE TABLE IF NOT EXISTS pmove_causes_pstatus (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  pstatus_generation_id TINYINT UNSIGNED NOT NULL,
  pstatus_id SMALLINT UNSIGNED NOT NULL,
  chance DECIMAL(5,2) UNSIGNED NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, pstatus_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pstatus_generation_id, pstatus_id) REFERENCES pstatus(generation_id, pstatus_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_causes_pstatus (pstatus_generation_id, pstatus_id, pmove_generation_id, pmove_id)
);

CREATE TABLE IF NOT EXISTS pmove_resists_pstatus (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  pstatus_generation_id TINYINT UNSIGNED NOT NULL,
  pstatus_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, pstatus_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pstatus_generation_id, pstatus_id) REFERENCES pstatus(generation_id, pstatus_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_resists_pstatus (pstatus_generation_id, pstatus_id, pmove_generation_id, pmove_id)
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

CREATE TABLE IF NOT EXISTS pmove_requires_item (
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
  usage_method_generation_id TINYINT UNSIGNED NOT NULL,
  usage_method_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, usage_method_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (usage_method_generation_id, usage_method_id) REFERENCES usage_method(generation_id, usage_method_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_usage_method (usage_method_generation_id, usage_method_id, pmove_generation_id, pmove_id)
);

CREATE TABLE IF NOT EXISTS pmove_creates_field_state (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,
  turns TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, field_state_generation_id, field_state_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_creates_field_state (field_state_generation_id, field_state_id, pmove_generation_id, pmove_id)
);

CREATE TABLE IF NOT EXISTS pmove_removes_field_state (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, field_state_generation_id, field_state_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_pmove_removes_field_state (field_state_generation_id, field_state_id, pmove_generation_id, pmove_id)
);