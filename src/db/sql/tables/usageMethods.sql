CREATE TABLE IF NOT EXISTS usage_method_activates_ability (
  usage_method_generation_id TINYINT UNSIGNED NOT NULL,
  usage_method_id SMALLINT UNSIGNED NOT NULL,
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (usage_method_generation_id, usage_method_id, ability_generation_id, ability_id),
  FOREIGN KEY (usage_method_generation_id, usage_method_id) REFERENCES usage_method(generation_id, usage_method_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_usage_method_activates_ability (ability_generation_id, ability_id, usage_method_generation_id, usage_method_id)
);

CREATE TABLE IF NOT EXISTS usage_method_activates_item (
  usage_method_generation_id TINYINT UNSIGNED NOT NULL,
  usage_method_id SMALLINT UNSIGNED NOT NULL,
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,

  PRIMARY KEY (usage_method_generation_id, usage_method_id, item_generation_id, item_id),
  FOREIGN KEY (usage_method_generation_id, usage_method_id) REFERENCES usage_method(generation_id, usage_method_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_usage_method_activates_item (item_generation_id, item_id, usage_method_generation_id, usage_method_id)
);