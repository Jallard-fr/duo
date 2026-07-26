"""Select platform for Duo (mood selector per partner)."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MOOD_LABELS, MOOD_NOT_TONIGHT, MOOD_OPTIONS, SIGNAL_UPDATE
from .coordinator import DuoCoordinator

MOOD_LABEL_TO_KEY = {label: key for key, label in MOOD_LABELS.items()}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: DuoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DuoMoodSelect(coordinator, entry, partner) for partner in coordinator.partners
    )


class DuoMoodSelect(SelectEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_icon = "mdi:emoticon-outline"
    _attr_options = [MOOD_LABELS[key] for key in MOOD_OPTIONS]

    def __init__(self, coordinator: DuoCoordinator, entry: ConfigEntry, partner: str) -> None:
        self.coordinator = coordinator
        self.entry = entry
        self.partner = partner
        self._attr_unique_id = f"{entry.entry_id}_mood_{partner}"
        self._attr_name = f"Humeur de {partner}"
        self._unsub = None

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.entry.title,
            manufacturer="Duo",
            model="Couple companion",
        )

    @property
    def current_option(self) -> str:
        mood_key = self.coordinator.profile.get("moods", {}).get(self.partner, MOOD_NOT_TONIGHT)
        return MOOD_LABELS.get(mood_key, MOOD_LABELS[MOOD_NOT_TONIGHT])

    async def async_select_option(self, option: str) -> None:
        mood_key = MOOD_LABEL_TO_KEY.get(option, MOOD_NOT_TONIGHT)
        await self.coordinator.async_set_mood(self.partner, mood_key)

    async def async_added_to_hass(self) -> None:
        self._unsub = async_dispatcher_connect(
            self.hass,
            SIGNAL_UPDATE.format(entry_id=self.entry.entry_id),
            self._handle_update,
        )

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()

    @callback
    def _handle_update(self) -> None:
        self.async_write_ha_state()
