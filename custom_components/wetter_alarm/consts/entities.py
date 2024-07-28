from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.typing import StateType

@dataclass(kw_only=True)
class WAEntityDescription(SensorEntityDescription):
    """Describes Wetter Alarm sensor entity."""
    exists_fn: Callable[[dict], bool] = lambda _: True
    value_fn: Callable[[dict], StateType]
    icon: str = None

class Data:
    COORDINATOR = "wetteralarm_coordinator"
    DATA = "wetteralarm_data"

class Entity:
    class Info:
        Sensors: tuple[WAEntityDescription, ...] = (
            WAEntityDescription(
                key="info_id",
                value_fn=lambda data: data['info_data']['id'],
                icon="mdi:information-outline"
            ),
            WAEntityDescription(
                key="info_kind",
                value_fn=lambda data: data['info_data']['kind'],
                icon="mdi:information-outline"
            ),
            WAEntityDescription(
                key="info_latitude",
                value_fn=lambda data: data['info_data']['latitude'],
                icon="mdi:information-outline"
            ),
            WAEntityDescription(
                key="info_longitude",
                value_fn=lambda data: data['info_data']['longitude'],
                icon="mdi:information-outline"
            ),
            WAEntityDescription(
                key="info_timezone",
                value_fn=lambda data: data['info_data']['timezone'],
                icon="mdi:information-outline"
            ),
            WAEntityDescription(
                key="info_zip",
                value_fn=lambda data: data['info_data']['zip'],
                icon="mdi:information-outline"
            ),
            WAEntityDescription(
                key="info_canton",
                value_fn=lambda data: data['info_data']['canton'],
                icon="mdi:information-outline"
            ),
            WAEntityDescription(
                key="info_name",
                value_fn=lambda data: data['info_data']['name'],
                icon="mdi:information-outline"
            ),
            WAEntityDescription(
                key="info_parent_name",
                value_fn=lambda data: data['info_data']['parent_name'],
                icon="mdi:information-outline"
            ),
            WAEntityDescription(
                key="info_full_name",
                value_fn=lambda data: data['info_data']['full_name'],
                icon="mdi:information-outline"
            ),
            WAEntityDescription(
                key="info_country",
                value_fn=lambda data: data['info_data']['country'],
                icon="mdi:information-outline"
            ),
            WAEntityDescription(
                key="info_is_international",
                value_fn=lambda data: data['info_data']['is_international'],
                icon="mdi:information-outline"
            ),
            WAEntityDescription(
                key="last_update",
                value_fn=lambda data: data['last_update'],
                icon="mdi:clock-time-four-outline"
            )
        )
    class Alert:
        Sensors: tuple[WAEntityDescription, ...] = (
            WAEntityDescription(
                key="alarm_count",
                value_fn=lambda data: data['meteo_alerts']['alert_count'],
                icon="mdi:alarm-light-outline"
            ),
            WAEntityDescription(
                key="alarm_selected",
                value_fn=lambda data: data['meteo_alerts']['selected'],
                icon="mdi:alarm-light-outline"
            ),
            WAEntityDescription(
                key="alarm_has_alerts",
                value_fn=lambda data: data['meteo_alerts']['has_alerts'],
                icon="mdi:alarm-light-outline"
            ),
            WAEntityDescription(
                key="alarm_id",
                value_fn=lambda data: data['meteo_alerts']['alert_list'][0]['id'],
                icon="mdi:alarm-light-outline"
            ),
            WAEntityDescription(
                key="alarm_valid_from",
                device_class=SensorDeviceClass.TIMESTAMP,
                value_fn=lambda data: data['meteo_alerts']['alert_list'][0]['valid_from'],
                icon="mdi:alarm-light-outline"
            ),
            WAEntityDescription(
                key="alarm_valid_to",
                device_class=SensorDeviceClass.TIMESTAMP,
                value_fn=lambda data: data['meteo_alerts']['alert_list'][0]['valid_to'],
                icon="mdi:alarm-light-outline"
            ),
            WAEntityDescription(
                key="alarm_priority",
                value_fn=lambda data: data['meteo_alerts']['alert_list'][0]['priority'],
                icon="mdi:alarm-light-outline"
            ),
            WAEntityDescription(
                key="alarm_region",
                value_fn=lambda data: data['meteo_alerts']['alert_list'][0]['region'],
                icon="mdi:alarm-light-outline"
            ),
            WAEntityDescription(
                key="alarm_title",
                value_fn=lambda data: data['meteo_alerts']['alert_list'][0]['title'],
                icon="mdi:alarm-light-outline"
            ),
            WAEntityDescription(
                key="alarm_info",
                value_fn=lambda data: data['meteo_alerts']['alert_list'][0]['info'],
                icon="mdi:alarm-light-outline"
            ),
            WAEntityDescription(
                key="alarm_signature",
                value_fn=lambda data: data['meteo_alerts']['alert_list'][0]['signature'],
                icon="mdi:alarm-light-outline"
            ),
            WAEntityDescription(
                key="alarm_paragraph",
                value_fn=lambda data: data['meteo_alerts']['alert_list'][0]['paragraph'],
                icon="mdi:alarm-light-outline"
            ),
            WAEntityDescription(
                key="alarm_cantons",
                value_fn=lambda data: data['meteo_alerts']['alert_list'][0]['cantons'],
                icon="mdi:alarm-light-outline"
            )
        )
        Calendar: tuple[WAEntityDescription, ...] = (
            WAEntityDescription(
                key="alarm_calendar",
                value_fn=lambda data: data['meteo_alerts']['alert_list'][0].get('calendar'),
                icon="mdi:alarm-light-outline"
            )
        )
    class Weather:
        Sensors: tuple[WAEntityDescription, ...] = (
            WAEntityDescription(
                key="weather_condition",
                value_fn=lambda data: data['weather_data']['current_condition'],
                icon="mdi:weather-sunny"
            ),
            WAEntityDescription(
                key="weather_temperature",
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement="°C",
                state_class=SensorStateClass.MEASUREMENT,
                value_fn=lambda data: data['weather_data']['current_ext_data']['temperature'],
                icon="mdi:thermometer"
            ),
            WAEntityDescription(
                key="weather_temperature_min",
                native_unit_of_measurement="°C",
                state_class=SensorStateClass.MEASUREMENT,
                value_fn=lambda data: data['weather_data']['current_ext_data']['temperature_min'],
                icon="mdi:thermometer"
            ),
            WAEntityDescription(
                key="weather_temperature_max",
                native_unit_of_measurement="°C",
                state_class=SensorStateClass.MEASUREMENT,
                value_fn=lambda data: data['weather_data']['current_ext_data']['temperature_max'],
                icon="mdi:thermometer"
            ),
            WAEntityDescription(
                key="weather_wind_speed",
                native_unit_of_measurement="km/h",
                state_class=SensorStateClass.MEASUREMENT,
                value_fn=lambda data: data['weather_data']['current_ext_data']['wind_speed_mean'],
                icon="mdi:weather-windy"
            ),
            WAEntityDescription(
                key="weather_wind_speed_max",
                native_unit_of_measurement="km/h",
                state_class=SensorStateClass.MEASUREMENT,
                value_fn=lambda data: data['weather_data']['current_ext_data']['wind_speed_max'],
                icon="mdi:weather-windy"
            ),
            WAEntityDescription(
                key="weather_wind_direction",
                native_unit_of_measurement="°",
                state_class=SensorStateClass.MEASUREMENT,
                value_fn=lambda data: data['weather_data']['current_ext_data']['wind_direction'],
                icon="mdi:compass"
            ),
            WAEntityDescription(
                key="weather_wind_chill_temperature",
                native_unit_of_measurement="°C",
                state_class=SensorStateClass.MEASUREMENT,
                value_fn=lambda data: data['weather_data']['current_ext_data']['wind_chill_temperature'],
                icon="mdi:thermometer"
            ),
            WAEntityDescription(
                key="weather_wind_direction_name",
                value_fn=lambda data: data['weather_data']['current_ext_data']['wind_direction_name'],
                icon="mdi:compass"
            ),
            WAEntityDescription(
                key="weather_insolation",
                native_unit_of_measurement="W/m²",
                state_class=SensorStateClass.MEASUREMENT,
                value_fn=lambda data: data['weather_data']['current_ext_data']['insolation'],
                icon="mdi:weather-sunny"
            ),
            WAEntityDescription(
                key="weather_insolation_max",
                native_unit_of_measurement="W/m²",
                state_class=SensorStateClass.MEASUREMENT,
                value_fn=lambda data: data['weather_data']['current_ext_data']['insolation_max'],
                icon="mdi:weather-sunny"
            ),
            WAEntityDescription(
                key="weather_precipitation_amount",
                native_unit_of_measurement="mm",
                state_class=SensorStateClass.MEASUREMENT,
                value_fn=lambda data: data['weather_data']['current_ext_data']['precipitation_amount'],
                icon="mdi:weather-rainy"
            ),
            WAEntityDescription(
                key="weather_precipitation_probability",
                native_unit_of_measurement="%",
                state_class=SensorStateClass.MEASUREMENT,
                value_fn=lambda data: data['weather_data']['current_ext_data']['precipitation_probability'],
                icon="mdi:weather-rainy"
            ),
            WAEntityDescription(
                key="weather_symbol",
                value_fn=lambda data: data['weather_data']['current_ext_data']['symbol'],
                icon="mdi:weather-sunny"
            ),
            WAEntityDescription(
                key="weather_mood",
                value_fn=lambda data: data['weather_data']['current_ext_data']['mood'],
                icon="mdi:weather-sunny"
            ),
            WAEntityDescription(
                key="weather_lunar_phase",
                value_fn=lambda data: data['weather_data']['current_ext_data']['lunar_phase'],
                icon="mdi:weather-night"
            ),
            WAEntityDescription(
                key="weather_lunar_phase_time",
                value_fn=lambda data: data['weather_data']['current_ext_data']['lunar_phase_time'],
                icon="mdi:weather-night"
            ),
            WAEntityDescription(
                key="weather_lunar_phase_percentage",
                value_fn=lambda data: data['weather_data']['current_ext_data']['lunar_phase_percentage'],
                icon="mdi:weather-night"
            ),
            WAEntityDescription(
                key="weather_sunrise",
                value_fn=lambda data: data['weather_data']['current_ext_data']['sunrise'],
                icon="mdi:weather-sunset-up"
            ),
            WAEntityDescription(
                key="weather_sunset",
                value_fn=lambda data: data['weather_data']['current_ext_data']['sunset'],
                icon="mdi:weather-sunset-down"
            )
        )
        Weather: tuple[WAEntityDescription, ...] = (
            WAEntityDescription(
                key="weather",
                value_fn=lambda data: data['weather_data'],
                icon="mdi:weather-sunny"
            )
        )
    class Camera:
        Sensors: tuple[WAEntityDescription, ...] = (
            WAEntityDescription(
                key="cam_live_url",
                value_fn=lambda data: data['camera_data']['cam_live_url'],
                icon="mdi:camera"
            ),
            WAEntityDescription(
                key="cam_name",
                value_fn=lambda data: data['camera_data']['cam_name'],
                icon="mdi:camera"
            ),
            WAEntityDescription(
                key="cam_nearby",
                value_fn=lambda data: data['camera_data']['cam_nearby'],
                icon="mdi:camera"
            ),
            WAEntityDescription(
                key="cam_nearby_count",
                value_fn=lambda data: data['camera_data']['cam_nearby_count'],
                icon="mdi:camera"
            )
        )
        Camera: tuple[WAEntityDescription, ...] = (
            WAEntityDescription(
                key="cam_live",
                value_fn=lambda data: data['camera_data'],
                icon="mdi:camera"
            )
        )
    class Maps:
        Sensors: tuple[WAEntityDescription, ...] = (
            WAEntityDescription(
                key="map_lightning",
                value_fn=lambda data: None,
                icon="mdi:weather-lightning"
            ),
            WAEntityDescription(
                key="map_rain",
                value_fn=lambda data: None,
                icon="mdi:weather-rainy"
            ),
            WAEntityDescription(
                key="map_snow",
                value_fn=lambda data: None,
                icon="mdi:weather-snowy"
            ),
            WAEntityDescription(
                key="map_temperature",
                value_fn=lambda data: None,
                icon="mdi:thermometer"
            ),
            WAEntityDescription(
                key="map_wind",
                value_fn=lambda data: None,
                icon="mdi:weather-windy"
            ),
            WAEntityDescription(
                key="map_weather",
                value_fn=lambda data: None,
                icon="mdi:weather-sunny"
            ),
            WAEntityDescription(
                key="map_forecast",
                value_fn=lambda data: None,
                icon="mdi:weather-sunny"
            ),
            WAEntityDescription(
                key="map_satellite",
                value_fn=lambda data: None,
                icon="mdi:weather-sunny"
            ),
            WAEntityDescription(
                key="map_radar",
                value_fn=lambda data: None,
                icon="mdi:weather-sunny"
            ),
            WAEntityDescription(
                key="map_sunshine",
                value_fn=lambda data: None,
                icon="mdi:weather-sunny"
            )
        )
