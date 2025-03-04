from acma_orm.database import initialize, close_db
from acma_orm.models import Site
from acma_orm.importer import import_all_data
from acma_orm import enable_debug_logging


def main():
    enable_debug_logging()
    db = initialize("acma.db")
    print("Database initialized and tables created.")

    # Run a simple query.
    site_count = Site.select().count()
    print(f"Total number of Site records: {site_count}")

    import_all_data("./examples/spectra_rrl")

    # Close the database connection.
    close_db()
    print("Database closed.")


if __name__ == "__main__":
    main()
