"""Config flow for the Duo integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_CONSENT,
    CONF_NOTIFY1,
    CONF_NOTIFY2,
    CONF_PARTNER1,
    CONF_PARTNER2,
    CONF_PERSON1,
    CONF_PERSON2,
    DOMAIN,
)

PERSON_SELECTOR = selector.EntitySelector(
    selector.EntitySelectorConfig(domain="person")
)
TEXT_SELECTOR = selector.TextSelector()

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PARTNER1): str,
        vol.Required(CONF_PARTNER2): str,
        vol.Optional(CONF_PERSON1): PERSON_SELECTOR,
        vol.Optional(CONF_PERSON2): PERSON_SELECTOR,
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
            person1 = user_input.get(CONF_PERSON1)
            person2 = user_input.get(CONF_PERSON2)

            if not partner1 or not partner2:
                errors["base"] = "missing_name"
            elif partner1.lower() == partner2.lower():
                errors["base"] = "same_name"
            elif person1 and person2 and person1 == person2:
                errors["base"] = "same_person"
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
                    options={
                        CONF_PERSON1: person1 or "",
                        CONF_PERSON2: person2 or "",
                        CONF_NOTIFY1: "",
                        CONF_NOTIFY2: "",
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return DuoOptionsFlow()


class DuoOptionsFlow(config_entries.OptionsFlow):
    """Permet de (re)définir l'association partenaire <-> personne HA."""

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        entry = self.config_entry
        partner1 = entry.data[CONF_PARTNER1]
        partner2 = entry.data[CONF_PARTNER2]

        if user_input is not None:
            person1 = user_input.get(CONF_PERSON1) or ""
            person2 = user_input.get(CONF_PERSON2) or ""
            if person1 and person1 == person2:
                errors["base"] = "same_person"
            else:
                return self.async_create_entry(title="", data=user_input)

        options = entry.options
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_PERSON1,
                    description={"suggested_value": options.get(CONF_PERSON1) or None},
                ): PERSON_SELECTOR,
                vol.Optional(
                    CONF_PERSON2,
                    description={"suggested_value": options.get(CONF_PERSON2) or None},
                ): PERSON_SELECTOR,
                vol.Optional(
                    CONF_NOTIFY1,
                    description={"suggested_value": options.get(CONF_NOTIFY1) or ""},
                ): TEXT_SELECTOR,
                vol.Optional(
                    CONF_NOTIFY2,
                    description={"suggested_value": options.get(CONF_NOTIFY2) or ""},
                ): TEXT_SELECTOR,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "partner1": partner1,
                "partner2": partner2,
            },
        )
