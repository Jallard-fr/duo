"""Runtime state and persistence for the Duo integration."""

from __future__ import annotations

import copy
import logging
import random
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_change, async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util, slugify

from .accessories import ACCESSORY_LABELS, accessory_matches_sex, owned_item_in_category
from .activities import ACTIVITIES, get_activity
from .const import (
    CONF_NOTIFY1,
    CONF_NOTIFY2,
    CONF_PARTNER1,
    CONF_PARTNER1_SEX,
    CONF_PARTNER2,
    CONF_PARTNER2_SEX,
    CONF_PERSON1,
    CONF_PERSON2,
    DECLINE_COOLDOWN_DAYS,
    DEFAULT_PROFILE,
    LEVEL_TARGET_COUNT,
    MAX_ACTIVITY_MINUTES,
    MAX_REROLLS,
    MOOD_EMOJI,
    MOOD_INTENSITY,
    MOOD_LABELS,
    MOOD_NOT_TONIGHT,
    MOOD_NOVELTY,
    NEW_IDEA_UNKNOWN,
    NEW_IDEA_UNKNOWN_LABEL,
    PHASE_EXCITATION,
    PHASES,
    PRACTICE_ANSWER_NON,
    PRACTICE_ANSWER_OUI,
    PRACTICE_JOUETS,
    SEX_INDIFFERENT,
    SIGNAL_UPDATE,
    STATUS_ACCEPTED,
    STATUS_COMPLETED,
    STATUS_DECLINED,
    STATUS_IDLE,
    STATUS_IN_PROGRESS,
    STATUS_PROPOSED,
    STORAGE_VERSION,
    mood_gauge,
)

_LOGGER = logging.getLogger(__name__)


