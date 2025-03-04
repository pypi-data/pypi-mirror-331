from __future__ import annotations
from typing import Self

from peewee import (
    AutoField,
    BigIntegerField,
    CharField,
    DateField,
    FloatField,
    ForeignKeyField,
    IntegerField,
    Model,
    TextField,
)

from .database import db


class BaseModel(Model):
    class Meta:
        database = db

    @classmethod
    def get_or_none(cls, *args, **kwargs) -> Self | None:
        return super().get_or_none(*args, **kwargs)

    @classmethod
    def get_by_id(cls, pk: int) -> Self:
        return super().get_by_id(pk)

    @classmethod
    def get(cls, *query, **filters) -> Self:
        return super().get(*query, **filters)

    @classmethod
    def get_or_create(cls, **kwargs) -> tuple[Self, bool]:
        return super().get_or_create(**kwargs)


class LicencingArea(BaseModel):
    licensing_area_id = IntegerField(primary_key=True)  # LICENSING_AREA_ID
    description = CharField(null=True)


class Site(BaseModel):
    site_id = IntegerField(primary_key=True)  # SITE_ID
    latitude = FloatField(null=True)
    longitude = FloatField(null=True)
    name = CharField(null=True)
    state = CharField(null=True)
    licensing_area = ForeignKeyField(
        LicencingArea, field="licensing_area_id", null=True, backref="sites"
    )
    postcode = CharField(null=True)
    site_precision = CharField(null=True)
    elevation = FloatField(null=True)
    hcis_l2 = CharField(null=True)


class Satellite(BaseModel):
    sa_id = IntegerField(primary_key=True)  # SA_ID
    sa_sat_name = CharField(null=True)
    sa_sat_long_nom = CharField(null=True)  # Could be numeric but stored as text here
    sa_sat_incexc = CharField(null=True)
    sa_sat_geo_pos = CharField(null=True)
    sa_sat_merit_g_t = CharField(null=True)


class ReportsTextBlock(BaseModel):
    rtb_item = CharField(primary_key=True)  # RTB_ITEM
    rtb_category = CharField(null=True)
    rtb_description = CharField(null=True)
    rtb_start_date = DateField(null=True)
    rtb_end_date = DateField(null=True)
    rtb_text = TextField(null=True)


class NatureOfService(BaseModel):
    code = CharField(primary_key=True)  # CODE
    description = CharField(null=True)


class LicenceStatus(BaseModel):
    status = CharField(primary_key=True)  # STATUS
    status_text = CharField(null=True)


class IndustryCat(BaseModel):
    cat_id = IntegerField(primary_key=True)  # CAT_ID
    description = CharField(null=True)
    name = CharField(null=True)


class FeeStatus(BaseModel):
    fee_status_id = IntegerField(primary_key=True)  # FEE_STATUS_ID
    fee_status_text = CharField(null=True)


class ClientType(BaseModel):
    type_id = IntegerField(primary_key=True)  # TYPE_ID
    name = CharField(null=True)


class Client(BaseModel):
    client_no = IntegerField(primary_key=True)  # CLIENT_NO
    licencee = CharField(null=True)
    trading_name = CharField(null=True)
    acn = CharField(null=True)
    abn = CharField(null=True)
    postal_street = CharField(null=True)
    postal_suburb = CharField(null=True)
    postal_state = CharField(null=True)
    postal_postcode = CharField(null=True)
    cat_id = ForeignKeyField(IndustryCat, field="cat_id", null=True, backref="clients")
    client_type = ForeignKeyField(
        ClientType, field="type_id", null=True, backref="clients"
    )
    fee_status_id = ForeignKeyField(
        FeeStatus, field="fee_status_id", null=True, backref="clients"
    )


class LicenceService(BaseModel):
    sv_id = IntegerField(primary_key=True)  # SV_ID
    sv_name = CharField(null=True)


class LicenceSubservice(BaseModel):
    ss_id = IntegerField(primary_key=True)  # SS_ID
    sv_sv_id = ForeignKeyField(
        LicenceService, field="sv_id", null=True, backref="subservices"
    )
    ss_name = CharField(null=True)


