from homeassistant.helpers.entity import Entity
from homeassistant.components.input_number import (
    DOMAIN as INPUT_NUMBER_DOMAIN,
    InputNumber,
    SERVICE_INCREMENT,
    SERVICE_DECREMENT,
)
from homeassistant.components.input_button import (
    DOMAIN as INPUT_BUTTON_DOMAIN,
    InputButton,
)

async def async_setup_entry(hass, config_entry):
    if INPUT_NUMBER_DOMAIN not in hass.data:
        hass.data[INPUT_NUMBER_DOMAIN] = {}

    if INPUT_BUTTON_DOMAIN not in hass.data:
        hass.data[INPUT_BUTTON_DOMAIN] = {}

    # Input Number
    hass.data[INPUT_NUMBER_DOMAIN]['wetter_alarm_index'] = InputNumber(
        hass,
        'Wetter Alarm Index',
        0,
        0,
        10,
        1,
        'index',
        config_entry.entry_id
    )

    # Input Buttons
    hass.data[INPUT_BUTTON_DOMAIN]['wetter_alarm_next'] = InputButton(
        hass,
        'Next Alarm',
        config_entry.entry_id,
    )

    hass.data[INPUT_BUTTON_DOMAIN]['wetter_alarm_previous'] = InputButton(
        hass,
        'Previous Alarm',
        config_entry.entry_id,
    )

    async def handle_next_alarm(service):
        await hass.services.async_call(
            INPUT_NUMBER_DOMAIN, SERVICE_INCREMENT, {'entity_id': 'input_number.wetter_alarm_index'}
        )

    async def handle_previous_alarm(service):
        await hass.services.async_call(
            INPUT_NUMBER_DOMAIN, SERVICE_DECREMENT, {'entity_id': 'input_number.wetter_alarm_index'}
        )

    hass.services.async_register(
        INPUT_BUTTON_DOMAIN, 'wetter_alarm_next', handle_next_alarm
    )

    hass.services.async_register(
        INPUT_BUTTON_DOMAIN, 'wetter_alarm_previous', handle_previous_alarm
    )

    return True
