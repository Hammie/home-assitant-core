from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN

MODES = ["Charge Minimum", "Charge Maximum", "Discharge Minimum", "Discharge Maximum"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Fronius Web API select entities."""
    hub = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FroniusModeSelect(hub)], True)


class FroniusModeSelect(SelectEntity):
    """Battert limit mode selection."""

    _attr_name = "Fronius Battery Limit Mode"
    _attr_icon = "mdi:solar-power"
    _attr_options = MODES

    def __init__(self, hub) -> None:
        self._hub = hub
        self._attr_unique_id = f"{DOMAIN}_battery_limit_mode_select"
        self._attr_current_option = MODES[0]  # default mode

    async def async_select_option(self, option: str) -> None:
        """Handle option selection."""
        if option not in MODES:
            raise ValueError(f"Invalid mode: {option}")

        self._attr_current_option = option

        # TODO: Send the mode change to your Fronius API if supported
        # await self._hub.set_mode(option)

        # Tell HA state machine that we changed
        self.async_write_ha_state()
