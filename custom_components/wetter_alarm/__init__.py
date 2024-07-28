"""The Wetter-Alarm integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, WETTERALARM_COORDINATOR, WETTERALARM_DATA
from .consts.options import Options as Opt
from .client import WetterAlarmApiClient
from .coordinator import WetterAlarmCoordinator  # Importiere den Coordinator


_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.WEATHER, Platform.CALENDAR]

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Wetter-Alarm from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    is_configured = config_entry.options.get(Opt.Base.BASE_CONFIG, {}).get(Opt.Base.Options.IS_CONFIGURED, False)

    if not is_configured:
        hass.components.persistent_notification.create(
            "Configuration not completed.",
            title="Wetter-Alarm",
            notification_id="wetter_alarm_config"
        )
        _LOGGER.error(f"Wetter-Alarm: Configuration for POI {config_entry.title} not completed. Please use Configure button to complete configuration.")
        return False
    # else:
    #     _LOGGER.error(f"Wetter-Alarm: Configuration for POI {config_entry.title} OK.")

    #TODO: Redo this part
    client = WetterAlarmApiClient(config_entry)
    valid_connection = await client.validate_poi_id_async(hass=hass)
    if not valid_connection:
        return False
    #end part

    coordinator = WetterAlarmCoordinator(
        hass=hass, config_entry=config_entry
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