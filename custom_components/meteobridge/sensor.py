"""Support for MeteobridgeSQL sensor data."""
from __future__ import annotations

import logging

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_MAC,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    DEGREE,
    PERCENTAGE,
    UnitOfIrradiance,
    UnitOfLength,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfVolumetricFlux,
    UV_INDEX,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from . import MeteobridgeSQLDataUpdateCoordinator
from .const import (
    ATTR_ATTRIBUTION,
    ATTR_MAX_SOLARRAD_TODAY,
    ATTR_MAX_TEMP_TODAY,
    ATTR_MIN_TEMP_TODAY,
    ATTR_MAX_UV_TODAY,
    ATTR_PRESSURE_TREND,
    ATTR_TEMP_15_MIN,
    CONCENTRATION_GRAMS_PER_CUBIC_METER,
    DOMAIN,
    MANUFACTURER
)

@dataclass(frozen=True)
class MeteobridgeSQLEntityDescription(SensorEntityDescription):
    """Describes MeteobridgeSQL sensor entity."""


SENSOR_TYPES: tuple[MeteobridgeSQLEntityDescription, ...] = (
    MeteobridgeSQLEntityDescription(
        key="absolute_humidity",
        name="Absolute Humidity",
        native_unit_of_measurement=CONCENTRATION_GRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        icon="mdi:water",
    ),
    MeteobridgeSQLEntityDescription(
        key="aqi",
        name="Air Quality Index",
        icon="mdi:air-filter",
        device_class=SensorDeviceClass.AQI,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    MeteobridgeSQLEntityDescription(
        key="beaufort",
        name="Beaufort",
        icon="mdi:windsock",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MeteobridgeSQLEntityDescription(
        key="beaufort_description",
        name="Beaufort Description",
        icon="mdi:windsock",
        translation_key="beaufort",
    ),
    MeteobridgeSQLEntityDescription(
        key="cloud_base",
        name="Cloud Base",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:arrow-expand-vertical",
        suggested_display_precision=0,
    ),
    MeteobridgeSQLEntityDescription(
        key="icon",
        name="Condition",
        icon="mdi:simple-icons",
    ),
    MeteobridgeSQLEntityDescription(
        key="conditions",
        name="Condition Text",
        icon="mdi:simple-icons",
    ),
    MeteobridgeSQLEntityDescription(
        key="description",
        name="Description",
        icon="mdi:image-text",
    ),
    MeteobridgeSQLEntityDescription(
        key="dewpoint",
        name="Dewpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MeteobridgeSQLEntityDescription(
        key="feels_like_temperature",
        name="Apparent Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MeteobridgeSQLEntityDescription(
        key="freezing_altitude",
        name="Freezing Altitude",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    MeteobridgeSQLEntityDescription(
        key="heatindex",
        name="Heat Index",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MeteobridgeSQLEntityDescription(
        key="humidity",
        name="Humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MeteobridgeSQLEntityDescription(
        key="pm1",
        name="Particulate Matter PM1",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM1,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MeteobridgeSQLEntityDescription(
        key="pm10",
        name="Particulate Matter PM10",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM10,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MeteobridgeSQLEntityDescription(
        key="pm25",
        name="Particulate Matter PM2.5",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM25,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MeteobridgeSQLEntityDescription(
        key="pressuretrend_text",
        name="Pressure Trend",
        translation_key="pressure_trend",
        icon="mdi:trending-up",
    ),
    MeteobridgeSQLEntityDescription(
        key="pressuretrend",
        name="Pressure Trend Value",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    MeteobridgeSQLEntityDescription(
        key="rainrate",
        name="Rain rate",
        native_unit_of_measurement=UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR,
        device_class=SensorDeviceClass.PRECIPITATION_INTENSITY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    MeteobridgeSQLEntityDescription(
        key="raintoday",
        name="Rain today",
        native_unit_of_measurement=UnitOfPrecipitationDepth.MILLIMETERS,
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    MeteobridgeSQLEntityDescription(
        key="rainyesterday",
        name="Rain yesterday",
        native_unit_of_measurement=UnitOfPrecipitationDepth.MILLIMETERS,
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    MeteobridgeSQLEntityDescription(
        key="sealevelpressure",
        name="Sealevel Pressure",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    MeteobridgeSQLEntityDescription(
        key="solarrad",
        name="Solar Radiation",
        native_unit_of_measurement=UnitOfIrradiance.WATTS_PER_SQUARE_METER,
        device_class=SensorDeviceClass.IRRADIANCE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MeteobridgeSQLEntityDescription(
        key="temperature",
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MeteobridgeSQLEntityDescription(
        key="uv",
        name="UV Index",
        native_unit_of_measurement=UV_INDEX,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sun-wireless",
        suggested_display_precision=1,
    ),
    MeteobridgeSQLEntityDescription(
        key="uv_description",
        name="UV Description",
        icon="mdi:sun-wireless",
        translation_key="uv_description",
    ),
    MeteobridgeSQLEntityDescription(
        key="visibility",
        name="Visibility",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    MeteobridgeSQLEntityDescription(
        key="windchill",
        name="Wind Chill",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MeteobridgeSQLEntityDescription(
        key="windbearing",
        name="Wind bearing",
        device_class=SensorDeviceClass.WIND_DIRECTION,
        native_unit_of_measurement=DEGREE,
        icon="mdi:compass",
    ),
    MeteobridgeSQLEntityDescription(
        key="windbearingavg10",
        name="Wind bearing avg. 10 min",
        device_class=SensorDeviceClass.WIND_DIRECTION,
        native_unit_of_measurement=DEGREE,
        icon="mdi:compass",
    ),
    MeteobridgeSQLEntityDescription(
        key="windbearingdavg",
        name="Wind bearing Day Average",
        device_class=SensorDeviceClass.WIND_DIRECTION,
        native_unit_of_measurement=DEGREE,
        icon="mdi:compass",
    ),
    MeteobridgeSQLEntityDescription(
        key="wind_direction",
        name="Wind Cardinal",
        icon="mdi:compass",
        translation_key="wind_cardinal",
    ),
    MeteobridgeSQLEntityDescription(
        key="windspeedavg",
        name="Wind Speed",
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MeteobridgeSQLEntityDescription(
        key="windgust",
        name="Wind Gust",
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


_LOGGER = logging.getLogger(__name__)

def _get_hw_platform(platform: str) -> str:
    """Get Meteobridge hardware platform."""
    if platform == "CARAMBOLA2":
        return "Meteobridge Pro"
    if platform == "mbnano":
        return "Meteobridge Nano"
    return platform

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """MeteobridgeSQL sensor platform."""
    coordinator: MeteobridgeSQLDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    if coordinator.data.sensor_data == {}:
        return

    entities: list[MeteobridgeSQLSensor[Any]] = [
        MeteobridgeSQLSensor(coordinator, description, config_entry)
        for description in SENSOR_TYPES if getattr(coordinator.data.sensor_data, description.key) is not None
    ]

    async_add_entities(entities, False)

class MeteobridgeSQLSensor(CoordinatorEntity[DataUpdateCoordinator], SensorEntity):
    """A MeteobridgeSQL sensor."""

    entity_description: MeteobridgeSQLEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MeteobridgeSQLDataUpdateCoordinator,
        description: MeteobridgeSQLEntityDescription,
        config: MappingProxyType[str, Any]
    ) -> None:
        """Initialize a MeteobridgeSQL sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._config = config
        self._coordinator = coordinator

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._config.data[CONF_MAC])},
            entry_type=DeviceEntryType.SERVICE,
            manufacturer=MANUFACTURER,
            model=_get_hw_platform(self.coordinator.data.sensor_data.mb_platform),
            name=f"{self.coordinator.data.sensor_data.mb_stationname} Sensor",
            configuration_url=f"http://{self.coordinator.data.sensor_data.mb_ip}",
            hw_version=f"{self.coordinator.data.sensor_data.mb_platform}",
            sw_version=f"{self.coordinator.data.sensor_data.mb_swversion}-{self.coordinator.data.sensor_data.mb_buildnum}",
        )
        self._attr_attribution = ATTR_ATTRIBUTION
        self._attr_unique_id = f"{config.data[CONF_MAC]} {description.key}"

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of sensor."""

        return super().native_unit_of_measurement

    @property
    def native_value(self) -> StateType:
        """Return state of the sensor."""

        return (
            getattr(self.coordinator.data.sensor_data, self.entity_description.key)
            if self.coordinator.data.sensor_data else None
        )

    @property
    def extra_state_attributes(self) -> None:
        """Return non standard attributes."""

        if self.entity_description.key == "temperature":
            return {
                ATTR_MAX_TEMP_TODAY: self.coordinator.data.sensor_data.tempmax,
                ATTR_MIN_TEMP_TODAY: self.coordinator.data.sensor_data.tempmin,
                ATTR_TEMP_15_MIN: self.coordinator.data.sensor_data.temp15min,
            }

        if self.entity_description.key == "uv":
            return {
                ATTR_MAX_UV_TODAY: self.coordinator.data.sensor_data.uvdaymax,
            }

        if self.entity_description.key == "solarrad":
            return {
                ATTR_MAX_SOLARRAD_TODAY: self.coordinator.data.sensor_data.solarraddaymax,
            }

        if self.entity_description.key == "pressuretrend_text":
            return {
                ATTR_PRESSURE_TREND: self.coordinator.data.sensor_data.pressuretrend,
            }

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
