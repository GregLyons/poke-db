/*
version_group
*/
CREATE TABLE IF NOT EXISTS version_group_pdescription (
  version_group_id TINYINT UNSIGNED NOT NULL,
  pdescription_id MEDIUMINT UNSIGNED NOT NULL,

  PRIMARY KEY (version_group_id, pdescription_id),
  FOREIGN KEY (version_group_id) REFERENCES version_group(version_group_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pdescription_id) REFERENCES pdescription(pdescription_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_version_group_pdescription (pdescription_id, version_group_id)
);

CREATE TABLE IF NOT EXISTS version_group_sprite (
  version_group_id TINYINT UNSIGNED NOT NULL,
  sprite_id MEDIUMINT UNSIGNED NOT NULL,

  PRIMARY KEY (version_group_id, sprite_id),
  FOREIGN KEY (version_group_id) REFERENCES version_group(version_group_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (sprite_id) REFERENCES sprite(sprite_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_version_group_sprite (sprite_id, version_group_id)
);

/*
pdescription
*/
CREATE TABLE IF NOT EXISTS pdescription_ability (
  ability_generation_id TINYINT UNSIGNED NOT NULL,
  pdescription_id MEDIUMINT UNSIGNED NOT NULL,
  ability_id SMALLINT UNSIGNED NOT NULL,
  version_group_code VARCHAR(45) NOT NULL,

  PRIMARY KEY (ability_generation_id, ability_id, pdescription_id, version_group_code),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pdescription_id) REFERENCES pdescription(pdescription_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS pdescription_pmove (
  pmove_generation_id TINYINT UNSIGNED NOT NULL,
  pmove_id SMALLINT UNSIGNED NOT NULL,
  pdescription_id MEDIUMINT UNSIGNED NOT NULL,
  version_group_code VARCHAR(45) NOT NULL,

  PRIMARY KEY (pmove_generation_id, pmove_id, pdescription_id, version_group_code),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pdescription_id) REFERENCES pdescription(pdescription_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS pdescription_item (
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,
  pdescription_id MEDIUMINT UNSIGNED NOT NULL,
  version_group_code VARCHAR(45) NOT NULL,

  PRIMARY KEY (item_generation_id, item_id, pdescription_id, version_group_code),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pdescription_id) REFERENCES pdescription(pdescription_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

/*
sprite
*/
CREATE TABLE IF NOT EXISTS sprite_pokemon (
  pokemon_generation_id TINYINT UNSIGNED NOT NULL,
  pokemon_id SMALLINT UNSIGNED NOT NULL,
  sprite_id MEDIUMINT UNSIGNED NOT NULL,
  version_group_code VARCHAR(45) NOT NULL,

  PRIMARY KEY (pokemon_generation_id, pokemon_id, sprite_id),
  FOREIGN KEY (pokemon_generation_id, pokemon_id) REFERENCES pokemon(generation_id, pokemon_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (sprite_id) REFERENCES sprite(sprite_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS sprite_item (
  item_generation_id TINYINT UNSIGNED NOT NULL,
  item_id SMALLINT UNSIGNED NOT NULL,
  sprite_id MEDIUMINT UNSIGNED NOT NULL,
  version_group_code VARCHAR(45) NOT NULL,

  PRIMARY KEY (item_generation_id, item_id, sprite_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (sprite_id) REFERENCES sprite(sprite_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);