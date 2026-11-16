-- SQLite schema for ijmdb
PRAGMA foreign_keys = ON;

-- Record Tables:

-- Musicians:
CREATE TABLE `musicians` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `entity_id` TEXT NOT NULL,
    `name` TEXT NOT NULL,
    `birth_year` INTEGER,
    `birth_month` INTEGER,
    `birth_day` INTEGER,
    `death_year` INTEGER,
    `death_month` INTEGER,
    `death_day` INTEGER
);

-- Albums:
CREATE TABLE `albums` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `entity_id` TEXT NOT NULL,
    `name` TEXT NOT NULL,
    `release_year` INTEGER,
    `release_month` INTEGER,
    `release_day` INTEGER
);

-- Labels
CREATE TABLE `labels` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `entity_id` TEXT NOT NULL,
    `name` TEXT NOT NULL
);

-- Instruments
CREATE TABLE `instruments` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `entity_id` TEXT NOT NULL,
    `name` TEXT NOT NULL
);

-- Junction Tables:
-- NOTE: The junctions use Wiki's enitity ID's.

-- 'recorded_by' connecting musicians to albums:
CREATE TABLE `recorded_by` (
    `musician_id` INTEGER NOT NULL,
    `album_id` INTEGER NOT NULL,
    PRIMARY KEY (`musician_id`, `album_id`),
    FOREIGN KEY (`musician_id`) REFERENCES `musicians`(`id`),
    FOREIGN KEY (`album_id`) REFERENCES `albums`(`id`)
);

-- 'recorded_on' connecting albums to labels:
CREATE TABLE `recorded_on` (
    `album_id` INTEGER NOT NULL,
    `label_id` INTEGER NOT NULL,
    PRIMARY KEY (`album_id`, `label_id`),
    FOREIGN KEY (`album_id`) REFERENCES `albums`(`id`),
    FOREIGN KEY (`label_id`) REFERENCES `labels`(`id`)
);

-- 'played' connecting musicians to the instrument(s) they play:
CREATE TABLE `played` (
    `musician_id` INTEGER NOT NULL,
    `instrument_id` INTEGER NOT NULL,
    PRIMARY KEY (`musician_id`, `instrument_id`),
    FOREIGN KEY (`musician_id`) REFERENCES `musicians`(`id`),
    FOREIGN KEY (`instrument_id`) REFERENCES `instruments`(`id`)
);

-- Temporary tables:
-- Used for getting the 'junction' tables in, and getting Wikibase codes to be my native IJMDB codes.
-- The INSERT statements that copy these rows into the real junction tables are in queries.sql.

CREATE TABLE `temp_recorded_by` (
    `musician_id` TEXT,
    `album_id` TEXT
);

CREATE TABLE `temp_recorded_on` (
    `album_id` TEXT,
    `label_id` TEXT
);

CREATE TABLE `temp_played` (
    `musician_id` TEXT,
    `instrument_id` TEXT
);

-- Views:

-- A view to see which instruments are most or least played across the data.
CREATE VIEW `instrument_count` AS
SELECT `instruments`.`name`, COUNT(*) AS `count`
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
SELECT `albums`.`name` AS `album_name`, `musicians`.`name` AS `recorded_by`
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
ON `musicians` (`name`, `birth_year`);

-- Stored procedures (MySQL-only; SQLite equivalents):
--
-- SQLite has no stored procedures, PREPARE/session variables, or SIGNAL.
-- Use these ad hoc queries (or application code) instead.

-- table_counts()
-- SELECT COUNT(*) AS `albums_row_count` FROM `albums`;
-- SELECT COUNT(*) AS `instruments_row_count` FROM `instruments`;
-- SELECT COUNT(*) AS `labels_row_count` FROM `labels`;
-- SELECT COUNT(*) AS `musicians_row_count` FROM `musicians`;

-- name_count(table, name) — example for musicians (repeat pattern for albums / labels):
-- SELECT COUNT(*) AS `name_count` FROM `musicians` WHERE `name` = 'Miles Davis';

-- insert_from_tmp — junction loads are in queries.sql (INSERT INTO ... SELECT ...).
