from __future__ import annotations

import json
import logging
from datetime import datetime

import requests
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    ALARM_ID,
    ALARM_HINT,
    ALARM_PRIORITY,
    ALARM_REGION,
    ALARM_SIGNATURE,
    ALARM_TITLE,
    ALARM_VALID_FROM,
    ALARM_VALID_TO,
    LAST_UPDATE
)

from .condition import symbol_convert, mood_convert

_LOGGER = logging.getLogger(__name__)
alert_url = "https://my.wetteralarm.ch/v8/alarms/meteo.json"


class WetterAlarmApiClient:
    def __init__(self, poi_id: int, config_entry):
        self.poi_id = poi_id
        self.poi_url = f"https://my.wetteralarm.ch/v8/pois/{poi_id}.json"
        self.config_entry = config_entry
        self.lang = config_entry.data.get("lang_short", "de")

    def validate_poi_id_sync(self) -> bool:
        try:
            res = requests.get(self.poi_url)
            if res:
                return True
            else:
                return False
        except requests.exceptions as er:
            _LOGGER.error("error validating the poi id", er)
            return False

    async def validate_poi_id_async(self, hass: HomeAssistant) -> bool:
        result = await hass.async_add_executor_job(self.validate_poi_id_sync)
        return result

    def get_poi_data_sync(self):
        try:
            res = requests.get(self.poi_url)
            _LOGGER.error("got info for POI ", res.text)
        except requests.exceptions.ConnectionError as ce:
            _LOGGER.error("generic connection error", ce)
            raise CannotConnect
        except json.decoder.JSONDecodeError:
            _LOGGER.error(f"Poi {self.poi_id} did not return a valid JSON")
        except (ValueError, KeyError) as e:
            _LOGGER.error("did not satisfy expectations:", self.poi_id, e)

    async def get_poi_data_async(self, hass: HomeAssistant):
        result = await hass.async_add_executor_job(self.get_poi_data_sync)
        return result

    def search_for_alerts_sync(self):
        try:
            res = requests.get(alert_url)
            parsed = json.loads(res.text)["meteo_alarms"]

            found_alarm = False
            for alarm in parsed:
                if self.poi_id in alarm["poi_ids"]:
                    return {
                        ALARM_ID: alarm["id"],
                        ALARM_VALID_FROM: datetime.strptime(
                            alarm["valid_from"], "%Y-%m-%dT%H:%M:%S.%fZ"
                        ),
                        ALARM_VALID_TO: datetime.strptime(
                            alarm["valid_to"], "%Y-%m-%dT%H:%M:%S.%fZ"
                        ),
                        ALARM_PRIORITY: alarm["priority"],
                        ALARM_REGION: alarm["region"][self.lang]["name"],
                        ALARM_TITLE: alarm[self.lang]["title"],
                        ALARM_HINT: alarm[self.lang]["hint"],
                        ALARM_SIGNATURE: alarm[self.lang]["signature"],
                    }
            if not found_alarm:
                return {
                    ALARM_ID: -1,
                    ALARM_VALID_FROM: None,
                    ALARM_VALID_TO: None,
                    ALARM_PRIORITY: None,
                    ALARM_REGION: None,
                    ALARM_TITLE: None,
                    ALARM_HINT: None,
                    ALARM_SIGNATURE: None,
                }

        except requests.exceptions.ConnectionError as ce:
            _LOGGER.error("generic connection error", ce)
            raise CannotConnect
        except json.decoder.JSONDecodeError:
            _LOGGER.error(f"Poi {self.poi_id} did not return a valid JSON")
        except (ValueError, KeyError) as e:
            _LOGGER.error("did not satisfy expectations:", self.poi_id, e)

    async def search_for_alerts_async(self, hass: HomeAssistant):
        result = await hass.async_add_executor_job(self.search_for_alerts_sync)
        return result

    def get_weather_data_sync(self):
        try:
            res = requests.get(self.poi_url)
            data = json.loads(res.text)

            name = data[self.lang]['label']
            if data[self.lang]['parent_label']:
                name = f"{data[self.lang]['parent_label']}, {name}"

            geo_subdivision_label = data[self.lang]['geo_subdivision_label']

            # Get current weather data from day_forecasts and hour_forecasts
            current_data = self._combine_forecast_data(data.get("day_forecasts", []), data.get("hour_forecasts", []))

            current_condition = mood_convert(current_data.get("mood"))

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
            }

        except requests.exceptions.ConnectionError as ce:
            _LOGGER.error("generic connection error", ce)
            raise CannotConnect
        except json.decoder.JSONDecodeError:
            _LOGGER.error(f"Poi {self.poi_id} did not return a valid JSON")
        except (ValueError, KeyError) as e:
            _LOGGER.error("did not satisfy expectations:", self.poi_id, e)

    async def get_weather_data_async(self, hass: HomeAssistant):
        result = await hass.async_add_executor_job(self.get_weather_data_sync)
        return result

    def _combine_forecast_data(self, day_forecasts, hour_forecasts):
        """Combine daily and hourly forecasts to get current weather data."""
        current_data = {}
        now = datetime.utcnow()

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


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class WetterAlarmApiError(HomeAssistantError):
    """Generic API errors"""

    def __init__(self, poi_id: str, msg: str | None = None) -> None:
        """sta: status code, msg: message"""
        Exception.__init__(self)
        self.poi_id = poi_id
        self.msg = msg

    def __str__(self):
        return f"<Emu API Error sta:{self.poi_id} message:{self.msg}>"
