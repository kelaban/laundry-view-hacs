"""Laundry View Sensor"""

import logging
import re
import aiohttp
from datetime import timedelta
from typing import Any, Callable, Dict, Optional
from functools import cached_property
from dataclasses import dataclass


import voluptuous as vol
from homeassistant import config_entries, core
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, CONF_LOC, CONF_RDM, CONF_ROOM, CONF_USERNUMBERS

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_LOC): cv.string,
        vol.Required(CONF_ROOM): cv.string,
        vol.Required(CONF_RDM): cv.string,
        vol.Required(CONF_USERNUMBERS): cv.string,
    }
)


_LOGGER = logging.getLogger(__name__)
_LOGGER.info("Sensor loaded")
# Time between updating data from GitHub
SCAN_INTERVAL = timedelta(minutes=1)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    _LOGGER.debug("Setting up entry")
    config = hass.data[DOMAIN][config_entry.entry_id]

    if config_entry.options:
        config.update(config_entry.options)

    session = async_get_clientsession(hass)
    coordinator = LaundryViewDataCoordinator(session, hass, config)
    _LOGGER.debug("About to start coordinator")
    await async_start_platform(coordinator, async_add_entities)

async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    _LOGGER.debug("Setting up platform")
    session = async_get_clientsession(hass)
    coordinator = LaundryViewDataCoordinator(session, hass, config)
    await async_start_platform(coordinator, async_add_entities)


async def async_start_platform(coordinator, async_add_entities: Callable):
    #
    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    _LOGGER.debug("Starting data coordinator")
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        LaundryRoomSensor(coordinator, idx)
        for idx, ent in enumerate(coordinator.data["machine_status"])
    )


class LaundryViewDataCoordinator(DataUpdateCoordinator):
    def __init__(
        self, session: aiohttp.ClientSession, hass: core.HomeAssistant, config: dict
    ) -> None:
        self._session = session
        self._config = config

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            update_method=self._async_update,
        )

    async def _async_update(self):
        notifications = {}
        if self._config.get(CONF_USERNUMBERS, ""):
            pass

        loc = self._config.get(CONF_LOC)
        room = self._config.get(CONF_ROOM)
        rdm = self._config.get(CONF_RDM)
        async with self._session.get(
            f"https://www.laundryview.com/api/c_room?loc={loc}&room={room}&rdm={rdm}"
        ) as response:
            response.raise_for_status()
            resp = await response.json()
            machine_status = resp["lRoom"]["app_data"]

            _LOGGER.debug(f"resp: {resp}")

            return {"notifications": notifications, "machine_status": machine_status}


@dataclass
class Appliance:
    state: str
    app_type: str
    channel: str
    time_remaining: int
    appliance_desc_key: str

    @property
    def app_type_name(self) -> str:
        if self.app_type == "W":
            return "WASHER"
        elif self.app_type == "D":
            return "DRYER"
        else:
            return "UNKNOWN"


class LaundryRoomSensor(CoordinatorEntity):
    def __init__(self, coordinator: LaundryViewDataCoordinator, idx: int):
        super().__init__(coordinator)
        self._idx = idx

    @cached_property
    def appliance(self) -> Appliance:
        data = self.coordinator.data["machine_status"][self._idx]
        return Appliance(
            state=data["status_toggle"],
            app_type=data["appliance_type"],
            channel=data["lrm_channel"],
            time_remaining=data["time_remaining"],
            appliance_desc_key=data["appliance_desc_key"],
        )

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return f"laundry room {self.appliance.app_type_name.lower()} {self.appliance.channel}"

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self.appliance.appliance_desc_key

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # TODO
        return True

    @property
    def state(self) -> Optional[str]:
        return self.appliance.state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return {
            "time_remaining": self.appliance.time_remaining,
            "type": self.appliance.app_type_name,
        }




# Example data Format
# {
#    "lRoom": {
#     "app_data": [
#       {
#         "lrm_serial_number": "L13176",
#         "laundry_room_desc_key": "10000000705",
#         "lrm_status": "1",
#         "appliance_desc_key": "10000010515",
#         "appliance_desc": "01",
#         "lrm_channel": "1",
#         "alert_idle_tolerance": 0,
#         "broken_ind": "0",
#         "speedqueen_ind": "1",
#         "inventory": "Stacked Dryer",
#         "appliance_type": "D",
#         "appliance_type_desc": "DRYER",
#         "status": "1",
#         "status_start_time": 1644010053,
#         "app_run_time": 0,
#         "avg_cycle_time": 60,
#         "percentage": 0,
#         "bar_width": 0,
#         "time_remaining": 60,
#         "status_toggle": "available"
#       } ]
#   }
# }
