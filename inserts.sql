-- Loading the junction tables:
-- The temp tables hold Wikidata entity IDs. These inserts resolve those IDs
-- to this database's own primary keys and copy the relationships across.
-- Stored procedures are used to automate this process. Check schema.sql for the procedure.

INSERT INTO `recorded_by`
SELECT `musicians`.`id` AS `musician_id`, `albums`.`id` AS `album_id`
FROM `musicians`
JOIN `temp_recorded_by`
ON `musicians`.`entity_id` = `temp_recorded_by`.`musician_id`
LEFT JOIN `albums`
ON `albums`.`entity_id` = `temp_recorded_by`.`album_id`
ORDER BY `album_id`
WHERE `albums`.`id` IS NOT NULL;

INSERT INTO `recorded_on`
SELECT `albums`.`id` AS `album_id`, `labels`.`id` AS `label_id`
FROM `albums`
INNER JOIN `temp_recorded_on`
ON `albums`.`entity_id` = `temp_recorded_on`.`album_id`
INNER JOIN `labels`
ON `labels`.`entity_id` = `temp_recorded_on`.`label_id`
ORDER BY `album_id`;

INSERT INTO `played`
SELECT DISTINCT `musicians`.`id` AS `musician_id`, `instruments`.`id` AS `instrument_id`
FROM `musicians`
INNER JOIN `temp_played`
ON `musicians`.`entity_id` = `temp_played`.`musician_id`
INNER JOIN `instruments`
ON `instruments`.`entity_id` = `temp_played`.`instrument_id`
ORDER BY `musician_id`;

-- Can't forget to optimize the tables!
VACUUM;
