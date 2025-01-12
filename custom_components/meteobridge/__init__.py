"""Meteobridge SQL Platform."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Self

from pymeteobridgesql import (
    ForecastDaily,
    ForecastHourly,
    MeteobridgeSQLDatabaseConnectionError,
    MeteobridgeSQLDataError,
    MeteobridgeSQL,
    RealtimeData,
)

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import (
    CONF_HOST,
    CONF_MAC,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import (
    HomeAssistantError,
    ConfigEntryNotReady,
    Unauthorized,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.loader import async_get_integration

from .const import (
    CONF_DATABASE,
    DOMAIN,
    STARTUP,
)

PLATFORMS = [Platform.SENSOR, Platform.WEATHER]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up MeteobridgeSQL as config entry."""
    hass.data.setdefault(DOMAIN, {})
    integration = await async_get_integration(hass, DOMAIN)
    _LOGGER.info(STARTUP, integration.version)

    coordinator = MeteobridgeSQLDataUpdateCoordinator(hass, config_entry)
    if ConfigEntryState == ConfigEntryState.SETUP_IN_PROGRESS:
        await coordinator.async_config_entry_first_refresh()
    else:
        await coordinator.async_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    config_entry.async_on_unload(config_entry.add_update_listener(async_update_entry))

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )

    hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def async_update_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Reload MeteobridgeSQL component when options changed."""
    await hass.config_entries.async_reload(config_entry.entry_id)


class CannotConnect(HomeAssistantError):
    """Unable to connect to the web site."""


class MeteobridgeSQLDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching WeatherFlow data."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize global MeteobridgeSQL data updater."""
        self.weather = MeteobridgeSQLData(hass, config_entry)
        self.weather.initialize_data()
        self.hass = hass
        self.config_entry = config_entry

        update_interval = timedelta(minutes=1)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
            config_entry=config_entry,
        )

    async def _async_update_data(self) -> MeteobridgeSQLData:
        """Fetch data from MeteobridgeSQL."""
        try:
            return await self.weather.fetch_data()
        except Exception as err:
            raise UpdateFailed(f"Update failed: {err}") from err


class MeteobridgeSQLData:
    """Keep data for MeteobridgeSQL entity data."""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry) -> None:
        """Initialise the weather entity data."""
        self.hass = hass
        self._config = config.data
        self._weather_data: MeteobridgeSQL
        self.sensor_data: RealtimeData
        self.daily_forecast: list[ForecastDaily]
        self.hourly_forecast: list[ForecastHourly]

    def initialize_data(self) -> bool:
        """Establish connection to API."""

        self._weather_data = MeteobridgeSQL(
            self._config[CONF_HOST],
            self._config[CONF_USERNAME],
            self._config[CONF_PASSWORD],
            self._config[CONF_DATABASE],
            self._config[CONF_PORT],
        )

        return True

    async def fetch_data(self) -> Self:
        """Fetch data from API - (current weather and forecast)."""

        try:
            await self.hass.async_add_executor_job(self._weather_data.initialize)
            self.sensor_data: RealtimeData = (
                await self._weather_data.async_get_realtime_data(self._config[CONF_MAC])
            )
            self.daily_forecast = await self._weather_data.async_get_forecast(False)
            self.hourly_forecast = await self._weather_data.async_get_forecast(True)
        except MeteobridgeSQLDatabaseConnectionError as unauthorized:
            _LOGGER.debug(unauthorized)
            raise Unauthorized from unauthorized
        except MeteobridgeSQLDataError as notreadyerror:
            _LOGGER.debug(notreadyerror)
            raise ConfigEntryNotReady from notreadyerror

        return self
