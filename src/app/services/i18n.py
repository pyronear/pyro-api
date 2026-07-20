# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Union
from zoneinfo import ZoneInfo

import pytz
from timezonefinder import TimezoneFinder

__all__ = ["build_alert_message"]

_tz_finder = TimezoneFinder()

# Invert pytz's country -> timezones table to resolve a timezone to its country
_COUNTRY_BY_TZ: Dict[str, str] = {tz: country for country, tzs in pytz.country_timezones.items() for tz in tzs}

_FRENCH_COUNTRIES = {"FR", "BE", "LU", "MC", "GF", "GP", "MQ", "RE", "YT", "NC", "PF", "PM", "WF"}
_SPANISH_COUNTRIES = {
    "ES",
    "CL",
    "AR",
    "BO",
    "CO",
    "CR",
    "CU",
    "DO",
    "EC",
    "GT",
    "HN",
    "MX",
    "NI",
    "PA",
    "PE",
    "PY",
    "SV",
    "UY",
    "VE",
}

_STRINGS: Dict[str, Dict[str, str]] = {
    "fr": {
        "title": "Un feu a été détecté !",
        "site": "Nom du site concerné",
        "azimuth": "Azimuth de détection",
        "link": "Visualiser l'alerte en détail sur la plateforme Pyronear",
    },
    "es": {
        "title": "¡Se ha detectado un incendio!",
        "site": "Nombre del sitio afectado",
        "azimuth": "Acimut de detección",
        "link": "Ver la alerta en detalle en la plataforma Pyronear",
    },
    "en": {
        "title": "A fire has been detected!",
        "site": "Site name",
        "azimuth": "Detection azimuth",
        "link": "View the alert in detail on the Pyronear platform",
    },
}


@dataclass(frozen=True)
class AlertMessage:
    title: str
    local_time: str
    site_line: str
    azimuth_line: str
    link_label: str
    url: str

    def as_text(self) -> str:
        """Plain-text rendering (Telegram, logs)."""
        return (
            f"{self.title}\n📅 {self.local_time}\n{self.site_line}\n{self.azimuth_line}\n{self.link_label} : {self.url}"
        )

    def as_mrkdwn(self) -> str:
        """Slack mrkdwn rendering (title is sent separately in the payload)."""
        return f":date: {self.local_time}\n {self.site_line}\n {self.azimuth_line}\n <{self.url}|{self.link_label}>"


def _resolve_locale(lat: float, lon: float) -> tuple[ZoneInfo, Dict[str, str]]:
    tz_name = _tz_finder.timezone_at(lat=lat, lng=lon) or "UTC"
    country = _COUNTRY_BY_TZ.get(tz_name, "")
    if country in _FRENCH_COUNTRIES:
        lang = "fr"
    elif country in _SPANISH_COUNTRIES:
        lang = "es"
    else:
        lang = "en"
    return ZoneInfo(tz_name), _STRINGS[lang]


def build_alert_message(
    lat: float,
    lon: float,
    created_at: datetime,
    camera_name: str,
    azimuth: Union[float, None],
    url: str,
) -> AlertMessage:
    """Build the alert notification, localized to the camera's timezone and country language."""
    tz, strings = _resolve_locale(lat, lon)
    local_dt = created_at.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz)
    return AlertMessage(
        title=strings["title"],
        local_time=local_dt.strftime("%Y-%m-%d %H:%M:%S"),
        site_line=f"{strings['site']} : {camera_name}",
        azimuth_line=f"{strings['azimuth']} : {azimuth}°",
        link_label=strings["link"],
        url=url,
    )