class DuoCoordinator:
    """Holds the couple's profile and the state of the current session."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        self.hass = hass
        self.entry = entry
        self.store: Store = Store(hass, STORAGE_VERSION, f"duo_{entry.entry_id}")
        self.profile: dict = copy.deepcopy(DEFAULT_PROFILE)

        self.current_suggestion: dict | None = None
        self.current_status: str = STATUS_IDLE
        self.current_turn: str | None = None

        self.timer_total_seconds: int = 0
        self.timer_remaining_seconds: int = 0
        self.timer_running: bool = False
        self._timer_unsub = None
        self._midnight_unsub = None

        # Progression guidée par niveau (= phase) : chaque partenaire doit
        # accepter LEVEL_TARGET_COUNT activités de la phase en cours avant
        # qu'elle ne passe automatiquement à la suivante. Volontairement pas
        # persisté : une nouvelle session repart de la phase Excitation.
        self.session_phase: str = PHASE_EXCITATION
        self.phase_progress: dict[str, int] = {}
        self._reroll_count: int = 0
        self._last_phase: str | None = None

    @property
    def partners(self) -> list[str]:
        return [self.entry.data[CONF_PARTNER1], self.entry.data[CONF_PARTNER2]]

    def other_partner(self, partner: str) -> str:
        partners = self.partners
        if partner == partners[0]:
            return partners[1]
        return partners[0]

    def sex_of(self, partner: str) -> str:
        partners = self.partners
        if partner == partners[0]:
            return self.entry.data[CONF_PARTNER1_SEX]
        return self.entry.data[CONF_PARTNER2_SEX]

    # ------------------------------------------------------------------
    # Association partenaire <-> personne Home Assistant
    # ------------------------------------------------------------------

    def person_entity_for(self, partner: str) -> str | None:
        """Entité person.* associée au partenaire, si configurée."""
        key = CONF_PERSON1 if partner == self.partners[0] else CONF_PERSON2
        value = self.entry.options.get(key) or self.entry.data.get(key)
        return value or None

    def user_id_for(self, partner: str) -> str | None:
        """Identifiant d'utilisateur HA associé au partenaire."""
        entity_id = self.person_entity_for(partner)
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        return state.attributes.get("user_id")

    def partner_for_user(self, user_id: str | None) -> str | None:
        """Partenaire correspondant à un utilisateur HA connecté."""
        if not user_id:
            return None
        for partner in self.partners:
            if self.user_id_for(partner) == user_id:
                return partner
        return None

    @property
    def mapping_configured(self) -> bool:
        """Vrai si au moins un partenaire est associé à une personne."""
        return any(self.person_entity_for(p) for p in self.partners)

    def check_partner_permission(
        self, partner: str, user_id: str | None, *, what: str = "cette action"
    ) -> None:
        """Vérifie qu'un utilisateur a le droit d'agir au nom de `partner`.

        - user_id None : appel interne (automatisation, réinitialisation) → autorisé.
        - Aucune association configurée → autorisé (compatibilité ascendante,
          carte utilisée sans compte HA individuel par partenaire).
        - Sinon, seul le propriétaire de l'entrée peut agir en son nom : ni
          l'humeur, ni les préférences, ni les limites d'un partenaire ne
          sont modifiables par l'autre.
        """
        if user_id is None or not self.mapping_configured:
            return
        owner = self.user_id_for(partner)
        if owner is None:
            return
        if owner != user_id:
            raise HomeAssistantError(
                f"Seul·e {partner} peut modifier {what}. "
                "Chacun gère uniquement ce qui le concerne."
            )

    def check_mood_permission(self, partner: str, user_id: str | None) -> None:
        self.check_partner_permission(partner, user_id, what="son humeur")

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    def notify_services_for(self, partner: str) -> list[str]:
        """Services notify.* couvrant tous les appareils du partenaire."""
        key = CONF_NOTIFY1 if partner == self.partners[0] else CONF_NOTIFY2
        manual = (self.entry.options.get(key) or "").strip()
        if manual:
            return [
                s.strip().replace("notify.", "")
                for s in manual.split(",")
                if s.strip()
            ]

        user_id = self.user_id_for(partner)
        if not user_id:
            return []

        services: list[str] = []
        for entry in self.hass.config_entries.async_entries("mobile_app"):
            if entry.data.get("user_id") != user_id:
                continue
            device_name = entry.data.get("device_name")
            if not device_name:
                continue
            service = f"mobile_app_{slugify(device_name)}"
            if self.hass.services.has_service("notify", service):
                services.append(service)
        return services

    async def async_load(self) -> None:
        stored = await self.store.async_load()
        if stored:
            self.profile.update(stored)
        for partner in self.partners:
            self.profile.setdefault("preferences", {}).setdefault(partner, {})
            self.profile.setdefault("moods", {}).setdefault(partner, MOOD_NOT_TONIGHT)
            self.profile.setdefault("evening", {}).setdefault(partner, {})
            self.profile.setdefault("brave_taboos", {}).setdefault(partner, False)
            self.profile.setdefault("practice_limits", {}).setdefault(partner, {})

        # Remise à zéro automatique chaque nuit à minuit (heure locale).
        self._midnight_unsub = async_track_time_change(
            self.hass, self._async_midnight_reset, hour=0, minute=0, second=0
        )

    async def async_save(self) -> None:
        await self.store.async_save(self.profile)

    @callback
    def _signal(self) -> None:
        async_dispatcher_send(self.hass, SIGNAL_UPDATE.format(entry_id=self.entry.entry_id))

    async def async_set_preference(self, partner: str, category: str, rating: int) -> None:
        self.profile.setdefault("preferences", {}).setdefault(partner, {})[category] = rating
        await self.async_save()
        self._signal()

    async def async_set_accessories(self, accessories: list[str]) -> None:
        self.profile["accessories"] = list(accessories)
        await self.async_save()
        self._signal()

    def brave_taboos(self, partner: str) -> bool:
        return bool(self.profile.get("brave_taboos", {}).get(partner, False))

    async def async_set_brave_taboos(self, partner: str, enabled: bool) -> None:
        """Un partenaire qui active ce mode redevient éligible aux catégories
        qu'il a mises à 0 et aux activités en cooldown, jusqu'à ce qu'il le
        désactive à nouveau."""
        self.profile.setdefault("brave_taboos", {})[partner] = bool(enabled)
        await self.async_save()
        self._signal()

    async def async_set_practice_limit(self, partner: str, key: str, answer: str) -> None:
        """Enregistre la réponse d'un partenaire à une question de limite
        (ex. key="oral_donne", answer="non") — voir practice_* dans
        activities.py pour la façon dont ça filtre les suggestions."""
        self.profile.setdefault("practice_limits", {}).setdefault(partner, {})[key] = answer
        await self.async_save()
        self._signal()

    async def async_set_mood(
        self,
        partner: str,
        mood: str,
        accessories: list[str] | None = None,
        new_idea: str | None = None,
        notify: bool = True,
    ) -> None:
        """Enregistre l'humeur du soir d'un partenaire et prévient l'autre."""
        previous = self.profile.setdefault("moods", {}).get(partner)
        evening = self.profile.setdefault("evening", {}).setdefault(partner, {})
        previous_evening = dict(evening)

        self.profile["moods"][partner] = mood

        # L'envie de nouveauté est la seule à porter une idée libre.
        if mood != MOOD_NOVELTY:
            new_idea = None

        evening["accessories"] = list(accessories or [])
        evening["new_idea"] = new_idea
        evening["updated"] = dt_util.now().isoformat(timespec="seconds")

        await self.async_save()
        self._signal()

        changed = (
            previous != mood
            or previous_evening.get("accessories") != evening["accessories"]
            or previous_evening.get("new_idea") != evening["new_idea"]
        )
        if notify and changed:
            await self._async_notify_partner(partner, mood, evening)

    def evening_state(self, partner: str) -> dict:
        """État de la soirée pour un partenaire, prêt à être exposé."""
        mood = self.profile.get("moods", {}).get(partner, MOOD_NOT_TONIGHT)
        evening = self.profile.get("evening", {}).get(partner, {})
        new_idea = evening.get("new_idea")
        return {
            "mood": mood,
            "mood_label": MOOD_LABELS.get(mood, mood),
            "emoji": MOOD_EMOJI.get(mood, ""),
            "intensity": MOOD_INTENSITY.get(mood, 0),
            "gauge": mood_gauge(mood),
            "accessories": list(evening.get("accessories") or []),
            "new_idea": new_idea,
            "new_idea_label": (
                NEW_IDEA_UNKNOWN_LABEL if new_idea == NEW_IDEA_UNKNOWN else new_idea
            ),
            "updated": evening.get("updated"),
            "person": self.person_entity_for(partner),
            "user_id": self.user_id_for(partner),
            "brave_taboos": self.brave_taboos(partner),
            "phase_progress": self.phase_progress.get(partner, 0),
            "phase_target": LEVEL_TARGET_COUNT,
        }

    def _build_notification(self, partner: str, mood: str, evening: dict) -> tuple[str, str]:
        """Titre et corps du message envoyé à l'autre partenaire."""
        emoji = MOOD_EMOJI.get(mood, "")
        label = MOOD_LABELS.get(mood, mood)
        title = f"Duo 💞 — {partner}"

        lines = [f"{emoji} {partner} : {label}", mood_gauge(mood)]

        accessories = evening.get("accessories") or []
        if accessories:
            labels = [ACCESSORY_LABELS.get(item, item) for item in accessories]
            lines.append("🧺 Accessoires proposés : " + ", ".join(labels))

        if mood == MOOD_NOVELTY:
            idea = evening.get("new_idea")
            if idea == NEW_IDEA_UNKNOWN or not idea:
                lines.append(f"✨ {NEW_IDEA_UNKNOWN_LABEL}")
            else:
                lines.append(f"✨ Idée en tête : {idea}")

        return title, "\n".join(lines)

    async def _async_notify_partner(self, partner: str, mood: str, evening: dict) -> None:
        """Diffuse l'humeur à tous les appareils de l'autre partenaire."""
        target = self.other_partner(partner)
        services = self.notify_services_for(target)
        if not services:
            _LOGGER.debug(
                "Duo : aucun appareil de notification trouvé pour %s", target
            )
            return

        title, message = self._build_notification(partner, mood, evening)
        payload = {
            "title": title,
            "message": message,
            "data": {
                "channel": "Duo",
                "importance": "high",
                # Masque le contenu sur l'écran verrouillé (Android).
                "visibility": "private",
                "notification_icon": "mdi:heart",
                "tag": f"duo_mood_{slugify(partner)}",
            },
        }

        for service in services:
            try:
                await self.hass.services.async_call(
                    "notify", service, payload, blocking=False
                )
            except Exception:  # noqa: BLE001 - un appareil absent ne doit rien casser
                _LOGGER.warning("Duo : échec de notification via notify.%s", service)

    @callback
    def _async_midnight_reset(self, _now) -> None:
        """Remet les humeurs et la soirée à zéro chaque nuit, sans notifier."""
        self.hass.async_create_task(self._async_do_midnight_reset())

    async def _async_do_midnight_reset(self) -> None:
        for partner in self.partners:
            self.profile.setdefault("moods", {})[partner] = MOOD_NOT_TONIGHT
            self.profile.setdefault("evening", {})[partner] = {
                "accessories": [],
                "new_idea": None,
                "updated": None,
            }
        await self.async_save()
        # Nouvelle soirée : la progression guidée repart de la phase Excitation.
        self.session_phase = PHASE_EXCITATION
        self.phase_progress = {}
        await self.async_reset_session()
        _LOGGER.debug("Duo : humeurs réinitialisées (minuit)")

    def _is_on_cooldown(self, activity_id: str) -> bool:
        declined_at = self.profile.get("declined", {}).get(activity_id)
        if not declined_at:
            return False
        try:
            declined_dt = dt_util.parse_datetime(declined_at)
        except (ValueError, TypeError):
            return False
        if declined_dt is None:
            return False
        return dt_util.utcnow() - declined_dt < timedelta(days=DECLINE_COOLDOWN_DAYS)

    def _accessory_usable(self, accessory: dict, actor_sex: str, receiver_sex: str) -> bool:
        """Owned, and compatible with the current actor/receiver sex pairing
        (e.g. an accessory meant to be worn by a female actor is not usable
        for a turn where the actor is a man). `accessory` is either
        {"id": ...} for one specific catalog entry, or {"category": ...} to
        match any owned item from that whole family (e.g. any vibrant toy)."""
        owned = self.profile.get("accessories", [])
        if "id" in accessory:
            accessory_id = accessory["id"]
            return accessory_id in owned and accessory_matches_sex(accessory_id, actor_sex, receiver_sex)
        category = accessory.get("category")
        return owned_item_in_category(owned, category, actor_sex, receiver_sex) is not None

    def _rating_for(self, partner: str, category: str) -> float:
        """Note de préférence (0-5) d'un partenaire pour une catégorie. Une
        note à 0 signifie "jamais" — sauf si ce partenaire a activé le mode
        "braver ses interdits", auquel cas la catégorie redevient possible,
        avec une note neutre plutôt que privilégiée."""
        rating = self.profile.get("preferences", {}).get(partner, {}).get(category, 3)
        if rating <= 0:
            return 2.0 if self.brave_taboos(partner) else 0.0
        return float(rating)

    def _weight_for(self, activity: dict, proposer: str, actor_sex: str, receiver_sex: str) -> float:
        """Score an activity from the point of view of the partner proposing it."""
        weight = self._rating_for(proposer, activity["category"])
        accessory = activity.get("accessory")
        if accessory and not self._accessory_usable(accessory, actor_sex, receiver_sex):
            # Un accessoire requis et manquant/incompatible est déjà exclu
            # par _matches_accessory ; ici on ne gère que le cas "conseillé
            # mais pas indispensable", qui reste possible mais moins probable.
            weight *= 0.4
        if self._is_on_cooldown(activity["id"]):
            mood = self.profile.get("moods", {}).get(proposer)
            if mood == MOOD_NOVELTY or self.brave_taboos(proposer):
                weight *= 1.0
            else:
                weight *= 0.05
        return weight

    def _matches_sex(self, activity: dict, actor_sex: str, receiver_sex: str) -> bool:
        activity_actor_sex = activity.get("actor_sex", SEX_INDIFFERENT)
        activity_receiver_sex = activity.get("receiver_sex", SEX_INDIFFERENT)
        actor_ok = activity_actor_sex in (SEX_INDIFFERENT, actor_sex)
        receiver_ok = activity_receiver_sex in (SEX_INDIFFERENT, receiver_sex)
        return actor_ok and receiver_ok

    def _matches_accessory(self, activity: dict, actor_sex: str, receiver_sex: str) -> bool:
        accessory = activity.get("accessory")
        if not accessory:
            return True
        if not accessory.get("required", True):
            return True
        return self._accessory_usable(accessory, actor_sex, receiver_sex)

    def _matches_preference(self, activity: dict, proposer: str) -> bool:
        """Note à 0 = catégorie exclue pour ce partenaire (questionnaire),
        sauf s'il a débloqué ses interdits."""
        return self._rating_for(proposer, activity["category"]) > 0

    def _practice_refused(self, partner: str, practice: str, role: str) -> bool:
        answer = (
            self.profile.get("practice_limits", {})
            .get(partner, {})
            .get(f"{practice}_{role}", PRACTICE_ANSWER_OUI)
        )
        return answer == PRACTICE_ANSWER_NON and not self.brave_taboos(partner)

    def _matches_practice_limits(self, activity: dict, actor: str, receiver: str) -> bool:
        """Un "non" au questionnaire de limites exclut l'activité
        correspondante (voir practice_* dans activities.py), sauf pour le
        partenaire qui a activé "braver ses interdits"."""
        practice = activity.get("practice")
        if not practice:
            return True
        if practice == PRACTICE_JOUETS:
            # Pratique symétrique : un "non" de l'un ou l'autre suffit à exclure.
            return not (
                self._practice_refused(actor, practice, "usage")
                or self._practice_refused(receiver, practice, "usage")
            )
        return not (
            self._practice_refused(actor, practice, "donne")
            or self._practice_refused(receiver, practice, "recoit")
        )

    def _matches_phase(self, activity: dict, phase: str | None) -> bool:
        if not phase:
            return True
        return activity.get("phase") == phase

    async def async_request_suggestion(
        self,
        turn: str | None = None,
        phase: str | None = None,
        *,
        _is_reroll: bool = False,
    ) -> dict:
        """Pick a new activity and propose it to `turn` (the partner performing it,
        i.e. the actor). The other partner is the receiver. `phase` optionally
        restricts the pick to a specific moment of the encounter (see PHASE_*
        in const.py); if omitted, the current guided level (`session_phase`)
        is used instead of picking from the whole catalog at random."""
        partners = self.partners
        if turn not in partners:
            turn = random.choice(partners)
        proposer = self.other_partner(turn)
        actor_sex = self.sex_of(turn)
        receiver_sex = self.sex_of(proposer)
        effective_phase = phase or self.session_phase

        if not _is_reroll:
            self._reroll_count = 0

        def _eligible(activity: dict, *, with_phase: bool) -> bool:
            return (
                self._matches_sex(activity, actor_sex, receiver_sex)
                and self._matches_accessory(activity, actor_sex, receiver_sex)
                and self._matches_preference(activity, proposer)
                and self._matches_practice_limits(activity, turn, proposer)
                and (self._matches_phase(activity, effective_phase) if with_phase else True)
            )

        candidates = [a for a in ACTIVITIES if _eligible(a, with_phase=True)]
        if not candidates:
            # Pas de candidat pour cette phase précise (accessoires manquants,
            # sexe acteur/récepteur, catégorie exclue...) : on élargit en
            # ignorant la phase plutôt que de ne rien proposer.
            candidates = [a for a in ACTIVITIES if _eligible(a, with_phase=False)]
        if not candidates:
            # Filet de sécurité : ne jamais se retrouver sans aucun candidat,
            # par ex. si le catalogue a été personnalisé de façon trop stricte.
            candidates = ACTIVITIES

        weights = [
            self._weight_for(activity, proposer, actor_sex, receiver_sex)
            for activity in candidates
        ]
        if sum(weights) <= 0:
            weights = [1.0 for _ in candidates]

        activity = random.choices(candidates, weights=weights, k=1)[0]

        self.current_suggestion = activity
        self.current_status = STATUS_PROPOSED
        self.current_turn = turn
        self._last_phase = effective_phase
        self._signal()
        return activity

    async def async_respond_suggestion(self, response: str) -> None:
        if not self.current_suggestion:
            return
        activity = self.current_suggestion

        if response == "accepted":
            self.current_status = STATUS_ACCEPTED
            self.profile.get("declined", {}).pop(activity["id"], None)
            await self._async_log_history(activity, response)
            self._reroll_count = 0
            self._async_register_level_progress(activity)
            await self.async_start_timer()
        else:
            self.current_status = STATUS_DECLINED
            self.profile.setdefault("declined", {})[activity["id"]] = dt_util.utcnow().isoformat()
            await self._async_log_history(activity, response)
            await self.async_save()
            self._signal()

            self._reroll_count += 1
            if self._reroll_count <= MAX_REROLLS:
                await self.async_request_suggestion(
                    turn=self.current_turn, phase=self._last_phase, _is_reroll=True
                )
            # Au-delà de MAX_REROLLS refus d'affilée, on laisse la main au
            # couple plutôt que d'insister automatiquement.

    def _async_register_level_progress(self, activity: dict) -> None:
        """Comptabilise une activité acceptée pour la progression de niveau,
        uniquement si elle correspond à la phase guidée en cours (une
        activité choisie manuellement sur une autre phase n'y contribue
        pas)."""
        if activity.get("phase") != self.session_phase:
            return
        actor = self.current_turn
        self.phase_progress[actor] = self.phase_progress.get(actor, 0) + 1
        if all(self.phase_progress.get(p, 0) >= LEVEL_TARGET_COUNT for p in self.partners):
            self._advance_session_phase()

    def _advance_session_phase(self) -> None:
        try:
            index = PHASES.index(self.session_phase)
        except ValueError:
            index = -1
        if index + 1 < len(PHASES):
            self.session_phase = PHASES[index + 1]
        # Déjà à la dernière phase (résolution) : on y reste, la soirée est
        # "complète" — rien de plus à avancer automatiquement.
        self.phase_progress = {}

    async def _async_log_history(self, activity: dict, response: str) -> None:
        history = self.profile.setdefault("history", [])
        history.append(
            {
                "activity_id": activity["id"],
                "name": activity["name"],
                "response": response,
                "turn": self.current_turn,
                "timestamp": dt_util.utcnow().isoformat(),
            }
        )
        del history[:-50]  # keep the last 50 entries only
        await self.async_save()

    def _effective_duration_minutes(self, activity: dict) -> float:
        """Durée du minuteur, en minutes. Pour une activité quantifiée en
        nombre d'actions plutôt qu'en temps, on dérive une durée indicative
        (~4 s par action) juste pour garder le même minuteur/bips sonores,
        sans jamais dépasser MAX_ACTIVITY_MINUTES."""
        if activity.get("duration_mode") == "count":
            count = random.randint(activity["count_min"], activity["count_max"])
            seconds = max(20, min(count * 4, MAX_ACTIVITY_MINUTES * 60))
            return seconds / 60
        return random.uniform(activity["duration_min"], activity["duration_max"])

    async def async_start_timer(self, minutes: float | None = None) -> None:
        if not self.current_suggestion:
            return
        activity = self.current_suggestion
        if minutes is None:
            minutes = self._effective_duration_minutes(activity)

        self.timer_total_seconds = int(minutes * 60)
        self.timer_remaining_seconds = self.timer_total_seconds
        self.timer_running = True
        self.current_status = STATUS_IN_PROGRESS
        self._signal()

        self._async_cancel_timer()
        self._timer_unsub = async_track_time_interval(
            self.hass, self._async_timer_tick, timedelta(seconds=1)
        )

    @callback
    def _async_timer_tick(self, _now) -> None:
        if not self.timer_running:
            return
        self.timer_remaining_seconds = max(0, self.timer_remaining_seconds - 1)
        if self.timer_remaining_seconds <= 0:
            self.timer_running = False
            self.current_status = STATUS_COMPLETED
            self._async_cancel_timer()
        self._signal()

    def _async_cancel_timer(self) -> None:
        if self._timer_unsub:
            self._timer_unsub()
            self._timer_unsub = None

    async def async_stop_timer(self) -> None:
        self.timer_running = False
        self._async_cancel_timer()
        self._signal()

    async def async_reset_session(self) -> None:
        self.current_suggestion = None
        self.current_status = STATUS_IDLE
        self.current_turn = None
        self.timer_total_seconds = 0
        self.timer_remaining_seconds = 0
        self.timer_running = False
        self._reroll_count = 0
        self._async_cancel_timer()
        self._signal()

    async def async_clear_profile(self) -> None:
        self.profile = copy.deepcopy(DEFAULT_PROFILE)
        for partner in self.partners:
            self.profile["preferences"][partner] = {}
            self.profile["moods"][partner] = MOOD_NOT_TONIGHT
            self.profile["evening"][partner] = {}
            self.profile["brave_taboos"][partner] = False
            self.profile["practice_limits"][partner] = {}
        self.session_phase = PHASE_EXCITATION
        self.phase_progress = {}
        await self.async_save()
        await self.async_reset_session()

    def async_unload(self) -> None:
        self._async_cancel_timer()
        if self._midnight_unsub:
            self._midnight_unsub()
            self._midnight_unsub = None
