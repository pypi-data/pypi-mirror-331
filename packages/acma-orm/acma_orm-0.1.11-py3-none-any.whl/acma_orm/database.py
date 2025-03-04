# my_acma_package/database.py

from peewee import SqliteDatabase

# Create a global database instance.
db = SqliteDatabase("acma.db")


def initialize(db_filename="acma.db"):
    """
    Initialize the database connection and create tables.
    Models are imported here to avoid circular imports.
    """
    db.init(db_filename)
    db.connect()

    # Import models dynamically to avoid circular imports.
    from . import models

    # List your models here.
    models_to_create = [
        models.Site,
        models.Client,
        models.Licence,
        models.Satellite,
        models.ReportsTextBlock,
        models.NatureOfService,
        models.LicencingArea,
        models.LicenceStatus,
        models.LicenceSubservice,
        models.LicenceService,
        models.IndustryCat,
        models.FeeStatus,
        models.AntennaPolarity,
        models.AccessArea,
        models.DeviceDetail,
        models.ClientType,
        models.ClassOfStation,
        models.Bsl,
        models.BslArea,
        models.AuthSpectrumFreq,
        models.AuthSpectrumArea,
        models.ApplicTextBlock,
        models.Antenna,
        models.AntennaPattern,
    ]
    db.drop_tables(models_to_create)
    db.create_tables(models_to_create, safe=True)
    return db


def close_db():
    """Close the database connection if open."""
    if not db.is_closed():
        db.close()
        print("Database closed.")
