INSERT INTO field_state_modifies_stat (
  field_state_generation_id,
  field_state_id,
  stat_generation_id,
  stat_id,
  stage,
  multiplier,
  chance,
  recipient
) VALUES ?;

INSERT INTO field_state_effect (
  field_state_generation_id,
  field_state_id,
  effect_generation_id,
  effect_id
) VALUES ?;

INSERT INTO field_state_causes_pstatus (
  field_state_generation_id,
  field_state_id,
  pstatus_generation_id,
  pstatus_id,
  chance
) VALUES ?;

INSERT INTO field_state_resists_pstatus (
  field_state_generation_id,
  field_state_id,
  pstatus_generation_id,
  pstatus_id
) VALUES ?;

INSERT INTO weather_ball (
  field_state_generation_id,
  field_state_id,
  ptype_generation_id,
  ptype_id
) VALUES ?;

INSERT INTO field_state_boosts_ptype (
  field_state_generation_id,
  field_state_id,
  ptype_generation_id,
  ptype_id,
  multiplier
) VALUES ?;

INSERT INTO field_state_resists_ptype (
  field_state_generation_id,
  field_state_id,
  ptype_generation_id,
  ptype_id,
  multiplier
) VALUES ?;

INSERT INTO field_state_activates_ability (
  field_state_generation_id,
  field_state_id,
  ability_generation_id,
  ability_id
) VALUES ?;

INSERT INTO field_state_activates_item (
  field_state_generation_id,
  field_state_id,
  item_generation_id,
  item_id
) VALUES ?;

INSERT INTO field_state_enhances_pmove (
  field_state_generation_id,
  field_state_id,
  pmove_generation_id,
  pmove_id
) VALUES ?;

INSERT INTO field_state_hinders_pmove (
  field_state_generation_id,
  field_state_id,
  pmove_generation_id,
  pmove_id
) VALUES ?;