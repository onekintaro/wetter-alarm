from __future__ import annotations

import logging
import json
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.json import JSONEncoder
from homeassistant.helpers.selector import (
    SelectSelector,
    NumberSelector,
    TextSelector,
    LocationSelector,
    )

from . import WetterAlarmApiClient
from .options_flow import WetterAlarmOptionsFlowHandler
from .translate import load_translations
from .const import (
    DOMAIN,

    WA_PREFIXES,

    OPT_POI_NAME,

    OPT_UPDATE_INTERVAL,
    OPT_UPDATE_INTERVAL_DEFAULT,
    OPT_UPDATE_INTERVAL_MIN,
    OPT_UPDATE_INTERVAL_TYPE,
    OPT_UPDATE_INTERVAL_TYPE_LIST,

    OPT_LANGUAGE,
    OPT_LANGUAGE_LIST,
    OPT_DEFAULT_LANGUAGE,

    CONF_ERROR_NO_POI_FOUND,
    CONF_ERROR_NO_CANTON,
    CONF_ERROR_NO_POI_ID,
    CONF_ERROR_INVALID_POI_ID,
  
    CONF_POI_DATA,
    CONF_POI_LIST,
    CONF_SET_POI_BY,
    CONF_BY_ID,
    CONF_BY_SEARCH,
    CONF_BY_MAP,
    CONF_POI_ID,
    CONF_POI_MAP,

    CONF_POI_KIND,
    CONF_POI_KINDS_DEFAULTS,
    CONF_POI_KINDS,

    CONF_POI_SEARCH,
    CONF_CANTON,
    CONF_CANTONS,
    )

# Load POIs from JSON file
with open('custom_components/wetter_alarm/pois.json', 'r') as file:
    POIS = json.load(file)

_LOGGER = logging.getLogger(__name__)

class WetterAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            self.context[OPT_LANGUAGE] = user_input[OPT_LANGUAGE]

            if user_input[CONF_SET_POI_BY] == CONF_BY_ID:
                return await self.async_step_enter_id()
            elif user_input[CONF_SET_POI_BY] == CONF_BY_SEARCH:
                return await self.async_step_search()
            elif user_input[CONF_SET_POI_BY] == CONF_BY_MAP:
                return await self.async_step_map()

        data_options = [
            CONF_BY_ID,
            CONF_BY_SEARCH,
            #TODO: Implement map selection, DISABLING FOR NOW
            #CONF_BY_MAP,
        ]
        data_schema=vol.Schema(
                {
                    vol.Required(
                        OPT_LANGUAGE,
                        default=OPT_DEFAULT_LANGUAGE
                    ): SelectSelector({
                        "options": list(OPT_LANGUAGE_LIST),
                        "custom_value": False,
                        "mode": "dropdown",
                        "translation_key": OPT_LANGUAGE
                    }),
                    vol.Required(
                        CONF_SET_POI_BY,
                        default=CONF_BY_SEARCH
                    ): SelectSelector({
                        "options": list(data_options),
                        "custom_value": False,
                        "mode": "list",
                        "translation_key": CONF_SET_POI_BY
                    })
                }
            )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "title": "title",
                "description": "description"
            }
        )

    async def async_step_enter_id(self, user_input=None):
        errors = {}
        if user_input is not None:
            poi_id = user_input.get(CONF_POI_ID)
            poi = next((poi for poi in POIS if poi['poiID'] == poi_id), None)

            if poi_id == 0:
                errors["base"] = CONF_ERROR_NO_POI_ID
            elif poi:
                self.context[CONF_POI_DATA] = poi
                return await self.async_step_options()
            else:
                errors["base"] = CONF_ERROR_INVALID_POI_ID

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_POI_ID,
                    default="0"
                ): NumberSelector({
                    "min": 0,
                    "max": 999999,
                    "step": 1,
                    "mode": "box",
                })
            }
        )

        return self.async_show_form(
            step_id="enter_id",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "title": "title",
                "description": "description" 
            }
        )

    async def async_step_search(self, user_input=None):
        errors = {}
        if user_input is not None:
            lang = self.context.get(OPT_LANGUAGE)
            poi_kind = user_input.get(CONF_POI_KIND)
            selected_canton = user_input.get(CONF_CANTON)
            poi_search = user_input.get(CONF_POI_SEARCH, "").lower()
            matching_pois = []

            if selected_canton == "none" and poi_search == "":
                errors["base"] = CONF_ERROR_NO_CANTON
            else:
                if selected_canton == "none" and poi_search != "":
                    for poi in POIS:
                        poi_name = poi[lang]
                        poi_parent_name = poi.get(f"parent_{lang}")
                        if poi_parent_name:
                            poi_name = f"{poi_parent_name}, {poi_name}"
                        
                        if poi_search in poi_name.lower():
                            poi['name'] = poi_name
                            if poi_kind and poi['kind'] in poi_kind:
                                matching_pois.append(poi)
                else:
                    for poi in POIS:
                        if selected_canton == "other" and poi['canton'] is None:
                            poi_name = poi[lang]
                            poi_parent_name = poi.get(f"parent_{lang}")
                            if poi_parent_name:
                                poi_name = f"{poi_parent_name}, {poi_name}"
                            
                            if poi_search in poi_name.lower():
                                poi['name'] = poi_name
                                if poi_kind and poi['kind'] in poi_kind:
                                    matching_pois.append(poi)
                                
                        elif poi['canton'] == selected_canton:
                            poi_name = poi[lang]
                            poi_parent_name = poi.get(f"parent_{lang}")
                            if poi_parent_name:
                                poi_name = f"{poi_parent_name}, {poi_name}"
                            
                            if poi_search in poi_name.lower():
                                poi['name'] = poi_name
                                if poi_kind and poi['kind'] in poi_kind:
                                    matching_pois.append(poi)
                    

                self.context[CONF_POI_KIND] = poi_kind
                if len(matching_pois) == 1:
                    self.context[CONF_POI_DATA] = matching_pois[0]
                    return await self.async_step_options()
                elif len(matching_pois) > 1:
                    matching_pois.sort(key=lambda poi: poi['name'])
                    self.context[CONF_POI_LIST] = matching_pois
                    return await self.async_step_select_poi()
                else:
                    errors["base"] = CONF_ERROR_NO_POI_FOUND


        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_CANTON,
                    default="none"
                ): SelectSelector({
                    "options": list(CONF_CANTONS),
                    "custom_value": False,
                    "mode": "dropdown",
                    "translation_key": CONF_CANTON
                }),
                vol.Required(
                    CONF_POI_KIND,
                    default=CONF_POI_KINDS_DEFAULTS
                ): SelectSelector({
                    "options": list(CONF_POI_KINDS),
                    "multiple": True,
                    "custom_value": False,
                    "mode": "dropdown",
                    "translation_key": CONF_POI_KIND
                }),

                vol.Optional(
                    CONF_POI_SEARCH,
                    default=""
                ): TextSelector({})
            }
        )

        return self.async_show_form(
            step_id="search",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "title": "title",
                "description": "description"
            }
        )
    
    async def async_step_select_poi(self, user_input=None):
        errors = {}
        matching_pois = self.context.get(CONF_POI_LIST)
        lang = self.context.get(OPT_LANGUAGE)
        lang_short = lang.split("_")[1]
        translations = load_translations(lang_short)

        if user_input is not None and CONF_POI_ID in user_input:
            selected_poi_id = user_input.get(CONF_POI_ID)
            selected_poi = next(poi for poi in POIS if poi['poiID'] == int(selected_poi_id))
            self.context[CONF_POI_DATA] = selected_poi
            return await self.async_step_options()
        
        
        options = []
        for poi in matching_pois:
            poi_name = poi[lang]
            poi_parent_name = poi.get(f"parent_{lang}")
            if poi_parent_name:
                poi_name = f"{poi_parent_name}, {poi_name}"
             
            poi_kind_translated = translations.get("selector", {}).get(CONF_POI_KIND, {}).get("options", {}).get(poi['kind'], poi['kind'])
            options.append({"label": f"{poi_name} ({poi_kind_translated})", "value": str(poi['poiID'])})

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_POI_ID
                ): SelectSelector({
                    "options": options,
                    "custom_value": False,
                    "mode": "dropdown",
                    "sort": True,
                    "translation_key": CONF_POI_ID
                })
            }
        )

        return self.async_show_form(
            step_id="select_poi",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "title": "title",
                "description": "description"
            }
        )
    
    async def async_step_map(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Hier kannst du die Benutzereingaben verarbeiten und passende POIs finden
            location = user_input.get(CONF_POI_MAP)
            radius = location.get("radius")
            lat = location.get("latitude")
            lon = location.get("longitude")

            # Implementiere die Logik, um POIs basierend auf der Karte zu finden
            matching_pois = [
                poi for poi in POIS
                if self._is_within_radius(poi['lat'], poi['long'], lat, lon, radius)
            ]

            if len(matching_pois) == 1:
                self.context[CONF_POI_DATA] = matching_pois[0]
                return await self.async_step_options()
            elif len(matching_pois) > 1:
                self.context[CONF_POI_LIST] = matching_pois
                return await self.async_step_select_poi()
            else:
                errors["base"] = CONF_ERROR_NO_POI_FOUND

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_POI_MAP
                ): LocationSelector({
                    "radius": True,
                })
            }
        )

        return self.async_show_form(
            step_id="map",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "title": "title",
                "description": "description"
            }
        )


    async def async_step_options(self, user_input=None):
        if user_input is not None:
            poi_data = self.context.get(CONF_POI_DATA)
            lang = self.context.get(OPT_LANGUAGE)
            lang_short = lang.split("_")[1]
            poi_name = user_input.get(OPT_POI_NAME)
            update_interval = user_input.get(OPT_UPDATE_INTERVAL)
            update_interval_type = user_input.get(OPT_UPDATE_INTERVAL_TYPE)


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

            data = {
                "poi_id": poi_data.get("poiID"),
                "poi_data": poi_data
            }

            return self.async_create_entry(
                title=poi_name,
                data=data,
                options=options,
                #unique_id=f"{poi_data.get('kind')}_{poi_data.get('poiID')}"
            )
        
        poi_data = self.context.get(CONF_POI_DATA)
        lang = self.context.get(OPT_LANGUAGE)
        poi_name = poi_data.get(lang)
        poi_parent_name = poi_data.get(f"parent_{lang}")

        if poi_parent_name:
            poi_name = f"{poi_parent_name}, {poi_name}"

        #add Prefix to poi_name
        poi_name_full = f"{WA_PREFIXES[lang]}{poi_name} ({poi_data['canton']})"
        
        
        data_schema = vol.Schema(
            {
                vol.Required(
                    OPT_POI_NAME,
                    default=poi_name_full
                ): TextSelector({}),
                vol.Required(
                    OPT_UPDATE_INTERVAL,
                    default=OPT_UPDATE_INTERVAL_DEFAULT
                ): NumberSelector({
                    "min": OPT_UPDATE_INTERVAL_MIN,
                    "step": 10,
                    "mode": "box",
                }),
                vol.Required(
                    OPT_UPDATE_INTERVAL_TYPE,
                    default=OPT_UPDATE_INTERVAL_TYPE_LIST[0]
                ): SelectSelector({
                    "options": list(OPT_UPDATE_INTERVAL_TYPE_LIST),
                    "custom_value": False,
                    "mode": "dropdown",
                    "translation_key": OPT_UPDATE_INTERVAL_TYPE
                })
            }
        )

        return self.async_show_form(
            step_id="options",
            data_schema=data_schema,
            description_placeholders={
                "poi_name": poi_name,
                "title": "title",
                "description": "description"
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WetterAlarmOptionsFlowHandler(config_entry, POIS)