"""
Run requests on Wikidata's SPARQL and MediaWiki endpoints, and run batch writing processes on the responses.
Specfically setup for requests about musicians/albums/labels + other music related things.

get_batch_data()
Runs a batched process, reading a list of entities to request, parsing them, and writing them to a CSV.

get_ids()
Requests, parses, and writes to CSV all entity ID's for a given query, via Wikidata's SPARQL Query Service.

get_page_from_id()
Requests and returns JSON objects representing entities in Wikidata.

entity_to_item()
Converts Entity JSON into a simpler dict, to be written to a file.

link_to_entity()
Returns an entity ID for every Wikidata link passed in.

link_batches()
Constructs a list of batches of entities, to be requested of Wikidata.

link_generator()
Wrapper for link_batches, acts as a Python generator object.

convert_dates()
Turns the date formats returned by Wikidata into a cleaner format.

write_to_file()
Write a set of Wikidata items to a CSV for DB upload.
"""
import csv
from collections.abc import Iterator
import requests
import time
import wiki_tools.wiki_types as wiki_types

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
"""Wikidata linked data endpoint, MediaWiki"""
MEDIAWIKI_ENDPOINT = "https://www.wikidata.org/w/api.php"
"""Wikidata's Query Service Endpoint"""

HEADERS = {
    'User-Agent': 'MyFinalProjectDatabaseQuery/1.0 (milestnnr@gmail.com)'
}
"""Headers requrired for requests."""

"""Specific file fields needed for different objects."""


def get_batch_data(mode: wiki_types.EntityTypes, infile: str, outfile: str) -> bool:
    """
    Processes batches of Wikidata entitites from the infile.
    Writes their data to the outfile. 
    Takes a 'mode' param which decided which data will be retrieved and returned

    Args:
        mode (str): the type of data/entities to be processed.
        infile(str): a file path to file containing Wikidata Entity links.
        outfile(str): a file path to write final output to.
    """
    count = 0
    for index, batch in enumerate(link_generator(infile)):
        batch_data = []
        batched_ids = "|".join(batch)
        # For each batch we should request it's data.
        entities = get_page_from_id(batched_ids)
        # If we get an error - entities will be None
        if not entities:
            print(f"Break at batch {index}.")
            return False
        for entity in entities:
            # For each entity we get back -  we should get the appropriate items.
            entity_item = entity_to_item(entity, mode)
            # Don't write empty items / key only items.
            if len(entity_item.keys()) == 1:
                continue
            count += 1
            batch_data.append(entity_item)
        write_to_file(batch_data, mode, outfile)
        print("-" * 30)
        print("Batch proccessed and written. Waiting 5 seconds to requery.")
        print(f"{count} items processed.")
        print("-" * 30)
        time.sleep(5)
    return True


def get_ids(query: str) -> list | None:
    """
    Pass in a query to Wikidata's SPARQL service,
    returns back the Entity ID's that satisfy the constraints as JSON.

    Args:
        query (str): The query to be sent to the SPARQL_ENDPOINT.
    Raises:
        RequestException: Raised whenever a non-200 OK code is returned.
    """
    items_list = []
    params = {'query': query, 'format': "JSON"}

    try:
        # Send the POST request
        response = requests.get(
            SPARQL_ENDPOINT, params=params, headers=HEADERS)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
        return None
    if response.status_code == 200:
        print("Success!")
    # Parse the JSON response
    result = response.json()

    if 'results' in result and 'bindings' in result['results']:
        bindings = result['results']['bindings']
        print(len(bindings), "results")
        for item in bindings:
            items_list.append(item['item']['value'])
        return items_list
    else:
        print("Nothing returned")
        return None


def get_page_from_id(ids: str) -> list[dict] | None:
    """
    Accept a list of Wikidata entity pages, send a request, return the JSON in a list.

    This function will silently handle 429 responses, and wait the appropriate amount.
    Anything else will print the status code and return None.

    Args:
        ids(str): the ids to be passed into the GET request for the MEDIAWIKI_ENDPOINT.
    """
    params = {
        "action": "wbgetentities",
        "ids": ids,
        "format": "json",
        "languages": "en"
    }

    response = requests.get(MEDIAWIKI_ENDPOINT, params=params, headers=HEADERS)
    # If we got something other than 429 or 200 (too many requests or OK)
    if not response.status_code in (200, 429):
        print(f"Response {response.status_code}")
        return None
    if response.status_code == 429:
        # Check if the server told us exactly how long to wait
        retry_after = int(response.headers.get("Retry-After", 5))
        print(f"Rate limited. Sleeping for {retry_after} seconds...")
        time.sleep(retry_after)

    data = response.json()
    try:
        entities = data['entities']  # type: dict
    except KeyError:
        return None
    entities_list = []
    # Take each entity in, put it in a list with the 'value' being the actual stuff inside.
    for key in entities.keys():
        entities_list.append({key: entities[key]})
    return entities_list


