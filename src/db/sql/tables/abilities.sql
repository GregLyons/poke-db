CREATE TABLE IF NOT EXISTS ability_boosts_ptype (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  ptype_generation_id TINYINT UNSIGNED NOT NULL,
  ptype_id SMALLINT UNSIGNED NOT NULL,
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
  ptype_id SMALLINT UNSIGNED NOT NULL,
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
  usage_method_generation_id TINYINT UNSIGNED NOT NULL,
  usage_method_id SMALLINT UNSIGNED NOT NULL,
  multiplier DECIMAL(4,3) UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, usage_method_generation_id, usage_method_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (usage_method_generation_id, usage_method_id) REFERENCES usage_method(generation_id, usage_method_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_boosts_usage_method (usage_method_generation_id, usage_method_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_resists_usage_method (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  usage_method_generation_id TINYINT UNSIGNED NOT NULL,
  usage_method_id SMALLINT UNSIGNED NOT NULL,
  multiplier DECIMAL(4,3) UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, usage_method_generation_id, usage_method_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (usage_method_generation_id, usage_method_id) REFERENCES usage_method(generation_id, usage_method_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_resists_usage_method (usage_method_generation_id, usage_method_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_modifies_stat (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  stat_generation_id TINYINT UNSIGNED NOT NULL,
  stat_id SMALLINT UNSIGNED NOT NULL,
  stage TINYINT NOT NULL, /* 0 for abilities which modify stat but not the stage */
  multiplier DECIMAL(3,2) UNSIGNED NOT NULL, /* 0.0 for abilities which modify stat but not via a multiplier */
  chance DECIMAL(5,2) UNSIGNED NOT NULL,
  recipient ENUM('target', 'user', 'all_foes'),

  PRIMARY KEY (ability_generation_id, ability_id, stat_generation_id, stat_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (stat_generation_id, stat_id) REFERENCES stat(generation_id, stat_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_stat (stat_generation_id, stat_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_effect (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  effect_generation_id TINYINT UNSIGNED NOT NULL,
  effect_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, effect_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (effect_generation_id, effect_id) REFERENCES effect(generation_id, effect_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_effect (effect_generation_id, effect_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_causes_pstatus (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  pstatus_generation_id TINYINT UNSIGNED NOT NULL,
  pstatus_id SMALLINT UNSIGNED NOT NULL,
  chance DECIMAL(5,2) UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, pstatus_generation_id, pstatus_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pstatus_generation_id, pstatus_id) REFERENCES pstatus(generation_id, pstatus_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  
  INDEX opposite_ability_causes_pstatus (pstatus_generation_id, pstatus_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_resists_pstatus (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  pstatus_generation_id TINYINT UNSIGNED NOT NULL,
  pstatus_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, pstatus_generation_id, pstatus_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pstatus_generation_id, pstatus_id) REFERENCES pstatus(generation_id, pstatus_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_resists_pstatus (pstatus_generation_id, pstatus_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_creates_field_state (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,
  turns TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, field_state_generation_id, field_state_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_creates_field_state (field_state_generation_id, field_state_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_removes_field_state (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, field_state_generation_id, field_state_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_removes_field_state (field_state_generation_id, field_state_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_prevents_field_state (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, field_state_generation_id, field_state_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_prevents_field_state (field_state_generation_id, field_state_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_suppresses_field_state (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, field_state_generation_id, field_state_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_suppresses_field_state (field_state_generation_id, field_state_id, ability_generation_id, ability_id)
);

CREATE TABLE IF NOT EXISTS ability_ignores_field_state (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  field_state_generation_id TINYINT UNSIGNED NOT NULL,
  field_state_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, field_state_generation_id, field_state_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (field_state_generation_id, field_state_id) REFERENCES field_state(generation_id, field_state_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_ability_ignores_field_state (field_state_generation_id, field_state_id, ability_generation_id, ability_id)
);