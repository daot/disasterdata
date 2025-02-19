# Script to remove some rows from the db files

import argparse
import sqlite3
import random

def main(args):
    try:
        connect = sqlite3.connect(args.database)
        cursor = connect.cursor()
    except Exception as e:
        print(f"Error connecting to database: {e}")
        exit(0)

    print("Connected to database successfully.")
    table_name = "posts"

    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_rows = cursor.fetchone()[0]

    remove = total_rows - args.rows
    if remove > 0:
        print(f"Removing {remove} rows from {args.database}.")
        response = input("Are you sure you want to remove rows? (y/n):")
        if response.lower() != "y":
            print("Exiting...")
            connect.close()
            exit(0)
        else:
            print("Continuing...")

        cursor.execute(f"SELECT id FROM {table_name}")
        ids = [row[0] for row in cursor.fetchall()] # get a list of the ids in the db
        random.shuffle(ids) # shuffle the ids
        for id in ids[:remove]: # remove until amount to remove is done
            cursor.execute(f"DELETE FROM {table_name} WHERE id = ?",(id,))

        connect.commit()
        print(f"Successfully removed {remove} rows from {args.database}.")
    else:
        print(f"No rows to remove; {args.database} already has less than or equal to {args.rows} rows.")

    connect.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d","--database",type=str,required=True,help="The database file name ending in .db")
    parser.add_argument("-i","--rows",type=int,default=1000,help="The number of rows to keep")
    main(parser.parse_args())