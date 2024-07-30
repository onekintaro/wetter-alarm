from datetime import timedelta, datetime, timezone
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
import logging

from .client import WetterAlarmApiClient
from .const import DOMAIN
from .helpers.const.config import Config as Cfg
from .helpers.const.options import OptionConsts as Opt, Options
from .helpers.const.devices import Device, DeviceConst

_LOGGER = logging.getLogger(__name__)

class WetterAlarmCoordinator(DataUpdateCoordinator):
    """Custom Wetter-Alarm Coordinator"""

    def __init__(self, hass: HomeAssistant, config_entry) -> None:
        self._poi_id = config_entry.data[Cfg.POI.ID]
        self._name = Opt.getName(config_entry.options)
        self._logger = _LOGGER
        self.last_update = None
        self._config_entry = config_entry
        
        Device.setConf(config_entry.options)
        self._devices = Device.getEntries()

        update_interval = Opt.getUpdateInterval(config_entry.options)
        #_LOGGER.error(f"Update interval set to: {update_interval}")

        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=self._name,
            update_interval=update_interval,
        )

    def get_device_info(self, device_name: str) -> DeviceInfo:
        """Return the device info based on device name."""
        device_info = self._devices.get(device_name, {})
        if device_info and device_name != DeviceConst.HUB:
            return DeviceInfo(
                identifiers={(DOMAIN, f"{self._poi_id}-{device_name}")},
                translation_key=device_name,
                translation_placeholders={"poi_name_short": self._name},
                manufacturer="Wetter-Alarm",
                model="API v8",
                entry_type="service",
                via_device=(DOMAIN, f"{self._poi_id}-hub") if device_info['active'] else None
            )
        return self.get_hub_device_info()

    def get_hub_device_info(self) -> DeviceInfo:
        """Return the device info for the city."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._poi_id}-hub")},
            translation_key=DeviceConst.HUB,
            translation_placeholders={"poi_name_short": self._name},
            manufacturer="Wetter-Alarm",
            model="API v8",
            entry_type="service"
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from API endpoint."""
        client = WetterAlarmApiClient(self._config_entry)

        alert_data = await client.get_meteo_alerts_async(self.hass)
        weather_data = await client.get_weather_data_async(self.hass)
        info_data = await client.get_poiinfo_data_async(self.hass)
        self.last_update = datetime.now(timezone.utc)

        api_data = {
            'devices': self._devices,
            'meteo_alerts': alert_data,
            'weather_data': weather_data,
            'info_data': info_data,
            'last_update': self.last_update
        }

        # _LOGGER.error("Device data: %s", self._devices)
        # _LOGGER.error("Alert data: %s", alert_data)
        # _LOGGER.error("Weather data: %s", weather_data)
        # _LOGGER.error("Info data: %s", info_data)
        # _LOGGER.error("Last update: %s", self.last_update)

        # _LOGGER.error("Data: %s", api_data)


        return api_data

    def get_alert_count(self, alert_list) -> int:
        """Return the number of alerts in the list."""
        length = len(alert_list)
        if length == 1 and alert_list[0].get('type') == 'no_alerts':
            return 0
        return length
