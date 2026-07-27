"""The Duo integration - a couple's intimacy companion for Home Assistant."""
from pathlib import Path
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig

URL_BASE = "/duo_frontend"
CARD_FILE = "duo-card.js"
CARD_VERSION = "0.1.0"
FRONTEND_KEY = f"{DOMAIN}_frontend_registered"

await _async_register_frontend(hass)

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
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
        vol.Required("partner"): cv.string,
        vol.Required("mood"): vol.In(MOOD_OPTIONS),
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


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = DuoCoordinator(hass, entry)
    await coordinator.async_load()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _async_register_services(hass)

    return True


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
        await coordinator.async_set_mood(call.data["partner"], call.data["mood"])

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
    async def _async_register_frontend(hass: HomeAssistant) -> None:
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
