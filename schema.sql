CREATE DATABASE `ijmdb`;
USE `ijmdb`;

-- Record Tables:

-- Musicians:
-- MySQL can't support years in the 1800's and doesn't have 'month' or 'day' data types, so I made them ints of various sizes
CREATE TABLE `musicians` (
    `id` MEDIUMINT UNSIGNED AUTO_INCREMENT,
    `entity_id` VARCHAR(15) NOT NULL,
    `name` VARCHAR(40) NOT NULL,
    `year_of_birth` SMALLINT UNSIGNED,
    `month_of_birth` TINYINT UNSIGNED,
    `day_of_birth` TINYINT UNSIGNED,
    `year_of_death` YEAR,
    `month_of_death` TINYINT UNSIGNED,
    `day_of_death` TINYINT UNSIGNED,
    PRIMARY KEY (`id`)
);

-- Albums:
-- `name` is really large because we had some suuuper long album titles.
CREATE TABLE `albums` (
    `id` MEDIUMINT UNSIGNED AUTO_INCREMENT,
    `entity_id` VARCHAR(15) NOT NULL,
    `name` VARCHAR(180) NOT NULL,
    `release_year` YEAR,
    `release_month` TINYINT UNSIGNED,
    `release_day` TINYINT UNSIGNED,
    PRIMARY KEY (`id`)
);

-- Labels
-- `name` is really long because of outliers
CREATE TABLE `labels` (
    `id` MEDIUMINT UNSIGNED AUTO_INCREMENT,
    `entity_id` VARCHAR(15) NOT NULL,
    `name` VARCHAR(65) NOT NULL,
    PRIMARY KEY (`id`)
);

-- Instruments
CREATE TABLE `instruments` (
    `id` MEDIUMINT UNSIGNED AUTO_INCREMENT,
    `entity_id` VARCHAR(15) NOT NULL,
    `name` VARCHAR(32) NOT NULL,
    PRIMARY KEY (`id`)
);

-- Junction Tables:
-- NOTE: The junctions use Wiki's enitity ID's.

-- 'recorded_by' connecting musicians to albums:
CREATE TABLE `recorded_by` (
    `musician_id` MEDIUMINT UNSIGNED,
    `album_id` MEDIUMINT UNSIGNED,
    PRIMARY KEY (`musician_id`, `album_id`),
    FOREIGN KEY (`musician_id`) REFERENCES `musicians`(`id`),
    FOREIGN KEY (`album_id`) REFERENCES `albums`(`id`)
);

-- 'recorded_on' connecting albums to labels:
CREATE TABLE `recorded_on` (
    `album_id` MEDIUMINT UNSIGNED,
    `label_id` MEDIUMINT UNSIGNED,
    PRIMARY KEY (`album_id`, `label_id`),
    FOREIGN KEY (`album_id`) REFERENCES `albums`(`id`),
    FOREIGN KEY (`label_id`) REFERENCES `labels`(`id`)
);

-- 'played' connecting musicians to the instrument(s) they play:
CREATE TABLE `played` (
    `musician_id` MEDIUMINT UNSIGNED,
    `instrument_id` MEDIUMINT UNSIGNED,
    PRIMARY KEY (`musician_id`, `instrument_id`),
    FOREIGN KEY (`musician_id`) REFERENCES `musicians`(`id`),
    FOREIGN KEY (`instrument_id`) REFERENCES `instruments`(`id`)
);

-- Temporary tables:
-- Used for getting the 'junction' tables in, and getting Wikibase codes to be my native IJMDB codes.
-- The INSERT statements that copy these rows into the real junction tables are in queries.sql.

CREATE TABLE `temp_recorded_by` (
    `musician_id` VARCHAR(32),
    `album_id` VARCHAR(32)
);

CREATE TABLE `temp_recorded_on` (
    `album_id` VARCHAR(32),
    `label_id` VARCHAR(32)
);

CREATE TABLE `temp_played` (
    `musician_id` VARCHAR(32),
    `instrument_id` VARCHAR(32)
);

-- Views:

-- A view to see which instruments are most or least played across the data.
CREATE VIEW `instrument_count` AS
SELECT `instruments`.`name`, COUNT(*) AS 'count'
FROM `played`
JOIN `instruments`
ON `played`.`instrument_id` = `instruments`.`id`
GROUP BY `played`.`instrument_id`
ORDER BY `count` DESC;

-- A view on the database containing essential 'stats' on a musician.
-- This table will have redundancy whenever that musician played multiple instruments.
CREATE VIEW `musician_stats` AS
SELECT DISTINCT `musicians`.`name`, `musicians`.`year_of_birth`, `instruments`.`name` AS `instrument`
FROM `musicians`
LEFT JOIN `played`
ON `played`.`musician_id` = `musicians`.`id`
LEFT JOIN `instruments`
ON `instruments`.`id` = `played`.`instrument_id`;

