INSERT INTO ability_boosts_ptype (
  ability_generation_id,
  ability_id,
  ptype_generation_id,
  ptype_id,
  multiplier
) VALUES ?;

INSERT INTO ability_resists_ptype (
  ability_generation_id,
  ability_id,
  ptype_generation_id,
  ptype_id,
  multiplier
) VALUES ?;

INSERT INTO ability_boosts_usage_method (
  ability_generation_id,
  ability_id,
  usage_method_generation_id,
  usage_method_id,
  multiplier
) VALUES ?;

INSERT INTO ability_resists_usage_method (
  ability_generation_id,
  ability_id,
  usage_method_generation_id,
  usage_method_id,
  multiplier
) VALUES ?;

INSERT INTO ability_modifies_stat (
  ability_generation_id,
  ability_id,
  stat_generation_id,
  stat_id,
  stage,
  multiplier,
  chance,
  recipient
) VALUES ?;

INSERT INTO ability_effect (
  ability_generation_id,
  ability_id,
  effect_generation_id,
  effect_id
) VALUES ?;

INSERT INTO ability_causes_pstatus (
  ability_generation_id,
  ability_id,
  pstatus_generation_id,
  pstatus_id,
  chance
) VALUES ?;

INSERT INTO ability_resists_pstatus (
  ability_generation_id,
  ability_id,
  pstatus_generation_id,
  pstatus_id
) VALUES ?;

INSERT INTO ability_creates_field_state (
  ability_generation_id,
  ability_id,
  field_state_generation_id,
  field_state_id,
  turns
) VALUES ?;

INSERT INTO ability_removes_field_state (
  ability_generation_id,
  ability_id,
  field_state_generation_id,
  field_state_id
) VALUES ?;

INSERT INTO ability_ignores_field_state (
  ability_generation_id,
  ability_id,
  field_state_generation_id,
  field_state_id
) VALUES ?;

INSERT INTO ability_prevents_field_state (
  ability_generation_id,
  ability_id,
  field_state_generation_id,
  field_state_id
) VALUES ?;

INSERT INTO ability_suppresses_field_state (
  ability_generation_id,
  ability_id,
  field_state_generation_id,
  field_state_id
) VALUES ?;