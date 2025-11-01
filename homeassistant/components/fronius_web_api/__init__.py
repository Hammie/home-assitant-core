"""The Fronius Web Api integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .config_flow import PlaceholderHub
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
_PLATFORMS: list[Platform] = [Platform.SENSOR]

# TODO Create ConfigEntry type alias with API object
# TODO Rename type alias and update all entry annotations
type New_NameConfigEntry = ConfigEntry


# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: New_NameConfigEntry) -> bool:
    """Set up Fronius Web API from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    hub = PlaceholderHub(hass, entry.data["host"])

    try:
        success = await hub.authenticate(entry.data["username"], entry.data["password"])
        if not success:
            raise Exception("Authentication failed")
    except Exception as err:
        _LOGGER.exception("Failed to authenticate with Fronius Web API: %s", err)
        return False

    # Store hub instance so platforms can access it
    hass.data[DOMAIN][entry.entry_id] = hub

    # Forward the entry setup to the platforms (sensors, etc.)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
