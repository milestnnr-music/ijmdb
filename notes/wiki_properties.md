# Wikidata Properties and JSON responses

Need to enter into:
entities -> Entity ID -> then aliases or 'claims'
'claims' is a long list of properties, with an associated object - a list which _contains one object_ for each item associated with that property.

Then items are under their property and inside a list of size one or longer:
"mainsnak" --> "datavalue" --> "value"

Names are all under:

> "labels" -> "en" -> Value

Times are of the form:

> "Property" --> first item in list --> "mainsnak" --> "datavalue" --> "value" --> "time"

Fields which are themselves "entities" are of the form

> "Property" --> for each item in list --> "mainsnak" --> "datavalue" --> "value" -> "id"

## Musician Properties

Date of Birth:

- Property P569
- Time value

Date of Death (if exists):

- Property P570
- Time value

Instrument (or multiple):

- Property 1303
- Returned as an entity

## Album Properties

Performers:

- Property P175
- Returned as an entity

Release Date:

- Property P577
- Time value

## Label Properties

- Property P264
- Returned as an entity
