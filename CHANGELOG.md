# CHANGELOG
> [!IMPORTANT]
> This is still a work in progress. The current version is not stable and may contain bugs.

## WIP-VERSION 0.5.6-BETA (2021-09-30)
- Moved: Translate Helper to helpers folder
- Moved: consts/ to helpers/const/ folder (still need some more rework)
- Moved: condition.py to helpers folder and renamed to mood.py
- Fix: Imports
- Fix: client.py (.utcnow() was deprecated, replaced with .now(timezone.utc))
- Fix Issue: #1 in weather.py (should now Update weather data correctly 🌞)

## WIP-VERSION 0.5.5-BETA (2021-09-26)
> [!CAUTION]
> You need to Delete all Configured Entities and Reconfigure the Integration, if you are Update from a lower Version. This is due to the rework of the Config.

Changes:
- Rework: Configuration Flow
- Add: Options Flow
- Add: Config/Options Flow helpers
- Rework: API-Client (and renamed from wetter_alarm_client.py to client.py)
- Rework: Constants (removed unused constants)
- Add: Constant Helpers
- Rework: Coordinator
- Fix Issue: #1 (Thanks to @Lutehi-Gregor) in Coordinator (should now Update the Data)
- Rework: Sensor
- Rework: Weather
- Fix: Translate Helper (i should move it to helpers folder 😅, will be fixed in next version)
- Feature[WIP] Add: Button entity (still WIP, not Usable)
- Feature[WIP] Add: Calendar entity (WIP, untested)
- Feature[WIP] Add: Remove unused sensors (WIP, Actually Disabled due Rewrite)
- Add: ContextEntry class for common helpers
- Add: recursive_search function (used in device.py)
- Update Language Files (EN, DE, FR, IT) (see Notes)

> [!NOTE]
> Language Files have been updated. But they need some more work. If you want to help, feel free to open a PR.
> - English: is the Language witch is used for Test and Debug the Integration, but my native language is German, so it may contain some errors. 😅
> - German: is my native language, so it should be the most accurate, but my Grammar is not the best 🫠.
> - French: I'm not a French speaker, so i used ChatGPT :robot: to translate the Language Files. If you are a French speaker and you see any errors, feel free to open a PR.
> - Italian: I'm not a Italian speaker, so i used ChatGPT :robot: to translate the Language Files. If you are a Italian speaker and you see any errors, feel free to open a PR.
> [!TIP]
> If you encounter any issues, feel free to open an issue in the repository. 😊


## WIP-VERSION 0.1.0 to 0.5.4 (NO DATE)
> [!IMPORTANT]
> This Versions are not documented. 😅

