import os
import hashlib
import sqlite3
import argparse
import logging
from datetime import datetime

# Function to calculate the checksum of a file
def calculate_checksum(file_path, algorithm='md5', chunk_size=4096):
    hash_object = hashlib.new(algorithm)
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(chunk_size)
            if not data:
                break
            hash_object.update(data)
    return hash_object.hexdigest()

# Function to create the SQLite database and table
def create_database(database_file):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS checksums
                      (creation_time TEXT, checksum TEXT PRIMARY KEY, full_path TEXT, filename TEXT, size INTEGER)''')
    conn.commit()
    conn.close()

# Function to insert a checksum record into the database
def insert_checksum(database_file, checksum, full_path, filename, size):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    creation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor.execute("INSERT INTO checksums VALUES (?, ?, ?, ?, ?)",
                       (creation_time, checksum, full_path, filename, size))
        conn.commit()
    except sqlite3.IntegrityError:
        logging.warning(f"Checksum already exists for file '{full_path}'")
    conn.close()

# Function to scan a directory and calculate checksums for files
def scan_directory(directory, database_file, algorithm='md5'):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                try:
                    size = os.path.getsize(file_path)
                    checksum = calculate_checksum(file_path, algorithm)
                    insert_checksum(database_file, checksum, file_path, file, size)
                    logging.info(f"File '{file_path}' processed.")
                except Exception as e:
                    logging.error(f"Error processing file '{file_path}': {str(e)}")

# Command-line interface setup
def parse_arguments():
    parser = argparse.ArgumentParser(description='File checksum calculator and database saver')
    parser.add_argument('-d', '--directory', nargs='+', required=True, help='Directory(s) to scan')
    parser.add_argument('-db', '--database', required=True, help='SQLite database file')
    parser.add_argument('-a', '--algorithm', default='md5', help='Hash algorithm (default: md5)')
    parser.add_argument('-l', '--loglevel', default='INFO', help='Logging level (default: INFO)')
    return parser.parse_args()

# Main function
def main():
    args = parse_arguments()

    # Set the logging level
    logging.basicConfig(level=args.loglevel.upper())

    create_database(args.database)
    for directory in args.directory:
        scan_directory(directory, args.database, args.algorithm)

if __name__ == '__main__':
    main()