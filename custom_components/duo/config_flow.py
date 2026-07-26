"""Config flow for the Duo integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_CONSENT, CONF_PARTNER1, CONF_PARTNER2, DOMAIN

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PARTNER1): str,
        vol.Required(CONF_PARTNER2): str,
        vol.Required(CONF_CONSENT, default=False): bool,
    }
)


class DuoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Duo."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            partner1 = user_input[CONF_PARTNER1].strip()
            partner2 = user_input[CONF_PARTNER2].strip()

            if not partner1 or not partner2:
                errors["base"] = "missing_name"
            elif partner1.lower() == partner2.lower():
                errors["base"] = "same_name"
            elif not user_input[CONF_CONSENT]:
                errors["base"] = "consent_required"
            else:
                await self.async_set_unique_id(f"{partner1.lower()}_{partner2.lower()}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Duo - {partner1} & {partner2}",
                    data={
                        CONF_PARTNER1: partner1,
                        CONF_PARTNER2: partner2,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )
