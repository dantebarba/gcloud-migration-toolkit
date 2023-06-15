import argparse
import sqlite3

def compare_databases(db1_file, db2_file):
    # Connect to the first database
    conn1 = sqlite3.connect(db1_file)
    cursor1 = conn1.cursor()

    # Connect to the second database
    conn2 = sqlite3.connect(db2_file)
    cursor2 = conn2.cursor()

    # Retrieve the primary key values from both databases
    cursor1.execute('SELECT checksum FROM checksums')
    rows_db1 = set(cursor1.fetchall())
    cursor2.execute('SELECT checksum FROM checksums')
    rows_db2 = set(cursor2.fetchall())

    # Find the differences
    rows_only_in_db1 = rows_db1 - rows_db2
    rows_only_in_db2 = rows_db2 - rows_db1

    # Close the database connections
    conn1.close()
    conn2.close()

    # Return the results
    return list(rows_only_in_db1), list(rows_only_in_db2)

if __name__ == '__main__':
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Compare two SQLite databases.')

    # Add the arguments
    parser.add_argument('db1', type=str, help='Path to the first SQLite database file')
    parser.add_argument('db2', type=str, help='Path to the second SQLite database file')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the compare_databases function with the provided file paths
    db1_records, db2_records = compare_databases(args.db1, args.db2)

    # Print the results
    print(f'Records only in {args.db1}: {db1_records}')
    print(f'Records only in {args.db2}: {db2_records}')