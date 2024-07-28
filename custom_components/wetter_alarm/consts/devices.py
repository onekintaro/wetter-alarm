import logging

from typing import List, Type, Dict, Any, Callable, Tuple, Union
from collections import defaultdict

from .options import Options
from .entities import Entity

from ..helpers.common.recursiveSearch import recursive_search

from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.typing import StateType

_LOGGER = logging.getLogger(__name__)

class DeviceConst:
    HUB = "device_hub"
    WEATHER = "device_weather"
    METEO_ALERT = "device_meteo_alerts"
    WATER_ALERT = "device_water_alerts"
    WIND_ALERT = "device_wind_alerts"
    SNOW_ALERT = "device_snow_alerts"
    EARTH_ALERT = "device_earth_alerts"
    FOREST_ALERT = "device_forest_alerts"
    PERSONAL_ALERT = "device_personal_alerts"
    CAMERA = "device_camera"
    MAPS = "device_maps"

    def getList() -> List[str]:
        device_list = []
        for device_name in dir(DeviceConst):
            if not device_name.startswith("__") and not device_name.startswith("get"):
                device_list.append(getattr(DeviceConst, device_name))
        return device_list
    
    def getListConfig() -> Dict[str, List[str]]:
        device_list = {}
        for device_name in dir(DeviceConst):
            if not device_name.startswith("__") and not device_name.startswith("get"):
                device_list[getattr(DeviceConst, device_name)] = []
        return device_list


class DeviceConfig:
    def __init__(self, option: str = None, entry: Type = None, override: str = None, type: str = None):
        self.option = option
        self.entry = entry
        self.override = override
        self.type = type
    # def __repr__(self):
    #     entry_name = self.entry.__name__ if hasattr(self.entry, '__name__') else str(self.entry)
    #     return (f"DeviceConfig(option={self.option}, entry={entry_name}, "
    #             f"override={self.override}, type={self.type})")


class Device:
    def __init__(self, name: str, config: List[DeviceConfig] = None):
        self.NAME = name
        self.CONFIG = config if config is not None else []
        self.TEMP_VALUES: Dict[str, Any] = {}
        # _LOGGER.error(f"Config for {self.NAME}: {self.CONFIG}")

    @staticmethod
    def get(device_type: Union[str, Type['Device']]) -> 'Device':
        if isinstance(device_type, str):
            return getattr(Devices, device_type)
        return device_type

    @staticmethod
    def getList() -> 'Devices':
        return devices

    @staticmethod
    def setConf(entity_config: dict):
        if Options.Entity.ENTITY_CONFIG in entity_config:
            entity_config = entity_config[Options.Entity.ENTITY_CONFIG]

        entity_config[Options.Entity.Hub.SENSORS] = True
        #_LOGGER.error(f"Entity config: {entity_config}")
        Device._entity_config = entity_config

    @staticmethod
    def active() -> Dict[str, List[str]]:
        if not hasattr(Device, '_entity_config'):
            return {}

        entity_config = Device._entity_config
        active_devices = {}

        for device_name in dir(devices):
            if not device_name.startswith("__"):
                device = getattr(devices, device_name)
                if isinstance(device, Device):
                    active_config = []
                    for config in device.CONFIG:
                        entry_option = recursive_search(entity_config, config.option)
                        if entry_option is not None and entry_option:
                            active_config.append(config.option)
                    active_devices[device.NAME] = active_config
        return active_devices
    
    @staticmethod
    def isActive(option: str) -> bool:
        if not hasattr(Device, '_entity_config'):
            return False

        entity_config = Device._entity_config
        entry_option = recursive_search(entity_config, option)
        return entry_option is not None and entry_option
        
    
    @staticmethod
    def all() -> Dict[str, List[str]]:
        all_devices = {}
        for device_name in dir(devices):
            if not device_name.startswith("__"):
                device = getattr(devices, device_name)
                if isinstance(device, Device):
                    all_devices[device.NAME] = [config.option for config in device.CONFIG]
        return all_devices

    @staticmethod
    def getEntries() -> Dict[str, Dict[str, Any]]:
        if not hasattr(Device, '_entity_config'):
            _LOGGER.error("No entity config found")
            return {}

        entity_config = Device._entity_config
        devices_entries = {}

        for device_conf in dir(devices):
            if not device_conf.startswith("__"):
                device = getattr(devices, device_conf)
                device_name = device.NAME
                if isinstance(device, Device):
                    #_LOGGER.error(f"Processing device: {device_name}")
                    active_configs = []
                    
                    # Sammeln der aktiven Konfigurationen
                    for config in device.CONFIG:
                        entry_option = recursive_search(entity_config, config.option)
                        if entry_option is not None and entry_option:
                            active_configs.append(config)

                    #_LOGGER.error(f"Active configs: {active_configs}")       

                    # Entfernen von Einträgen mit Overrides
                    active_configs_filtered = []
                    overrides = {config.override for config in active_configs if config.override}
                    for config in active_configs:
                        if config.option not in overrides:
                            active_configs_filtered.append(config)
                    
                    #_LOGGER.error(f"Active configs filtered: {active_configs_filtered}")

                    # Sortieren der aktiven Konfigurationen nach Typ
                    active_configs_sorted = {}
                    for config in active_configs_filtered:
                        if config.type not in active_configs_sorted:
                            active_configs_sorted[config.type] = []
                        if isinstance(config.entry, tuple):
                            active_configs_sorted[config.type].extend(config.entry)
                        else:
                            active_configs_sorted[config.type].append(config.entry)

                    # Erstellen des Ausgabewerts
                    if active_configs_filtered:
                        devices_entries[device_name] = {
                            "name": device_name,
                            "active": True,
                            "entries": {key: tuple(value) for key, value in active_configs_sorted.items()}
                        }
                    else:
                        devices_entries[device_name] = {
                            "name": device_name,
                            "active": False,
                            "entries": {}
                        }
                else:
                    _LOGGER.error(f"Device not found or not a Device instance: {device_name}")

        return devices_entries


    def set_temp_value(self, key: str, value: Any):
        self.TEMP_VALUES[key] = value

    def get_temp_value(self, key: str) -> Any:
        return self.TEMP_VALUES.get(key)


