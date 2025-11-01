from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Fronius Web API sensors."""
    hub = hass.data[DOMAIN][entry.entry_id]

    # Example: create one placeholder sensor
    async_add_entities([FroniusPlaceholderSensor(hub)], True)


class FroniusPlaceholderSensor(SensorEntity):
    """A simple example sensor."""

    def __init__(self, hub) -> None:
        self._hub = hub
        self._attr_name = "Fronius Example Sensor"
        self._attr_unique_id = "fronius_example_sensor"

    @property
    def native_value(self) -> int:
        """Return some dummy data for now."""
        return 42
