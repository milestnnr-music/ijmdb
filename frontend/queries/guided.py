"""Parameterized SQL for guided (non–free-form) screens."""

DISCOGRAPHY = """
SELECT a.name
FROM albums a
WHERE a.id IN (
    SELECT rb.album_id
    FROM recorded_by rb
    WHERE rb.musician_id = (
        SELECT id FROM musicians
        WHERE name = :musician_name
        AND (:birth_year IS NULL OR year_of_birth = :birth_year)
        LIMIT 1
    )
)
ORDER BY a.name
"""

MUSICIAN_MATCH_COUNT = """
SELECT COUNT(*) AS n
FROM musicians
WHERE name = :name
"""

MUSICIANS_BY_NAME = """
SELECT id, name, year_of_birth, year_of_death
FROM musicians
WHERE name = :name
ORDER BY year_of_birth
"""

LABELS_FOR_MUSICIAN = """
SELECT DISTINCT l.name
FROM labels l
WHERE l.id IN (
    SELECT ro.label_id
    FROM recorded_on ro
    WHERE ro.album_id IN (
        SELECT rb.album_id
        FROM recorded_by rb
        WHERE rb.musician_id = (
            SELECT id FROM musicians
            WHERE name = :name
            AND (:birth_year IS NULL OR year_of_birth = :birth_year)
            LIMIT 1
        )
    )
)
ORDER BY l.name
"""

ALBUMS_BY_YEAR = """
SELECT name
FROM albums
WHERE release_year = :year
ORDER BY name
"""

ALBUMS_PER_YEAR = """
SELECT release_year, COUNT(*) AS album_count
FROM albums
GROUP BY release_year
ORDER BY release_year DESC
"""

INDIVIDUAL_ALBUMS_STATS = """
SELECT name, release_year
FROM albums
WHERE name LIKE :name_pattern
ORDER BY release_year DESC
"""

INSTRUMENT_POPULARITY = """
SELECT name, count
FROM instrument_count
ORDER BY count DESC
"""

SAXOPHONE_BREAKDOWN = """
SELECT i.name, COUNT(*) AS count
FROM played p
JOIN instruments i ON p.instrument_id = i.id
WHERE i.name LIKE '%saxophone'
GROUP BY p.instrument_id, i.name
ORDER BY count DESC
"""

KEYBOARD_BREAKDOWN = """
SELECT i.name, COUNT(*) AS count
FROM played p
JOIN instruments i ON p.instrument_id = i.id
WHERE i.name LIKE '%keyboard' OR i.name LIKE '%piano'
GROUP BY p.instrument_id, i.name
ORDER BY count DESC
"""

RARE_INSTRUMENTS = """
SELECT name, count
FROM instrument_count
WHERE count <= :max_count
ORDER BY count DESC, name
"""

INSTRUMENTS_FOR_MUSICIAN = """
SELECT DISTINCT instrument
FROM musician_stats
WHERE name = :name
AND (:birth_year IS NULL OR year_of_birth = :birth_year)
ORDER BY instrument
"""

MUSICIAN_COUNT = """
SELECT COUNT(*) AS n FROM musicians
"""

ALBUM_COUNT = """
SELECT COUNT(*) AS n FROM albums
"""

LABEL_COUNT = """
SELECT COUNT(*) AS n FROM labels
"""

LEARN_MORE_MUSICIANS = """
SELECT name, entity_id
FROM musicians
WHERE name LIKE :name_pattern
ORDER BY name, entity_id
LIMIT 500
"""

LEARN_MORE_ALBUMS = """
SELECT name, entity_id
FROM albums
WHERE name LIKE :name_pattern
ORDER BY name, entity_id
LIMIT 500
"""

LEARN_MORE_LABELS = """
SELECT name, entity_id
FROM labels
WHERE name LIKE :name_pattern
ORDER BY name, entity_id
LIMIT 500
"""
