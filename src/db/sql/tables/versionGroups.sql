/*
version_group
*/
CREATE TABLE version_group_pdescription (
  version_group_generation_id TINYINT NOT NULL UNSIGNED,
  version_group_id TINYINT NOT NULL UNSIGNED,
  pdescription_id MEDIUMINT NOT NULL UNSIGNED,

  PRIMARY KEY (version_group_generation_id, version_group_id, pdescription_id),
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (pdescription_id) REFERENCES pdescription(pdescription_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_version_group_pdescription (pdescription_id, version_group_generation_id, version_group_id),
);

CREATE TABLE version_group_sprite (
  version_group_generation_id TINYINT NOT NULL UNSIGNED,
  version_group_id TINYINT NOT NULL UNSIGNED,
  sprite_id MEDIUMINT NOT NULL UNSIGNED,

  PRIMARY KEY (version_group_generation_id, version_group_id, sprite_id),
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (sprite_id) REFERENCES sprite(sprite_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_version_group_sprite (sprite_id, version_group_generation_id, version_group_id),
);

/*
pdescription
*/
CREATE TABLE pdescription_ability (
  ability_generation_id TINYINT NOT NULL UNSIGNED,
  ability_id SMALLINT NOT NULL UNSIGNED,
  version_group_generation_id TINYINT NOT NULL UNSIGNED,
  version_group_id TINYINT NOT NULL UNSIGNED,
  pdescription_id MEDIUMINT NOT NULL UNSIGNED,

  PRIMARY KEY (ability_generation_id, ability_id, version_group_generation_id, version_group_id, pdescription_id),
  FOREIGN KEY (ability_generation_id, ability_id) REFERENCES ability(generation_id, ability_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY pdescription_id REFERENCES pdescription(pdescription_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE pdescription_pmove (
  pmove_generation_id TINYINT NOT NULL UNSIGNED,
  pmove_id SMALLINT NOT NULL UNSIGNED,
  version_group_generation_id TINYINT NOT NULL UNSIGNED,
  version_group_id TINYINT NOT NULL UNSIGNED,
  pdescription_id MEDIUMINT NOT NULL UNSIGNED,

  PRIMARY KEY (pmove_generation_id, pmove_id, version_group_generation_id, version_group_id, pdescription_id),
  FOREIGN KEY (pmove_generation_id, pmove_id) REFERENCES pmove(generation_id, pmove_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY pdescription_id REFERENCES pdescription(pdescription_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE pdescription_item (
  item_generation_id TINYINT NOT NULL UNSIGNED,
  item_id SMALLINT NOT NULL UNSIGNED,
  version_group_generation_id TINYINT NOT NULL UNSIGNED,
  version_group_id TINYINT NOT NULL UNSIGNED,
  pdescription_id MEDIUMINT NOT NULL UNSIGNED,

  PRIMARY KEY (item_generation_id, item_id, version_group_generation_id, version_group_id, pdescription_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY pdescription_id REFERENCES pdescription(pdescription_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

/*
sprite
*/
CREATE TABLE sprite_pokemon (
  pokemon_generation_id TINYINT NOT NULL UNSIGNED,
  pokemon_id SMALLINT NOT NULL UNSIGNED,
  version_group_generation_id TINYINT NOT NULL UNSIGNED,
  version_group_id TINYINT NOT NULL UNSIGNED,
  sprite_id MEDIUMINT NOT NULL UNSIGNED,

  PRIMARY KEY (pokemon_generation_id, pokemon_id, version_group_generation_id, version_group_id, sprite_id),
  FOREIGN KEY (pokemon_generation_id, pokemon_id) REFERENCES pokemon(generation_id, pokemon_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY sprite_id REFERENCES sprite(sprite_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE sprite_item (
  item_generation_id TINYINT NOT NULL UNSIGNED,
  item_id SMALLINT NOT NULL UNSIGNED,
  version_group_generation_id TINYINT NOT NULL UNSIGNED,
  version_group_id TINYINT NOT NULL UNSIGNED,
  sprite_id MEDIUMINT NOT NULL UNSIGNED,

  PRIMARY KEY (item_generation_id, item_id, version_group_generation_id, version_group_id, sprite_id),
  FOREIGN KEY (item_generation_id, item_id) REFERENCES item(generation_id, item_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (version_group_generation_id, version_group_id) REFERENCES version_group(generation_id, version_group_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY sprite_id REFERENCES sprite(sprite_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);