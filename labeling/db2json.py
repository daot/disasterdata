import sqlite3
import logging
import argparse
import sys
import json
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
        default="DB.json",
        help="db location",
    )
    return parser.parse_args()


def format_json(posts):
    j = []
    for i, post in zip(range(len(posts)), posts):
        j.append({"id": i, "data": {"text": post["text"]}})
    return j


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
    j = format_json(posts)
    s = json.dumps(j)
    o_folder = (
        os.path.abspath(args.db)
        if args.output == "DB.json"
        else 
        args.output
    )

    output_path = os.path.join(
        os.path.dirname(o_folder), db_name + ".json"
    )
    '''
    pp = pprint.PrettyPrinter(
        stream=open(output_path, "w", encoding="utf-8"), compact=False
    )
    pp.pprint(j)
    '''

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(j, f, ensure_ascii=False, indent=4)

    db.close()


if __name__ == "__main__":
    main()
