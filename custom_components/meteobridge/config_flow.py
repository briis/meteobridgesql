"""Config flow to configure WeatherFlow Forecast component."""

from __future__ import annotations

import logging
import voluptuous as vol
from typing import Any
from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_MAC,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.core import callback
from homeassistant.helpers.event import async_call_later
from pymeteobridgesql import (
    MeteobridgeSQL,
    MeteobridgeSQLDatabaseConnectionError,
    MeteobridgeSQLDataError,
    StationData,
)
from . import async_setup_entry, async_unload_entry
from .const import (
    CONF_DATABASE,
    DEFAULT_PORT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class MeteobridgeSQLConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow for MeteobridgeSQL."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for WeatherFlow Forecast."""
        return MeteobridgeSQLOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle a flow initialized by the user."""

        if user_input is None:
            return await self._show_setup_form(user_input)

        errors = {}
        try:
            meteobridge = MeteobridgeSQL(
                host=user_input[CONF_HOST],
                user=user_input[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
                database=user_input[CONF_DATABASE],
            )
            await self.hass.async_add_executor_job(meteobridge.initialize)
            station_data: StationData = await meteobridge.async_get_station_data(user_input[CONF_MAC])

        except MeteobridgeSQLDatabaseConnectionError as error:
            _LOGGER.error("Error connecting to MySQL Database: %s", error)
            errors["base"] = "cannot_connect"
            return await self._show_setup_form(errors)
        except MeteobridgeSQLDataError as error:
            _LOGGER.error("Failed to lookup data in the database: %s", error)
            errors["base"] = "no_data"
            return await self._show_setup_form(errors)

        await self.async_set_unique_id(user_input[CONF_MAC])
        self._abort_if_unique_id_configured

        return self.async_create_entry(
            title=f"Meteobride SQL ({station_data.mb_stationname})",
            data={
                CONF_MAC: user_input[CONF_MAC],
                CONF_HOST: user_input[CONF_HOST],
                CONF_PORT: user_input[CONF_PORT],
                CONF_USERNAME: user_input[CONF_USERNAME],
                CONF_PASSWORD: user_input[CONF_PASSWORD],
                CONF_DATABASE: user_input[CONF_DATABASE],
            },
        )

    async def _show_setup_form(self, errors=None):
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MAC): str,
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_DATABASE): str,
                }
            ),
            errors=errors or {},
        )


class MeteobridgeSQLOptionsFlowHandler(config_entries.OptionsFlow):
    """Options Flow forMeteobridgeSQL."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the WeatherFlow Forecast Options Flows."""
        self._config_entry = config_entry

    async def _do_update(
        self,
        *args,
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        """Update after settings change."""
        await async_unload_entry(self.hass, self.config_entry)
        await async_setup_entry(self.hass, self.config_entry)

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Configure Options for WeatherFlow Forecast."""

        if user_input is not None:
            async_call_later(self.hass, 2, self._do_update)
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_MAC, default=self._config_entry.data.get(CONF_MAC, "")
                    ): str,
                    vol.Required(
                        CONF_HOST, default=self._config_entry.data.get(CONF_HOST, "")
                    ): str,
                    vol.Required(
                        CONF_PORT,
                        default=self._config_entry.data.get(CONF_PORT, DEFAULT_PORT),
                    ): int,
                    vol.Required(
                        CONF_USERNAME,
                        default=self._config_entry.data.get(CONF_USERNAME, ""),
                    ): str,
                    vol.Required(
                        CONF_PASSWORD,
                        default=self._config_entry.data.get(CONF_PASSWORD, ""),
                    ): str,
                    vol.Required(
                        CONF_DATABASE,
                        default=self._config_entry.data.get(CONF_DATABASE, ""),
                    ): str,
                }
            ),
        )
