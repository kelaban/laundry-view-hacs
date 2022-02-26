"""Tests for the sensor"""
from unittest import mock

import pytest
from custom_components.laundry_view.const import DOMAIN, CONF_LOC, CONF_RDM, CONF_ROOM, CONF_USERNUMBERS
from custom_components.laundry_view import sensor
from homeassistant.setup import async_setup_component
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker, AiohttpClientMockResponse

async def test_async_update_success(hass, aioclient_mock: AiohttpClientMocker, laundry_test_data):
    """Tests a fully successful async_update."""
    conf = {CONF_LOC: "1298", CONF_RDM: "1644085830159", CONF_ROOM: "4697601", CONF_USERNUMBERS: "4"}
    
    aioclient_mock.get(
            f"https://www.laundryview.com/api/c_room?loc={conf[CONF_LOC]}&room={conf[CONF_ROOM]}&rdm={conf[CONF_RDM]}",
            json=laundry_test_data
    )

    
    entry = MockConfigEntry(domain=DOMAIN, data=conf)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    
    entity_registry = er.async_get(hass)
    state_entity_ids = hass.states.async_entity_ids()
    assert aioclient_mock.call_count == 1
    assert len(state_entity_ids) == 11


