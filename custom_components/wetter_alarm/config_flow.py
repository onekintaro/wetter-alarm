from __future__ import annotations

import logging
import json
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from . import WetterAlarmApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Load POIs from JSON file
with open('custom_components/wetter_alarm/pois.json', 'r') as file:
    POIS = json.load(file)

class WetterAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            if "poi_search" in user_input:
                return await self.async_step_select_poi(user_input)

            poi_id = user_input.get("poi_id", "")
            client = WetterAlarmApiClient(poi_id)
            valid_poi = await client.validate_poi_id_async(hass=self.hass)
            if valid_poi:
                poi_name = user_input.get("poi_name", "")
                return self.async_create_entry(
                    title="Wetter-Alarm",
                    data={"pois": {(poi_name, poi_id)}},
                )
            else:
                _LOGGER.error("async step_user determined invalid POI")
                errors["base"] = "invalid_connection"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional("poi_search"): str,
                }
            ),
            errors=errors,
        )

    async def async_step_select_poi(self, user_input=None):
        errors = {}
        if user_input is not None:
            poi_search = user_input.get("poi_search", "").lower()
            matching_pois = [
                poi for poi in POIS
                if poi_search in poi['label_de'].lower() or
                   poi_search in poi['label_fr'].lower() or
                   poi_search in poi['label_it'].lower() or
                   poi_search in poi['label_en'].lower()
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
                            vol.Required("poi_id"): vol.In(options),
                        }
                    ),
                    errors=errors,
                )
            else:
                errors["base"] = "no_pois_found"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional("poi_search"): str,
                }
            ),
            errors=errors,
        )
