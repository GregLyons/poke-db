/*
ptype
*/
CREATE TABLE IF NOT EXISTS ptype_matchup (
  attacking_ptype_generation_id TINYINT UNSIGNED NOT NULL,
  attacking_ptype_id TINYINT UNSIGNED NOT NULL,
  defending_ptype_generation_id TINYINT UNSIGNED NOT NULL,
  defending_ptype_id TINYINT UNSIGNED NOT NULL,
  multiplier DECIMAL(3,2) UNSIGNED NOT NULL,

  PRIMARY KEY (attacking_ptype_generation_id, attacking_ptype_id, defending_ptype_generation_id, defending_ptype_id),
  FOREIGN KEY (attacking_ptype_generation_id, attacking_ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (defending_ptype_generation_id, defending_ptype_id) REFERENCES ptype(generation_id, ptype_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  
  INDEX opposite_attacking_ptype_defending_ptype (defending_ptype_generation_id, defending_ptype_id, attacking_ptype_generation_id, attacking_ptype_id)
);