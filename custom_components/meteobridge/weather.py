"""Support forVisual Crossing weather service via MySQL services."""
from __future__ import annotations

import logging

from types import MappingProxyType
from typing import Any

from homeassistant.components.weather import (
    DOMAIN as WEATHER_DOMAIN,
    Forecast,
    SingleCoordinatorWeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_MAC,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.unit_system import METRIC_SYSTEM
from homeassistant.util.dt import as_utc

from . import MeteobridgeSQLDataUpdateCoordinator
from .const import (
    ATTR_WEATHER_ATTRIBUTION,
    DOMAIN,
    WEATHER_MANUFATURER,
    WEATHER_MODEL,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Add a weather entity from a config_entry."""
    coordinator: MeteobridgeSQLDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    entity_registry = er.async_get(hass)

    name: str = f"{coordinator.data.sensor_data.mb_stationname} Weather"
    is_metric = hass.config.units is METRIC_SYSTEM

    entities = [MeteobridgeSQLWeather(coordinator, config_entry.data,
                                   False, name, is_metric)]

    # Add hourly entity to legacy config entries
    if entity_registry.async_get_entity_id(
        WEATHER_DOMAIN,
        DOMAIN,
        _calculate_unique_id(config_entry.data, True)
    ):
        name = f"{name} hourly"
        entities.append(MeteobridgeSQLWeather(coordinator, config_entry.data, True, name, is_metric))

    async_add_entities(entities)

def _calculate_unique_id(config: MappingProxyType[str, Any], hourly: bool) -> str:
    """Calculate unique ID."""
    name_appendix = ""
    if hourly:
        name_appendix = "-hourly"

    return f"{config[CONF_MAC]}{name_appendix}"


class MeteobridgeSQLWeather(SingleCoordinatorWeatherEntity[MeteobridgeSQLDataUpdateCoordinator]):
    """Implementation of a MeteobridgeSQL weather condition."""

    _attr_attribution = (
        ATTR_WEATHER_ATTRIBUTION
    )
    _attr_has_entity_name = True
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY
    )

    def __init__(
            self,
            coordinator: MeteobridgeSQLDataUpdateCoordinator,
            config: MappingProxyType[str, Any],
            hourly: bool,
            name: str,
            is_metric: bool,
    ) -> None:
        """Initialise the platform with a data instance and station."""
        super().__init__(coordinator)

        self._attr_unique_id = _calculate_unique_id(config, hourly)
        self._attr_name = name

        self._config = config
        self._is_metric = is_metric
        self._hourly = hourly
        self._attr_entity_registry_enabled_default = not hourly
        self._attr_device_info = DeviceInfo(
            name="Weather Entity",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN,)},  # type: ignore[arg-type]
            manufacturer=WEATHER_MANUFATURER,
            model=WEATHER_MODEL,
            configuration_url="https://www.visualcrossing.com/weather-api",
        )

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        return self.coordinator.data.sensor_data.icon

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        return self.coordinator.data.sensor_data.temperature

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure."""
        return self.coordinator.data.sensor_data.sealevelpressure

    @property
    def humidity(self) -> float | None:
        """Return the humidity."""
        return self.coordinator.data.sensor_data.humidity

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        return self.coordinator.data.sensor_data.windspeedavg

    @property
    def wind_bearing(self) -> float | str | None:
        """Return the wind direction."""
        return self.coordinator.data.sensor_data.wind_direction

    @property
    def native_wind_gust_speed(self) -> float | None:
        """Return the wind gust speed in native units."""
        return self.coordinator.data.sensor_data.windgust

    @property
    def native_dew_point(self) -> float | None:
        """Return the dew point."""
        return self.coordinator.data.sensor_data.dewpoint

    def _forecast(self, hourly: bool) -> list[Forecast] | None:
        """Return the forecast array."""
        ha_forecast: list[Forecast] = []

        if hourly:
            for item in self.coordinator.data.hourly_forecast:
                condition = item.icon
                datetime =  as_utc(item.datetime).isoformat()
                humidity = item.humidity
                precipitation_probability = item.precipitation_probability
                native_precipitation = item.precipitation
                native_pressure = item.pressure
                native_temperature = item.temperature
                native_apparent_temperature = item.apparent_temperature
                wind_bearing = item.wind_bearing
                native_wind_gust_speed = item.wind_gust
                native_wind_speed = item.wind_speed
                uv_index = item.uv_index

                ha_item = {
                    "condition": condition,
                    "datetime": datetime,
                    "humidity": humidity,
                    "precipitation_probability": precipitation_probability,
                    "native_precipitation": native_precipitation,
                    "native_pressure": native_pressure,
                    "native_temperature": native_temperature,
                    "native_apparent_temperature": native_apparent_temperature,
                    "wind_bearing": wind_bearing,
                    "native_wind_gust_speed": native_wind_gust_speed,
                    "native_wind_speed": native_wind_speed,
                    "uv_index": uv_index,
                }
                ha_forecast.append(ha_item)
        else:
            for item in self.coordinator.data.daily_forecast:
                condition = item.icon
                datetime = as_utc(item.datetime).isoformat()
                precipitation_probability = item.precipitation_probability
                native_temperature = item.temperature
                native_templow = item.temp_low
                native_precipitation = item.precipitation
                wind_bearing = int(item.wind_bearing)
                native_wind_speed = item.wind_speed
                native_wind_gust_speed = item.wind_gust

                ha_item = {
                    "condition": condition,
                    "datetime": datetime,
                    "precipitation_probability": precipitation_probability,
                    "native_precipitation": native_precipitation,
                    "native_temperature": native_temperature,
                    "native_templow": native_templow,
                    "wind_bearing": wind_bearing,
                    "native_wind_speed": native_wind_speed,
                    "native_wind_gust_speed": native_wind_gust_speed,
                }
                ha_forecast.append(ha_item)

        return ha_forecast

    @callback
    def _async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast in native units."""
        return self._forecast(False)

    @callback
    def _async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the hourly forecast in native units."""
        return self._forecast(True)
