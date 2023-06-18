"""Setup Config"""
import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import DOMAIN, CONF_LOC, CONF_RDM, CONF_ROOM, CONF_USERNUMBERS

_LOGGER = logging.getLogger(__name__)

LAUNDRY_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_LOC): cv.string,
        vol.Required(CONF_ROOM): cv.string,
        vol.Required(CONF_RDM): cv.string,
        vol.Required(CONF_USERNUMBERS): cv.string,
    }
)


class LaundryViewConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Laundry View config flow."""

    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            return self.async_create_entry(title="Laundry View", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=LAUNDRY_SCHEMA, errors=errors
        )
