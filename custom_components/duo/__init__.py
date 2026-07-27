"""The Duo integration - a couple's intimacy companion for Home Assistant."""

from __future__ import annotations

from pathlib import Path

import voluptuous as vol

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import (
    CATEGORIES,
    DOMAIN,
    MOOD_OPTIONS,
    SERVICE_CLEAR_PROFILE,
    SERVICE_REQUEST_SUGGESTION,
    SERVICE_RESET_SESSION,
    SERVICE_RESPOND_SUGGESTION,
    SERVICE_SET_ACCESSORIES,
    SERVICE_SET_MOOD,
    SERVICE_SET_PREFERENCE,
    SERVICE_START_TIMER,
    SERVICE_STOP_TIMER,
)
from .coordinator import DuoCoordinator

PLATFORMS = ["sensor", "select"]

# --- Carte Lovelace servie par l'intégration -------------------------------
# Le fichier custom_components/duo/frontend/duo-card.js est exposé sur
# /duo_frontend/duo-card.js puis déclaré automatiquement au frontend :
# aucune ressource Lovelace à ajouter manuellement.
URL_BASE = "/duo_frontend"
CARD_FILE = "duo-card.js"
CARD_VERSION = "0.3.0"  # à incrémenter à chaque modification du JS
FRONTEND_KEY = f"{DOMAIN}_frontend_registered"

SET_PREFERENCE_SCHEMA = vol.Schema(
    {
        vol.Required("entry_id"): cv.string,
        vol.Required("partner"): cv.string,
        vol.Required("category"): vol.In(CATEGORIES),
        vol.Required("rating"): vol.All(vol.Coerce(int), vol.Range(min=0, max=5)),
    }
)

SET_ACCESSORIES_SCHEMA = vol.Schema(
    {
        vol.Required("entry_id"): cv.string,
        vol.Required("accessories"): vol.All(cv.ensure_list, [cv.string]),
    }
)

SET_MOOD_SCHEMA = vol.Schema(
    {
        vol.Required("entry_id"): cv.string,
        # Facultatif : déduit de l'utilisateur connecté si absent.
        vol.Optional("partner"): cv.string,
        vol.Required("mood"): vol.In(MOOD_OPTIONS),
        vol.Optional("accessories"): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional("new_idea"): vol.Any(cv.string, None),
    }
)

REQUEST_SUGGESTION_SCHEMA = vol.Schema(
    {
        vol.Required("entry_id"): cv.string,
        vol.Optional("turn"): cv.string,
    }
)

RESPOND_SUGGESTION_SCHEMA = vol.Schema(
    {
        vol.Required("entry_id"): cv.string,
        vol.Required("response"): vol.In(["accepted", "declined"]),
    }
)

START_TIMER_SCHEMA = vol.Schema(
    {
        vol.Required("entry_id"): cv.string,
        vol.Optional("minutes"): vol.Coerce(float),
    }
)

ENTRY_ONLY_SCHEMA = vol.Schema({vol.Required("entry_id"): cv.string})


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Sert la carte Lovelace et la déclare au frontend (une seule fois)."""
    if hass.data.get(FRONTEND_KEY):
        return

    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                URL_BASE,
                str(Path(__file__).parent / "frontend"),
                False,
            )
        ]
    )
    add_extra_js_url(hass, f"{URL_BASE}/{CARD_FILE}?v={CARD_VERSION}")
    hass.data[FRONTEND_KEY] = True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await _async_register_frontend(hass)

    coordinator = DuoCoordinator(hass, entry)
    await coordinator.async_load()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _async_register_services(hass)

    # Recharge l'intégration quand l'association des personnes change.
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: DuoCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        coordinator.async_unload()
    return unload_ok


def _get_coordinator(hass: HomeAssistant, entry_id: str) -> DuoCoordinator:
    coordinator = hass.data.get(DOMAIN, {}).get(entry_id)
    if coordinator is None:
        raise vol.Invalid(f"Unknown Duo entry_id: {entry_id}")
    return coordinator


def _async_register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_SET_PREFERENCE):
        return

    async def handle_set_preference(call: ServiceCall) -> None:
        coordinator = _get_coordinator(hass, call.data["entry_id"])
        await coordinator.async_set_preference(
            call.data["partner"], call.data["category"], call.data["rating"]
        )

    async def handle_set_accessories(call: ServiceCall) -> None:
        coordinator = _get_coordinator(hass, call.data["entry_id"])
        await coordinator.async_set_accessories(call.data["accessories"])

    async def handle_set_mood(call: ServiceCall) -> None:
        coordinator = _get_coordinator(hass, call.data["entry_id"])
        user_id = call.context.user_id

        partner = call.data.get("partner") or coordinator.partner_for_user(user_id)
        if not partner:
            raise HomeAssistantError(
                "Impossible de déterminer le partenaire : associez votre compte "
                "Home Assistant à une personne dans les options de Duo."
            )
        if partner not in coordinator.partners:
            raise HomeAssistantError(f"Partenaire inconnu : {partner}")

        coordinator.check_mood_permission(partner, user_id)

        await coordinator.async_set_mood(
            partner,
            call.data["mood"],
            accessories=call.data.get("accessories"),
            new_idea=call.data.get("new_idea"),
        )

    async def handle_request_suggestion(call: ServiceCall) -> None:
        coordinator = _get_coordinator(hass, call.data["entry_id"])
        await coordinator.async_request_suggestion(call.data.get("turn"))

    async def handle_respond_suggestion(call: ServiceCall) -> None:
        coordinator = _get_coordinator(hass, call.data["entry_id"])
        await coordinator.async_respond_suggestion(call.data["response"])

    async def handle_start_timer(call: ServiceCall) -> None:
        coordinator = _get_coordinator(hass, call.data["entry_id"])
        await coordinator.async_start_timer(call.data.get("minutes"))

    async def handle_stop_timer(call: ServiceCall) -> None:
        coordinator = _get_coordinator(hass, call.data["entry_id"])
        await coordinator.async_stop_timer()

    async def handle_reset_session(call: ServiceCall) -> None:
        coordinator = _get_coordinator(hass, call.data["entry_id"])
        await coordinator.async_reset_session()

    async def handle_clear_profile(call: ServiceCall) -> None:
        coordinator = _get_coordinator(hass, call.data["entry_id"])
        await coordinator.async_clear_profile()

    hass.services.async_register(
        DOMAIN, SERVICE_SET_PREFERENCE, handle_set_preference, schema=SET_PREFERENCE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_ACCESSORIES, handle_set_accessories, schema=SET_ACCESSORIES_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_MOOD, handle_set_mood, schema=SET_MOOD_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REQUEST_SUGGESTION,
        handle_request_suggestion,
        schema=REQUEST_SUGGESTION_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_RESPOND_SUGGESTION,
        handle_respond_suggestion,
        schema=RESPOND_SUGGESTION_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_START_TIMER, handle_start_timer, schema=START_TIMER_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_STOP_TIMER, handle_stop_timer, schema=ENTRY_ONLY_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_RESET_SESSION, handle_reset_session, schema=ENTRY_ONLY_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_CLEAR_PROFILE, handle_clear_profile, schema=ENTRY_ONLY_SCHEMA
    )
