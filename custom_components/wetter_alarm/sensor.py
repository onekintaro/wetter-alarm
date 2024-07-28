from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

from .const import (
    DOMAIN, WETTERALARM_COORDINATOR
)
from .coordinator import WetterAlarmCoordinator
from .helpers.sensor.remove import remove_unused_sensors

from .consts.entities import WAEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    # _LOGGER.error(f"async_setup_entry called with config_entry {config_entry}")

    hass_data = hass.data[DOMAIN][config_entry.entry_id]
    options = config_entry.options
    # _LOGGER.error(f"WA Options {options}")

    coordinator = hass_data[WETTERALARM_COORDINATOR]

    sensors = []

    for device_name, device_info in coordinator.data['devices'].items():
        if device_info['active']:
            sensors += [
                WetterAlarmSensorEntity(coordinator, device_name, description)
                for description in device_info['entries'].get('sensor', [])
            ]

    # _LOGGER.error(f"async_setup_entry called with sensors {sensors}")

    await coordinator.async_config_entry_first_refresh()
    async_add_entities(sensors)

    #TODO: Remove unused sensors Repair!
    # if not options.get("alert_sensors"):
    #     await remove_unused_sensors(hass, config_entry, ALERT_SENSORS_LIST)
    # if not options.get("weather_sensors"):
    #     await remove_unused_sensors(hass, config_entry, WEATHER_SENSORS_LIST)

class WetterAlarmSensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of a Wetter-Alarm Sensor."""

    entity_description: WAEntityDescription
    _attr_has_entity_name = True

    def __init__(self, coordinator: WetterAlarmCoordinator, device_name: str, description: WAEntityDescription) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._coordinator = coordinator
        self.device_name = device_name
        self._attr_unique_id = f"{coordinator._poi_id}_{description.key}"
        self._attr_translation_key = description.key
        self._attr_translation_placeholders = {"poi_name": coordinator._name}

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        value = self.entity_description.value_fn(self._coordinator.data)
        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP and value is not None:
            try:
                value = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as e:
                _LOGGER.error(f"Error parsing datetime for {self.entity_description.key}: {e}")
                return None
        return value
    
    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self.entity_description.icon

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._coordinator.get_device_info(self.device_name)

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