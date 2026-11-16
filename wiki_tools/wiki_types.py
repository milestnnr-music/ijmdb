# Enums for the different types of items in the database.
from enum import Enum


class EntityTypes(Enum):
    MUSICIAN = 'musician'
    ALBUM = 'album'
    NAMEONLY = 'name-only'


class WikiProperties(Enum):
    BIRTH = 'P569'
    DEATH = 'P570'
    INST = 'P1303'
    PERFS = 'P175'
    PUBDATE = 'P577'
    LABEL = 'P264'


class DatabaseTables(Enum):
    MUSICIANS = 'musicians'
    ALBUMS = 'albums'
    LABELS = 'labels'
    INSTRUMENTS = 'instruments'
    RECORDED_BY = 'recorded_by'
    RECORDED_ON = 'recorded_on'
    PLAYED = 'played'
    TEMP_RECORDED_BY = 'temp_recorded_by'
    TEMP_RECORDED_ON = 'temp_recorded_on'
    TEMP_PLAYED = 'temp_played'

# Defining fields in addition to names and ids


class MusicianTypes(Enum):
    wiki_properties = {'birth': WikiProperties.BIRTH,
                       'death': WikiProperties.DEATH, 'inst': WikiProperties.INST}
    file_fields = ['entity_id', 'name', 'birth', 'death', 'inst']
    date_fields = ['birth', 'death']
    record_table = DatabaseTables.MUSICIANS


class AlbumTypes(Enum):
    wiki_properties = {'perfs': WikiProperties.PERFS,
                       'pubdate': WikiProperties.PUBDATE, 'label': WikiProperties.LABEL}
    file_fields = ['entity_id', 'name', 'perfs', 'pubdate', 'label']
    date_fields = ['pubdate']
    record_table = DatabaseTables.ALBUMS


class NameOnlyTypes(Enum):
    file_fields = ['entity_id', 'name']
