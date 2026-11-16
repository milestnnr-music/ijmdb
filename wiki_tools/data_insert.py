"""
Functions to read flat files returned from Wikibase queries into databases.

make_junction()
Makes a junction table as a CSV.

list_parse()
Updates a Wikibase entity with a string of items to have a list.

make_list()
Take a string that looks like a list, returns it as an actual list.

update_lists()
Updates a CSV's columns to eliminate extraneous items.

flatfile_to_df()
Take a flat file that contains all record information returned by Wikidata requests, return a pandas DataFrame.

df_to_db()
Wraps the to_sql pandas function to automatically connect with the SQLite DB.

"""
import csv
from pathlib import Path
import wiki_tools.web_queries as queries
import wiki_tools.wiki_types as wiki_types
import numpy as np
import pandas
from sqlalchemy import create_engine, event
import argparse
import sys

_ROOT = Path(__file__).resolve().parents[1]
DB_URI = f"sqlite:///{_ROOT / 'ijmdb.db'}"


def main():
    """A data insert script to be run at the commandline."""
    parser = argparse.ArgumentParser(
        prog="IJMDB data insert",
    )
    arg_group = parser.add_mutually_exclusive_group()
    parser.add_argument('type', type=str)
    arg_group.add_argument('-f', '--file', action="store_true", nargs=1)
    arg_group.add_argument('-i', '--item', action="store_true", nargs=1)
    arg_group.add_argument('-j', '--junction', action="store_true", nargs=2)

    args = parser.parse_args()

    if args.type not in wiki_types.EntityTypes:
        sys.exit("Invalid type.")

    if args.file:
        type = args.type.title()
        new_df = flatfile_to_df(args.file, args.type)
        df_to_db(new_df, getattr(
            wiki_types, f"{type}Types").record_table)
    elif args.item:
        # Define procedure for inserting an individual item
        ...
    elif args.junction:
        # Define procedure for making a junction out of a table with lists
        ...
    else:
        ...


def _make_engine(*, echo: bool = False):
    """Create a SQLAlchemy engine with SQLite foreign-key enforcement enabled."""
    engine = create_engine(DB_URI, echo=echo)

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def make_junction(infile: str, outfile: str, fieldname: str) -> None:
    """
    Make a "many to many" relationship or junction table as a CSV.

    Args: 
        infile(str): a filepath to a csv with id's and items
        outfile(str): a filepath to a csv to be written to.
        fieldname(str): the field that is to be searched for lists
    """
    with open(infile, 'r') as read_file:
        reader = csv.DictReader(read_file)
        with open(outfile, 'a') as write_file:
            writer = csv.DictWriter(write_file, fieldnames=['id', 'item'])
            for row in reader:
                parsed_dict = list_parse(
                    {"id": row["id"],
                     "items": row[fieldname]}
                )
                # Write in a row for each instance of an item.
                for item in parsed_dict['items']:
                    writer.writerow(
                        {'id': parsed_dict['id'], 'item': item})


def list_parse(entry: dict) -> dict:
    """
    Take a dictionary, with an id and a string of items, 
    return the same but with a Python list rather than a string.

    Args: 
        entry(dict): a dict with 'entity_id' as it's Wikibase ID, and an 'items' str.
    """
    parsed_dict = {}
    parsed_dict['id'] = entry['id']
    # Make this string an actual list of its items
    items_list = make_list(entry['items'])
    parsed_dict['items'] = items_list
    return parsed_dict


def make_list(str: str) -> list:
    """
    Take a string that looks like a list, returns it as an actual list.
    """
    return str.removeprefix("[").removesuffix("]").replace("'", "").split(", ")


