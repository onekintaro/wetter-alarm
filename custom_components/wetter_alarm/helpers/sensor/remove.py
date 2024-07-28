from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.config_entries import ConfigEntry
from homeassistant.util import slugify

import logging

_LOGGER = logging.getLogger(__name__)


async def remove_unused_sensors(hass: HomeAssistant, config_entry: ConfigEntry, sensors_to_disable: dict):
    options = config_entry.options.get("remove_unused")
    if options:
        entity_registry = async_get_entity_registry(hass)
        poi_name = config_entry.data["poi_data"]["name"]

        for sensor_type in sensors_to_disable:
            id_name = slugify(poi_name).lower()
            sensor_name = slugify(sensors_to_disable[sensor_type][0]).lower()
            entity_id = f"sensor.{id_name}_{sensor_name}"
            _LOGGER.error(f"Trying to remove sensor: {entity_id}")
            entity_entry = entity_registry.async_get(entity_id)
            if entity_entry and not entity_entry.disabled:
                _LOGGER.error(f"Removing sensor: {entity_id}")
                entity_registry.async_remove(entity_id)
            else:
                _LOGGER.error(f"Sensor {entity_id} not found or already disabled")