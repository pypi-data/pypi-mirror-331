# my_acma_package/importer.py

import os
import sqlite3
import pandas as pd
from . import logger


def import_table(
    conn, data_dir, csv_filename, table_name, delimiter=",", chunksize=10000
):
    """
    Read a CSV file into a Pandas DataFrame and write it to an SQLite table.

    Parameters:
      conn         : sqlite3.Connection object.
      data_dir     : Directory containing CSV files.
      csv_filename : Name of the CSV file.
      table_name   : Name of the target SQLite table.
      delimiter    : CSV delimiter.
      chunksize    : Number of rows per chunk.
    """
    file_path = os.path.join(os.path.abspath(data_dir), csv_filename)
    logger.info(f"Importing {table_name} from {file_path}...")
    try:
        # Read CSV in chunks if desired:
        df_iter = pd.read_csv(file_path, delimiter=delimiter, chunksize=chunksize)
        total = 0
        for chunk in df_iter:
            # Convert column names to lowercase to match the SQLite table schema.
            chunk.columns = [col.lower() for col in chunk.columns]
            chunk.to_sql(table_name, con=conn, if_exists="append", index=False)
            total += len(chunk)
        logger.info(f"Imported {total} records into {table_name}.")
    except Exception as e:
        logger.error(f"Error importing {table_name} from {file_path}: {e}")


def import_all_data(data_dir, db_filename="acma.db"):
    """
    Bulk import all CSV files into the SQLite database using Pandas.
    This function sets PRAGMA options for speed, performs the import,
    and then closes the connection.
    """
    # Create SQLite connection
    conn = sqlite3.connect(db_filename)

    # Set PRAGMA options for faster inserts.
    conn.execute("PRAGMA synchronous = OFF;")
    conn.execute("PRAGMA journal_mode = MEMORY;")

    # Import tables in the required order (adjust table names to your schema):
    # Lookup Tables
    import_table(conn, data_dir, "licencing_area.csv", "licencingarea")
    import_table(conn, data_dir, "satellite.csv", "satellite")
    import_table(conn, data_dir, "reports_text_block.csv", "reportstextblock")
    import_table(conn, data_dir, "nature_of_service.csv", "natureofservice")
    import_table(conn, data_dir, "licence_status.csv", "licencestatus")
    import_table(conn, data_dir, "industry_cat.csv", "industrycat")
    import_table(conn, data_dir, "fee_status.csv", "feestatus")
    import_table(conn, data_dir, "client_type.csv", "clienttype")
    import_table(conn, data_dir, "licence_service.csv", "licenceservice")
    import_table(conn, data_dir, "antenna_polarity.csv", "antennapolarity")
    import_table(conn, data_dir, "access_area.csv", "accessarea")
    import_table(conn, data_dir, "bsl_area.csv", "bslarea")

    # Dependent Tables
    import_table(conn, data_dir, "site.csv", "site")
    import_table(conn, data_dir, "client.csv", "client")
    import_table(conn, data_dir, "licence_subservice.csv", "licencesubservice")
    import_table(conn, data_dir, "bsl.csv", "bsl")
    import_table(conn, data_dir, "licence.csv", "licence")

    # Complex Tables
    import_table(conn, data_dir, "antenna.csv", "antenna")
    import_table(conn, data_dir, "device_details.csv", "devicedetail")
    import_table(conn, data_dir, "auth_spectrum_freq.csv", "authspectrumfreq")
    import_table(conn, data_dir, "auth_spectrum_area.csv", "authspectrumarea")
    import_table(conn, data_dir, "applic_text_block.csv", "applictextblock")
    import_table(conn, data_dir, "antenna_pattern.csv", "antennapattern")

    conn.close()
    logger.info("Data import completed successfully.")
