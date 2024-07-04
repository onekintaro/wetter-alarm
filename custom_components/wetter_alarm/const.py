"""Constant values for wetter-alarm integration."""

DOMAIN = "wetter_alarm"
ATTRIBUTION = "attribution"
WA_PREFIXES = {
    "label_de": "Wetter-Alarm: ",
    "label_fr": "Alarme-Météo: ",
    "label_it": "Allarme-Meteo: ",
    "label_en": "Weather-Alarm: "
}


# Common Sensors
LAST_UPDATE = "last_update"

# Info Sensors
INFO_ID = "info_id"
INFO_KIND = "kind"
INFO_LATITUDE = "latitude"
INFO_LONGITUDE = "longitude"
INFO_ZIP = "zip"
INFO_LABEL = "name"
INFO_PARENT_LABEL = "parent_name"
INFO_FULL_LABEL = "full_name"
INFO_EXTERNAL_URL = "external_url"
INFO_COUNTRY = "country"
INFO_CANTON = "canton"
INFO_CANTON_SHORT = "canton"
INFO_IS_INTERNATIONAL = "is_international"

# Alarm Sensors
ALARM_ID = "alarm_id"
ALARM_VALID_FROM = "valid_from"
ALARM_VALID_TO = "valid_to"
ALARM_PRIORITY = "priority"
ALARM_REGION = "region"
ALARM_TITLE = "title"
ALARM_HINT = "description"
ALARM_SIGNATURE = "signature"
ALARM_NOALERT = "no_alert"
ALARM_CALENDAR_EVENT = "calendar"

# Weather entity Sensors
WEATHER_ENTITY = "weather"
WETTERALARM_COORDINATOR = "wetteralarm_coordinator"
WETTERALARM_DATA = "wetteralarm_data"

# Weather Sensors
WEATHER_CONDITION = "condition"
WEATHER_TEMPERATURE = "temperature"
WEATHER_TEMPERATURE_MIN = "temperature_min"
WEATHER_TEMPERATURE_MAX = "temperature_max"
WEATHER_WIND_SPEED = "wind_speed"
WEATHER_WIND_CHILL = "wind_chill_temperature"
WEATHER_WIND_SPEED_MEAN = "wind_speed_mean"
WEATHER_WIND_SPEED_MAX = "wind_speed_max"
WEATHER_WIND_DIRECTION = "wind_direction"
WEATHER_WIND_DIRECTION_NAME = "wind_direction_name"
WEATHER_INSOLATION = "insolation"
WEATHER_INSOLATION_MAX = "insolation_max"
WEATHER_PRECIPITATION_AMOUNT = "precipitation_amount"
WEATHER_PRECIPITATION_PROBABILITY = "precipitation_probability"
WEATHER_SYMBOL = "weather_icon"
WEATHER_MOOD = "mood"
WEATHER_LUNAR_PHASE = "lunar_phase"
WEATHER_LUNAR_PHASE_TIME = "lunar_phase_time"
WEATHER_LUNAR_PHASE_PERCENTAGE = "lunar_phase_percentage"
WEATHER_SUNRISE = "sunrise"
WEATHER_SUNSET = "sunset"

# Live Cameras
CAM_LIVECAM = "live_camera"
CAM_LIVECAM_URL = "live_camera_url"
CAM_LIVECAM_NAME = "live_camera_name"
CAM_NEARBY_CAMS = "nearby"
CAM_NEARBY_CAMS_COUNT = "nearby_count"

# Options (Configuration, Options-Flow)
OPT_POI_NAME = "poi_name"
OPT_UPDATE_INTERVAL = "update_interval"
OPT_UPDATE_INTERVAL_DEFAULT = 30
OPT_UPDATE_INTERVAL_TYPE = "minutes"
OPT_UPDATE_INTERVAL_TYPE_LIST = ["minutes", "hours"]
OPT_UPDATE_INTERVAL_MIN = 30
OPT_LANGUAGE = "poi_language"
OPT_DEFAULT_LANGUAGE = "label_de"
OPT_LANGUAGE_LIST = [
    "label_de",
    "label_fr",
    "label_it",
    "label_en"
]


# Configuration (Config-Flow)
CONF_ERROR_NO_POI_FOUND = "error_no_poi_found"
CONF_ERROR_NO_CANTON = "error_no_canton"
CONF_ERROR_NO_POI_ID = "error_no_poi_id"
CONF_ERROR_INVALID_POI_ID = "error_invalid_poi_id"

CONF_POI_ID = "poi_id"
CONF_POI_MAP = "poi_map"
CONF_POI_DATA = "poi_data"
CONF_POI_LIST = "poi_list"
CONF_SET_POI_BY = "set_poi_by"
CONF_BY_ID = "set_by_id"
CONF_BY_SEARCH = "set_by_search"
CONF_BY_MAP = "set_by_map"
CONF_POI_SEARCH = "poi_search"

CONF_POI_KIND = "poi_kind"
CONF_POI_KINDS_DEFAULTS = ['town', 'town_section']
CONF_POI_KINDS = [
    'airport',
    'alpine_hut',
    'building_of_interest',
    'campground',
    'golf',
    'pass',
    'peak', 
    'ski_area',
    'stadium',
    'town',
    'town_section',
    'unknown',
    'valley',
    'viewpoint',
    'zoo'
    ]


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