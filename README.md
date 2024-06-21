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

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/wetter-alarm/__init__.py
custom_components/wetter-alarm/config_flow.py
custom_components/wetter-alarm/manifest.json
custom_components/wetter-alarm/sensor.py
custom_components/wetter-alarm/wetter_alarm_client.py
custom_components/wetter-alarm/translations/en.json
```

## Configuration

No matter which way you installed the Integration, you need to restart Home Assistant before configuring the integration.

Go to the `Settings -> Devices & Services -> Integrations` tab of your Home Assistant instance.
Click `ADD INTEGRATION` and search for "Wetter-Alarm".
The Configuration flow will start when you click install.

## How to find the ID of your location
You can find the ID of your location in the POI-Folder [here](POIs/).

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Credits
Fork of [redlukas/wetter-alarm](https://github.com/redlukas/wetter-alarm).
Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template

---

[logo]: https://github.com/onekintaro/wetter-alarm/blob/master/logo.png?raw=true

[integration_blueprint]: https://github.com/custom-components/integration_blueprint

[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Default-green.svg

[license-shield]: https://img.shields.io/github/license/onekintaro/wetter-alarm.svg
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40onekintaro-blue.svg

[user_profile]: https://github.com/onekintaro

[open-in-hacs]: https://my.home-assistant.io/redirect/hacs_repository/?owner=onekintaro&repository=wetter-alarm&category=integration
[my-hacs-badge]: https://my.home-assistant.io/badges/hacs_repository.svg
