"""Laundry View Sensor"""

import logging
import re
import aiohttp
from datetime import timedelta
from typing import Any, Callable, Dict, Optional
from urllib import parse

import voluptuous as vol
from config.custom_components.laundry_view.const import CONF_USERNUMBERS, DOMAIN
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

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    vol.Schema(
        {
            vol.Required(CONF_LOC): cv.string,
            vol.Required(CONF_ROOM): cv.string,
            vol.Required(CONF_RDM): cv.string,
            vol.Required(CONF_USERNUMBERS): cv.string,
        }
    )
)


_LOGGER = logging.getLogger(__name__)
# Time between updating data from GitHub
SCAN_INTERVAL = timedelta(minutes=10)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]

    if config_entry.options:
        config.update(config_entry.options)

    session = async_get_clientsession(hass)
    coordinator = LaundryViewDataCoordinator(session, hass, config)

    #
    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        MyEntity(coordinator, idx) for idx, ent in enumerate(coordinator.data)
    )


class LaundryViewDataCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        hass: core.HomeAssistant,
        config: dict,
    ):
        self._session = session
        self._config = config

        super.__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            update_method=self._async_update,
        )

   """Example data Format
   {
       "lRoom": {
        "app_data": [
          {
            "lrm_serial_number": "L13176",
            "laundry_room_desc_key": "10000000705",
            "lrm_status": "1",
            "appliance_desc_key": "10000010515",
            "appliance_desc": "01",
            "lrm_channel": "1",
            "alert_idle_tolerance": 0,
            "broken_ind": "0",
            "speedqueen_ind": "1",
            "inventory": "Stacked Dryer",
            "appliance_type": "D",
            "appliance_type_desc": "DRYER",
            "status": "1",
            "status_start_time": 1644010053,
            "app_run_time": 0,
            "avg_cycle_time": 60,
            "percentage": 0,
            "bar_width": 0,
            "time_remaining": 60,
            "status_toggle": "available"
          } ]
      }
   }
      """


    async def _async_update(self):
        notifications = {}
        if self.config.get(CONF_USERNUMBERS, ""):
            pass

        async with self._session.get(
            f"https://www.laundryview.com/api/c_room?loc={self.loc}&room={self.room}&rdm={self.rdm}"
        ) as response:
            response.raise_for_status()
            resp = await response.json()
            machine_status = resp["lRoom"]["app_data"]

            return {"notifications": notifications, "machine_status": machine_status}


class LaundryRoomSensor(CoordinatorEntity):
    def __init__(self, coordinator: LaundryViewDataCoordinator, idx: int):
        super.__init__(coordinator)
        self._idx = idx

    # app_type_name = LaundryView.appliance_type_name(appliance["appliance_type"])
    # channel = appliance["lrm_channel"]
    # time_remaining = appliance["time_remaining"]
    # current_state = appliance["status_toggle"]
    # has_notification = appliance["has_notification"]

    # return (
    #     f'{ha_prefix}laundry_room_{app_type_name.lower()}_{channel}',
    #     {
    #         "state": current_state,
    #         "attributes": {
    #             "friendly_name": f'{app_type_name.lower()} {channel}',
    #             "time_remaining": time_remaining,
    #             "type": app_type_name,
    #             "has_notification": has_notification
    #         }
    #     }
    # )

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self.repo

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        return self.attrs


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    raise NotImplementedError()
    # session = async_get_clientsession(hass)
    # github = GitHubAPI(session, "requester", oauth_token=config[CONF_ACCESS_TOKEN])
    # sensors = [GitHubRepoSensor(github, repo) for repo in config[CONF_REPOS]]
    # async_add_entities(sensors, update_before_add=True)
