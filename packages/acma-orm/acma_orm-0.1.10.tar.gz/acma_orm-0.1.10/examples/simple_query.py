"""
A simple query example that counts the number of Site records in the database.

Run with:
    uv run examples/simple_query.py
"""

from acma_orm import enable_debug_logging
from acma_orm.models import Site
from acma_orm.database import close_db


def main():
    enable_debug_logging()
    site_count = Site.select().count()
    print(f"Total number of Site records: {site_count}")
    close_db()
    print("Simple query example completed.")


if __name__ == "__main__":
    main()
