from .helpers.common.ContextEntry import ContextEntry
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from homeassistant.helpers.selector import (
    SelectSelector,
    NumberSelector,
    TextSelector,
    BooleanSelector,
)
from .const import DOMAIN
from .helpers.const.options import Options as Opt
from .helpers.flow.baseOptions import get_base_vars, get_base_schema, get_input_vars
from .helpers.flow.entityOptions import get_entity_vars, get_entity_schema, create_options


Base = Opt.Base
Entity = Opt.Entity

class WetterAlarmOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry
        
    async def async_step_init(self, user_input=None):
        return await self.async_step_base()

    async def async_step_base(self, user_input=None):
        errors = {}        

        if user_input is not None:
            self.context[Base.BASE_CONFIG] = get_input_vars(user_input)
            return await self.async_step_entitys()
            
        base_vars = get_base_vars(self.config_entry)    
        data_schema = get_base_schema(base_vars)

        return self.async_show_form(
            step_id="base",
            data_schema=data_schema,
            errors=errors,
        )
    
    async def async_step_entitys(self, user_input=None):
        errors = {}

        base_config = self.context.get(Base.BASE_CONFIG)

        if user_input is not None:
            poi_name_new = base_config.get(Base.POI.NAME)
            options = create_options(base_config, user_input)
            
            self.hass.config_entries.async_update_entry(
                self.config_entry, title=poi_name_new, options=options
            )

            return self.async_create_entry(
                title=poi_name_new,
                data=options,
                #unique_id=f"{poi_data.get('kind')}_{poi_data.get('poiID')}"
            )

        

        entity_vars = get_entity_vars(self.config_entry)
        data_schema = get_entity_schema(entity_vars)

        return self.async_show_form(
            step_id="entitys",
            data_schema=data_schema,
            errors=errors,
        )

async def async_setup_entry(hass, config_entry):
    hass.data.setdefault(DOMAIN, {})

    config_entry.async_on_unload(
        config_entry.add_update_listener(update_listener)
    )

    return True

async def update_listener(hass, config_entry):
    await hass.config_entries.async_reload(config_entry.entry_id)
