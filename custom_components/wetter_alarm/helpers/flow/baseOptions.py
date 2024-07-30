import voluptuous as vol
from homeassistant.helpers.selector import SelectSelector, NumberSelector, TextSelector, BooleanSelector

from ..const.options import Options as Opt

Base = Opt.Base

def get_base_vars(config_entry):
    poi_name = config_entry.title
    poi_options = config_entry.options
    options_base = poi_options.get(Base.BASE_CONFIG, {})
    
    poi_name_short = options_base.get(Base.POI.NAME_SHORT)
    lang = options_base.get(Base.Language.LANGUAGE)
    update_interval = options_base.get(Base.Update.INTERVAL, Base.Update.DEFAULT)
    update_interval_type = options_base.get(Base.Update.TYPE, Base.Update.TYPE_LIST[0])
    # remove_unused = options_base.get(Base.Options.REMOVE_UNUSED, False)
    
    return {
        Base.POI.NAME: poi_name,
        Base.POI.NAME_SHORT: poi_name_short,
        Base.Language.LANGUAGE: lang,
        Base.Update.INTERVAL: update_interval,
        Base.Update.TYPE: update_interval_type,
        # Base.Options.REMOVE_UNUSED: remove_unused,
        Base.Options.REMOVE_UNUSED: False, # Remove unused is not fully implemented yet
    }

def get_input_vars(user_input):
    return {
        Base.POI.NAME: user_input.get(Base.POI.NAME),
        Base.POI.NAME_SHORT: user_input.get(Base.POI.NAME_SHORT),
        Base.Update.INTERVAL: user_input.get(Base.Update.INTERVAL),
        Base.Update.TYPE: user_input.get(Base.Update.TYPE),
        Base.Language.LANGUAGE: user_input.get(Base.Language.LANGUAGE),
        # Base.Options.REMOVE_UNUSED: user_input.get(Base.Options.REMOVE_UNUSED),
        Base.Options.REMOVE_UNUSED: False, # Remove unused is not fully implemented yet
    }

def get_base_schema(options_base, include_lang=True):
    schema = {
        vol.Required(
            Base.POI.NAME,
            default=options_base.get(Base.POI.NAME)
        ): TextSelector({}),
        vol.Required(
            Base.POI.NAME_SHORT,
            default=options_base.get(Base.POI.NAME_SHORT)
        ): TextSelector({}),
        vol.Required(
            Base.Update.INTERVAL,
            default=options_base.get(Base.Update.INTERVAL, Base.Update.DEFAULT)
        ): NumberSelector({
            #"min": Base.Update.MIN,
            "step": 1,
            "mode": "box",
        }),
        vol.Required(
            Base.Update.TYPE,
            default=options_base.get(Base.Update.TYPE, Base.Update.TYPE_LIST[0])
        ): SelectSelector({
            "options": list(Base.Update.TYPE_LIST),
            "custom_value": False,
            "mode": "dropdown",
            "translation_key": Base.Update.TYPE
        }),
        # Remove unused is not fully implemented yet
        # vol.Required(
        #     Base.Options.REMOVE_UNUSED,
        #     default=options_base.get(Base.Options.REMOVE_UNUSED, False)
        # ): BooleanSelector({}),
    }
    
    if include_lang:
        schema = {
            vol.Required(
                Base.Language.LANGUAGE,
                default=options_base.get(Base.Language.LANGUAGE, Base.Language.DEFAULT)
            ): SelectSelector({
                "options": list(Base.Language.LIST),
                "custom_value": False,
                "mode": "dropdown",
                "translation_key": Base.Language.LANGUAGE
            }),
            **schema
        }

    return vol.Schema(schema)
