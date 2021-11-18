INSERT INTO pokemon_evolution (
  prevolution_generation_id,
  prevolution_id,
  evolution_generation_id,
  evolution_id,
  evolution_method
) VALUES ?;

INSERT INTO pokemon_form (
  base_form_generation_id,
  base_form_id,
  form_generation_id,
  form_id,
  form_class
) VALUES ?;

INSERT INTO cosmetic_form (
  base_form_generation_id,
  base_form_id,
  cosmetic_form_generation_id,
  cosmetic_form_id
) VALUES ?;

INSERT INTO pokemon_ptype (
  pokemon_generation_id,
  pokemon_id,
  ptype_generation_id,
  ptype_id
) VALUES ?;

INSERT INTO pokemon_pmove (
  pokemon_generation_id,
  pokemon_id,
  pmove_generation_id,
  pmove_id,
  learn_method
) VALUES ?;

INSERT INTO pokemon_ability (
  pokemon_generation_id,
  pokemon_id,
  ability_generation_id,
  ability_id,
  ability_slot
) VALUES ?;