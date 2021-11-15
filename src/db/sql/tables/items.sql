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