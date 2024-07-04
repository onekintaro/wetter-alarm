from datetime import timedelta, datetime, timezone
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
import logging

from .wetter_alarm_client import WetterAlarmApiClient

#SCAN_INTERVAL = timedelta(minutes=30)

class WetterAlarmCoordinator(DataUpdateCoordinator):
    """Custom Wetter-Alarm Coordinator"""

    def __init__(self, hass: HomeAssistant, logger: logging.Logger, config_entry, poi_id: int, poi_name: str) -> None:
        self._hass = hass
        self._poi_id = poi_id
        self._name = poi_name
        self._logger = logger
        self.last_update = None
        self._config_entry = config_entry

        update_interval = timedelta(minutes=config_entry.options.get('api_update_interval', 30))

        super().__init__(
            hass=hass,
            logger=logger,
            name=self._name,
            update_interval=update_interval,
        )

    @property
    def get_hass(self):
        return self._hass

    @property
    def get_poi_id(self):
        return self._poi_id

    async def _async_update_data(self) -> dict:
        """Fetch data from API endpoint."""
        client = WetterAlarmApiClient(self._poi_id, self._config_entry)
        alert_data = await client.search_for_alerts_async(hass=self._hass)
        weather_data = await client.get_weather_data_async(hass=self._hass)
        self.last_update = datetime.now(timezone.utc)
        self._logger.debug(f"Data fetched at {self.last_update}: {alert_data}, {weather_data}")
        return {**alert_data, **weather_data, 'last_update': self.last_update}
