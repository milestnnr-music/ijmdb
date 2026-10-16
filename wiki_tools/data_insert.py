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
Wraps the to_sql pandas function to automatically connect with the MySQL DB.

"""
import csv
import pandas
import numpy as np
from sqlalchemy import create_engine

DB_URI = "mysql+pymysql://root:@localhost:3306/ijmdb"


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


def flatfile_to_df(file: str, columns: list, dates: list | None = None) -> pandas.DataFrame:
    """
    Take a flat file that contains all record information returned by Wikidata requests, return a pandas DataFrame.

    Splits out any dates into columns of year, month, day. All of datatype Int64, the nulllable integer type.

    Args:
        file(str): a file to be imported into a DF
        columns(list): a list of columns that are included.
        dates(list): a list of those columns which are dates
    """
    if dates:
        df = pandas.read_csv(file, usecols=columns,
                             parse_dates=dates)
    else:
        df = pandas.read_csv(file, usecols=columns)

    # Making sure we make an actual copy of this DataFrame, as we intend to modify it.
    if 'name' in columns:
        removed_na_df = df[df['name'].notna()].copy()
    # For all of the values that are okay to be null, set them to None, as this will actually become NULL in the DB
    # Note that I needed to use NumPy because that is where pandas gets its datatypes.
        removed_na_df = removed_na_df.replace({np.nan: None})
    else:
        # no name and no dates means it was a junction table - guard against any NaN's
        df = df.dropna(how='any')
        return df
    if dates:
        edited_df = pandas.DataFrame()
        # TODO: Figure out if the iterating here is correct:
        # Each time, we should act on the original DF - removing a column, joining the new three in its place.
        for date in dates:
            # Creates a new dataframe with 3 cols, each with a different number
            split_date = removed_na_df[date].str.split('-', expand=True)
            split_date = split_date.astype('Int64')
            split_date = split_date.rename(
                columns={0: f"{date}_year", 1: f"{date}_month", 2: f"{date}_day"})
            edited_df = removed_na_df.drop(date, axis=1)
            edited_df = edited_df.join(split_date)
            edited_df = edited_df.replace({0: None})
        return edited_df
    else:
        return removed_na_df


def df_to_db(df: pandas.DataFrame, table: str):
    """
    Wraps the to_sql pandas function to automatically connect with the MySQL DB.

    Sets if_exists = 'append' as to never delete information from a table that already exists.

    Args:
        df(pandas.DataFrame): the dataframe to be inserted
        table(str): the name of the table to be created or appended to.
    """
    engine = create_engine(DB_URI, echo=True)
    rows = df.to_sql(table, engine, if_exists='append',
                     index=False)
    print(rows, "rows added.")
