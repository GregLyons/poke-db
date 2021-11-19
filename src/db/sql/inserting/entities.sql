/*
Simple entities, not dependent on generation_id
*/

-- Most entities have generation_id as a foreign key, so we create this first. Unlike the other entities, the generation_id column is not autoincremented. Instead, we just use the generation number as the id.
INSERT INTO generation (
  generation_id,
  generation_code
) VALUES ?;

INSERT INTO pdescription (
  pdescription_text,
  pdescription_index,
  pdescription_type,
  entity_name
) VALUES ?;

INSERT INTO sprite (
  sprite_id,
  sprite_path
) VALUES ?;


INSERT INTO pstatus (
  pstatus_name,
  pstatus_formatted_name
) VALUES ?;

INSERT INTO stat (
  stat_name,
  stat_formatted_name
) VALUES ?;

/*
More complicated entities, depending on generation_id
*/

INSERT INTO version_group (
  generation_id,
  version_group_code,
  version_group_formatted_name
) VALUES ?;

INSERT INTO effect (
  effect_name,
  effect_formatted_name,
  introduced
) VALUES ?;

INSERT INTO usage_method (
  usage_method_name,
  usage_method_formatted_name,
  introduced
) VALUES ?;

INSERT INTO ability (
  generation_id,
  ability_name,
  ability_formatted_name,
  introduced,
  affects_item
) VALUES ?;

INSERT INTO item (
  generation_id,
  item_name,
  item_formatted_name,
  introduced,
  item_class
) VALUES ?;

INSERT INTO ptype (
  generation_id,
  ptype_name,
  ptype_formatted_name,
  introduced
) VALUES ?;

-- Need to create ptype first since it is a foreign key for pmove.
INSERT INTO pmove (
  generation_id,
  pmove_name,
  pmove_formatted_name,
  introduced,
  ptype_generation_id,
  ptype_id,
  pmove_power,
  pmove_pp,
  pmove_accuracy,
  pmove_category,
  pmove_priority,
  pmove_contact,
  pmove_target
) VALUES ?;

INSERT INTO pokemon (
  generation_id,
  pokemon_id,
  pokemon_name,
  pokemon_formatted_name,
  pokemon_species,
  pokemon_dex,
  pokemon_height,
  pokemon_weight,
  introduced,
  pokemon_hp,
  pokemon_attack,
  pokemon_defense,
  pokemon_special_defense,
  pokemon_special_attack,
  pokemon_speed
) VALUES ?;