"""Sensor platform for Duo."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CATEGORY_LABELS, DOMAIN, SIGNAL_UPDATE, STATUS_IDLE
from .coordinator import DuoCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: DuoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            DuoSuggestionSensor(coordinator, entry),
            DuoTimerSensor(coordinator, entry),
            DuoHistorySensor(coordinator, entry),
        ]
    )


class DuoEntityBase(SensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator: DuoCoordinator, entry: ConfigEntry) -> None:
        self.coordinator = coordinator
        self.entry = entry
        self._unsub = None

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.entry.title,
            manufacturer="Duo",
            model="Couple companion",
        )

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


class DuoSuggestionSensor(DuoEntityBase):
    _attr_translation_key = "current_suggestion"
    _attr_icon = "mdi:heart-flash"

    def __init__(self, coordinator: DuoCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_current_suggestion"

    @property
    def native_value(self) -> str:
        if not self.coordinator.current_suggestion:
            return "Aucune suggestion"
        return self.coordinator.current_suggestion["name"]

    @property
    def extra_state_attributes(self) -> dict:
        activity = self.coordinator.current_suggestion
        if not activity:
            return {"status": STATUS_IDLE}
        return {
            "status": self.coordinator.current_status,
            "turn": self.coordinator.current_turn,
            "category": CATEGORY_LABELS.get(activity["category"], activity["category"]),
            "description": activity["description"],
            "intensity": activity["intensity"],
            "duration_min": activity["duration_min"],
            "duration_max": activity["duration_max"],
            "accessory": activity.get("accessory"),
            "reminder": "Chacun peut refuser à tout moment, sans justification.",
        }


class DuoTimerSensor(DuoEntityBase):
    _attr_translation_key = "timer"
    _attr_icon = "mdi:timer-sand"
    _attr_native_unit_of_measurement = "s"

    def __init__(self, coordinator: DuoCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_timer"

    @property
    def native_value(self) -> int:
        return self.coordinator.timer_remaining_seconds

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "running": self.coordinator.timer_running,
            "total_seconds": self.coordinator.timer_total_seconds,
        }


class DuoHistorySensor(DuoEntityBase):
    _attr_translation_key = "history"
    _attr_icon = "mdi:history"

    def __init__(self, coordinator: DuoCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_history"

    @property
    def native_value(self) -> int:
        return len(self.coordinator.profile.get("history", []))

    @property
    def extra_state_attributes(self) -> dict:
        history = self.coordinator.profile.get("history", [])
        return {"last_entries": history[-10:]}
