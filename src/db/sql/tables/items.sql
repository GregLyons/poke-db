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
);

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