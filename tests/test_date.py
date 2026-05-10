import pytest
from datetime import datetime
from django.utils import timezone

from utils.date_processor import parse_booking_date


@pytest.mark.parametrize(
    'input_date_str, expected_datetime',
    [
        # Good format (POST-request)
        ('29.06.2026T20:00', datetime(2026, 6, 29, 20, 0)),

        # 1 space
        ('29.06.2026T 20:00', datetime(2026, 6, 29, 20, 0)),

        # Random space positions
        ('  29.06.2026T20:00 ', datetime(2026, 6, 29, 20, 0)),
    ]
)
def test_parse_booking_date_valid(input_date_str: str, expected_datetime: datetime):
    result = parse_booking_date(input_date_str)

    assert result is not None

    assert timezone.is_aware(result)

    expected_aware = timezone.make_aware(expected_datetime)
    assert result == expected_aware


@pytest.mark.parametrize(
    'invalid_input',
    [
        '',
        None,
        'invalid-string',
        '2026-06-29T20:00',
        '29.06.2026',
        '32.06.2026T20:00',
    ]
)
def test_parse_booking_date_invalid(invalid_input: str | None):
    assert parse_booking_date(invalid_input) is None
