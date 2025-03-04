"""
An aggregation query example that counts licences grouped by status.

Run with:
    uv run examples/aggregation_query.py
"""

from acma_orm import enable_debug_logging
from acma_orm.models import Licence
from acma_orm.database import close_db
from peewee import fn


def main():
    enable_debug_logging()
    print("Executing aggregation query: counting licences by status...\n")
    query = Licence.select(
        Licence.status, fn.COUNT(Licence.licence_no).alias("count")
    ).group_by(Licence.status)
    for row in query.dicts():
        print(row)
    close_db()
    print("\nAggregation query example completed.")


if __name__ == "__main__":
    main()
