"""Support for Wetter-Alarm weather service."""

import logging
from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEvent,
    STATE_ON,
    STATE_OFF
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import slugify
import homeassistant.util.dt as dt_util

from .const import (
    DOMAIN,
    WETTERALARM_COORDINATOR
)

from .consts.devices import DeviceConst

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigType, async_add_entities
) -> None:
    """Add a calendar entity from a config_entry."""
    hass_data = hass.data[DOMAIN][entry.entry_id]
    coordinator = hass_data[WETTERALARM_COORDINATOR]
    async_add_entities([WetterAlarmCalendar(coordinator)], False)


class WetterAlarmCalendar(CalendarEntity):
    """Implementation of Wetter-Alarm alert calendar."""

    def __init__(self, coordinator):
        """Initialize the platform with a data instance and site."""
        self._coordinator = coordinator
        self._attr_name = f"{coordinator._name} Alert Calendar"
        self._attr_unique_id = slugify(self._attr_name)
        self._events = []
        self._attr_state = STATE_OFF
        #_LOGGER.debug(f"Setting up Calendar with id {self._attr_unique_id}")
        super().__init__()

    @property
    def name(self):
        """Return the name of the entity."""
        return self._attr_name

    @property
    def unique_id(self):
        """Return the unique id of the entity."""
        return self._attr_unique_id
    
    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._coordinator.get_device_info(DeviceConst.METEO_ALERT)

    @property
    def event(self):
        """Return the next upcoming event."""
        if self._events:
            return self._events[0]
        return None

    @property
    def state(self):
        """Return the state of the calendar."""
        now = dt_util.now()
        for event in self._events:
            if event.start <= now <= event.end:
                return STATE_ON
        return STATE_OFF

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "events": [event.as_dict() for event in self._events]
        }

    async def async_added_to_hass(self) -> None:
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self._handle_coordinator_update)
        )
        await self._handle_coordinator_update()

    async def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        #_LOGGER.debug(f"Coordinator data: {self._coordinator.data}")

        events = []
        for alarm in self._coordinator.data['meteo_alerts'].get("alert_list", []):
            if isinstance(alarm, dict):
                #_LOGGER.debug(f"Processing alarm: {alarm}")
                start_date = dt_util.parse_datetime(alarm.get("valid_from"))
                end_date = dt_util.parse_datetime(alarm.get("valid_to"))
                if start_date and end_date:
                    event = CalendarEvent(
                        summary=alarm.get("title", "No Title"),
                        start=start_date,
                        end=end_date,
                        description=alarm.get("info", ""),
                        location=alarm.get("region", "")
                    )
                    events.append(event)
                else:
                    _LOGGER.error(f"Invalid start or end date for alarm: {alarm}")
            else:
                _LOGGER.error(f"Unexpected alarm format: {alarm}")

        self._events = events
        #_LOGGER.debug(f"Updated events: {self._events}")
        self.async_write_ha_state()

    async def async_get_events(self, hass, start_date, end_date):
        """Get all events in a specific time frame."""
        return [
            event for event in self._events
            if event.start >= start_date and event.end <= end_date
        ]
