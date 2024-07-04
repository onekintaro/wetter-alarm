"""Support for Wetter-Alarm weather service."""

import logging
from homeassistant.components.weather import (
    WeatherEntity,
    WeatherEntityFeature,
    Forecast,
)
from homeassistant.const import (
    UnitOfLength,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import (
    ATTRIBUTION,
    DOMAIN,
    WETTERALARM_COORDINATOR,
    WETTERALARM_DATA,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigType, async_add_entities
) -> None:
    """Add a weather entity from a config_entry."""
    hass_data = hass.data[DOMAIN][entry.entry_id]
    coordinator = hass_data[WETTERALARM_COORDINATOR]
    wetteralarm_data = hass_data[WETTERALARM_DATA]
    async_add_entities([WetterAlarmWeather(entry.data, wetteralarm_data, coordinator)], False)


class WetterAlarmWeather(WeatherEntity):
    """Implementation of Wetter-Alarm weather."""

    def __init__(self, entry_data, wetteralarm_data, coordinator):
        """Initialize the platform with a data instance and site."""
        self._wetteralarm_data = wetteralarm_data
        self._coordinator = coordinator
        self._poi_id = entry_data["poi_id"]
        self._poi_name = entry_data["poi_data"]["label_de"].replace(" ", "_").lower()
        self._attr_unique_id = f"{coordinator.get_poi_id}_weather"
        self._attr_name = f"{coordinator._name} Weather"
        _LOGGER.debug(f"Setting up weather with id {self._attr_unique_id}")
        super().__init__()

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast in native units."""
        return self._wetteralarm_data.get("day_forecasts")

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the hourly forecast in native units."""
        return self._wetteralarm_data.get("hour_forecasts")

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def condition(self):
        """Return the current condition."""
        return self._wetteralarm_data.get("current_condition", "unknown")

    @property
    def supported_features(self):
        """Return the supported features."""
        return WeatherEntityFeature.FORECAST_HOURLY | WeatherEntityFeature.FORECAST_DAILY

    @property
    def native_temperature(self):
        """Return the temperature."""
        return self._wetteralarm_data.get("current_temperature")

    @property
    def native_temperature_unit(self):
        """Return the temperature unit."""
        return UnitOfTemperature.CELSIUS

    @property
    def native_wind_speed(self):
        """Return the wind speed."""
        return self._wetteralarm_data.get("current_wind_speed")

    @property
    def native_wind_speed_unit(self):
        """Return the wind speed unit."""
        return UnitOfSpeed.KILOMETERS_PER_HOUR

    @property
    def wind_bearing(self):
        """Return the wind direction."""
        return self._wetteralarm_data.get("current_wind_direction")

    @property
    def native_precipitation_unit(self):
        """Return the precipitation unit."""
        return UnitOfLength.MILLIMETERS

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        return {
            "last_update": self._coordinator.last_update,
            "poi_name": self._wetteralarm_data.get("poi_name"),
            "poi_geo_subdivision_label": self._wetteralarm_data.get("poi_geo_subdivision_label"),
        }

    async def async_added_to_hass(self) -> None:
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )
