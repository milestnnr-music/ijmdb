-- SQLite schema for ijmdb
PRAGMA foreign_keys = ON;

-- Common queries:

-- Which albums did 'x' musician record/was the bandleader on?
-- Here, it's Miles Davis's discography
-- (I turned this into a view, 'albums_list')
SELECT `name` 
FROM `albums` 
WHERE `id` IN 
    (SELECT `album_id` 
     FROM `recorded_by` 
     WHERE `musician_id` = (SELECT `id`
                            FROM `musicians`
                            WHERE `name` = 'Miles Davis'));

-- Which albums came out in 'x' year? 
-- Here it's 1959 (an important year in Jazz music)

SELECT `name`
FROM `albums`
WHERE `release_year` = 1959
ORDER BY `name`;

-- How many albums came out each year, for each year?
-- Interesting to note, there are a lot of NULL years, where WikiData didn't know

SELECT `release_year`, COUNT(*) as '#_of_albums'
FROM `albums`
GROUP BY `release_year`
ORDER BY `release_year` DESC;

-- There are occasional double names - "Bill Evans" is not only a pianist, but also a saxophonist!
-- Let's figure out which is which. ID and date of birth should be good enough.

SELECT `musicians`.`id`,`musicians`.`name`, `musicians`.`year_of_birth`, `instruments`.`name`
FROM `musicians`
LEFT JOIN `played`
ON `played`.`musician_id` = `musicians`.`id`
LEFT JOIN `instruments`
ON `played`.`instrument_id` = `instruments`.`id`
WHERE `musicians`.`name` = 'Bill Evans';

-- With which labels was 'x' musician affilliated with?
-- Drawn from all of the albums they have been listed on Wikipedia, could be incomplete for all appearances.
-- Here, we ask about Bill Evans - the pianist! (born 1929)

SELECT `name`
FROM `labels`
WHERE `id` IN 
    (SELECT `label_id` 
     FROM `recorded_on`
     WHERE `album_id` IN 
        (SELECT `album_id`
         FROM `recorded_by`
         WHERE `musician_id` =
            (SELECT `id`
             FROM `musicians`
             WHERE `name` = 'Bill Evans' AND
                    `year_of_birth` = 1929)));

-- The `instruments` table contains some seriously weird instruments.. (Including many I wasn't expecting.)
-- I want to see the most common and least common instruments played in this dataset, for starters.

SELECT `instruments`.`name`, COUNT(*) AS 'count'
FROM `played`
JOIN `instruments`
ON `played`.`instrument_id` = `instruments`.`id`
GROUP BY `played`.`instrument_id`
ORDER BY `count` DESC;

-- Let's see the rankings of which "saxophone" is the most played, specifically. (There are rivalries to be resolved here...)
-- Lots of generic 'saxophone' listings, but looks like tenor saxophone wins!

SELECT `instruments`.`name`, COUNT(*) AS 'count'
FROM `played`
JOIN `instruments`
ON `played`.`instrument_id` = `instruments`.`id`
WHERE `instruments`.`name` LIKE '%saxophone'
GROUP BY `played`.`instrument_id`
ORDER BY `count` DESC;

-- Ok, about those weird instruments: Let's see which ones are played by less or equal to 5 people.
-- Let's refer to a new view on the table, 'instruments_count' (written in schema.sql, same as the query at line 62)

SELECT *
FROM `instrument_count`
WHERE `count` <= 5;

-- Some musicians were extremely experimental / adventurers in the land of instruments
-- What instruments did 'x' person play?
-- This is facilitated by referring to a new view on the table, `musician_stats`
-- Here, it's Herbie Hancock. (He was listed as playing 8 instruments! Most being keyboard based, but still)

SELECT `instrument` FROM `musician_stats` WHERE `name` = 'Herbie Hancock';