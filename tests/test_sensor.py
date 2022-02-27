"""Tests for the sensor"""
from html import entities
from unittest import mock

import pytest
import asyncio
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

    states = [hass.states.get(e) for e in state_entity_ids]
    washers = [x for x in states if x.attributes["type"] == "WASHER"]
    dryers = [x for x in states if x.attributes["type"] == "DRYER"]
    assert len(dryers) == 5
    assert len(washers) == 6

@pytest.mark.skip(reason="Not sure how to test this yet")
async def test_async_updates_work(hass, aioclient_mock: AiohttpClientMocker, laundry_test_data):
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
    
    test_id = "sensor.laundry_room_dryer_5"
    entity_registry = er.async_get(hass)
    entity = entity_registry.async_get(test_id)
    assert hass.states.get(entity.entity_id).state == "inuse"

    for value in laundry_test_data["lRoom"]["app_data"]:
        if value["lrm_channel"] == "5":
            value["status_toggle"] = "available"
        
    aioclient_mock.get(
            f"https://www.laundryview.com/api/c_room?loc={conf[CONF_LOC]}&room={conf[CONF_ROOM]}&rdm={conf[CONF_RDM]}",
            json=laundry_test_data
    )
    
    await entity.async_update_entity
    assert hass.states.get(entity.entity_id).state == "available"
