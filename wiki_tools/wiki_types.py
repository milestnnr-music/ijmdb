# Enums for the different types of items in the database.
from enum import Enum

PROPERTIES_TABLE = {
    'birth': 'P569',
    'death': 'P570',
    'inst': 'P1303',
    'perfs': 'P175',
    'pubdate': 'P577',
    'label': 'P264'
}

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

# Defining fields in addition to names and ids
class MusicianTypes(Enum):
    file_fields = ['entity_id', 'name', 'birth', 'death', 'inst']
    date_fields = ['birth', 'death']

class AlbumTypes(Enum):
    file_fields = ['entity_id', 'name', 'perfs', 'pubdate', 'label']
    date_fields = ['pubdate']

class NameOnlyTypes(Enum):
    file_fields = ['entity_id', 'name']

class FileColumns(Enum):
    MUSICIAN = MusicianTypes.file_fields
    ALBUM = AlbumTypes.file_fields
    NAMEONLY = NameOnlyTypes.file_fields