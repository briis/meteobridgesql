"""Constants for Meteobridge SQL component."""

# Startup banner
STARTUP = """
-------------------------------------------------------------------
MeteobridgeSQL

Version: %s
This is a custom integration
If you have any issues with this you need to open an issue here:
https://github.com/briis/meteobridgesql/issues
-------------------------------------------------------------------
"""

ATTR_ATTRIBUTION = "Data provided by Meteobridge"
ATTR_MAX_SOLARRAD_TODAY = "max_solar_radiation_today"
ATTR_MAX_TEMP_TODAY = "max_temperature_today"
ATTR_MAX_UV_TODAY = "max_uv_today"
ATTR_MIN_TEMP_TODAY = "min_temperature_today"
ATTR_PRESSURE_TREND = "pressure_trend"
ATTR_TEMP_15_MIN = "temperature_15_min_ago"
ATTR_WEATHER_ATTRIBUTION = "Data provided by Visual Crossing"

CONCENTRATION_GRAMS_PER_CUBIC_METER = "g/m³"
CONF_DATABASE = "database"
CONF_UPDATE_INTERVAL = "update_interval"

DEFAULT_PORT = 3306
DEFAULT_UPDATE_INTERVAL = 60
DOMAIN = "meteobridge"

MANUFACTURER = "Meteobridge"

WEATHER_MANUFATURER = "Visual Crossing"
WEATHER_MODEL = "Forecast"
