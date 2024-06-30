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
from .const import (
    DOMAIN,

    CONF_WA_PREFIXES,

    CONF_LANGUAGE,
    CONF_LANGUAGE_LIST,
    CONF_DEFAULT_LANGUAGE,

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
    CONF_POI_NAME,

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
            self.context[CONF_LANGUAGE] = user_input[CONF_LANGUAGE]

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
                        CONF_LANGUAGE,
                        default=CONF_DEFAULT_LANGUAGE
                    ): SelectSelector({
                        "options": list(CONF_LANGUAGE_LIST),
                        "custom_value": False,
                        "mode": "dropdown",
                        "translation_key": CONF_LANGUAGE
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
                return await self.async_step_name()
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
            lang = self.context.get(CONF_LANGUAGE)
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
                            matching_pois.append(poi)
                else:
                    for poi in POIS:
                        if selected_canton == "other" and poi['canton'] is None:
                            poi_name = poi[lang]
                            poi_parent_name = poi.get(f"parent_{lang}")
                            if poi_parent_name:
                                poi_name = f"{poi_parent_name}, {poi_name}"
                            
                            if poi_search in poi_name.lower():
                                matching_pois.append(poi)
                                
                        elif poi['canton'] == selected_canton:
                            poi_name = poi[lang]
                            poi_parent_name = poi.get(f"parent_{lang}")
                            if poi_parent_name:
                                poi_name = f"{poi_parent_name}, {poi_name}"
                            
                            if poi_search in poi_name.lower():
                                poi['name'] = poi_name
                                matching_pois.append(poi)
                    

                if len(matching_pois) == 1:
                    self.context[CONF_POI_DATA] = matching_pois[0]
                    return await self.async_step_name()
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
        lang = self.context.get(CONF_LANGUAGE)

        if user_input is not None and CONF_POI_ID in user_input:
            selected_poi_id = user_input.get(CONF_POI_ID)
            selected_poi = next(poi for poi in POIS if poi['poiID'] == int(selected_poi_id))
            self.context[CONF_POI_DATA] = selected_poi
            return await self.async_step_name()

        options = []
        for poi in matching_pois:
            poi_name = poi[lang]
            poi_parent_name = poi.get(f"parent_{lang}")
            if poi_parent_name:
                poi_name = f"{poi_parent_name}, {poi_name}"
            options.append({"label": f"{poi_name} ({poi['canton']})", "value": str(poi['poiID'])})

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
        _LOGGER.error("Entered map step")
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
                return await self.async_step_name()
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


    async def async_step_name(self, user_input=None):
        if user_input is not None:
            poi_data = self.context.get(CONF_POI_DATA)
            poi_name = user_input.get(CONF_POI_NAME)
            
            _LOGGER.error(f"POI data: {poi_data}")

            return self.async_create_entry(
                title=f"{poi_name}",
                data={"pois": [(poi_name, poi_data)]},
            )
        
        poi_data = self.context.get(CONF_POI_DATA)
        lang = self.context.get(CONF_LANGUAGE)
        poi_name = poi_data.get(lang)
        poi_parent_name = poi_data.get(f"parent_{lang}")

        if poi_parent_name:
            poi_name = f"{poi_parent_name}, {poi_name}"

        #add Prefix to poi_name
        poi_name_full = f"{CONF_WA_PREFIXES[lang]}{poi_name} ({poi_data['canton']})"
        
        
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_POI_NAME,
                    default=poi_name_full
                ): TextSelector({}),
            }
        )

        return self.async_show_form(
            step_id="name",
            data_schema=data_schema,
            description_placeholders={
                "poi_name": poi_name,
                "title": "title",
                "description": "description"
            }
        )