class BslArea(BaseModel):
    area_code = CharField(primary_key=True)  # AREA_CODE
    area_name = CharField(null=True)


class Bsl(BaseModel):
    bsl_no = IntegerField(primary_key=True)  # BSL_NO
    medium_category = CharField(null=True)
    region_category = CharField(null=True)
    community_interest = CharField(null=True)
    bsl_state = CharField(null=True)
    date_commenced = DateField(null=True)
    on_air_id = CharField(null=True)
    call_sign = CharField(null=True)
    ibl_target_area = CharField(null=True)
    area_code = ForeignKeyField(
        BslArea,
        field="area_code",
        column_name="area_code",
        null=True,
        backref="bsl_records",
    )
    reference = CharField(null=True)


class Licence(BaseModel):
    licence_no = CharField(primary_key=True)  # LICENCE_NO
    client = ForeignKeyField(
        Client,
        field="client_no",
        column_name="client_no",
        null=True,
        backref="licences",
    )
    sv_id = ForeignKeyField(
        LicenceService, field="sv_id", null=True, backref="licences"
    )
    ss_id = ForeignKeyField(
        LicenceSubservice, field="ss_id", null=True, backref="licences"
    )
    licence_type_name = CharField(null=True)
    licence_category_name = CharField(null=True)
    date_issued = DateField(null=True)
    date_of_effect = DateField(null=True)
    date_of_expiry = DateField(null=True)
    status = ForeignKeyField(
        LicenceStatus,
        field="status",
        column_name="status",
        null=True,
        backref="licences",
    )
    status_text = ForeignKeyField(
        LicenceStatus,
        field="status_text",
        column_name="status_text",
        null=True,
        backref="licences",
    )
    ap_id = CharField(null=True)
    ap_prj_ident = CharField(null=True)
    ship_name = CharField(null=True)
    bsl = ForeignKeyField(
        Bsl, field="bsl_no", column_name="bsl_no", null=True, backref="licences"
    )


class AntennaPolarity(BaseModel):
    polarisation_code = CharField(primary_key=True)  # POLARISATION_CODE
    polarisation_text = CharField(null=True)


class AccessArea(BaseModel):
    area_id = IntegerField(primary_key=True)  # AREA_ID
    area_code = CharField(null=True)
    area_name = CharField(null=True)
    area_category = CharField(null=True)


class Antenna(BaseModel):
    antenna_id = IntegerField(primary_key=True)  # ANTENNA_ID
    gain = FloatField(null=True)
    front_to_back = FloatField(null=True)
    h_beamwidth = FloatField(null=True)
    v_beamwidth = FloatField(null=True)
    band_min_freq = FloatField(null=True)
    band_min_freq_unit = CharField(null=True)
    band_max_freq = FloatField(null=True)
    band_max_freq_unit = CharField(null=True)
    antenna_size = FloatField(null=True)
    antenna_type = CharField(null=True)
    model = CharField(null=True)
    manufacturer = CharField(null=True)


# 15. class_of_station.csv → ClassOfStation
class ClassOfStation(BaseModel):
    code = CharField(primary_key=True)  # CODE
    description = CharField(null=True)


