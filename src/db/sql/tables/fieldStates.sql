CREATE TABLE IF NOT EXISTS field_state_modifies_stat (
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,
  stat_generation_id TINYINT UNSIGNED NOT NULL,
  stat_id SMALLINT UNSIGNED NOT NULL,
  stage TINYINT NOT NULL, /* 0 for field_states which modify stat but not the stage */
  multiplier DECIMAL(3,2) UNSIGNED NOT NULL, /* 0.0 for field_states which modify stat but not via a multiplier */
  chance DECIMAL(5,2) UNSIGNED NOT NULL,
  recipient ENUM('target', 'user', 'all_allies', 'all_foes', 'all'),

  PRIMARY KEY (field_state_generation_id, field_state_id, stat_generation_id, stat_id),
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (stat_generation_id, stat_id) REFERENCES stat(generation_id, stat_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_field_state_stat (stat_generation_id, stat_id, field_state_generation_id, field_state_id)
);

CREATE TABLE IF NOT EXISTS weather_ball (
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,
  ptype_generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (field_state_generation_id, field_state_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_weather_ball (ptype_generation_id, ptype_id, field_state_generation_id, field_state_id)
);

CREATE TABLE IF NOT EXISTS field_state_effect (
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,
  effect_generation_id TINYINT UNSIGNED NOT NULL,
  effect_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (field_state_generation_id, field_state_id, effect_generation_id, effect_id),
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (effect_generation_id, effect_id) REFERENCES effect(generation_id, effect_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_field_state_effect (effect_generation_id, effect_id, field_state_generation_id, field_state_id)
);

CREATE TABLE IF NOT EXISTS field_state_causes_pstatus (
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,
  pstatus_generation_id TINYINT UNSIGNED NOT NULL,
  pstatus_id SMALLINT UNSIGNED NOT NULL,
  chance DECIMAL(5,2) UNSIGNED NOT NULL,

  PRIMARY KEY (field_state_generation_id, field_state_id, pstatus_generation_id, pstatus_id),
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pstatus_generation_id, pstatus_id) REFERENCES pstatus(generation_id, pstatus_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_field_state_causes_pstatus (pstatus_generation_id, pstatus_id, field_state_generation_id, field_state_id)
);

CREATE TABLE IF NOT EXISTS field_state_prevents_pstatus (
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,
  pstatus_generation_id TINYINT UNSIGNED NOT NULL,
  pstatus_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (field_state_generation_id, field_state_id, pstatus_generation_id, pstatus_id),
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pstatus_generation_id, pstatus_id) REFERENCES pstatus(generation_id, pstatus_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_field_state_prevents_pstatus (pstatus_generation_id, pstatus_id, field_state_generation_id, field_state_id)
);

CREATE TABLE IF NOT EXISTS field_state_boosts_ptype (
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,
  ptype_generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id SMALLINT UNSIGNED NOT NULL,
  multiplier DECIMAL(4,3) UNSIGNED NOT NULL,

  PRIMARY KEY (field_state_generation_id, field_state_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_field_state_boosts_ptype (ptype_generation_id, ptype_id, field_state_generation_id, field_state_id)
);

CREATE TABLE IF NOT EXISTS field_state_resists_ptype (
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,
  ptype_generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id SMALLINT UNSIGNED NOT NULL,
  multiplier DECIMAL(4,3) UNSIGNED NOT NULL,

  PRIMARY KEY (field_state_generation_id, field_state_id, ptype_generation_id, ptype_id),
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ptype_generation_id, ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_field_state_resists_ptype (ptype_generation_id, ptype_id, field_state_generation_id, field_state_id)
);

CREATE TABLE IF NOT EXISTS field_state_activates_ability (
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (field_state_generation_id, field_state_id, ability_generation_id, ability_id),
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_field_state_activates_ability (ability_generation_id, ability_id, field_state_generation_id, field_state_id)
);

CREATE TABLE IF NOT EXISTS field_state_activates_item (
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (field_state_generation_id, field_state_id, item_generation_id, item_id),
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_field_state_activates_item (item_generation_id, item_id, field_state_generation_id, field_state_id)
);

CREATE TABLE IF NOT EXISTS field_state_enhances_pmove (
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (field_state_generation_id, field_state_id, pmove_generation_id, pmove_id),
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_field_state_enhances_pmove (pmove_generation_id, pmove_id, field_state_generation_id, field_state_id)
);

CREATE TABLE IF NOT EXISTS field_state_hinders_pmove (
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (field_state_generation_id, field_state_id, pmove_generation_id, pmove_id),
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    
  INDEX opposite_field_state_hinders_pmove (pmove_generation_id, pmove_id, field_state_generation_id, field_state_id)
);