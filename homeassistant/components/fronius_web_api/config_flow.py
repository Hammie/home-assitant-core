"""Config flow for the Fronius Web Api integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError

from .const import DEFAULT_USERNAME, DOMAIN

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class PlaceholderHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Initialize."""
        self.hass = hass
        self.host = host
        self._client = None

    def authenticate_sync(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        try:
            from fronius_web_api import FroniusGen24Client
        except Exception as err:
            _LOGGER.error("Missing dependency fronius-gen24-client: %s", err)
            raise ConfigEntryNotReady("fronius-web-api not installed") from err
        self._client = FroniusGen24Client(base_url=self.host)
        self._client.login(username, password)
        return True

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        return await self.hass.async_add_executor_job(
            self.authenticate_sync, username, password
        )

    async def set_battery_schedule(self, schedule_data: list[dict[str, Any]]) -> None:
        """Set the battery schedule."""
        # Implement the logic to set the battery schedule using the client
        _LOGGER.info("Setting battery schedule with data: %s", schedule_data)

        if not self._client:
            raise RuntimeError("Client not authenticated")

        from fronius_web_api import TimeOfUsePayload

        await self.hass.async_add_executor_job(
            self._client.set_battery_limit,
            TimeOfUsePayload.model_validate(schedule_data),
        )


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data[CONF_USERNAME], data[CONF_PASSWORD]
    # )

    hub = PlaceholderHub(hass, data[CONF_HOST])

    if not await hub.authenticate(data[CONF_USERNAME], data[CONF_PASSWORD]):
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "Name of the device"}


class FroniusWebApiConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fronius Web Api."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
