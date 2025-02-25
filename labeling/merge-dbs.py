import sqlite3
import glob
import os


def merge_databases(source_folder, output_db):
    # Get all SQLite database files in the source folder
    db_files = glob.glob(os.path.join(source_folder, "*-labeled.db"))

    if not db_files:
        print("No database files found in the source folder.")
        return

    # Connect to the output database
    output_conn = sqlite3.connect(output_db)
    output_cursor = output_conn.cursor()

    # Create the table in the output database if it doesn't exist
    output_cursor.execute(
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
    output_conn.commit()

    for db_file in db_files:
        print(f"Processing {db_file}...")

        # Connect to the source database
        source_conn = sqlite3.connect(db_file)
        source_cursor = source_conn.cursor()

        # Copy data from source database to output database
        source_cursor.execute("SELECT * FROM posts")
        rows = source_cursor.fetchall()

        for row in rows:
            try:
                output_cursor.execute(
                    "INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?)", row
                )
            except sqlite3.IntegrityError:
                # Skip duplicate primary key entries
                pass

        # Commit and close the source database connection
        output_conn.commit()
        source_conn.close()

    # Close the output database connection
    output_conn.close()
    print(f"Merging complete. Data saved to {output_db}")


if __name__ == "__main__":
    source_folder = "./db-files"  # Change to the folder containing the databases
    output_db = "merged.db"  # Name of the output database
    merge_databases(source_folder, output_db)
