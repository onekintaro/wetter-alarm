"""The Wetter-Alarm integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, WETTERALARM_COORDINATOR, WETTERALARM_DATA
from .wetter_alarm_client import WetterAlarmApiClient
from .coordinator import WetterAlarmCoordinator  # Importiere den Coordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.WEATHER]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Wetter-Alarm from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    poi_id = config_entry.data["poi_id"]
    client = WetterAlarmApiClient(poi_id, config_entry)

    valid_connection = await client.validate_poi_id_async(hass=hass)

    if not valid_connection:
        return False

    poi_name = config_entry.data["poi_data"]["name"]

    coordinator = WetterAlarmCoordinator(
        hass=hass, logger=_LOGGER, config_entry=config_entry, poi_name=poi_name, poi_id=poi_id
    )
    
    await coordinator.async_config_entry_first_refresh()

    await coordinator.async_refresh()

    hass.data[DOMAIN][config_entry.entry_id] = {
        WETTERALARM_COORDINATOR: coordinator,
        WETTERALARM_DATA: coordinator.data,
    }

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
