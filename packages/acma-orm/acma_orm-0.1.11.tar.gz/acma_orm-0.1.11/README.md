# ACMA ORM

ACMA ORM is a Python library designed to quickly import the AMCA specrta_rrl data dump into a termporary SQLite database and provide an intuitive Peewee ORM interface for querying records. This library is intended to be used locally for data analytics.

## Features

-   **Bulk CSV Import**: Efficiently load ACMA CSV dumps into a SQLite database using Pandas
-   **ORM Interface**: Query your data using Peewee ORM. Examples provided below

## Installation and Usage

```sh
pip install acma-orm
```

Download [spectra_rrl](https://web.acma.gov.au/rrl-updates/spectra_rrl.zip) and extract all files into `path/to/spectra_rrl_directory` (wherever you want, as long as Python can find it)

Once installed use like below:

```py
from acma_orm.importer import import_all_data
from acma_orm.models import Licence, Client
from playhouse.shortcuts import model_to_dict

# Import your CSV dump (ensure your CSV files are in the specified folder)
import_all_data("path/to/spectra_rrl_directory")

# Query licences for a specific client.
query = (Licence
         .select(Licence)
         .join(Client)
         .where((Client.licencee == "TELSTRA LIMITED") &
                (Client.trading_name == "Telstra - Commerical Engineering - Spectrum Strategy")))
for licence in query:
    print(model_to_dict(licence, recurse=True))

```

## Contributing

1. **Install UV**:

    ```sh
    pip install uv
    ```

2. Close the Repo and sync environment

    ```sh
    git clone https://github.com/jacksonbowe/acma-orm.git
    cd acma-orm

    uv sync
    ```

3. Download [spectra_rrl](https://web.acma.gov.au/rrl-updates/spectra_rrl.zip) and extract all files into `examples/spectral_rrl`

4. Run Example Scripts:  
   The `examples/` directory contains individual scripts that demonstrate various query types. For instance, run:

    ```sh
    uv run examples/init.py
    uv run examples/simple_query.py
    uv run examples/join_query.py
    uv run examples/aggregation_query.py
    uv run examples/complex_query.py
    ```

## Project Structure

```
acma-orm/
├── pyproject.toml            # Build configuration for UV (and PyPI metadata)
├── README.md                # This file
├── LICENSE                  # License file (MIT License)
├── examples/                # Example scripts demonstrating package usage
│   ├── spectra_rrl/
│   │   ├── <put_spectra_rrl_data_in_here>
│   ├── init.py              # Run me first
│   ├── simple_query.py
│   ├── join_query.py
│   ├── aggregation_query.py
│   └── complex_query.py
├── src/
│   └── acma_orm/            # Package source code
│       ├── __init__.py      # Exposes package API (including enable_debug_logging)
│       ├── database.py      # Database connection and initialization logic
│       ├── importer.py      # Functions to import CSV data
│       └── models.py        # Peewee ORM model definitions
```

## License

This project is licensed under the MIT License
