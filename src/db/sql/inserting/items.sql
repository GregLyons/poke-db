INSERT INTO natural_gift (
  item_generation_id,
  item_id,
  ptype_generation_id,
  ptype_id,
  power
) VALUES ?;

INSERT INTO item_boosts_ptype (
  item_generation_id,
  item_id,
  ptype_generation_id,
  ptype_id,
  multiplier
) VALUES ?; 

INSERT INTO item_resists_ptype (
  item_generation_id,
  item_id,
  ptype_generation_id,
  ptype_id,
  multiplier
) VALUES ?; 

INSERT INTO item_boosts_usage_method (
  item_generation_id,
  item_id,
  usage_method_generation_id,
  usage_method_id,
  multiplier
) VALUES ?; 

INSERT INTO item_resists_usage_method (
  item_generation_id,
  item_id,
  usage_method_generation_id,
  usage_method_id,
  multiplier
) VALUES ?; 

INSERT INTO item_modifies_stat (
  item_generation_id,
  item_id,
  stat_generation_id,
  stat_id,
  stage,
  multiplier,
  chance,
  recipient
) VALUES ?;

INSERT INTO item_effect (
  item_generation_id,
  item_id,
  effect_generation_id,
  effect_id
) VALUES ?;

INSERT INTO item_causes_pstatus (
  item_generation_id,
  item_id,
  pstatus_generation_id,
  pstatus_id
) VALUES ?;

INSERT INTO item_resists_pstatus (
  item_generation_id,
  item_id,
  pstatus_generation_id,
  pstatus_id
) VALUES ?;

INSERT INTO item_requires_pokemon (
  item_generation_id,
  item_id,
  pokemon_generation_id,
  pokemon_id
) VALUES ?;

INSERT INTO item_ignores_field_state (
  item_generation_id,
  item_id,
  field_state_generation_id,
  field_state_id
) VALUES ?;

INSERT INTO item_resists_field_state (
  item_generation_id,
  item_id,
  field_state_generation_id,
  field_state_id,
  multiplier
) VALUES ?;

INSERT INTO item_extends_field_state (
  item_generation_id,
  item_id,
  field_state_generation_id,
  field_state_id,
  turns
) VALUES ?;