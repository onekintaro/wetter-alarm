from __future__ import annotations

import logging
import json
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig
from homeassistant.helpers.translation import async_get_translations

from . import WetterAlarmApiClient
from .const import DOMAIN, CANTONS

_LOGGER = logging.getLogger(__name__)

# Load POIs from JSON file
with open('custom_components/wetter_alarm/pois.json', 'r') as file:
    POIS = json.load(file)

class WetterAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def canton_options(self):
        translations = await async_get_translations(self.hass, 'strings', 'en')
        options = {"": translations.get("config.canton.placeholder", "Please select a canton")}
        options.update({canton['code']: translations.get(f"config.canton.{canton['code']}", canton['name']) for canton in CANTONS})
        return options

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            if user_input["selection"] == "by_id":
                return await self.async_step_enter_id()
            elif user_input["selection"] == "by_search":
                return await self.async_step_search()

        translations = await async_get_translations(self.hass, 'strings', 'en')
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("selection"): vol.In({
                        "by_id": translations.get("config.selection.by_id", "Enter POI ID"),
                        "by_search": translations.get("config.selection.by_search", "Search by Canton and Location")
                    })
                }
            ),
            errors=errors,
            description_placeholders={
                "title": translations.get("config.step.user.title", "Wetter-Alarm Setup"),
                "description": translations.get("config.step.user.description", "Choose how you want to set up the POI.")
            }
        )

    async def async_step_enter_id(self, user_input=None):
        errors = {}
        translations = await async_get_translations(self.hass, 'strings', 'en')
        if user_input is not None:
            poi_id = user_input.get("poi_id")
            poi = next((poi for poi in POIS if poi['poiID'] == poi_id), None)

            if poi:
                return await self.async_step_name({
                    "poi_id": poi['poiID'],
                    "poi_name": poi['label_de']
                })
            else:
                errors["base"] = "config.error.invalid_poi_id"

        return self.async_show_form(
            step_id="enter_id",
            data_schema=vol.Schema(
                {
                    vol.Required("poi_id"): int,
                }
            ),
            errors=errors,
            description_placeholders={
                "title": translations.get("config.step.enter_id.title", "Enter POI ID"),
                "description": translations.get("config.step.enter_id.description", "Please enter the POI ID.")
            }
        )

    async def async_step_search(self, user_input=None):
        errors = {}
        translations = await async_get_translations(self.hass, 'strings', 'en')
        if user_input is not None:
            selected_canton = user_input.get("canton")
            poi_search = user_input.get("poi_search", "").lower()

            # Filter POIs based on selected canton and search input
            matching_pois = [
                poi for poi in POIS
                if (selected_canton == "Ohne Kanton" and poi['canton'] is None) or
                   (poi['canton'] == selected_canton and (
                    poi_search in poi['label_de'].lower() or
                    poi_search in poi['label_fr'].lower() or
                    poi_search in poi['label_it'].lower() or
                    poi_search in poi['label_en'].lower()
                ))
            ]

            if len(matching_pois) == 1:
                return await self.async_step_name({
                    "poi_id": matching_pois[0]['poiID'],
                    "poi_name": matching_pois[0]['label_de']
                })
            elif len(matching_pois) > 1:
                return await self.async_step_select_poi({
                    "canton": selected_canton,
                    "matching_pois": matching_pois
                })
            else:
                errors["base"] = "config.error.no_pois_found"

        return self.async_show_form(
            step_id="search",
            data_schema=vol.Schema(
                {
                    vol.Required("canton"): vol.In(await self.canton_options()),
                    vol.Optional("poi_search"): TextSelector(TextSelectorConfig(type="text")),
                }
            ),
            errors=errors,
            description_placeholders={
                "title": translations.get("config.step.search.title", "Search by Canton and Location"),
                "description": translations.get("config.step.search.description", "Select a canton and optionally enter a location to search for POIs.")
            }
        )

    async def async_step_select_poi(self, user_input=None):
        errors = {}
        translations = await async_get_translations(self.hass, 'strings', 'en')
        matching_pois = user_input.get("matching_pois", [])

        if user_input is not None and "poi_id" in user_input:
            selected_poi_id = user_input.get("poi_id")
            selected_poi = next(poi for poi in POIS if poi['poiID'] == int(selected_poi_id))
            return await self.async_step_name({
                "poi_id": selected_poi['poiID'],
                "poi_name": selected_poi['label_de']
            })

        options = {str(poi['poiID']): f"{poi['label_de']} ({poi['canton']})" for poi in matching_pois}

        return self.async_show_form(
            step_id="select_poi",
            data_schema=vol.Schema(
                {
                    vol.Required("poi_id"): vol.In(options),
                }
            ),
            errors=errors,
            description_placeholders={
                "title": translations.get("config.step.select_poi.title", "Select POI"),
                "description": translations.get("config.step.select_poi.description", "Multiple POIs found. Please select one.")
            }
        )

    async def async_step_name(self, user_input=None):
        translations = await async_get_translations(self.hass, 'strings', 'en')
        if user_input is not None:
            poi_id = user_input.get("poi_id")
            poi_name = user_input.get("poi_name")
            custom_name = user_input.get("custom_name") or poi_name

            return self.async_create_entry(
                title=f"{custom_name}",
                data={"pois": [(custom_name, poi_id)]},
            )

        return self.async_show_form(
            step_id="name",
            data_schema=vol.Schema(
                {
                    vol.Required("poi_name"): str,
                    vol.Optional("custom_name"): str,
                }
            ),
            description_placeholders={
                "title": translations.get("config.step.name.title", "Set POI Name"),
                "description": translations.get("config.step.name.description", "You can give the POI a custom name.")
            }
        )
