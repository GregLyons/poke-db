/*
ptype
*/
CREATE TABLE IF NOT EXISTS ptype_matchup (
  attacking_ptype_generation_id TINYINT UNSIGNED NOT NULL,
  attacking_ptype_id SMALLINT UNSIGNED NOT NULL,
  defending_ptype_generation_id TINYINT UNSIGNED NOT NULL,
  defending_ptype_id SMALLINT UNSIGNED NOT NULL,
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

CREATE TABLE IF NOT EXISTS ptype_removes_field_state (
  ptype_generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id SMALLINT UNSIGNED NOT NULL,
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (ptype_generation_id, ptype_id, field_state_generation_id, field_state_id),
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ptype_removes_field_state (field_state_generation_id, field_state_id, ptype_generation_id, ptype_id)
);

CREATE TABLE IF NOT EXISTS ptype_resists_field_state (
  ptype_generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id SMALLINT UNSIGNED NOT NULL,
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id TINYINT UNSIGNED NOT NULL,
  multiplier DECIMAL(4,3) UNSIGNED NOT NULL,

  PRIMARY KEY (ptype_generation_id, ptype_id, field_state_generation_id, field_state_id),
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ptype_resists_field_state (field_state_generation_id, field_state_id, ptype_generation_id, ptype_id)
);

CREATE TABLE IF NOT EXISTS ptype_ignores_field_state (
  ptype_generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id SMALLINT UNSIGNED NOT NULL,
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (ptype_generation_id, ptype_id, field_state_generation_id, field_state_id),
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ptype_ignores_field_state (field_state_generation_id, field_state_id, ptype_generation_id, ptype_id)
);