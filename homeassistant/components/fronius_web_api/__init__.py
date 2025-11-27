"""The Fronius Web Api integration."""

from __future__ import annotations

import logging
import voluptuous

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .config_flow import PlaceholderHub
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
_PLATFORMS: list[Platform] = [Platform.SELECT]

# TODO Create ConfigEntry type alias with API object
# TODO Rename type alias and update all entry annotations
type New_NameConfigEntry = ConfigEntry


SERVICE_SCHEMA = voluptuous.Schema(
    {
        voluptuous.Required("power", default=1000): int,
        voluptuous.Required("schedule_type", default="CHARGE_MIN"): voluptuous.In(
            ["CHARGE_MIN", "CHARGE_MAX", "DISCHARGE_MIN", "DISCHARGE_MAX"]
        ),
        voluptuous.Optional("start_time", default="00:00"): str,
        voluptuous.Optional("end_time", default="23:59"): str,
    }
)


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
    await hass.config_entries.async_forward_entry_setups(entry, ["select"])

    async def set_battery_schedule(service_call):
        """Set the battery schedule based on the service call."""
        # Implement the logic to set the battery schedule using the hub instance
        _LOGGER.info("Setting battery schedule with data: %s", service_call.data)
        await hub.set_battery_schedule(
            [
                {
                    "Active": True,
                    "Power": service_call.data.get("power", 0),
                    "ScheduleType": service_call.data.get(
                        "schedule_type", "CHARGE_MIN"
                    ),
                    "TimeTable": {
                        "Start": service_call.data.get("start_time", "00:00"),
                        "End": service_call.data.get("end_time", "23:59"),
                    },
                    "Weekdays": {
                        "Mon": True,
                        "Tue": True,
                        "Wed": True,
                        "Thu": True,
                        "Fri": True,
                        "Sat": True,
                        "Sun": True,
                    },
                }
            ]
        )

    hass.services.async_register(
        domain=DOMAIN,
        service="set_battery_schedule",
        service_func=set_battery_schedule,
        schema=SERVICE_SCHEMA,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["select"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
