# Meteobridge SQL

Home Assistant custom integration that reads weather data from a [Meteobridge](https://www.meteobridge.com/) weather logger via a MySQL database.

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]
[![Community Forum][forum-shield]][forum]

<a href="https://www.buymeacoffee.com/briis" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 145px !important;" ></a>

## Overview

Meteobridge is a hardware device that bridges personal weather stations to various internet weather services. This integration connects Home Assistant directly to the MySQL database that Meteobridge populates, exposing all weather measurements as sensors and providing a weather entity with hourly and daily forecasts sourced from Visual Crossing (stored in the database by Meteobridge).

## Prerequisites

Before installing this integration, Meteobridge must be configured to push data into a MySQL database. The database must be reachable from your Home Assistant instance over the network.

You will need:
- The IP address or hostname of the MySQL server
- The MySQL port (default: `3306`)
- A MySQL username and password with read access to the database
- The database name
- The MAC address of your Meteobridge device

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant.
2. Go to **Integrations** and click the three-dot menu in the top right.
3. Select **Custom repositories**.
4. Add `https://github.com/briis/meteobridgesql` as an **Integration**.
5. Search for **Meteobridge SQL** and install it.
6. Restart Home Assistant.

### Manual

1. Download the `custom_components/meteobridge` folder from this repository.
2. Copy it into your Home Assistant `config/custom_components/` directory.
3. Restart Home Assistant.

## Configuration

1. Go to **Settings → Devices & Services**.
2. Click **+ Add Integration** and search for **Meteobridge SQL**.
3. Fill in the configuration form:

| Field | Description |
|---|---|
| MAC Address | MAC address of your Meteobridge device — used as the unique device identifier |
| Host | IP address or hostname of the MySQL server |
| Port | MySQL port (default: `3306`) |
| Username | MySQL username |
| Password | MySQL password |
| Database | Name of the Meteobridge database |

4. Click **Submit**.

You can add more than one Meteobridge device by repeating the setup with a different MAC address.

To update any of these settings later, go to the integration in **Settings → Devices & Services** and click **Configure**.

## Entities

### Sensors

| Sensor | Unit | Description |
|---|---|---|
| Temperature | °C | Current outdoor temperature (+ daily min/max and 15-min-ago as attributes) |
| Apparent Temperature | °C | Feels-like temperature |
| Heat Index | °C | Heat index |
| Wind Chill | °C | Wind chill temperature |
| Dewpoint | °C | Dew point temperature |
| Humidity | % | Relative humidity |
| Absolute Humidity | g/m³ | Absolute humidity |
| Sealevel Pressure | hPa | Barometric pressure at sea level |
| Pressure Trend | hPa | Pressure change over the last 3 hours |
| Pressure Trend Text | — | Rising / Falling / Steady |
| Rain Rate | mm/h | Current precipitation intensity |
| Rain Today | mm | Total precipitation today |
| Rain Yesterday | mm | Total precipitation yesterday |
| Wind Speed | m/s | Average wind speed |
| Wind Gust | m/s | Wind gust speed |
| Wind Bearing | ° | Instantaneous wind direction |
| Wind Bearing avg. 10 min | ° | 10-minute average wind direction |
| Wind Bearing Day Average | ° | Daily average wind direction |
| Wind Cardinal | — | Compass direction (e.g. NNW) |
| Beaufort | — | Beaufort wind scale value |
| Beaufort Description | — | Beaufort description text |
| UV Index | UV index | UV index (+ daily maximum as attribute) |
| UV Description | — | UV risk level text |
| Solar Radiation | W/m² | Solar irradiance (+ daily maximum as attribute) |
| Cloud Base | m | Estimated cloud base altitude |
| Freezing Altitude | m | Estimated freezing level altitude |
| Visibility | km | Estimated visibility |
| Air Quality Index | — | Calculated AQI |
| Particulate Matter PM1 | µg/m³ | PM1 concentration |
| Particulate Matter PM2.5 | µg/m³ | PM2.5 concentration |
| Particulate Matter PM10 | µg/m³ | PM10 concentration |
| Condition | — | Current weather condition icon key |
| Condition Text | — | Current weather condition description |
| Description | — | Extended weather description |

Sensors are only created if the corresponding data field is present in the database.

### Weather Entity

A **weather entity** is created for each Meteobridge device, providing:
- Current conditions
- Hourly forecast (48 hours)
- Daily forecast

Forecast data is sourced from Visual Crossing and stored by Meteobridge in the MySQL database.

## Issues and Contributions

Please open issues at [github.com/briis/meteobridgesql/issues](https://github.com/briis/meteobridgesql/issues).

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

***

[commits-shield]: https://img.shields.io/github/commit-activity/y/briis/meteobridgesql.svg?style=flat-square
[commits]: https://github.com/briis/meteobridgesql/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=flat-square
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/briis/meteobridgesql.svg?style=flat-square
[maintenance-shield]: https://img.shields.io/badge/maintainer-Bjarne%20Riis%20%40briis-blue.svg?style=flat-square
[releases-shield]: https://img.shields.io/github/release/briis/meteobridgesql.svg?style=flat-square
[releases]: https://github.com/briis/meteobridgesql/releases
