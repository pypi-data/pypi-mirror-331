# my_acma_package/importer.py

import csv
import os
from datetime import datetime

from . import logger
from .database import db
from .models import (
    AccessArea,
    Antenna,
    AntennaPattern,
    AntennaPolarity,
    ApplicTextBlock,
    AuthSpectrumArea,
    AuthSpectrumFreq,
    Bsl,
    BslArea,
    Client,
    ClientType,
    DeviceDetail,
    FeeStatus,
    IndustryCat,
    Licence,
    LicenceService,
    LicenceStatus,
    LicenceSubservice,
    LicencingArea,
    NatureOfService,
    ReportsTextBlock,
    Satellite,
    Site,
)

DEFAULT_BATCH_SIZE = 1000

# -------------------------
# Lookup Table Imports
# -------------------------


def import_licensing_area(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "licensing_area.csv")
    logger.info(f"Importing LicencingArea from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "licensing_area_id": int(row["LICENSING_AREA_ID"]),
                    "description": row.get("DESCRIPTION"),
                }
            )
    if records:
        with db.atomic():
            for idx in range(0, len(records), batch_size):
                LicencingArea.insert_many(records[idx : idx + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into LicencingArea.")
    else:
        logger.info("No LicencingArea records found.")


def import_satellite(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "satellite.csv")
    logger.info(f"Importing Satellite from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "sa_id": int(row["SA_ID"]),
                    "sa_sat_name": row.get("SA_SAT_NAME"),
                    "sa_sat_long_nom": row.get("SA_SAT_LONG_NOM"),
                    "sa_sat_incexc": row.get("SA_SAT_INCEXC"),
                    "sa_sat_geo_pos": row.get("SA_SAT_GEO_POS"),
                    "sa_sat_merit_g_t": row.get("SA_SAT_MERIT_G_T"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                Satellite.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into Satellite.")
    else:
        logger.info("No Satellite records found.")


def import_reports_text_block(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "reports_text_block.csv")
    logger.info(f"Importing ReportsTextBlock from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "rtb_item": row["RTB_ITEM"],
                    "rtb_category": row.get("RTB_CATEGORY"),
                    "rtb_description": row.get("RTB_DESCRIPTION"),
                    "rtb_start_date": datetime.strptime(
                        row["RTB_START_DATE"], "%Y-%m-%d"
                    ).date()
                    if row.get("RTB_START_DATE")
                    else None,
                    "rtb_end_date": datetime.strptime(
                        row["RTB_END_DATE"], "%Y-%m-%d"
                    ).date()
                    if row.get("RTB_END_DATE")
                    else None,
                    "rtb_text": row.get("RTB_TEXT"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                ReportsTextBlock.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into ReportsTextBlock.")
    else:
        logger.info("No ReportsTextBlock records found.")


def import_nature_of_service(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "nature_of_service.csv")
    logger.info(f"Importing NatureOfService from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "code": row["CODE"],
                    "description": row.get("DESCRIPTION"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                NatureOfService.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into NatureOfService.")
    else:
        logger.info("No NatureOfService records found.")


def import_licence_status(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "licence_status.csv")
    logger.info(f"Importing LicenceStatus from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "status": row["STATUS"],
                    "status_text": row.get("STATUS_TEXT"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                LicenceStatus.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into LicenceStatus.")
    else:
        logger.info("No LicenceStatus records found.")


def import_industry_cat(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "industry_cat.csv")
    logger.info(f"Importing IndustryCat from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "cat_id": int(row["CAT_ID"]),
                    "description": row.get("DESCRIPTION"),
                    "name": row.get("NAME"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                IndustryCat.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into IndustryCat.")
    else:
        logger.info("No IndustryCat records found.")


def import_fee_status(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "fee_status.csv")
    logger.info(f"Importing FeeStatus from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "fee_status_id": int(row["FEE_STATUS_ID"]),
                    "fee_status_text": row.get("FEE_STATUS_TEXT"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                FeeStatus.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into FeeStatus.")
    else:
        logger.info("No FeeStatus records found.")


def import_client_type(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "client_type.csv")
    logger.info(f"Importing ClientType from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "type_id": int(row["TYPE_ID"]),
                    "name": row.get("NAME"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                ClientType.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into ClientType.")
    else:
        logger.info("No ClientType records found.")


def import_licence_service(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "licence_service.csv")
    logger.info(f"Importing LicenceService from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "sv_id": int(row["SV_ID"]),
                    "sv_name": row.get("SV_NAME"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                LicenceService.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into LicenceService.")
    else:
        logger.info("No LicenceService records found.")


def import_antenna_polarity(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "antenna_polarity.csv")
    logger.info(f"Importing AntennaPolarity from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "polarisation_code": row["POLARISATION_CODE"],
                    "polarisation_text": row.get("POLARISATION_TEXT"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                AntennaPolarity.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into AntennaPolarity.")
    else:
        logger.info("No AntennaPolarity records found.")


def import_access_area(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "access_area.csv")
    logger.info(f"Importing AccessArea from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "area_id": int(row["AREA_ID"]),
                    "area_code": row.get("AREA_CODE"),
                    "area_name": row.get("AREA_NAME"),
                    "area_category": row.get("AREA_CATEGORY"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                AccessArea.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into AccessArea.")
    else:
        logger.info("No AccessArea records found.")


def import_bsl_area(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "bsl_area.csv")
    logger.info(f"Importing BslArea from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "area_code": row["AREA_CODE"],
                    "area_name": row.get("AREA_NAME"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                BslArea.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into BslArea.")
    else:
        logger.info("No BslArea records found.")


# -------------------------
# Dependent Table Imports
# -------------------------


def import_site(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "site.csv")
    logger.info(f"Importing Site from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "site_id": int(row["SITE_ID"]),
                    "latitude": float(row["LATITUDE"]) if row.get("LATITUDE") else None,
                    "longitude": float(row["LONGITUDE"])
                    if row.get("LONGITUDE")
                    else None,
                    "name": row.get("NAME"),
                    "state": row.get("STATE"),
                    "licensing_area": int(row["LICENSING_AREA_ID"])
                    if row.get("LICENSING_AREA_ID")
                    else None,
                    "postcode": row.get("POSTCODE"),
                    "site_precision": row.get("SITE_PRECISION"),
                    "elevation": float(row["ELEVATION"])
                    if row.get("ELEVATION")
                    else None,
                    "hcis_l2": row.get("HCIS_L2"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                Site.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into Site.")
    else:
        logger.info("No Site records found.")


def import_client(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "client.csv")
    logger.info(f"Importing Client from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "client_no": int(row["CLIENT_NO"]),
                    "licencee": row.get("LICENCEE"),
                    "trading_name": row.get("TRADING_NAME"),
                    "acn": row.get("ACN"),
                    "abn": row.get("ABN"),
                    "postal_street": row.get("POSTAL_STREET"),
                    "postal_suburb": row.get("POSTAL_SUBURB"),
                    "postal_state": row.get("POSTAL_STATE"),
                    "postal_postcode": row.get("POSTAL_POSTCODE"),
                    "industry_cat": int(row["CAT_ID"]) if row.get("CAT_ID") else None,
                    "client_type": int(row["CLIENT_TYPE_ID"])
                    if row.get("CLIENT_TYPE_ID")
                    else None,
                    "fee_status": int(row["FEE_STATUS_ID"])
                    if row.get("FEE_STATUS_ID")
                    else None,
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                Client.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into Client.")
    else:
        logger.info("No Client records found.")


def import_licence_subservice(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "licence_subservice.csv")
    logger.info(f"Importing LicenceSubservice from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "ss_id": int(row["SS_ID"]),
                    "sv_sv_id": int(row["SV_SV_ID"]) if row.get("SV_SV_ID") else None,
                    "ss_name": row.get("SS_NAME"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                LicenceSubservice.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into LicenceSubservice.")
    else:
        logger.info("No LicenceSubservice records found.")


def import_bsl(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "bsl.csv")
    logger.info(f"Importing Bsl from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bsl_no_str = row.get("BSL_NO", "").strip()
            if not bsl_no_str:
                logger.warning("Skipping row in bsl.csv with empty BSL_NO")
                continue  # Skip rows with empty primary key
            try:
                bsl_no = int(bsl_no_str)
            except ValueError:
                logger.warning(f"Skipping row with invalid BSL_NO value: {bsl_no_str}")
                continue
            records.append(
                {
                    "bsl_no": int(row["BSL_NO"]),
                    "medium_category": row.get("MEDIUM_CATEGORY"),
                    "region_category": row.get("REGION_CATEGORY"),
                    "community_interest": row.get("COMMUNITY_INTEREST"),
                    "bsl_state": row.get("BSL_STATE"),
                    "date_commenced": datetime.strptime(
                        row["DATE_COMMENCED"], "%Y-%m-%d"
                    ).date()
                    if row.get("DATE_COMMENCED")
                    else None,
                    "on_air_id": row.get("ON_AIR_ID"),
                    "call_sign": row.get("CALL_SIGN"),
                    "ibl_target_area": row.get("IBL_TARGET_AREA"),
                    "area_code": row.get("AREA_CODE"),  # Resolved via ForeignKey in Bsl
                    "reference": row.get("REFERENCE"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                Bsl.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into Bsl.")
    else:
        logger.info("No Bsl records found.")


def import_licence(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "licence.csv")
    logger.info(f"Importing Licence from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "licence_no": row["LICENCE_NO"],
                    "client": int(row["CLIENT_NO"]) if row.get("CLIENT_NO") else None,
                    "sv_id": int(row["SV_ID"]) if row.get("SV_ID") else None,
                    "ss_id": int(row["SS_ID"]) if row.get("SS_ID") else None,
                    "licence_type_name": row.get("LICENCE_TYPE_NAME"),
                    "licence_category_name": row.get("LICENCE_CATEGORY_NAME"),
                    "date_issued": datetime.strptime(
                        row["DATE_ISSUED"], "%Y-%m-%d"
                    ).date()
                    if row.get("DATE_ISSUED")
                    else None,
                    "date_of_effect": datetime.strptime(
                        row["DATE_OF_EFFECT"], "%Y-%m-%d"
                    ).date()
                    if row.get("DATE_OF_EFFECT")
                    else None,
                    "date_of_expiry": datetime.strptime(
                        row["DATE_OF_EXPIRY"], "%Y-%m-%d"
                    ).date()
                    if row.get("DATE_OF_EXPIRY")
                    else None,
                    "status": row.get("STATUS"),
                    "status_text": row.get("STATUS_TEXT"),
                    "ap_id": row.get("AP_ID"),
                    "ap_prj_ident": row.get("AP_PRJ_IDENT"),
                    "ship_name": row.get("SHIP_NAME"),
                    "bsl_no": int(row["BSL_NO"]) if row.get("BSL_NO") else None,
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                Licence.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into Licence.")
    else:
        logger.info("No Licence records found.")


# -------------------------
# Complex Table Imports
# -------------------------


def import_antenna(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "antenna.csv")
    logger.info(f"Importing Antenna from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "antenna_id": int(row["ANTENNA_ID"]),
                    "gain": float(row["GAIN"]) if row.get("GAIN") else None,
                    "front_to_back": float(row["FRONT_TO_BACK"])
                    if row.get("FRONT_TO_BACK")
                    else None,
                    "h_beamwidth": float(row["H_BEAMWIDTH"])
                    if row.get("H_BEAMWIDTH")
                    else None,
                    "v_beamwidth": float(row["V_BEAMWIDTH"])
                    if row.get("V_BEAMWIDTH")
                    else None,
                    "band_min_freq": float(row["BAND_MIN_FREQ"])
                    if row.get("BAND_MIN_FREQ")
                    else None,
                    "band_min_freq_unit": row.get("BAND_MIN_FREQ_UNIT"),
                    "band_max_freq": float(row["BAND_MAX_FREQ"])
                    if row.get("BAND_MAX_FREQ")
                    else None,
                    "band_max_freq_unit": row.get("BAND_MAX_FREQ_UNIT"),
                    "antenna_size": float(row["ANTENNA_SIZE"])
                    if row.get("ANTENNA_SIZE")
                    else None,
                    "antenna_type": row.get("ANTENNA_TYPE"),
                    "model": row.get("MODEL"),
                    "manufacturer": row.get("MANUFACTURER"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                Antenna.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into Antenna.")
    else:
        logger.info("No Antenna records found.")


def import_device_detail(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "device_details.csv")
    logger.info(f"Importing DeviceDetail from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "sdd_id": int(row["SDD_ID"]),
                    "licence_no": row["LICENCE_NO"],
                    "device_registration_identifier": row.get(
                        "DEVICE_REGISTRATION_IDENTIFIER"
                    ),
                    "former_device_identifier": row.get("FORMER_DEVICE_IDENTIFIER"),
                    "authorisation_date": datetime.strptime(
                        row["AUTHORISATION_DATE"], "%Y-%m-%d"
                    ).date()
                    if row.get("AUTHORISATION_DATE")
                    else None,
                    "certification_method": row.get("CERTIFICATION_METHOD"),
                    "group_flag": row.get("GROUP_FLAG"),
                    "site_radius": float(row["SITE_RADIUS"])
                    if row.get("SITE_RADIUS")
                    else None,
                    "frequency": int(float(row["FREQUENCY"]))
                    if row.get("FREQUENCY")
                    else None,
                    "bandwidth": int(float(row["BANDWIDTH"]))
                    if row.get("BANDWIDTH")
                    else None,
                    "carrier_freq": int(float(row["CARRIER_FREQ"]))
                    if row.get("CARRIER_FREQ")
                    else None,
                    "emission": row.get("EMISSION"),
                    "device_type": row.get("DEVICE_TYPE"),
                    "transmitter_power": float(row["TRANSMITTER_POWER"])
                    if row.get("TRANSMITTER_POWER")
                    else None,
                    "transmitter_power_unit": row.get("TRANSMITTER_POWER_UNIT"),
                    "site": int(row["SITE_ID"]) if row.get("SITE_ID") else None,
                    "antenna": int(row["ANTENNA_ID"])
                    if row.get("ANTENNA_ID")
                    else None,
                    "polarisation": row.get("POLARISATION"),
                    "azimuth": float(row["AZIMUTH"]) if row.get("AZIMUTH") else None,
                    "height": float(row["HEIGHT"]) if row.get("HEIGHT") else None,
                    "tilt": float(row["TILT"]) if row.get("TILT") else None,
                    "feeder_loss": float(row["FEEDER_LOSS"])
                    if row.get("FEEDER_LOSS")
                    else None,
                    "level_of_protection": row.get("LEVEL_OF_PROTECTION"),
                    "eirp": float(row["EIRP"]) if row.get("EIRP") else None,
                    "eirp_unit": row.get("EIRP_UNIT"),
                    "licence_service": int(row["SV_ID"]) if row.get("SV_ID") else None,
                    "licence_subservice": int(row["SS_ID"])
                    if row.get("SS_ID")
                    else None,
                    "efl_id": row.get("EFL_ID"),
                    "efl_freq_ident": row.get("EFL_FREQ_IDENT"),
                    "efl_system": row.get("EFL_SYSTEM"),
                    "leqd_mode": row.get("LEQD_MODE"),
                    "receiver_threshold": float(row["RECEIVER_THRESHOLD"])
                    if row.get("RECEIVER_THRESHOLD")
                    else None,
                    "area_area_id": int(row["AREA_AREA_ID"])
                    if row.get("AREA_AREA_ID")
                    else None,
                    "call_sign": row.get("CALL_SIGN"),
                    "area_description": row.get("AREA_DESCRIPTION"),
                    "ap_id": row.get("AP_ID"),
                    "class_of_station_code": row.get("CLASS_OF_STATION_CODE"),
                    "supplimental_flag": row.get("SUPLIMENTAL_FLAG"),
                    "eq_freq_range_min": float(row["EQ_FREQ_RANGE_MIN"])
                    if row.get("EQ_FREQ_RANGE_MIN")
                    else None,
                    "eq_freq_range_max": float(row["EQ_FREQ_RANGE_MAX"])
                    if row.get("EQ_FREQ_RANGE_MAX")
                    else None,
                    "nature_of_service": row.get("NATURE_OF_SERVICE_ID"),
                    "hours_of_operation": row.get("HOURS_OF_OPERATION"),
                    "satellite": int(row["SA_ID"]) if row.get("SA_ID") else None,
                    "related_efl_id": row.get("RELATED_EFL_ID"),
                    "eqp_id": row.get("EQP_ID"),
                    "antenna_multi_mode": row.get("ANTENNA_MULTI_MODE"),
                    "power_ind": row.get("POWER_IND"),
                    "lpon_center_longitude": float(row["LPON_CENTER_LONGITUDE"])
                    if row.get("LPON_CENTER_LONGITUDE")
                    else None,
                    "lpon_center_latitude": float(row["LPON_CENTER_LATITUDE"])
                    if row.get("LPON_CENTER_LATITUDE")
                    else None,
                    "tcs_id": row.get("TCS_ID"),
                    "tech_spec_id": row.get("TECH_SPEC_ID"),
                    "dropthrough_id": row.get("DROPTHROUGH_ID"),
                    "station_type": row.get("STATION_TYPE"),
                    "station_name": row.get("STATION_NAME"),
                }
            )
    if records:
        # Save current PRAGMA settings.
        cur = db.execute_sql("PRAGMA synchronous;")
        old_synchronous = cur.fetchone()[0]
        cur = db.execute_sql("PRAGMA journal_mode;")
        old_journal_mode = cur.fetchone()[0]

        # Set PRAGMA for faster bulk insertion.
        db.execute_sql("PRAGMA synchronous = OFF;")
        db.execute_sql("PRAGMA journal_mode = MEMORY;")
        try:
            with db.atomic():
                for i in range(0, len(records), batch_size):
                    DeviceDetail.insert_many(records[i : i + batch_size]).execute()
            logger.info(f"Imported {len(records)} records into DeviceDetail.")
        finally:
            # Revert PRAGMA settings even if import fails.
            db.execute_sql(f"PRAGMA synchronous = {old_synchronous};")
            db.execute_sql(f"PRAGMA journal_mode = {old_journal_mode};")
    else:
        logger.info("No DeviceDetail records found.")


def import_auth_spectrum_freq(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "auth_spectrum_freq.csv")
    logger.info(f"Importing AuthSpectrumFreq from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "licence": row["LICENCE_NO"],
                    "area_code": row.get("AREA_CODE"),
                    "area_name": row.get("AREA_NAME"),
                    "lw_frequency_start": int(row["LW_FREQUENCY_START"])
                    if row.get("LW_FREQUENCY_START")
                    else None,
                    "lw_frequency_end": int(row["LW_FREQUENCY_END"])
                    if row.get("LW_FREQUENCY_END")
                    else None,
                    "up_frequency_start": int(row["UP_FREQUENCY_START"])
                    if row.get("UP_FREQUENCY_START")
                    else None,
                    "up_frequency_end": int(row["UP_FREQUENCY_END"])
                    if row.get("UP_FREQUENCY_END")
                    else None,
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                AuthSpectrumFreq.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into AuthSpectrumFreq.")
    else:
        logger.info("No AuthSpectrumFreq records found.")


def import_auth_spectrum_area(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "auth_spectrum_area.csv")
    logger.info(f"Importing AuthSpectrumArea from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "licence": row["LICENCE_NO"],
                    "area_code": row.get("AREA_CODE"),
                    "area_name": row.get("AREA_NAME"),
                    "area_description": row.get("AREA_DESCRIPTION"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                AuthSpectrumArea.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into AuthSpectrumArea.")
    else:
        logger.info("No AuthSpectrumArea records found.")


def import_applic_text_block(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "applic_text_block.csv")
    logger.info(f"Importing ApplicTextBlock from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "aptb_id": int(row["APTB_ID"]),
                    "aptb_table_prefix": row.get("APTB_TABLE_PREFIX"),
                    "aptb_table_id": row.get("APTB_TABLE_ID"),
                    "licence": row.get("LICENCE_NO"),
                    "aptb_description": row.get("APTB_DESCRIPTION"),
                    "aptb_category": row.get("APTB_CATEGORY"),
                    "aptb_text": row.get("APTB_TEXT"),
                    "aptb_item": row.get("APTB_ITEM"),
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                ApplicTextBlock.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into ApplicTextBlock.")
    else:
        logger.info("No ApplicTextBlock records found.")


def import_antenna_pattern(data_dir, batch_size=DEFAULT_BATCH_SIZE):
    file_path = os.path.join(data_dir, "antenna_pattern.csv")
    logger.info(f"Importing AntennaPattern from {file_path}...")
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "antenna": int(row["ANTENNA_ID"])
                    if row.get("ANTENNA_ID")
                    else None,
                    "az_type": row.get("AZ_TYPE"),
                    "angle_ref": float(row["ANGLE_REF"])
                    if row.get("ANGLE_REF")
                    else None,
                    "angle": float(row["ANGLE"]) if row.get("ANGLE") else None,
                    "attenuation": float(row["ATTENUATION"])
                    if row.get("ATTENUATION")
                    else None,
                }
            )
    if records:
        with db.atomic():
            for i in range(0, len(records), batch_size):
                AntennaPattern.insert_many(records[i : i + batch_size]).execute()
        logger.info(f"Imported {len(records)} records into AntennaPattern.")
    else:
        logger.info("No AntennaPattern records found.")


# -------------------------
# Master Import Function
# -------------------------


def import_all_data(data_dir):
    # Convert relative path to an absolute path:
    data_dir = os.path.abspath(data_dir)
    logger.info(f"Starting data import from directory: {data_dir}")

    # Lookup Tables
    logger.info("Importing Lookup Tables...")
    import_licensing_area(data_dir)
    import_satellite(data_dir)
    import_reports_text_block(data_dir)
    import_nature_of_service(data_dir)
    import_licence_status(data_dir)
    import_industry_cat(data_dir)
    import_fee_status(data_dir)
    import_client_type(data_dir)
    import_licence_service(data_dir)
    import_antenna_polarity(data_dir)
    import_access_area(data_dir)
    import_bsl_area(data_dir)

    # Dependent Tables
    logger.info("Importing Dependent Tables...")
    import_site(data_dir)
    import_client(data_dir)
    import_licence_subservice(data_dir)
    import_bsl(data_dir)
    import_licence(data_dir)

    # Complex Tables
    logger.info("Importing Complex Tables...")
    import_antenna(data_dir)
    import_device_detail(data_dir)
    import_auth_spectrum_freq(data_dir)
    import_auth_spectrum_area(data_dir)
    import_applic_text_block(data_dir)
    import_antenna_pattern(data_dir)

    logger.info("Data import completed successfully.")
