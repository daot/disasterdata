import sqlite3
import logging
import argparse
import sys
import csv
import os
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import pprint


logger = logging.getLogger(__name__)


def setup_parser():
    """Reads user options from command line arguments."""
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        add_help=False,
        description="Converts db to Label Studio JSON.",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="show help and exit",
    )
    parser.add_argument(
        "-d",
        "--db",
        type=str,
        required=True,
        help="input db",
    )
    parser.add_argument(
        "-l",
        "--log",
        type=str,
        default="db2json.log",
        help="log file",
    )
    parser.add_argument(
        "-ll",
        "--loglevel",
        type=str,
        default="info",
        help="log level (debug, info, warning, error, critical)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="DB.tsv",
        help="db location",
    )
    return parser.parse_args()


def read_posts(db, cursor):
    cursor.execute("SELECT * FROM posts")
    column_names = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(column_names, row)) for row in rows]


def open_db(db_name):
    """Initializes the SQLite database and creates the necessary table."""
    logger.info("Conntecting to database.")
    db = sqlite3.connect(db_name)
    cursor = db.cursor()
    logger.info("Conntected to database successfully.")
    return db, cursor


def main():
    logger.info("Converting db to json")

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
    db_name = os.path.splitext(os.path.basename(args.db))[0]

    posts = read_posts(db, cursor)
    o_folder = os.path.abspath(args.db) if args.output == "DB.tsv" else args.output

    output_path = os.path.join(os.path.dirname(o_folder), db_name + ".tsv")

    keys = list(posts[0].keys())

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")

        # Write the header
        writer.writerow(keys)

        # Write the rows
        for row in zip(posts):
            writer.writerow(row[0].values())

    db.close()


if __name__ == "__main__":
    main()
