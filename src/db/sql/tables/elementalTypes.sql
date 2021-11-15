/*
ptype
*/
CREATE TABLE ptype_matchup (
  attacking_ptype_generation_id TINYINT NOT NULL UNSIGNED,
  attacking_ptype_id TINYINT NOT NULL UNSIGNED,
  defending_ptype_generation_id TINYINT NOT NULL UNSIGNED,
  defending_ptype_id TINYINT NOT NULL UNSIGNED,
  multiplier DECIMAL(3,2) NOT NULL UNSIGNED,

  PRIMARY KEY (attacking_ptype_generation_id, attacking_ptype_id, defending_ptype_generation_id, defending_ptype_id),
  FOREIGN KEY (attacking_ptype_generation_id, attacking_ptype_id) REFERENCES ptype(generation_id, ptype_id),
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (defending_ptype_generation_id, defending_ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  
  INDEX opposite_attacking_ptype_defending_ptype (defending_ptype_generation_id, defending_ptype_id, attacking_ptype_generation_id, attacking_ptype_id)
);