# Wetter-Alarm [WIP/Rework]

![Logo][logo]

[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]


**This component will set up the following platforms.**

| Platform | Description                      |
| -------- | -------------------------------- |
| `sensor` | Show info from Wetter-Alarm API. |

## Overview

Wetter-Alarm is an app that alerts you of severe weather events in Switzerland.
This Integration will poll the [Wetter-Alarm](https://wetteralarm.ch/) API and expose the available Alerts to Home Assistant.

## Features
- Get Alerts from Wetter-Alarm API as Sensors
- Weather Entry & Forecast in Home Assistant
- Configuration via UI
- Reconfigure via UI
- Search for POIs in Configuration Flow
- Multi-Language Support (English, German, French, Italian)

## Planned Features
- Weather Sensors
- Flood Alerts and other Alerts
- Earthquake Alerts (if available in API, currently not available in the API)
- Avalanche Alerts (if available in API, currently not available in the API)
- Livecam Integration
- and more... :)

## Installation

### Automated (suggested):

Just click here: [![Open in HACS.][my-hacs-badge]][open-in-hacs]

### Manual:

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `wetter-alarm`.
4. Download _all_ the files from the `custom_components/wetter-alarm/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant

## Configuration

No matter which way you installed the Integration, you need to restart Home Assistant before configuring the integration.

Go to the `Settings -> Devices & Services -> Integrations` tab of your Home Assistant instance.
Click `ADD INTEGRATION` and search for "Wetter-Alarm".
The Configuration flow will start when you click install.

## How to find the ID of your location
You can find the ID of your location in the POI-Folder [here](POIs/).
Since Version 0.4.0 you can also search for POIs in the configuration flow.


## Contributions are welcome!
If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Credits
Based on Fork of [redlukas/wetter-alarm](https://github.com/redlukas/wetter-alarm).
Code template from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint]

---

[logo]: https://raw.githubusercontent.com/onekintaro/wetter-alarm/main/logo.png

[integration_blueprint]: https://github.com/custom-components/integration_blueprint

[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Default-green.svg

[license-shield]: https://img.shields.io/github/license/onekintaro/wetter-alarm.svg
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40onekintaro-blue.svg

[user_profile]: https://github.com/onekintaro

[open-in-hacs]: https://my.home-assistant.io/redirect/hacs_repository/?owner=onekintaro&repository=wetter-alarm&category=integration
[my-hacs-badge]: https://my.home-assistant.io/badges/hacs_repository.svg
