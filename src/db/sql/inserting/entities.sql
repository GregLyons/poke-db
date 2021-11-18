INSERT INTO generation (generation_id, generation_code) VALUES ?;
ON DUPLICATE KEY UPDATE 

INSERT INTO version_group (generation_id, version_group_code) VALUES ?;

INSERT INTO ability (generation_id, ability_name, ability_formatted_name, introduced, affects_item)