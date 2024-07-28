from __future__ import annotations
from .helpers.common.ContextEntry import ContextEntry

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
    BooleanSelector
    )

from . import WetterAlarmApiClient
from .options_flow import WetterAlarmOptionsFlowHandler
from .translate import load_translations
from .const import (
    DOMAIN,
    WA_PREFIXES
    )
from .consts.options import Options as Opt
from .consts.config import Config as Conf

from .helpers.flow.baseOptions import get_base_vars, get_base_schema, get_input_vars
from .helpers.flow.entityOptions import get_entity_vars, get_entity_schema, create_options

# Load POIs from JSON file
with open('custom_components/wetter_alarm/pois.json', 'r') as file:
    POIS = json.load(file)

class WetterAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            self.context[Opt.Base.Language.LANGUAGE] = user_input[Opt.Base.Language.LANGUAGE]

            if user_input[Conf.POI.SET_BY] == Conf.POI.BY_ID:
                return await self.async_step_enter_id()
            elif user_input[Conf.POI.SET_BY] == Conf.POI.BY_SEARCH:
                return await self.async_step_search()
            elif user_input[Conf.POI.SET_BY] == Conf.POI.BY_MAP:
                return await self.async_step_map()

        data_options = [
            Conf.POI.BY_ID,
            Conf.POI.BY_SEARCH,
            #TODO: Implement map selection, DISABLING FOR NOW
            #Conf.POI.BY_MAP
        ]
        data_schema=vol.Schema(
                {
                    vol.Required(
                        Opt.Base.Language.LANGUAGE,
                        default=Opt.Base.Language.DEFAULT
                    ): SelectSelector({
                        "options": list(Opt.Base.Language.LIST),
                        "custom_value": False,
                        "mode": "dropdown",
                        "translation_key": Opt.Base.Language.LANGUAGE
                    }),
                    vol.Required(
                        Conf.POI.SET_BY,
                        default=Conf.POI.BY_SEARCH
                    ): SelectSelector({
                        "options": list(data_options),
                        "custom_value": False,
                        "mode": "list",
                        "translation_key": Conf.POI.SET_BY
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
            poi_id = user_input.get(Conf.POI.ID)
            poi = next((poi for poi in POIS if poi['poiID'] == poi_id), None)

            if poi_id == 0:
                errors["base"] = Conf.Errors.NO_POI_ID
            elif poi:
                self.context[Conf.POI.DATA] = poi
                return await self.async_step_options()
            else:
                errors["base"] = Conf.Errors.INVALID_POI_ID

        data_schema = vol.Schema(
            {
                vol.Required(
                    Conf.POI.ID,
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
            lang = self.context.get(Opt.Base.Language.LANGUAGE)
            lang_label = f"label_{lang}"
            lang_parent = f"parent_{lang_label}"
            poi_kind = user_input.get(Conf.POI.KIND)
            selected_canton = user_input.get(Conf.POI.CANTON)
            poi_search = user_input.get(Conf.POI.SEARCH, "").lower()
            matching_pois = []

            if selected_canton == "none" and poi_search == "":
                errors["base"] = Conf.Errors.NO_CANTON
            else:
                if selected_canton == "none" and poi_search != "":
                    for poi in POIS:
                        poi_name = poi[lang_label]
                        poi_parent_name = poi.get(lang_parent)
                        if poi_parent_name:
                            poi_name = f"{poi_parent_name}, {poi_name}"
                        
                        if poi_search in poi_name.lower():
                            poi['name'] = poi_name
                            if poi_kind and poi['kind'] in poi_kind:
                                matching_pois.append(poi)
                else:
                    for poi in POIS:
                        if selected_canton == "other" and poi['canton'] is None:
                            poi_name = poi[lang_label]
                            poi_parent_name = poi.get(lang_parent)
                            if poi_parent_name:
                                poi_name = f"{poi_parent_name}, {poi_name}"
                            
                            if poi_search in poi_name.lower():
                                poi['name'] = poi_name
                                if poi_kind and poi['kind'] in poi_kind:
                                    matching_pois.append(poi)
                                
                        elif poi['canton'] == selected_canton:
                            poi_name = poi[lang_label]
                            poi_parent_name = poi.get(lang_parent)
                            if poi_parent_name:
                                poi_name = f"{poi_parent_name}, {poi_name}"
                            
                            if poi_search in poi_name.lower():
                                poi['name'] = poi_name
                                if poi_kind and poi['kind'] in poi_kind:
                                    matching_pois.append(poi)
                    

                self.context[Conf.POI.KIND] = poi_kind
                if len(matching_pois) == 1:
                    self.context[Conf.POI.DATA] = matching_pois[0]
                    return await self.async_step_options()
                elif len(matching_pois) > 1:
                    matching_pois.sort(key=lambda poi: poi['name'])
                    self.context[Conf.POI.LIST] = matching_pois
                    return await self.async_step_select_poi()
                else:
                    errors["base"] = Conf.Errors.NO_POI_FOUND


        data_schema = vol.Schema(
            {
                vol.Required(
                    Conf.POI.CANTON,
                    default="none"
                ): SelectSelector({
                    "options": list(Conf.POI.CANTONS),
                    "custom_value": False,
                    "mode": "dropdown",
                    "translation_key": Conf.POI.CANTON
                }),
                vol.Required(
                    Conf.POI.KIND,
                    default=Conf.POI.KINDS_DEFAULTS
                ): SelectSelector({
                    "options": list(Conf.POI.KINDS),
                    "multiple": True,
                    "custom_value": False,
                    "mode": "dropdown",
                    "translation_key": Conf.POI.KIND
                }),

                vol.Optional(
                    Conf.POI.SEARCH,
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
        matching_pois = self.context.get(Conf.POI.LIST)
        lang = self.context.get(Opt.Base.Language.LANGUAGE)
        lang_label = f"label_{lang}"
        lang_parent = f"parent_{lang_label}"

        translations = await load_translations(lang)

        if user_input is not None and Conf.POI.ID in user_input:
            selected_poi_id = user_input.get(Conf.POI.ID)
            selected_poi = next(poi for poi in POIS if poi['poiID'] == int(selected_poi_id))
            self.context[Conf.POI.DATA] = selected_poi
            return await self.async_step_options()
        
        
        options = []
        for poi in matching_pois:
            poi_name = poi[lang_label]
            poi_parent_name = poi.get(lang_parent)
            if poi_parent_name:
                poi_name = f"{poi_parent_name}, {poi_name}"
             
            poi_kind_translated = translations.get("selector", {}).get(Conf.POI.KIND, {}).get("options", {}).get(poi['kind'], poi['kind'])
            options.append({"label": f"{poi_name} ({poi_kind_translated})", "value": str(poi['poiID'])})

        data_schema = vol.Schema(
            {
                vol.Required(
                    Conf.POI.ID
                ): SelectSelector({
                    "options": options,
                    "custom_value": False,
                    "mode": "dropdown",
                    "sort": True,
                    "translation_key": Conf.POI.ID
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
    
    # TODO: Implement this function correctly
    async def async_step_map(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Hier kannst du die Benutzereingaben verarbeiten und passende POIs finden
            location = user_input.get(Conf.POI.MAP)
            radius = location.get("radius")
            lat = location.get("latitude")
            lon = location.get("longitude")

            # Implementiere die Logik, um POIs basierend auf der Karte zu finden
            matching_pois = [
                poi for poi in POIS
                if self._is_within_radius(poi['lat'], poi['long'], lat, lon, radius)
            ]

            if len(matching_pois) == 1:
                self.context[Conf.POI.DATA] = matching_pois[0]
                return await self.async_step_options()
            elif len(matching_pois) > 1:
                self.context[Conf.POI.LIST] = matching_pois
                return await self.async_step_select_poi()
            else:
                errors["base"] = Conf.Errors.NO_POI_FOUND

        data_schema = vol.Schema(
            {
                vol.Required(
                    Conf.POI.MAP
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
        
        poi_data = self.context.get(Conf.POI.DATA)
        lang = self.context.get(Opt.Base.Language.LANGUAGE)
        lang_label = f"label_{lang}"
        lang_parent = f"parent_{lang_label}"
        
        poi_name = poi_data.get(lang_label)
        poi_parent_name = poi_data.get(lang_parent)
        if poi_parent_name:
            poi_name = f"{poi_parent_name}, {poi_name}"

        poi_name_full = f"{WA_PREFIXES[lang]}{poi_name} ({poi_data['canton']})"
        
        options = {
            Opt.Base.POI.NAME: poi_name_full,
            Opt.Base.POI.NAME_SHORT: poi_name,
            Opt.Base.Language.LANGUAGE: lang,
            Opt.Base.Options.IS_CONFIGURED: False,
        }

        data = {
            Conf.POI.ID: poi_data.get("poiID"),
            Conf.POI.DATA: poi_data
        }

        self.context['entry_data'] = data
        self.context['entry_options'] = options        

        return await self.async_step_base()       
       
    #! Options Configuration
    async def async_step_base(self, user_input=None): 
        errors = {}

        base_vars = self.context['entry_options']
        if user_input is not None:
            self.context['entry_options'] = get_input_vars(user_input)
            return await self.async_step_entitys()
             
        data_schema = get_base_schema(base_vars, False)

        return self.async_show_form(
            step_id="base",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_entitys(self, user_input=None): 
        errors = {}
       
        getOptions = self.context['entry_options']

        if user_input is not None:
            data = self.context['entry_data']
            options = create_options(getOptions, user_input)
            options[Opt.Base.BASE_CONFIG][Opt.Base.Language.LANGUAGE] = self.context.get(Opt.Base.Language.LANGUAGE)
            poi_name_full = options[Opt.Base.BASE_CONFIG][Opt.Base.POI.NAME]
            
            return self.async_create_entry(
                title=poi_name_full,
                data=data,
                options=options,
                #unique_id=f"{poi_data.get('kind')}_{poi_data.get('poiID')}"
            )
                  

        entity_vars = get_entity_vars(getOptions, True)
        data_schema = get_entity_schema(entity_vars)

        return self.async_show_form(
            step_id="entitys",
            data_schema=data_schema,
            errors=errors,
        ) 


    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WetterAlarmOptionsFlowHandler(config_entry)