def entity_to_item(entity: dict, mode: wiki_types.EntityTypes) -> dict:
    """
    Accepts a Wikidata Entry, returns the necessary properties as dict, where
    operating modes decide which properties are used. 

    "musician", "album", "name-only" modes accepted.

    Args:
        entity(dict): a nested JSON object returned by MEDIAWIKI_ENDPOINT.
        mode(wiki_types.EntityTypes): the operating mode, "musician", "album" or "name_only". (Like for 'instruments' or 'labels'.)
    """
    new_item = {}

    # Set the entity_id as the only 'key' of this dictionary, as grabbed by the list() function
    # Note that we use this id later
    id = list(entity)[0]
    new_item['entity_id'] = id

    # If there is no name item - we can't identify this thing and it's not useful to us.
    # Return just it's id for checking later
    if len(entity[id]['labels']) == 0:
        return new_item

    # Names are in the 'labels' sub-dictionary
    new_item['name'] = entity[id]['labels']['en']['value']

    match mode:
        case wiki_types.EntityTypes.MUSICIAN:
            properties = wiki_types.MusicianTypes.wiki_properties
        case wiki_types.EntityTypes.ALBUM:
            properties = wiki_types.AlbumTypes.wiki_properties
        # We only really need the name and id of the label or instrument
        case wiki_types.EntityTypes.NAMEONLY:
            return new_item

    for prop, w_prop in properties.__dict__.items():
        # Skip over date of death where not applicable (yet.)
        if w_prop not in entity[id]['claims']:
            continue
        # Index into this particular property - this will be a list
        property_obj = entity[id]['claims'][w_prop]
        property_list = []
        for property_item in property_obj:
            sub_item = property_item['mainsnak']
            if sub_item['datatype'] == 'time':
                try:
                    time = sub_item['datavalue']['value']['time']
                    time = convert_dates(time)
                except KeyError:
                    time = None
                property_list.append(time)
            elif sub_item['datatype'] == 'wikibase-item':
                try:
                    linked_entity = sub_item['datavalue']['value']['id']
                except KeyError:
                    linked_entity = None
                property_list.append(linked_entity)

        # In the case we have only one thing we should use the first item of this list immediately.
        if (len(property_list) == 1):
            new_item[prop] = property_list[0]
        else:
            new_item[prop] = property_list

    return new_item


def link_to_entity(link: str) -> str:
    """Returns an entity ID for every Wikidata link passed in."""
    new_entity = link.removeprefix(
        'http://www.wikidata.org/entity/').removesuffix('\n')
    return new_entity


def link_generator(file: str) -> Iterator:
    """
    Takes in a file argument and creates a list of lists containing entity ids in groups of 50, returns the list as a generator.

    Args:
        file(str): a file containing many Wikdata links to read in
    """
    with open(file, 'r') as id_file:
        # Skip top line ('id')
        id_file.readline()
        # Store all of the lines in one big list, then each batch in a sublist, max size ~50 or 45 or so.
        entity_container = []
        finished = False
        while not finished:
            entity_batch = []
            while len(entity_batch) < 50:
                # Either we get a EOF error or link will be = ''
                try:
                    if (link := id_file.readline()):
                        new_entity = link_to_entity(link)
                        entity_batch.append(new_entity)
                    else:
                        finished = True
                        break
                except EOFError:
                    finished = True
                    break
            else:
                # Batch filled to 50; keep reading the next one.
                entity_container.append(entity_batch)
                continue
            # EOF: keep a trailing partial batch, including an empty one.
            entity_container.append(entity_batch)
        print(f"Length: {len(entity_container)} batches.")

    for index in range(len(entity_container)):
        yield entity_container[index]


def convert_dates(date: str) -> str:
    """
    Turns the date formats returned by Wikidata into a cleaner format.

    For example: +1928-04-02T00:00:00Z -> 1928-04-02

    Args:
        date(str): a date string to be cleaned
    """
    # Split on T to remove time, the rest is in ISO format
    date_time = date.partition('T')
    actual_date = date_time[0].removeprefix("+")
    return actual_date


def write_to_file(items: list[dict], mode: wiki_types.EntityTypes, outfile: str):
    """
    Write a set of Wikidata items to a CSV for DB upload.

    Presumably, these items have been constructed by calling entity_to_item().

    Args:
        items(list[dict]): A list of items to be printed, each contained in a dict.
        mode(wiki_types.EntityTypes): the operating mode of this file, specifing the fields to be printed
        outfile(str): a file path to append items to.
    """

    fieldnames = getattr(wiki_types, f"{mode}Types").file_fields
    with open(outfile, 'a') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        for item in items:
            writer.writerow(item)
