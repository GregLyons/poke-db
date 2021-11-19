INSERT INTO version_group_pdescription (
  version_group_id,
  pdescription_id
) VALUES ?;

INSERT INTO version_group_sprite (
  version_group_id,
  sprite_id
) VALUES ?;

INSERT INTO pdescription_ability (
  ability_generation_id,
  ability_id,
  version_group_id,
  pdescription_id
) VALUES ?;

INSERT INTO pdescription_pmove (
  pmove_generation_id,
  pmove_id,
  version_group_id,
  pdescription_id
) VALUES ?;

INSERT INTO pdescription_item (
  item_generation_id,
  item_id,
  version_group_id,
  pdescription_id
) VALUES ?;

INSERT INTO sprite_pokemon (
  pokemon_generation_id,
  pokemon_id,
  version_group_id,
  sprite_id
) VALUES ?;

INSERT INTO sprite_item (
  item_generation_id,
  item_id,
  version_group_id,
  sprite_id
) VALUES ?;