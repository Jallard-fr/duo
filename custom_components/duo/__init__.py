"""The Duo integration - a couple's intimacy companion for Home Assistant."""

from __future__ import annotations

import logging

from pathlib import Path

import voluptuous as vol

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.start import async_at_started
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv

from .const import (
    CATEGORIES,
    DOMAIN,
    MOOD_OPTIONS,
    PHASES,
    SERVICE_CLEAR_PROFILE,
    SERVICE_REQUEST_SUGGESTION,
    SERVICE_RESET_SESSION,
    SERVICE_RESPOND_SUGGESTION,
    SERVICE_SET_ACCESSORIES,
    SERVICE_SET_BRAVE_TABOOS,
    SERVICE_SET_MOOD,
    SERVICE_SET_PREFERENCE,
    SERVICE_START_TIMER,
    SERVICE_STOP_TIMER,
)
from .coordinator import DuoCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "select"]

# --- Carte Lovelace servie par l'intégration -------------------------------
# Le fichier custom_components/duo/frontend/duo-card.js est exposé sur
# /duo_frontend/duo-card.js puis déclaré automatiquement au frontend :
# aucune ressource Lovelace à ajouter manuellement.
URL_BASE = "/duo_frontend"
CARD_FILE = "duo-card.js"
CARD_VERSION = "0.13.0"  # à incrémenter à chaque modification du JS
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

SET_BRAVE_TABOOS_SCHEMA = vol.Schema(
    {
        vol.Required("entry_id"): cv.string,
        vol.Required("partner"): cv.string,
        vol.Required("enabled"): cv.boolean,
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
        vol.Optional("phase"): vol.In(PHASES),
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


CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

CARD_URL = f"{URL_BASE}/{CARD_FILE}?v={CARD_VERSION}"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Enregistre la carte dès le chargement du composant.

    Volontairement ici et non uniquement dans async_setup_entry : la carte
    reste disponible même si l'entrée de configuration échoue à démarrer.
    async_setup_entry appelle aussi cette fonction (elle est idempotente)
    car c'est le seul point dont on est certain qu'il s'exécute réellement
    quand une entrée Duo est configurée.
    """
    await _async_register_frontend(hass)
    async_at_started(hass, _async_register_lovelace_resource)
    return True


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Sert le fichier de la carte et le déclare au frontend (une seule fois)."""
    if hass.data.get(FRONTEND_KEY):
        return

    try:
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    URL_BASE,
                    str(Path(__file__).parent / "frontend"),
                    False,
                )
            ]
        )
        add_extra_js_url(hass, CARD_URL)
    except Exception as err:  # noqa: BLE001 - ne doit jamais bloquer le démarrage
        _LOGGER.error(
            "Duo : échec de l'enregistrement automatique de la carte (%s). "
            "Ajoutez %s manuellement dans Paramètres > Tableaux de bord > "
            "Ressources (type « Module JavaScript »).",
            err,
            f"{URL_BASE}/{CARD_FILE}",
            exc_info=True,
        )
        await _async_notify_frontend_issue(
            hass,
            "Duo n'a pas pu enregistrer sa carte automatiquement",
            f"Erreur : {err}\n\n"
            f"Ajoutez la ressource manuellement : Paramètres → Tableaux de "
            f"bord → Ressources → Ajouter une ressource, type « Module "
            f"JavaScript », URL `{URL_BASE}/{CARD_FILE}`.",
        )
        return

    hass.data[FRONTEND_KEY] = True
    _LOGGER.info("Duo : carte servie sur %s", CARD_URL)


async def _async_notify_frontend_issue(hass: HomeAssistant, title: str, message: str) -> None:
    """Rend un échec d'enregistrement visible dans l'UI, sans dépendre des journaux."""
    try:
        await hass.services.async_call(
            "persistent_notification",
            "create",
            {"title": title, "message": message, "notification_id": f"{DOMAIN}_frontend_error"},
            blocking=False,
        )
    except Exception:  # noqa: BLE001 - un échec de notification ne doit rien casser
        pass


async def _async_register_lovelace_resource(hass: HomeAssistant) -> None:
    """Déclare la carte dans les ressources Lovelace.

    Ceinture et bretelles : add_extra_js_url ne se propage pas toujours aux
    clients déjà ouverts, alors qu'une ressource enregistrée est persistante
    et visible dans Paramètres > Tableaux de bord > Ressources.
    """
    try:
        data = hass.data.get("lovelace")
        if data is None:
            return

        resources = getattr(data, "resources", None)
        if resources is None and isinstance(data, dict):
            resources = data.get("resources")

        # Mode YAML : la collection est en lecture seule, l'utilisateur gère
        # lui-même ses ressources.
        if resources is None or not hasattr(resources, "async_create_item"):
            _LOGGER.debug(
                "Duo : ressources Lovelace en lecture seule, ajoutez %s à la main",
                CARD_URL,
            )
            return

        if not getattr(resources, "loaded", True):
            await resources.async_load()
            resources.loaded = True

        base = f"{URL_BASE}/{CARD_FILE}"
        for item in resources.async_items():
            url = str(item.get("url", ""))
            if url.split("?")[0] != base:
                continue
            if url != CARD_URL:
                await resources.async_update_item(item["id"], {"url": CARD_URL})
                _LOGGER.info("Duo : ressource Lovelace mise à jour (%s)", CARD_URL)
            return

        await resources.async_create_item({"res_type": "module", "url": CARD_URL})
        _LOGGER.info("Duo : ressource Lovelace créée (%s)", CARD_URL)
    except Exception as err:  # noqa: BLE001 - ne doit jamais bloquer le démarrage
        _LOGGER.warning(
            "Duo : impossible d'enregistrer la ressource Lovelace (%s). "
            "Ajoutez %s manuellement dans Paramètres > Tableaux de bord > Ressources.",
            err,
            CARD_URL,
            exc_info=True,
        )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Refait ici, en plus de async_setup : c'est le seul point dont on est
    # certain qu'il s'exécute chaque fois qu'une entrée Duo est chargée.
    # _async_register_frontend est idempotente (elle ressort tout de suite
    # si déjà enregistrée avec succès).
    await _async_register_frontend(hass)
    async_at_started(hass, _async_register_lovelace_resource)

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

    async def handle_set_brave_taboos(call: ServiceCall) -> None:
        coordinator = _get_coordinator(hass, call.data["entry_id"])
        await coordinator.async_set_brave_taboos(call.data["partner"], call.data["enabled"])

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
        await coordinator.async_request_suggestion(
            call.data.get("turn"), call.data.get("phase")
        )

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
        DOMAIN,
        SERVICE_SET_BRAVE_TABOOS,
        handle_set_brave_taboos,
        schema=SET_BRAVE_TABOOS_SCHEMA,
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
