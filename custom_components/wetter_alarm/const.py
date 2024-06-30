"""Constant values for wetter-alarm integration."""

DOMAIN = "wetter_alarm"

ALARM_ID = "alarm_id"
VALID_FROM = "valid_from"
VALID_TO = "valid_to"
PRIORITY = "priority"
REGION = "region"
TITLE = "title"
HINT = "description"
SIGNATURE = "signature"

CONF_LANGUAGE = "poi_language"
CONF_DEFAULT_LANGUAGE = "label_de"
CONF_LANGUAGE_LIST = [
    "label_de",
    "label_fr",
    "label_it",
    "label_en"
]

CONF_WA_PREFIXES = {
    "label_de": "Wetter-Alarm: ",
    "label_fr": "Alarme-Météo: ",
    "label_it": "Allarme-Meteo: ",
    "label_en": "Weather-Alarm: "
}

CONF_ERROR_NO_POI_FOUND = "error_no_poi_found"
CONF_ERROR_NO_CANTON = "error_no_canton"
CONF_ERROR_NO_POI_ID = "error_no_poi_id"
CONF_ERROR_INVALID_POI_ID = "error_invalid_poi_id"

CONF_POI_ID = "poi_id"
CONF_POI_MAP = "poi_map"
CONF_POI_NAME = "poi_name"
CONF_POI_DATA = "poi_data"
CONF_POI_LIST = "poi_list"
CONF_SET_POI_BY = "set_poi_by"
CONF_BY_ID = "set_by_id"
CONF_BY_SEARCH = "set_by_search"
CONF_BY_MAP = "set_by_map"
CONF_POI_SEARCH = "poi_search"

CONF_CANTON = "canton"
CONF_CANTONS = [
    "none",
    "AG",
    "AI",
    "AR",
    "BE",
    "BL",
    "BS",
    "FR",
    "GE",
    "GL",
    "GR",
    "JU",
    "LU",
    "NE",
    "NW",
    "OW",
    "SG",
    "SH",
    "SO",
    "SZ",
    "TG",
    "TI",
    "UR",
    "VD",
    "VS",
    "ZG",
    "ZH",
    "other"
]