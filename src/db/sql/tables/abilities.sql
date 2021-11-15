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