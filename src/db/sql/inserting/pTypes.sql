INSERT INTO ptype_matchup (
  attacking_ptype_generation_id,
  attacking_ptype_id,
  defending_ptype_generation_id,
  defending_ptype_id,
  multiplier
) VALUES ?;

INSERT INTO ptype_ignores_field_state (
  ptype_generation_id,
  ptype_id,
  field_state_generation_id,
  field_state_id
) VALUES ?;

INSERT INTO ptype_resists_field_state (
  ptype_generation_id,
  ptype_id,
  field_state_generation_id,
  field_state_id,
  multiplier
) VALUES ?;

INSERT INTO ptype_removes_field_state (
  ptype_generation_id,
  ptype_id,
  field_state_generation_id,
  field_state_id
) VALUES ?;