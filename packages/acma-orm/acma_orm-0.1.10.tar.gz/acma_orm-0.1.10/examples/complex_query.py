"""
A complex query example that retrieves a limited number of DeviceDetail records,
joined with the related Site and Licence data for detailed inspection.

Run with:
    uv run examples/complex_query.py
"""

from pprint import pprint
from playhouse.shortcuts import model_to_dict
from acma_orm import enable_debug_logging
from acma_orm.models import DeviceDetail, Site, Licence
from acma_orm.database import close_db


def main():
    enable_debug_logging()
    print(
        "Executing complex query for DeviceDetail records with joined Site and Licence data...\n"
    )
    query = (
        DeviceDetail.select(DeviceDetail, Site, Licence)
        .join(Site, on=(DeviceDetail.site == Site.site_id))
        .switch(DeviceDetail)
        .join(Licence, on=(DeviceDetail.licence_no == Licence.licence_no))
        .limit(10)
    )
    for record in query:
        # try:
        pprint(model_to_dict(record))
        # except:
        #     pass
    close_db()
    print("\nComplex query example completed.")


if __name__ == "__main__":
    main()