-- A view on just albums and the musicians who recorded it
-- This table has redundant album names whenever that album was recorded by multiple instruments
CREATE VIEW `album_list` AS
SELECT `albums`.`name` AS 'album_name', `musicians`.`name` AS 'recorded_by'
FROM `albums`
JOIN `recorded_by`
ON `recorded_by`.`album_id` = `albums`.`id`
JOIN `musicians`
ON `recorded_by`.`musician_id` = `musicians`.`id`;

-- Indexes:

-- I'm guessing users will want to search for various albums or musicians by name. 
-- Let's make indexes on the 'name' columns for those tables

CREATE INDEX `musician_names`
ON `musicians` (`name`);

CREATE INDEX `album_names`
ON `albums` (`name`);

-- Years are important markers of jazz history - different periods of time might be of interest to different users..
-- Indexing on years could be useful too - especially albums

CREATE INDEX `albums_by_year`
ON `albums` (`name`, `release_year`);

-- Also, we often had to find a unique musician who might have a common name like 'Bill Evans' by also finding their birth year to identify them.
-- Indexing on birth year will make searches faster.

CREATE INDEX `musicians_by_birth_year`
ON `musicians` (`name`, `year_of_birth`);

-- Stored Procedures:

-- I can look at the amount of the rows with an external database GUI - or running COUNT(*) individually..
-- A stored procedure that does this automatically for all tables would be good.

delimiter //
CREATE PROCEDURE table_counts()
BEGIN
    SELECT COUNT(*) AS `albums_row_count` FROM `albums`;
    SELECT COUNT(*) AS `instruments_row_count`FROM `instruments`;
    SELECT COUNT(*) AS `labels_row_count` FROM `labels`;
    SELECT COUNT(*) AS `musicians_row_count` FROM `musicians`;
END //
delimiter ;

-- Sub queries that return multiple/duplicates can change the outer queries or cause errors when we don't expect them.
-- Let's add a quick tool that tells us how many things are named a certain parameter - in a given table
-- Here a quick check of names and prepared statement was needed

delimiter //
CREATE PROCEDURE name_count(IN p_table_name VARCHAR(10), item_name VARCHAR(100))
BEGIN
    IF p_table_name NOT IN ('musicians', 'albums', 'labels') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid table name provided.';
    END IF;

    SET @query = CONCAT('SELECT COUNT(*) AS name_count FROM ', p_table_name, ' WHERE `name` = ?');
    SET @name = item_name;

    PREPARE stmt FROM @query;
    EXECUTE stmt USING @name;
    DEALLOCATE PREPARE stmt;
END //
delimiter ;

-- Finally, when I want to extend this database, for the junction tables - 
-- I need to do the insertion to the temp table, then insert from it into the actual table.
-- I want to make a stored procedure that does this a little easier.

delimiter //
CREATE PROCEDURE insert_from_tmp(IN p_table_name VARCHAR(12))
BEGIN
    IF p_table_name NOT IN ('recorded_on', 'recorded_by', 'played') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid table name provided.';
    END IF;

    IF p_table_name = 'recorded_on' THEN
        SET @query = 
            'INSERT INTO `recorded_on`
             SELECT `albums`.`id` AS `album_id`, `labels`.`id` AS `label_id`
             FROM `albums`
             INNER JOIN `temp_recorded_on`
             ON `albums`.`entity_id` = `temp_recorded_on`.`album_id`
             INNER JOIN `labels`
             ON `labels`.`entity_id` = `temp_recorded_on`.`label_id`
             ORDER BY `album_id`';
    ELSEIF p_table_name = 'recorded_by' THEN
        SET @query = 
            'INSERT INTO `recorded_by`
             SELECT `musicians`.`id` AS `musician_id`, `albums`.`id` AS `album_id`
             FROM `musicians`
             JOIN `temp_recorded_by`
             ON `musicians`.`entity_id` = `temp_recorded_by`.`musician_id`
             LEFT JOIN `albums`
             ON `albums`.`entity_id` = `temp_recorded_by`.`album_id`
             ORDER BY `album_id`';
    ELSE
        SET @query =
            'INSERT INTO `played`
             SELECT DISTINCT `musicians`.`id` AS `musician_id`, `instruments`.`id` AS `instrument_id`
             FROM `musicians`
             INNER JOIN `temp_played`
             ON `musicians`.`entity_id` = `temp_played`.`musician_id`
             INNER JOIN `instruments`
             ON `instruments`.`entity_id` = `temp_played`.`instrument_id`
             ORDER BY `musician_id`';
    END IF;

    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END //
delimiter ;

