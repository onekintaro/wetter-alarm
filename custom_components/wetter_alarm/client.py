from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

import requests
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError


from .helpers.weather.mood import mood_convert

from .helpers.const.config import Config as Cfg
from .helpers.const.options import OptionConsts as Opt, Options
from .helpers.const.devices import Device

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://my.wetteralarm.ch/v8/"

METEO_ALERT_URL = "alarms/meteo.json"
METEO_HAIL_ALERT_URL = "alarms/meteo-and-hail.json"
FLOOD_ALERT_URL = "alarms/flood.json"


class WetterAlarmApiClient:
    def __init__(self, config_entry):
        self.poi_id = config_entry.data[Cfg.POI.ID]
        self.poi_url = f"{BASE_URL}pois/{self.poi_id}.json"
        self.lang = Opt.getLang(config_entry.options)

    def validate_poi_id_sync(self) -> bool:
        try:
            res = requests.get(self.poi_url)
            return res.status_code == 200
        except requests.exceptions.RequestException as e:
            _LOGGER.error("Error validating the poi id", e)
            return False

    async def validate_poi_id_async(self, hass: HomeAssistant) -> bool:
        return await hass.async_add_executor_job(self.validate_poi_id_sync)

    def get_poi_data_sync(self):
        try:
            res = requests.get(self.poi_url)
            _LOGGER.error("Got info for POI: %s", res.text)
            return res.json()
        except requests.exceptions.ConnectionError as ce:
            _LOGGER.error("Generic connection error", ce)
            raise CannotConnect
        except json.decoder.JSONDecodeError:
            _LOGGER.error(f"Poi {self.poi_id} did not return a valid JSON")
        except (ValueError, KeyError) as e:
            _LOGGER.error("Did not satisfy expectations:", self.poi_id, e)

    async def get_poi_data_async(self, hass: HomeAssistant):
        return await hass.async_add_executor_job(self.get_poi_data_sync)

    def get_meteo_alerts_sync(self):
        try:
            sensor_data_default = {
                "id": 0,
                "valid_from": None,
                "valid_to": None,
                "priority": None,
                "region": None,
                "title": None,
                "info": None,
                "signature": None,
                "paragraph": None,
                "cantons": None,
            }
            
            ALERT_URL = None
            alert_count = 0
            has_alerts = False
            sensor_data = []

            meteoAlertSensors = Options.Entity.Alert.Meteo.SENSORS
            meteoHailSensors = Options.Entity.Alert.Hail.SENSORS

            if Device.isActive(meteoAlertSensors) and not Device.isActive(meteoHailSensors):
                ALERT_URL = f"{BASE_URL}{METEO_ALERT_URL}"
            elif Device.isActive(meteoHailSensors):
                ALERT_URL = f"{BASE_URL}{METEO_HAIL_ALERT_URL}"

            if not ALERT_URL:
                sensor_data.append(sensor_data_default)
                return {
                    "selected": 0,
                    "has_alerts": has_alerts,
                    "alert_count": alert_count,
                    "alert_list": sensor_data,
                }
            
            if ALERT_URL:
                res = requests.get(ALERT_URL)
                parsed = res.json()["meteo_alarms"]

                for alarm in parsed:
                    if self.poi_id in alarm["poi_ids"]:
                        sensor_data.append({
                            "id": alarm["id"],
                            "valid_from": alarm["valid_from"],
                            "valid_to": alarm["valid_to"],
                            "priority": alarm["priority"],
                            "region": alarm["region"][self.lang]["name"],
                            "title": alarm[self.lang]["title"],
                            "info": alarm[self.lang]["hint"],
                            "signature": alarm[self.lang]["signature"],
                            "paragraph": alarm[self.lang]["paragraph"],
                            "cantons": alarm["cantons"],
                        })

                if not sensor_data:
                    sensor_data.append(sensor_data_default)
                else:
                    has_alerts = True
                    alert_count = len(sensor_data)
                    
                return {
                    "selected": 0,
                    "has_alerts": has_alerts,
                    "alert_count": alert_count,
                    "alert_list": sensor_data,
                }

        except requests.exceptions.ConnectionError as ce:
            _LOGGER.error("Generic connection error", ce)
            raise CannotConnect
        except json.decoder.JSONDecodeError:
            _LOGGER.error(f"Poi {self.poi_id} did not return a valid JSON")
        except (ValueError, KeyError) as e:
            _LOGGER.error("Did not satisfy expectations:", self.poi_id, e)

    async def get_meteo_alerts_async(self, hass: HomeAssistant):
        return await hass.async_add_executor_job(self.get_meteo_alerts_sync)
    
    def get_poiinfo_data_sync(self):
        try:
            res = requests.get(self.poi_url)
            data = res.json()
            full_name = data[self.lang]['label']
            if data[self.lang]['parent_label']:
                full_name = f"{data[self.lang]['parent_label']}, {full_name}"
            return {
                "id": data["id"],
                "kind": data["kind"],
                "latitude": data["lat"],
                "longitude": data["long"],
                "timezone": data["time_zone"],
                "zip": data["zip_value"],
                "canton": data["canton"],
                "name": data[self.lang]['label'],
                "parent_name": data[self.lang]['parent_label'],
                "full_name": full_name,
                "external_url": data[self.lang]["external_url"],
                "geo_subdivision": data[self.lang]['geo_subdivision_label'],
                "geo_subdivisions": data[self.lang]['geo_subdivisions'],
                "country": data[self.lang]['country_label'],
                "is_international": data["is_international"],
            }
        except requests.exceptions.ConnectionError as ce:
            _LOGGER.error("Generic connection error", ce)
            raise CannotConnect
        except json.decoder.JSONDecodeError:
            _LOGGER.error(f"Poi {self.poi_id} did not return a valid JSON")
        except (ValueError, KeyError) as e:
            _LOGGER.error("Did not satisfy expectations:", self.poi_id, e)

    async def get_poiinfo_data_async(self, hass: HomeAssistant):
        return await hass.async_add_executor_job(self.get_poiinfo_data_sync)

    def get_weather_data_sync(self):
        try:
            res = requests.get(self.poi_url)
            data = res.json()

            name = data[self.lang]['label']
            if data[self.lang]['parent_label']:
                name = f"{data[self.lang]['parent_label']}, {name}"

            geo_subdivision_label = data[self.lang]['geo_subdivision_label']

            # Get current weather data from day_forecasts and hour_forecasts
            current_data = self._combine_forecast_data(data.get("day_forecasts", []), data.get("hour_forecasts", []))

            current_condition = mood_convert(current_data.get("mood"))
            #_LOGGER.error("Current Data: %s", current_data)

            day_forecasts = self._format_forecast_daily(data.get("day_forecasts"))
            hour_forecasts = self._format_forecast_hourly(data.get("hour_forecasts"))

            return {
                "poi_name": name,
                "poi_geo_subdivision_label": geo_subdivision_label,
                "current_condition": current_condition,
                "current_temperature": current_data.get("temperature"),
                "current_wind_speed": current_data.get("wind_speed_mean"),
                "current_wind_direction": current_data.get("wind_direction"),
                "day_forecasts": day_forecasts,
                "hour_forecasts": hour_forecasts,
                "current_ext_data": current_data,
            }

        except requests.exceptions.ConnectionError as ce:
            _LOGGER.error("Generic connection error", ce)
            raise CannotConnect
        except json.decoder.JSONDecodeError:
            _LOGGER.error(f"Poi {self.poi_id} did not return a valid JSON")
        except (ValueError, KeyError) as e:
            _LOGGER.error("Did not satisfy expectations:", self.poi_id, e)

    async def get_weather_data_async(self, hass: HomeAssistant):
        return await hass.async_add_executor_job(self.get_weather_data_sync)

    def _combine_forecast_data(self, day_forecasts, hour_forecasts):
        """Combine daily and hourly forecasts to get current weather data."""
        current_data = {}
        now = datetime.now(timezone.utc)

        # Find the latest day forecast
        latest_day_forecast = None
        for forecast in day_forecasts:
            forecast_date = datetime.strptime(forecast["date"], "%Y-%m-%d")
            if forecast_date.date() == now.date():
                latest_day_forecast = forecast
                break

        # Find the latest hour forecast
        latest_hour_forecast = None
        for forecast in hour_forecasts:
            forecast_time = datetime.strptime(forecast["valid_time"], "%Y-%m-%dT%H:%M:%S.%fZ")
            if forecast_time.date() == now.date() and forecast_time.hour == now.hour:
                latest_hour_forecast = forecast
                break

        # Combine the data
        if latest_day_forecast:
            current_data.update(latest_day_forecast)
        if latest_hour_forecast:
            current_data.update(latest_hour_forecast)

        return current_data

    def _format_forecast_daily(self, forecast_data):
        data = []
        for forecast in forecast_data:
            data.append(
                {
                    "datetime": f"{forecast['date']}T12:00:00.000Z",
                    "condition": mood_convert(forecast.get("mood")),
                    "native_temperature": forecast.get("temperature_max"),
                    "native_templow": forecast.get("temperature_min"),
                    "native_wind_speed": forecast.get("wind_speed_max"),
                    "wind_bearing": forecast.get("wind_direction"),
                    "native_precipitation": forecast.get("precipitation_amount"),
                    "precipitation_probability": forecast.get("precipitation_probability"),
                }
            )
        return data

    def _format_forecast_hourly(self, forecast_data):
        data = []
        for forecast in forecast_data:
            data.append(
                {
                    "datetime": forecast["valid_time"],
                    "condition": mood_convert(forecast.get("mood")),
                    "native_temperature": forecast.get("temperature"),
                    "native_wind_speed": forecast.get("wind_speed_mean"),
                    "wind_bearing": forecast.get("wind_direction"),
                    "native_precipitation": forecast.get("precipitation_amount"),
                    "precipitation_probability": forecast.get("precipitation_probability"),
                }
            )
        return data


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
