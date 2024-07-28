import voluptuous as vol
from homeassistant.helpers.selector import SelectSelector

from ...consts.options import Options as Opt
from ...consts.devices import Device, DeviceConst

Entity = Opt.Entity

def get_entity_vars(config_entry, is_conf=False):
    selected = {}
    all_devices = Device.all()

    if is_conf:
        selected = DeviceConst.getListConfig()
    else:
        poi_options = config_entry.options
        options_entity = poi_options.get(Entity.ENTITY_CONFIG, {})
        
        Device.setConf(options_entity)
        selected = Device.active()    

    return {
        "selected": selected,
        "all": all_devices
    }

def get_input_entity_vars(user_input):
    selected_options = user_input.get(DeviceConst.WEATHER, [])

    return {
        Entity.Weather.SENSORS: Entity.Weather.SENSORS in selected_options,
        Entity.Weather.ENTITY: Entity.Weather.ENTITY in selected_options
    }

def get_entity_schema(entity_options):
    device_list = DeviceConst.getList()
    return vol.Schema(
        {
            vol.Optional(
                DeviceConst.WEATHER,
                default=entity_options['selected'].get(DeviceConst.WEATHER, [])
            ): SelectSelector({
                "options": list(entity_options['all'].get(DeviceConst.WEATHER, [])),
                "multiple": True,
                "custom_value": False,
                "mode": "dropdown",
                "translation_key": DeviceConst.WEATHER
            }),
            vol.Optional(
                DeviceConst.METEO_ALERT,
                default=entity_options['selected'].get(DeviceConst.METEO_ALERT, [])
            ): SelectSelector({
                "options": list(entity_options['all'].get(DeviceConst.METEO_ALERT, [])),
                "multiple": True,
                "custom_value": False,
                "mode": "dropdown",
                "translation_key": DeviceConst.METEO_ALERT
            }),            
        }
    )


def create_options(base_config, user_input):

    base_config[Opt.Base.Options.IS_CONFIGURED] = True

    weather = user_input.get(DeviceConst.WEATHER, [])
    meteo_alert = user_input.get(DeviceConst.METEO_ALERT, [])

    return {
        Opt.Base.BASE_CONFIG: base_config,
        Entity.ENTITY_CONFIG: {
            Entity.Alert.NAME: {
                Entity.Alert.Meteo.NAME: {
                    Entity.Alert.Meteo.SENSORS: Entity.Alert.Meteo.SENSORS in meteo_alert,
                    Entity.Alert.Meteo.CALENDAR: Entity.Alert.Meteo.CALENDAR in meteo_alert,
                },
                Entity.Alert.Hail.NAME: {
                    Entity.Alert.Hail.SENSORS: Entity.Alert.Hail.SENSORS in meteo_alert,
                },
                Entity.Alert.Flood.NAME: {
                    Entity.Alert.Flood.SENSORS: False,
                },
                Entity.Alert.Wind.NAME: {
                    Entity.Alert.Wind.SENSORS: False,
                },
                Entity.Alert.SnowIce.NAME: {
                    Entity.Alert.SnowIce.SENSORS: False,
                },
                Entity.Alert.Avalanche.NAME: {
                    Entity.Alert.Avalanche.SENSORS: False,
                },
                Entity.Alert.Earthquake.NAME: {
                    Entity.Alert.Earthquake.SENSORS: False,
                },
                Entity.Alert.ForestFire.NAME: {
                    Entity.Alert.ForestFire.SENSORS: False,
                },
                Entity.Alert.Landslide.NAME: {
                    Entity.Alert.Landslide.SENSORS: False,
                },
                Entity.Alert.Personal.NAME: {
                    Entity.Alert.Personal.SENSORS: False,
                },
            },
            Entity.Weather.NAME: {
                Entity.Weather.ENTITY: Entity.Weather.ENTITY in weather,
                Entity.Weather.SENSORS: Entity.Weather.SENSORS in weather,
            },
            Entity.Camera.NAME: {
                Entity.Camera.SENSORS: False,
                Entity.Camera.ENTITY: False,
                Entity.Camera.MAX: 0,                                          
            },
            Entity.Maps.NAME: {
                Entity.Maps.NAME: False,
                Entity.Maps.LIGHTNING: False,
                Entity.Maps.RAIN: False,
                Entity.Maps.SNOW: False,
                Entity.Maps.TEMPERATURE: False,
                Entity.Maps.WIND: False,
                Entity.Maps.WEATHER: False,
                Entity.Maps.FORECAST: False,
                Entity.Maps.SATELLITE: False,
                Entity.Maps.RADAR: False,
                Entity.Maps.SUNSHINE: False,
            },
        },
    }
