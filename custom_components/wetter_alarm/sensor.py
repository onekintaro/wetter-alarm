from __future__ import annotations

import logging
from datetime import timedelta, datetime, timezone
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ATTRIBUTION,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import (
    DOMAIN, ALARM_ID, ALARM_VALID_FROM, ALARM_VALID_TO, ALARM_PRIORITY, ALARM_REGION,
    ALARM_TITLE, ALARM_HINT, ALARM_SIGNATURE, ALARM_NOALERT, LAST_UPDATE, WETTERALARM_DATA
)
from .coordinator import WetterAlarmCoordinator

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    ALARM_ID: ["Alarm ID", None, None, "mdi:identifier", False, None],
    ALARM_VALID_FROM: ["Valid From", SensorDeviceClass.TIMESTAMP, None, "mdi:calendar-arrow-left", False, None],
    ALARM_VALID_TO: ["Valid To", SensorDeviceClass.TIMESTAMP, None, "mdi:calendar-arrow-right", False, None],
    ALARM_PRIORITY: ["Priority", None, None, "mdi:chevron-triple-up", False, None],
    ALARM_REGION: ["Region", None, None, "mdi:map-marker-check-outline", False, None],
    ALARM_TITLE: ["Title", None, None, "mdi:format-title", False, None],
    ALARM_HINT: ["Hint", None, None, "mdi:account-alert", False, None],
    ALARM_SIGNATURE: ["Signature", None, None, "mdi:signature-freehand", False, None],
    LAST_UPDATE: ["Last Update", SensorDeviceClass.TIMESTAMP, None, "mdi:clock-check", False, None],

    #TODO: Weather Sensors DAY (for Today/Actual Weather) from api-data (day_forecasts (array) -> find today's forecast with date = today key: date)
    #! No Double Sensors for today (DAY and HOUR) -> HOUR values overwrite DAY values for today to prevent duplicate sensors
    # temperature_min
    # temperature_max
    # wind_speed_max
    # wind_direction
    # wind_direction_name
    # insolation
    # insolation_max
    # precipitation_amount
    # precipitation_probability
    # weather_icon (id to icon function needed from key symbol:int in api-data) ?
    # mood
    # lunar_phase
    # lunar_phase_time
    # lunar_phase_percentage
    # sunrise
    # sunset

    #TODO: Weather Sensors HOUR (for Today/Actual Weather) from api-data (hour_forecasts (array) -> find today's forecast with date/time = today key: valid_time)
    #! this values overwrite the DAY values for today to prevent duplicate sensors    
    # temperature
    # wind_speed_mean
    # wind_speed_max
    # wind_direction
    # wind_direction_name
    # wind_chill_temperature
    # weather_icon (id to icon function needed from key symbol:int in api-data) ?
    # precipitation_amount
    # precipitation_probability
    # mood
    # lunar_phase
    
    #TODO: Camera Sensors from api-data. Possible a option in config to enable/disable
    #! first get livecams_nearby from api-data (array) -> get the first 3 cams

}


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    _LOGGER.error(f"async_setup_entry called with config_entry {config_entry}")
    poi_data = config_entry.data["poi_data"]
    poi_id = poi_data["poiID"]
    poi_name = poi_data["name"]

    coordinator = WetterAlarmCoordinator(
        hass=hass, logger=_LOGGER, config_entry=config_entry, poi_name=poi_name, poi_id=poi_id
    )
    sensors = [
        WetterAlarmSensor(coordinator, sensor_type)
        for sensor_type in SENSOR_TYPES
    ]
    await coordinator.async_config_entry_first_refresh()
    async_add_entities(sensors)


class WetterAlarmSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Wetter-Alarm Sensor."""

    def __init__(self, coordinator: WetterAlarmCoordinator, sensor_type: str):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._sensor_type = sensor_type
        self._name = SENSOR_TYPES[sensor_type][0]
        self._device_class = SENSOR_TYPES[sensor_type][1]
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][2]
        self._icon = SENSOR_TYPES[sensor_type][3]
        self._entity_registry_enabled_default = SENSOR_TYPES[sensor_type][4]
        self._state_class = SENSOR_TYPES[sensor_type][5]
        self._attr_unique_id = f"{coordinator.get_poi_id}_{sensor_type}"
        self._attr_name = f"{coordinator._name} {self._name}"
        _LOGGER.debug(f"created Sensor of class {self.__class__.__name__} with uid {self._attr_unique_id}")

    @property
    def name(self) -> str | None:
        return self._attr_name

    @property
    def unique_id(self) -> str | None:
        return self._attr_unique_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._coordinator.get_poi_id))},
            name=f"Point of Interest - {self._coordinator._name}",
            manufacturer="Wetter-Alarm",
            model="API",
        )

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return self._state_class

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self._sensor_type == LAST_UPDATE:
            return self._coordinator.last_update if self._coordinator.last_update else None
        value = self._coordinator.data.get(self._sensor_type)
        _LOGGER.debug(f"Sensor {self._sensor_type} value: {value}")
        if self._sensor_type in [ALARM_VALID_FROM, ALARM_VALID_TO] and value is None:
            return None
        return value if value is not None else ALARM_NOALERT

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        return {
            ATTR_ATTRIBUTION: "Data provided by Wetter-Alarm",
        }

    @property
    def available(self):
        """Return if state is available."""
        return self._coordinator.data is not None

    async def async_added_to_hass(self) -> None:
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self) -> None:
        """Get the latest data and updates the states."""
        await self._coordinator.async_request_refresh()
