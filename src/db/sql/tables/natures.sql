CREATE TABLE IF NOT EXISTS nature_modifies_stat (
  nature_generation_id TINYINT UNSIGNED NOT NULL,
  nature_id SMALLINT UNSIGNED NOT NULL,
  stat_generation_id TINYINT UNSIGNED NOT NULL,
  stat_id SMALLINT UNSIGNED NOT NULL,
  stage TINYINT NOT NULL, /* 0 for natures which modify stat but not the stage */
  multiplier DECIMAL(3,2) UNSIGNED NOT NULL, /* 0.0 for natures which modify stat but not via a multiplier */
  chance DECIMAL(5,2) UNSIGNED NOT NULL,
  recipient ENUM('target', 'user'),

  PRIMARY KEY (nature_generation_id, nature_id, stat_generation_id, stat_id),
  FOREIGN KEY (nature_generation_id, nature_id) REFERENCES nature(generation_id, nature_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (stat_generation_id, stat_id) REFERENCES stat(generation_id, stat_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX opposite_nature_stat (stat_generation_id, stat_id, nature_generation_id, nature_id)
);