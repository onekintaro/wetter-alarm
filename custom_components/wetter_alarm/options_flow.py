from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from homeassistant.helpers.selector import (
    SelectSelector,
    NumberSelector,
    TextSelector,
)

import logging

from .const import (
    DOMAIN,
    OPT_POI_NAME,
    OPT_UPDATE_INTERVAL,
    OPT_UPDATE_INTERVAL_DEFAULT,
    OPT_UPDATE_INTERVAL_MIN,
    OPT_UPDATE_INTERVAL_TYPE,
    OPT_UPDATE_INTERVAL_TYPE_LIST,
    OPT_LANGUAGE,
    OPT_LANGUAGE_LIST,
    OPT_DEFAULT_LANGUAGE,
)

_LOGGER = logging.getLogger(__name__)

class WetterAlarmOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry, POIS):
        self.config_entry = config_entry
        self.POIS = POIS

    async def async_step_init(self, user_input=None):
        errors = {}

        poi_name = self.config_entry.title
        poi_options = self.config_entry.options

        lang = poi_options.get("lang")
        lang_short = poi_options.get("lang_short")
        update_interval = poi_options.get(OPT_UPDATE_INTERVAL)
        update_interval_type = poi_options.get(OPT_UPDATE_INTERVAL_TYPE)

        if user_input is not None:
            poi_name_new = user_input.get(OPT_POI_NAME)
            lang = user_input.get(OPT_LANGUAGE)
            lang_short = lang.split("_")[0]
            update_interval = user_input.get(OPT_UPDATE_INTERVAL)
            update_interval_type = user_input.get(OPT_UPDATE_INTERVAL_TYPE)

            _LOGGER.error(f"POI Name: {poi_name}")
            _LOGGER.error(f"IN: {poi_name_new}")
                        
            options = {
                "lang": lang,
                "lang_short": lang_short,
                "camera_sensors": False, #TODO: Implement camera sensors
                "camera_entitys": False,
                "max_cameras": 0,
                "weather_sensors": False, #TODO: Implement weather sensors / Switch
                "weather_entity": False, #TODO: Implement weather entity Switch
                "alert_sensors": False, #TODO: Implement alert sensors Swiches
                "flood_sensors": False, #TODO: Implement flood sensors
                "get_location_details": False, #TODO: Implement location details / location sensors
                "get_maps": False, #TODO: Implement map selection / map sensors
                "api_update_interval": update_interval,
                "api_update_interval_type": update_interval_type,
                "force_update_input": False, #TODO: Implement force update
            }

            self.hass.config_entries.async_update_entry(
                self.config_entry, title=poi_name_new, options=options
            )

            return self.async_create_entry(
                title=poi_name_new,
                data=options,
                #unique_id=f"{poi_data.get('kind')}_{poi_data.get('poiID')}"
            )

        options = self.config_entry.options

        data_schema = vol.Schema(
            {
                vol.Required(
                    OPT_POI_NAME,
                    default=poi_name
                ): TextSelector({}),
                vol.Required(
                    OPT_LANGUAGE,
                    default=options.get(OPT_LANGUAGE, OPT_DEFAULT_LANGUAGE)
                ): SelectSelector({
                    "options": list(OPT_LANGUAGE_LIST),
                    "custom_value": False,
                    "mode": "dropdown",
                    "translation_key": OPT_LANGUAGE
                }),
                vol.Required(
                    OPT_UPDATE_INTERVAL,
                    default=options.get(OPT_UPDATE_INTERVAL, OPT_UPDATE_INTERVAL_DEFAULT)
                ): NumberSelector({
                    "min": OPT_UPDATE_INTERVAL_MIN,
                    "step": 10,
                    "mode": "box",
                }),
                vol.Required(
                    OPT_UPDATE_INTERVAL_TYPE,
                    default=options.get(OPT_UPDATE_INTERVAL_TYPE, OPT_UPDATE_INTERVAL_TYPE_LIST[0])
                ): SelectSelector({
                    "options": list(OPT_UPDATE_INTERVAL_TYPE_LIST),
                    "custom_value": False,
                    "mode": "dropdown",
                    "translation_key": OPT_UPDATE_INTERVAL_TYPE
                })
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )

# Update your __init__.py to register the options flow
async def async_setup_entry(hass, config_entry):
    hass.data.setdefault(DOMAIN, {})

    # Register the options flow handler
    config_entry.async_on_unload(
        config_entry.add_update_listener(update_listener)
    )

    return True

async def update_listener(hass, config_entry):
    await hass.config_entries.async_reload(config_entry.entry_id)
