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
  pdescription_entity_class,
  pdescription_entity_name
) VALUES ?;

INSERT INTO sprite (
  sprite_id,
  sprite_path
) VALUES ?;

INSERT INTO pstatus (
  generation_id,
  pstatus_name,
  pstatus_formatted_name,
  introduced,
  pstatus_description,
  pstatus_volatile,
  pstatus_unformatted_name
) VALUES ?;

INSERT INTO stat (
  generation_id,
  stat_name,
  stat_formatted_name,
  introduced,
  stat_description,
  stat_unformatted_name
) VALUES ?;

/*
More complicated entities, depending on generation_id (or the generation table through introduced, e.g. version_group)
*/

INSERT INTO version_group (
  version_group_code,
  version_group_name,
  version_group_formatted_name,
  introduced
) VALUES ?;

INSERT INTO effect (
  generation_id,
  effect_name,
  effect_formatted_name,
  introduced,
  effect_description,
  effect_unformatted_name,
  effect_class
) VALUES ?;

INSERT INTO usage_method (
  generation_id,
  usage_method_name,
  usage_method_formatted_name,
  introduced,
  usage_method_description,
  usage_method_unformatted_name
) VALUES ?;

INSERT INTO ability (
  generation_id,
  ability_name,
  ability_formatted_name,
  ability_ps_id,
  ability_formatted_ps_id,
  introduced
) VALUES ?;

INSERT INTO item (
  generation_id,
  item_name,
  item_formatted_name,
  introduced,
  item_ps_id,
  item_formatted_ps_id,
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
  pmove_power,
  pmove_pp,
  pmove_accuracy,
  pmove_category,
  pmove_priority,
  pmove_contact,
  pmove_target,
  pmove_removed_from_swsh,
  pmove_removed_from_bdsp,
  pmove_ps_id,
  pmove_formatted_ps_id,
  pmove_ptype_name
) VALUES ?;

INSERT INTO pokemon (
  generation_id,
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
  pokemon_special_attack,
  pokemon_special_defense,
  pokemon_speed,
  pokemon_base_stat_total,
  pokemon_form_class,
  pokemon_ps_id,
  pokemon_formatted_ps_id,
  pokemon_pokeapi_name,
  pokemon_pokeapi_id,
  pokemon_ptype_name_1,
  pokemon_ptype_name_2,
  pokemon_removed_from_swsh,
  pokemon_removed_from_bdsp,
  pokemon_male_rate,
  pokemon_female_rate,
  pokemon_genderless
) VALUES ?;

INSERT INTO field_state (
  generation_id,
  field_state_name,
  field_state_formatted_name,
  introduced,
  field_state_damage_percent,
  field_state_max_layers,
  field_state_only_grounded,
  field_state_class,
  field_state_target,
  field_state_description,
  field_state_unformatted_name
) VALUES ?;

INSERT INTO nature (
  generation_id,
  nature_name,
  nature_formatted_name,
  introduced,
  nature_favorite_flavor,
  nature_disliked_flavor
) VALUES ?;