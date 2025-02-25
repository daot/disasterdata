import sqlite3
import logging
import argparse
import csv
import os
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

logger = logging.getLogger(__name__)


def setup_parser():
    """Reads user options from command line arguments."""
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        add_help=False,
        description="Converts TSV file to SQLite database.",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="show help and exit",
    )
    parser.add_argument(
        "-t",
        "--tsv",
        type=str,
        required=True,
        help="Input TSV file",
    )
    parser.add_argument(
        "-d",
        "--db",
        type=str,
        required=True,
        help="Output SQLite database",
    )
    parser.add_argument(
        "-l",
        "--log",
        type=str,
        default="tsv2db.log",
        help="Log file",
    )
    parser.add_argument(
        "-ll",
        "--loglevel",
        type=str,
        default="info",
        help="Log level (debug, info, warning, error, critical)",
    )
    return parser.parse_args()


def open_db(db_name):
    """Initializes the SQLite database."""
    logger.info("Connecting to database.")
    db = sqlite3.connect(db_name)
    cursor = db.cursor()
    logger.info("Connected to database successfully.")
    return db, cursor


def create_table(cursor, table_name, columns):
    """Creates a table with the given column names."""
    columns_def = ", ".join([f'"{col}" TEXT' for col in columns])
    create_stmt = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_def});'
    cursor.execute(create_stmt)


def insert_data(db, cursor, table_name, rows):
    """Inserts rows into the table."""
    if not rows:
        return
    columns = rows[0].keys()
    placeholders = ", ".join(["?"] * len(columns))
    insert_stmt = (
        f'INSERT INTO "{table_name}" ({", ".join(columns)}) VALUES ({placeholders});'
    )
    cursor.executemany(insert_stmt, [tuple(row.values()) for row in rows])
    db.commit()


def read_tsv(tsv_file):
    """Reads the TSV file and returns a list of dictionaries."""
    with open(tsv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return list(reader)


def main():
    args = setup_parser()

    try:
        levels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        loglevel = levels[args.loglevel.lower()]
    except KeyError:
        logger.error("Invalid log level")
        exit()

    logger.setLevel(loglevel)
    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(args.log, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    db, cursor = open_db(args.db)
    table_name = os.path.splitext(os.path.basename(args.tsv))[0]

    rows = read_tsv(args.tsv)
    if not rows:
        logger.error("TSV file is empty or improperly formatted.")
        exit()

    create_table(cursor, table_name, rows[0].keys())
    insert_data(db, cursor, table_name, rows)

    logger.info("TSV file successfully converted to SQLite database.")
    db.close()


if __name__ == "__main__":
    main()
