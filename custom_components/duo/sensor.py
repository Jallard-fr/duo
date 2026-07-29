"""Sensor platform for Duo."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .accessories import (
    ACCESSORY_CATALOG,
    ACCESSORY_CATEGORY_LABELS,
    ACCESSORY_LABELS,
    accessory_categories_as_list,
)
from .const import (
    CATEGORY_LABELS,
    DOMAIN,
    PHASE_LABELS,
    POSITION_LABELS,
    SEX_FEMME,
    SEX_HOMME,
    SEX_LABELS,
    SIGNAL_UPDATE,
    STATUS_IDLE,
)
from .coordinator import DuoCoordinator


def _oral_label(sex: str | None) -> str:
    """Libellé de l'acte oral selon le sexe de la personne qui le reçoit
    (fellation pour un homme, cunnilingus pour une femme), générique sinon
    — même logique que oralLabel() côté carte pour le questionnaire de
    limites."""
    if sex == SEX_HOMME:
        return "une fellation"
    if sex == SEX_FEMME:
        return "un cunnilingus"
    return "une stimulation orale"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: DuoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            DuoSuggestionSensor(coordinator, entry),
            DuoTimerSensor(coordinator, entry),
            DuoHistorySensor(coordinator, entry),
            DuoEveningSensor(coordinator, entry),
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
        actor = self.coordinator.current_turn
        receiver = self.coordinator.other_partner(actor) if actor else None
        accessory = activity.get("accessory")
        phase = activity.get("phase")
        position = activity.get("position")

        if accessory and "id" in accessory:
            accessory_value = accessory["id"]
            accessory_label = ACCESSORY_LABELS.get(accessory_value, accessory_value)
        elif accessory:
            accessory_value = accessory.get("category")
            accessory_label = "Un accessoire « {} »".format(
                ACCESSORY_CATEGORY_LABELS.get(accessory_value, accessory_value)
            )
        else:
            accessory_value = None
            accessory_label = None

        # Le nom réel des partenaires (déjà connu, voir CONF_PARTNER1/2) est
        # substitué ici dans la description, pour personnaliser l'expérience
        # sans jamais afficher les mots "acteur"/"récepteur" — ce vocabulaire
        # technique reste interne (filtrage par sexe, etc.). Le titre reste
        # le nom brut de l'activité : l'accessoire à utiliser, s'il y en a
        # un, se retrouve dans le texte de la description, pas dans le titre.
        title = activity["name"]

        description = activity["description"]
        if actor and receiver:
            description = description.format(
                actor=actor,
                receiver=receiver,
                oral_on_receiver=_oral_label(self.coordinator.sex_of(receiver)),
                oral_on_actor=_oral_label(self.coordinator.sex_of(actor)),
            )
        if accessory_label:
            description = f"{description} (avec {accessory_label})"

        return {
            "status": self.coordinator.current_status,
            "turn": actor,
            "title": title,
            "category": CATEGORY_LABELS.get(activity["category"], activity["category"]),
            "phase": phase,
            "phase_label": PHASE_LABELS.get(phase, phase),
            "description": description,
            "intensity": activity["intensity"],
            "duration_mode": activity.get("duration_mode", "time"),
            "duration_minutes": activity.get("duration_minutes"),
            "count": self.coordinator.current_count,
            "count_unit": activity.get("count_unit"),
            "position": position,
            "position_label": POSITION_LABELS.get(position),
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


class DuoEveningSensor(DuoEntityBase):
    """Expose l'état de la soirée : humeurs, accessoires, idées, mapping."""

    _attr_translation_key = "evening"
    _attr_icon = "mdi:weather-night"

    def __init__(self, coordinator: DuoCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_evening"

    @property
    def native_value(self) -> str:
        """Résumé lisible : les deux émoticônes d'humeur."""
        return " ".join(
            self.coordinator.evening_state(partner)["emoji"]
            for partner in self.coordinator.partners
        )

    @property
    def extra_state_attributes(self) -> dict:
        partners = self.coordinator.partners
        return {
            "partners": partners,
            "states": {
                partner: self.coordinator.evening_state(partner)
                for partner in partners
            },
            "available_accessories": list(
                self.coordinator.profile.get("accessories", [])
            ),
            # Catalogue de référence exposé ici pour que la carte n'ait pas
            # sa propre copie du contenu : accessories.py reste la seule
            # source de vérité, la carte se contente de le lire.
            "accessory_catalog": ACCESSORY_CATALOG,
            "accessory_categories": accessory_categories_as_list(),
            "mapping_configured": self.coordinator.mapping_configured,
            "entry_id": self.entry.entry_id,
            # Sexe de chaque partenaire, pour que la carte adapte le libellé
            # de ses questions (ex. fellation/cunnilingus selon le sexe
            # concerné) sans dupliquer cette donnée côté frontend.
            "partner_sex": {
                partner: SEX_LABELS.get(self.coordinator.sex_of(partner))
                for partner in partners
            },
            # Progression guidée par niveau (= phase).
            "session_phase": self.coordinator.session_phase,
            "session_phase_label": PHASE_LABELS.get(
                self.coordinator.session_phase, self.coordinator.session_phase
            ),
        }