class DeviceDetail(BaseModel):
    sdd_id = BigIntegerField(primary_key=True)  # SDD_ID
    licence = ForeignKeyField(
        Licence,
        field="licence_no",
        column_name="licence_no",
        null=True,
        backref="device_details",
    )
    device_registration_identifier = CharField(null=True)
    former_device_identifier = CharField(null=True)
    authorisation_date = DateField(null=True)
    certification_method = CharField(null=True)
    group_flag = CharField(null=True)
    site_radius = FloatField(null=True)
    frequency = BigIntegerField(null=True)
    bandwidth = BigIntegerField(null=True)
    carrier_freq = BigIntegerField(null=True)
    emission = CharField(null=True)
    device_type = CharField(null=True)
    transmitter_power = FloatField(null=True)
    transmitter_power_unit = CharField(null=True)
    site = ForeignKeyField(Site, field="site_id", null=True, backref="device_details")
    antenna = ForeignKeyField(
        Antenna, field="antenna_id", null=True, backref="device_details"
    )
    polarisation = ForeignKeyField(
        AntennaPolarity,
        field="polarisation_code",
        column_name="polarisation",
        null=True,
        backref="device_details",
    )
    azimuth = FloatField(null=True)
    height = FloatField(null=True)
    tilt = FloatField(null=True)
    feeder_loss = FloatField(null=True)
    level_of_protection = CharField(null=True)
    eirp = FloatField(null=True)
    eirp_unit = CharField(null=True)
    licence_service = ForeignKeyField(
        LicenceService,
        field="sv_id",
        column_name="sv_id",
        null=True,
        backref="device_details",
    )
    licence_subservice = ForeignKeyField(
        LicenceSubservice,
        field="ss_id",
        column_name="ss_id",
        null=True,
        backref="device_details",
    )
    efl_id = CharField(null=True)
    efl_freq_ident = CharField(null=True)
    efl_system = CharField(null=True)
    leqd_mode = CharField(null=True)
    receiver_threshold = FloatField(null=True)
    area_area_id = ForeignKeyField(
        AccessArea, field="area_id", null=True, backref="device_details"
    )
    call_sign = CharField(null=True)
    area_description = CharField(null=True)
    ap_id = CharField(null=True)
    class_of_station_code = ForeignKeyField(
        ClassOfStation,
        field="code",
        column_name="class_of_station_code",
        null=True,
        backref="device_details",
    )
    supplimental_flag = CharField(null=True)
    eq_freq_range_min = FloatField(null=True)
    eq_freq_range_max = FloatField(null=True)
    nature_of_service = ForeignKeyField(
        NatureOfService, field="code", null=True, backref="device_details"
    )
    hours_of_operation = CharField(null=True)
    satellite = ForeignKeyField(
        Satellite,
        field="sa_id",
        column_name="sa_id",
        null=True,
        backref="device_details",
    )
    related_efl_id = CharField(null=True)
    eqp_id = CharField(null=True)
    antenna_multi_mode = CharField(null=True)
    power_ind = CharField(null=True)
    lpon_center_longitude = FloatField(null=True)
    lpon_center_latitude = FloatField(null=True)
    tcs_id = CharField(null=True)
    tech_spec_id = CharField(null=True)
    dropthrough_id = CharField(null=True)
    station_type = CharField(null=True)
    station_name = CharField(null=True)


class AuthSpectrumFreq(BaseModel):
    # Using a surrogate primary key; composite keys can be set up via Meta.unique_together if needed.
    id = AutoField()
    licence = ForeignKeyField(
        Licence,
        field="licence_no",
        column_name="licence_no",
        null=True,
        backref="auth_spectrum_freqs",
    )
    area_code = CharField(null=True)
    area_name = CharField(null=True)
    lw_frequency_start = BigIntegerField(null=True)
    lw_frequency_end = BigIntegerField(null=True)
    up_frequency_start = BigIntegerField(null=True)
    up_frequency_end = BigIntegerField(null=True)


class AuthSpectrumArea(BaseModel):
    id = AutoField()
    licence_no = ForeignKeyField(
        Licence,
        field="licence_no",
        column_name="licence_no",
        null=True,
        backref="auth_spectrum_areas",
    )
    area_code = CharField(null=True)
    area_name = CharField(null=True)
    area_description = CharField(null=True)


class ApplicTextBlock(BaseModel):
    aptb_id = BigIntegerField(primary_key=True)  # APTB_ID
    aptb_table_prefix = CharField(null=True)
    aptb_table_id = CharField(null=True)
    licence_no = ForeignKeyField(
        Licence,
        field="licence_no",
        column_name="licence_no",
        null=True,
        backref="applic_text_blocks",
    )
    aptb_description = CharField(null=True)
    aptb_category = CharField(null=True)
    aptb_text = TextField(null=True)
    aptb_item = CharField(null=True)


class AntennaPattern(BaseModel):
    id = AutoField()
    antenna = ForeignKeyField(Antenna, field="antenna_id", backref="patterns")
    az_type = CharField(null=True)
    angle_ref = FloatField(null=True)
    angle = FloatField(null=True)
    attenuation = FloatField(null=True)
