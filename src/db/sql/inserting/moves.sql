INSERT INTO pmove_ptype (
  pmove_generation_id,
  pmove_id,
  ptype_generation_id,
  ptype_id
) VALUES ?;

INSERT INTO pmove_requires_ptype (
  pmove_generation_id,
  pmove_id,
  ptype_generation_id,
  ptype_id
) VALUES ?;

INSERT INTO pmove_requires_pmove (
  requiring_pmove_generation_id,
  requiring_pmove_id,
  required_pmove_generation_id,
  required_pmove_id
) VALUES ?;

INSERT INTO pmove_requires_pokemon (
  pmove_generation_id,
  pmove_id,
  pokemon_generation_id,
  pokemon_id
) VALUES ?;

INSERT INTO pmove_requires_item (
  pmove_generation_id,
  pmove_id,
  item_generation_id,
  item_id
) VALUES ?;

INSERT INTO pmove_modifies_stat (
  pmove_generation_id,
  pmove_id,
  stat_generation_id,
  stat_id,
  stage,
  multiplier,
  chance,
  recipient
) VALUES ?;

INSERT INTO pmove_effect (
  pmove_generation_id,
  pmove_id,
  effect_generation_id,
  effect_id
) VALUES ?;

INSERT INTO pmove_usage_method (
  pmove_generation_id,
  pmove_id,
  usage_method_generation_id,
  usage_method_id
) VALUES ?;

INSERT INTO pmove_causes_pstatus (
  pmove_generation_id,
  pmove_id,
  pstatus_generation_id,
  pstatus_id,
  chance
) VALUES ?;

INSERT INTO pmove_resists_pstatus (
  pmove_generation_id,
  pmove_id,
  pstatus_generation_id,
  pstatus_id
) VALUES ?;

INSERT INTO pmove_creates_field_state (
  pmove_generation_id,
  pmove_id,
  field_state_generation_id,
  field_state_id
) VALUES ?;

INSERT INTO pmove_removes_field_state (
  pmove_generation_id,
  pmove_id,
  field_state_generation_id,
  field_state_id,
  multiplier
) VALUES ?;

INSERT INTO pmove_prevents_field_state (
  pmove_generation_id,
  pmove_id,
  field_state_generation_id,
  field_state_id
) VALUES ?;

INSERT INTO pmove_suppresses_field_state (
  pmove_generation_id,
  pmove_id,
  field_state_generation_id,
  field_state_id
) VALUES ?;