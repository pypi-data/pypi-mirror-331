"""
A join query example that retrieves all licences (with full details)
for clients with a specific licencee and trading name.

Run with:
    uv run examples/join_query.py
"""

from acma_orm import enable_debug_logging
from acma_orm.models import Licence, Client
from acma_orm.database import close_db
from playhouse.shortcuts import model_to_dict


def main():
    enable_debug_logging()
    print(
        "Executing join query for licences of TELSTRA LIMITED with specific trading name... (limiting printing to first record to avoid spamming terminal)\n"
    )
    query = (
        Licence.select(Licence)
        .join(Client)
        .where(
            (Client.licencee == "TELSTRA LIMITED")
            & (
                Client.trading_name
                == "Telstra - Commerical Engineering - Spectrum Strategy"
            )
        )
    )
    for licence in query:
        # Convert the model (with joined Client data) to a dictionary.
        data = model_to_dict(licence, recurse=True)
        print(data)
        break  # Limit to one print to avoid spamming terminal
    close_db()
    print("\nJoin query example completed.")


if __name__ == "__main__":
    main()
