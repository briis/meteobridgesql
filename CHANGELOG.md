
## Release 1.1.13

Date: `2025-01-11`

### Changes

* Added two new fields to the realtime table. `windbearingavg10` and `windbearingdavg`. The two fields represent the last 10 minute average wind bearing and the daily average wind bearing. This is a breaking change as these fields need to be manually created in the table as follows:

  `windbearingavg10` INT NULL DEFAULT 'NULL' ,
  `windbearingdavg` INT NULL DEFAULT 'NULL' ,

These fields are currently not exposed in the Home Assistant Integration, but will be later. This is a hotfix to make sure the integration keeps running with the new fields added to the database and this requires 1.4.0 of `pymeteobridgesql`

## Release 1.1.11

Date: `2025-01-11`

### Changes

* Fixing Blocking Errors in Home Assistant 2025.1
* Bumped `pymeteobridgesql` to 1.3.3

## Release 1.1.10

Date: `2025-01-11`

### Changes

* Fixing Blocking Errors in Home Assistant 2025.1
* Fixed errors in config flow.
* Added Startup LOGGER Banner. Thanks to MTrab for the code.

## Release 1.1.9

Date: `2025-01-11`

### Changes

* Fixed errors in config flow, causing blocking calls errors.
* Fixed missing AQI value if PM2.5 was 0
* Bumped `pymeteobridgesql` to 1.3.2

## Release 1.1.8

Date: `2025-01-11`

### Changes

* Bumped development environment to Python 3.13

## Release 1.1.6

Date: `2024-05-05`

### Changes

* Added `visibility` to Minute Data
- Bumped pymeteobridgesql to 1.2.2 to support new database fields
- Added visibility to Hourly Forecast

## Release 1.1.5

Date: `2024-05-01`

### Changes

- Bumped pymeteobridgesql to 1.2.1 to support new database fields

## Release 1.1.4

Date: `2024-04-28`

### Changes

- Bumped pymeteobridgesql to 1.1.7 to support new database fields

## Release 1.1.2

Date: `2024-02-13`

### Changes

- Added new sensor `Condition Text`


## Release 1.1.1

Date: `2024-02-10`

### Changes

- Renamed the Integration to `meteobridge`. This will conflict another of my Integrations, but this no longer maintained.
- Ensure there is always 48 hours of Hourly Forecast data
- Bumped pymeteobridgesql to 1.1.2


## Release 1.1.0

Date: `2024-02-10`

### Changes

- Added Condition Icon.
- Added Weather Forecast Description
- Bumped pymeteobridgesql to 1.1.0
- Added `weather` entity, using visual crossing as source


## Release 1.0.5

Date: `2024-02-08`

### Changes

- Added Cloud Base sensor.
- Enforced only 1 decimal on Air Quality Index
- Bumped pymeteobridgesql to 1.0.6
- Upgraded to Python 3.12 in development container


## Release 1.0.4

Date: `2024-01-27`

### Changes

- Added Air Quality sensor.