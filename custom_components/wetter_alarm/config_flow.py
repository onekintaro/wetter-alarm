from __future__ import annotations

import logging
import json
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, TextSelector, TextSelectorConfig

from . import WetterAlarmApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Load POIs from JSON file
with open('custom_components/wetter_alarm/pois.json', 'r') as file:
    POIS = json.load(file)

CANTONS = sorted(set(poi['canton'] for poi in POIS))

class WetterAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            selected_canton = user_input.get("canton")
            return await self.async_step_select_poi({"canton": selected_canton})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("canton"): SelectSelector(
                        SelectSelectorConfig(options=CANTONS)
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_select_poi(self, user_input=None):
        errors = {}
        selected_canton = user_input.get("canton")
        if user_input is not None and "poi_search" in user_input:
            poi_search = user_input.get("poi_search", "").lower()
            matching_pois = [
                poi for poi in POIS
                if poi['canton'] == selected_canton and (
                    poi_search in poi['label_de'].lower() or
                    poi_search in poi['label_fr'].lower() or
                    poi_search in poi['label_it'].lower() or
                    poi_search in poi['label_en'].lower()
                )
            ]

            if len(matching_pois) == 1:
                poi = matching_pois[0]
                return self.async_create_entry(
                    title=f"Wetter-Alarm: {poi['label_de']}",
                    data={"pois": {(poi['label_de'], poi['poiID'])}},
                )
            elif len(matching_pois) > 1:
                options = {str(poi['poiID']): f"{poi['label_de']} ({poi['canton']})" for poi in matching_pois}
                return self.async_show_form(
                    step_id="select_poi",
                    data_schema=vol.Schema(
                        {
                            vol.Required("poi_id"): SelectSelector(
                                SelectSelectorConfig(options=options)
                            ),
                        }
                    ),
                    errors=errors,
                )
            else:
                errors["base"] = "no_pois_found"

        return self.async_show_form(
            step_id="select_poi",
            data_schema=vol.Schema(
                {
                    vol.Required("canton"): SelectSelector(
                        SelectSelectorConfig(options=CANTONS, default=selected_canton)
                    ),
                    vol.Optional("poi_search"): TextSelector(
                        TextSelectorConfig(type="text")
                    ),
                }
            ),
            errors=errors,
        )
