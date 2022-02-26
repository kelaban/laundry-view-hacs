"""Tests for the config flow."""
from unittest import mock

import pytest
from custom_components.laundry_view.const import DOMAIN, CONF_LOC, CONF_RDM, CONF_ROOM, CONF_USERNUMBERS
from custom_components.laundry_view import config_flow



async def test_flow_user_init(hass):
    """Test the initialization of the form in the first step of the config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    expected = {
        "data_schema": config_flow.LAUNDRY_SCHEMA,
        "description_placeholders": None,
        "errors": {},
        "flow_id": mock.ANY,
        "handler": "laundry_view",
        "step_id": "user",
        "type": "form",
        "last_step": None,
    }
    assert expected == result
    
async def test_flow_creates_config_entry(hass):
    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )
    data = {CONF_LOC: 1, CONF_ROOM: 2, CONF_RDM: 3, CONF_USERNUMBERS: 1234}
    result = await hass.config_entries.flow.async_configure(
        _result["flow_id"],
        user_input=data
    )
    expected = {
        "version": 1,
        "type": "create_entry",
        "flow_id": mock.ANY,
        "handler": "laundry_view",
        "title": "Laundry View",
        # coerce input values to string
        "data": dict((x, str(y)) for x, y in data.items()),
        "description": None,
        "description_placeholders": None,
        "options": {},
        "result": mock.ANY,
    }
    assert expected == result