class Devices:
    def __init__(self):
        self.Hub = Device(
            name=DeviceConst.HUB,
            config=[DeviceConfig(option=Options.Entity.Hub.SENSORS, entry=Entity.Info.Sensors, type="sensor")]
        )
        self.Weather = Device(
            name=DeviceConst.WEATHER,
            config=[
                DeviceConfig(option=Options.Entity.Weather.SENSORS, entry=Entity.Weather.Sensors, type="sensor"),
                DeviceConfig(option=Options.Entity.Weather.ENTITY, entry=Entity.Weather.Weather, type="weather")
            ]
        )
        self.Meteo = Device(
            name=DeviceConst.METEO_ALERT,
            config=[
                DeviceConfig(option=Options.Entity.Alert.Meteo.SENSORS, entry=Entity.Alert.Sensors, type="sensor"),
                DeviceConfig(option=Options.Entity.Alert.Meteo.CALENDAR, entry=Entity.Alert.Calendar, type="calendar"),
                DeviceConfig(option=Options.Entity.Alert.Hail.SENSORS, entry=Entity.Alert.Sensors, override=Options.Entity.Alert.Meteo.SENSORS, type="sensor"),
            ]
        )
        self.Water = Device(
            name=DeviceConst.WATER_ALERT,
            config=[DeviceConfig(option=Options.Entity.Alert.Flood.SENSORS, entry=Entity.Alert.Sensors, type="sensor")]
        )
        self.Wind = Device(
            name=DeviceConst.WIND_ALERT,
            config=[DeviceConfig(option=Options.Entity.Alert.Wind.SENSORS, entry=Entity.Alert.Sensors, type="sensor")]
        )
        self.Snow = Device(
            name="alert_snow_device",
            config=[
                DeviceConfig(option=Options.Entity.Alert.SnowIce.SENSORS, entry=Entity.Alert.Sensors, type="sensor"),
                DeviceConfig(option=Options.Entity.Alert.Avalanche.SENSORS, entry=Entity.Alert.Sensors, type="sensor")
            ]
        )
        self.Earth = Device(
            name=DeviceConst.EARTH_ALERT,
            config=[
                DeviceConfig(option=Options.Entity.Alert.Earthquake.SENSORS, entry=Entity.Alert.Sensors, type="sensor"),
                DeviceConfig(option=Options.Entity.Alert.Landslide.SENSORS, entry=Entity.Alert.Sensors, type="sensor")
            ]
        )
        self.Forest = Device(
            name=DeviceConst.FOREST_ALERT,
            config=[DeviceConfig(option=Options.Entity.Alert.ForestFire.SENSORS, entry=Entity.Alert.Sensors, type="sensor")]
        )
        self.Personal = Device(
            name=DeviceConst.PERSONAL_ALERT,
            config=[DeviceConfig(option=Options.Entity.Alert.Personal.SENSORS, entry=Entity.Alert.Sensors, type="sensor")]
        )
        # Deaktiviert bis zur Implementierung
        # self.Camera = Device(
        #     name=DeviceConst.CAMERA,
        #     config=[
        #         DeviceConfig(option=Options.Entity.Camera.SENSORS, entry=Entity.Camera),
        #         DeviceConfig(option=Options.Entity.Camera.ENTITY, entry=Entity.Camera)
        #     ]
        # )
        # self.Maps = Device(
        #     name=DeviceConst.MAPS,
        #     config=[
        #         DeviceConfig(option=Options.Entity.Maps, entry=Entity.Maps)
        #     ]
        # )


devices = Devices()
