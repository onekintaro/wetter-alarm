from datetime import timedelta
import logging

_LOGGER = logging.getLogger(__name__)

# Neue Gruppierung in verschachtelten Klassen
class Options:
    class Base:
        BASE_CONFIG = "base_config"
        class POI:
            NAME = "poi_name"
            NAME_SHORT = "poi_name_short"

        class Update:
            INTERVAL = "update_interval"
            DEFAULT = 30
            MIN = 30
            TYPE = "update_interval_type"
            TYPE_LIST = ["minutes", "hours"]
            FORCE = "force_update"

        class Language:
            LANGUAGE = "poi_language"
            DEFAULT = "de"
            LIST = ["de", "fr", "it", "en"]

        class Options:
            IS_CONFIGURED = "is_configured"
            REMOVE_UNUSED = "remove_unused"

    class Entity:
        ENTITY_CONFIG = "entity_config"
        class Hub:
            NAME = "hub"
            SENSORS = "hub_sensors"
        class Weather:
            NAME = "weather"
            SENSORS = "weather_sensors"
            ENTITY = "weather_entity"

        class Alert:
            NAME = "alerts"
            class Meteo:
                NAME = "meteo_alerts"
                SENSORS = "meteo_alert_sensors"
                CALENDAR = "meteo_alert_calendar"
            class Hail:
                NAME = "hail_alerts"
                SENSORS = "hail_alert_sensors"
            class Flood:
                NAME = "flood_alerts"
                SENSORS = "flood_alert_sensors"
            class Wind:
                NAME = "wind_alerts"
                SENSORS = "wind_alert_sensors"
            class SnowIce:
                NAME = "snow_alerts"
                SENSORS = "snow_alert_sensors"
            class Avalanche:
                NAME = "avalanche_alerts"
                SENSORS = "avalanche_alert_sensors"
            class Earthquake:
                NAME = "earthquake_alerts"
                SENSORS = "earthquake_alert_sensors"
            class ForestFire:
                NAME = "forest_fire_alerts"
                SENSORS = "forest_fire_alert_sensors"
            class Landslide:
                NAME = "landslide_alerts"
                SENSORS = "landslide_alert_sensors"
            class Personal:
                NAME = "personal_alerts"
                SENSORS = "personal_alert_sensors"

        class Camera:
            NAME = "camera"
            SENSORS = "camera_sensors"
            ENTITY = "camera_entitys"
            MAX = "max_cameras"

        class Maps:
            NAME = "maps"
            LIGHTNING = "lightning_map"
            RAIN = "rain_map"
            SNOW = "snow_map"
            TEMPERATURE = "temperature_map"
            WIND = "wind_map"
            WEATHER = "weather_map"
            FORECAST = "weather_forecast_map"
            SATELLITE = "weather_satellite_map"
            RADAR = "weather_radar_map"
            SUNSHINE = "weather_sunshine_map"


class OptionConsts:
    def getName(options=None):
        if not options:
            return Options.Base.POI.NAME
        else:
            name = options[Options.Base.BASE_CONFIG][Options.Base.POI.NAME]
            return name
        
    def getLang(options=None):
        if not options:
            return Options.Base.Language.DEFAULT
        else:
            lang = options[Options.Base.BASE_CONFIG][Options.Base.Language.LANGUAGE]
            if not lang:
                return Options.Base.Language.DEFAULT
            return lang
        
    def getUpdateInterval(options=None):
        if not options:
            return timedelta(minutes=Options.Base.Update.DEFAULT)
        else:
            int_type = options[Options.Base.BASE_CONFIG][Options.Base.Update.TYPE]
            int_val = options[Options.Base.BASE_CONFIG][Options.Base.Update.INTERVAL]

            # Check update interval type and value is smaller than 30 min to prevent abuse
            # Return default 30 minutes
            if int_type == Options.Base.Update.TYPE_LIST[0] and int_val < Options.Base.Update.MIN:
                _LOGGER.warning(f"Update interval is smaller than {Options.Base.Update.MIN} minutes. To prevent abuse, the interval is set to {Options.Base.Update.DEFAULT} minutes.")
                return timedelta(minutes=Options.Base.Update.DEFAULT)
                #DEBUG
                #return timedelta(minutes=int_val)

            if not int_type:
                return timedelta(minutes=Options.Base.Update.DEFAULT)
            if not int_val:
                return timedelta(minutes=Options.Base.Update.DEFAULT)
            if int_type == Options.Base.Update.TYPE_LIST[0]:
                return timedelta(minutes=int_val)
            if int_type == Options.Base.Update.TYPE_LIST[1]:
                return timedelta(hours=int_val)
            return timedelta(minutes=Options.Base.Update.DEFAULT)