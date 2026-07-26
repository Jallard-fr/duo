"""Runtime state and persistence for the Duo integration."""

from __future__ import annotations

import copy
import logging
import random
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .activities import ACTIVITIES, get_activity
from .const import (
    CONF_PARTNER1,
    CONF_PARTNER2,
    DECLINE_COOLDOWN_DAYS,
    DEFAULT_PROFILE,
    MOOD_NOT_TONIGHT,
    MOOD_NOVELTY,
    SIGNAL_UPDATE,
    STATUS_ACCEPTED,
    STATUS_COMPLETED,
    STATUS_DECLINED,
    STATUS_IDLE,
    STATUS_IN_PROGRESS,
    STATUS_PROPOSED,
    STORAGE_VERSION,
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

    @property
    def partners(self) -> list[str]:
        return [self.entry.data[CONF_PARTNER1], self.entry.data[CONF_PARTNER2]]

    def other_partner(self, partner: str) -> str:
        partners = self.partners
        if partner == partners[0]:
            return partners[1]
        return partners[0]

    async def async_load(self) -> None:
        stored = await self.store.async_load()
        if stored:
            self.profile.update(stored)
        for partner in self.partners:
            self.profile.setdefault("preferences", {}).setdefault(partner, {})
            self.profile.setdefault("moods", {}).setdefault(partner, MOOD_NOT_TONIGHT)

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

    async def async_set_mood(self, partner: str, mood: str) -> None:
        self.profile.setdefault("moods", {})[partner] = mood
        await self.async_save()
        self._signal()

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

    def _weight_for(self, activity: dict, proposer: str) -> float:
        """Score an activity from the point of view of the partner proposing it."""
        rating = (
            self.profile.get("preferences", {})
            .get(proposer, {})
            .get(activity["category"], 3)
        )
        weight = float(rating) + 0.1  # keep a small floor so nothing is impossible
        accessory = activity.get("accessory")
        if accessory and accessory not in self.profile.get("accessories", []):
            weight *= 0.15
        if self._is_on_cooldown(activity["id"]):
            mood = self.profile.get("moods", {}).get(proposer)
            if mood == MOOD_NOVELTY:
                weight *= 1.0
            else:
                weight *= 0.05
        return weight

    async def async_request_suggestion(self, turn: str | None = None) -> dict:
        """Pick a new activity and propose it to `turn` (the partner performing it)."""
        partners = self.partners
        if turn not in partners:
            turn = random.choice(partners)
        proposer = self.other_partner(turn)

        candidates = ACTIVITIES
        weights = [self._weight_for(activity, proposer) for activity in candidates]
        if sum(weights) <= 0:
            weights = [1.0 for _ in candidates]

        activity = random.choices(candidates, weights=weights, k=1)[0]

        self.current_suggestion = activity
        self.current_status = STATUS_PROPOSED
        self.current_turn = turn
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
            await self.async_start_timer()
        else:
            self.current_status = STATUS_DECLINED
            self.profile.setdefault("declined", {})[activity["id"]] = dt_util.utcnow().isoformat()
            await self._async_log_history(activity, response)
            await self.async_save()
            self._signal()

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

    async def async_start_timer(self, minutes: float | None = None) -> None:
        if not self.current_suggestion:
            return
        activity = self.current_suggestion
        if minutes is None:
            minutes = random.uniform(activity["duration_min"], activity["duration_max"])

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
        self._async_cancel_timer()
        self._signal()

    async def async_clear_profile(self) -> None:
        self.profile = copy.deepcopy(DEFAULT_PROFILE)
        for partner in self.partners:
            self.profile["preferences"][partner] = {}
            self.profile["moods"][partner] = MOOD_NOT_TONIGHT
        await self.async_save()
        await self.async_reset_session()

    def async_unload(self) -> None:
        self._async_cancel_timer()
