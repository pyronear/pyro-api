from datetime import datetime

import pytest

from app.services.i18n import build_alert_message

DT = datetime(2026, 7, 10, 12, 0, 0)  # naive UTC, as stored in the DB


@pytest.mark.parametrize(
    ("lat", "lon", "title", "local_time"),
    [
        # Marseille, France -> French, UTC+2 in July
        (43.3, 5.4, "Un feu a été détecté !", "2026-07-10 14:00:00"),
        # Santiago, Chile -> Spanish, UTC-4 in July
        (-33.45, -70.66, "¡Se ha detectado un incendio!", "2026-07-10 08:00:00"),
        # New York, USA -> English fallback, UTC-4 in July
        (40.7, -74.0, "A fire has been detected!", "2026-07-10 08:00:00"),
        # Middle of the ocean -> Etc/GMT+9 (UTC-9), no country -> English
        (0.0, -140.0, "A fire has been detected!", "2026-07-10 03:00:00"),
    ],
)
def test_build_alert_message_locale(lat: float, lon: float, title: str, local_time: str):
    message = build_alert_message(lat, lon, DT, "station-01", 45.6, "https://platform.pyronear.org/alert/1")
    assert message.title == title
    assert message.local_time == local_time
    assert "station-01" in message.site_line
    assert "45.6°" in message.azimuth_line


def test_alert_message_renderings():
    message = build_alert_message(43.3, 5.4, DT, "station-01", 45.6, "https://platform.pyronear.org/alert/1")
    text = message.as_text()
    assert text.startswith("Un feu a été détecté !")
    assert "https://platform.pyronear.org/alert/1" in text
    mrkdwn = message.as_mrkdwn()
    assert "<https://platform.pyronear.org/alert/1|" in mrkdwn
