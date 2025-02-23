from pydantic import BaseModel
from openai import OpenAI
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import sqlite3
import logging
import argparse
import sys
import time
import os
import yaml

logger = logging.getLogger(__name__)


def setup_parser():
    """Reads user options from command line arguments."""
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        add_help=False,
        description="Labels DB with ChatGPT.",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="show help and exit",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="config.yaml",
        help="config file",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="input db",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="output db",
    )
    parser.add_argument(
        "-l",
        "--log",
        type=str,
        default="labeldb.log",
        help="log file",
    )
    parser.add_argument(
        "-ll",
        "--loglevel",
        type=str,
        default="info",
        help="log level (debug, info, warning, error, critical)",
    )
    return parser.parse_args()


def init_db(db_name):
    """Initializes the SQLite database and creates the necessary table."""
    logger.info("Initializing database.")
    db = sqlite3.connect(db_name)
    cursor = db.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            author TEXT,
            handle TEXT,
            timestamp TEXT,
            query TEXT,
            text TEXT,
            label TEXT
        )
        """
    )
    db.commit()
    logger.info("Database initialized successfully.")
    return db, cursor


def open_db(db_name):
    """Initializes the SQLite database and creates the necessary table."""
    logger.info("Conntecting to database.")
    db = sqlite3.connect(db_name)
    cursor = db.cursor()
    logger.info("Conntected to database successfully.")
    return db, cursor


model = "gpt-4o-mini"


def process_row(client, row, event, true_value="true", false_value="false"):
    id_, author, handle, timestamp, query, text, *_ = row

    global model
    start = time.time()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"Tell me if the internet post is about {event}. You should only return true or false.",
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        store=True,
    )
    diff = time.time() - start
    if diff > 5:
        model = "gpt-4o-mini" if "gpt-3.5-turbo" in model else "gpt-3.5-turbo"
    label = completion.choices[0].message.content.lower()
    logger.info(f"{str(diff)[:5]}s - {model} - {label}")

    if "true" in label:
        label = true_value
    else:
        label = false_value

    return (
        id_,
        author,
        handle,
        timestamp,
        query,
        text,
        label,
    )


def load_config(config_file):
    """Reads user options in config file."""
    if not os.path.exists(config_file):
        logger.error("No config file found")
        create = input(f"Create {config_file} y/n: ").lower()
        if create == "y":
            with open(config_file, "w") as file:
                file.write("user:\npass:")
        exit()
    with open(config_file, "r") as file:
        return yaml.safe_load(file)


def main():
    logger.info("Labeling DB data")

    args = setup_parser()
    config = load_config(args.config)
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
    input_db, input_cursor = open_db(args.input)
    output_db, output_cursor = init_db(args.output)

    api_key = config.get("openai_api_key")
    client = OpenAI(api_key=api_key)

    input_cursor.execute("SELECT * FROM posts")
    rows = input_cursor.fetchall()

    event = "a blizzard and dangerous winter weather conditions"
    true_value = "blizzard"
    for row in rows:
        logger.info((" ".join(row[5].split("\n")))[:200])
        if not output_cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM posts WHERE id = (?))", (row[0],)
        ).fetchone()[0]:
            new_row = process_row(
                client, row, event, true_value=true_value, false_value="other"
            )
            output_cursor.execute(
                "INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?)", new_row
            )
            output_db.commit()
            time.sleep(1)
        else:
            logger.info("Post already in DB")

    input_db.close()
    output_db.close()


if __name__ == "__main__":
    main()