def update_lists(file: str, field: str):
    """
    Updates a csv with strings that contain multiple items to contain just the first item.

    Args:
        file(str): a file path to read from
        field(str): the field to read into
    """
    fieldnames = []
    updated_rows = []
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            # Remove any "empty rows"
            if row['name'] == '':
                continue
            try:
                target_list = row[field]
            except ValueError:
                print(f"Error: Column '{field}' not found.")
                return
            # If this is a fake "list"
            if target_list.startswith("["):
                # Make this string a list
                target_list = make_list(target_list)
                # Just get the first item from this list
                new_item = target_list[0]
                # Update the row
                row[field] = new_item
                # Add it to the new list
            updated_rows.append(row)

    with open(file, 'w') as f:
        if fieldnames:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
        # Fieldnames should never be none - but return if it is
        else:
            print("Need field names.")
            return
        writer.writeheader()
        writer.writerows(updated_rows)
        print(f"Updated {len(updated_rows)} rows.")


def flatfile_to_df(file: str, type: wiki_types.EntityTypes) -> pandas.DataFrame:
    """
    Take a flat file that contains all record information returned by Wikidata requests, return a pandas DataFrame.

    Splits out any dates into columns of year, month, day. All of datatype Int64, the nulllable integer type.

    Args:
        file(str): a file to be imported into a DF
        type(wiki_types.EntityTypes): the type of the item
    """

    # Keep date columns as strings. Wikidata uses 00 for an unknown month or day,
    # which is not a real calendar date, so parse_dates cannot be used here.
    columns = getattr(wiki_types, f"{type}Types").file_fields
    df = pandas.read_csv(file, usecols=columns)

    # Making sure we make an actual copy of this DataFrame, as we intend to modify it.
    # If name in columns, this is a record table - remove any rows with a null name
    if 'name' in columns:
        removed_na_df = df[df['name'].notna()].copy()
    # For all of the values that are okay to be null, set them to None, as this will actually become NULL in the DB
    # Note that I needed to use NumPy because that is where pandas gets its datatypes.
        removed_na_df = removed_na_df.replace({np.nan: None})
        removed_na_df = resolve_dates(removed_na_df, getattr(
            wiki_types, f"{type}Types").date_fields)
        return removed_na_df
    else:
        # no name and no dates means it was a junction table - guard against any NaN's
        return df.dropna(how='any')


def item_to_df(id: str, type: wiki_types.EntityTypes) -> pandas.DataFrame:
    """
    Takes a Wikidata ID and returns a DataFrame of the item.

    Args:
        id(str): the Wikidata ID of the item
        type(wiki_types.EntityTypes): the type of the item

    Returns:
        pandas.DataFrame: the dataframe of the item
    """
    entities = queries.get_page_from_id(id)
    if entities:
        entity_0 = entities[0]
        item = queries.entity_to_item(entity_0, type)
    else:
        print(f"No entity found for ID: {id}")
        return pandas.DataFrame()

    item_df = pandas.DataFrame(item)
    item_df = resolve_dates(item_df, getattr(
        wiki_types, f"{type}Types").date_fields)
    return item_df


def resolve_dates(dataframe: pandas.DataFrame, date_cols: list) -> pandas.DataFrame:
    """
    Resolves dates into year, month, day columns.

    Args:
        dataframe(pandas.DataFrame): the dataframe to be resolved
        date_cols(list): the columns that are dates

    Returns:
        pandas.DataFrame: the dataframe with the dates resolved
    """
    for date in date_cols:
        split_date = dataframe[date].astype(
            "string").str.split("-", expand=True)
        split_date = split_date.reindex(columns=range(3))
        split_date = split_date.astype("Int64")
        split_date = split_date.rename(
            columns={0: f"{date}_year", 1: f"{date}_month", 2: f"{date}_day"})
        split_date = split_date.replace({0: None})
        dataframe = dataframe.drop(columns=date).join(split_date)
    return dataframe


def df_to_db(df: pandas.DataFrame, table: str):
    """
    Wraps the to_sql pandas function to automatically connect with the SQLite DB.

    Sets if_exists = 'append' as to never delete information from a table that already exists.

    Args:
        df(pandas.DataFrame): the dataframe to be inserted
        table(str): the name of the table to be created or appended to.
    """
    engine = _make_engine(echo=True)
    rows = df.to_sql(table, engine, if_exists='append',
                     index=False)
    print(rows, "rows added.")
