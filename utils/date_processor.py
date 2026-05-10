from datetime import datetime

from django.utils import timezone


def parse_booking_date(date_str: str) -> datetime | None:
    """
    Parses a booking date string into a timezone-aware datetime object.

    This utility function cleans the input by removing any accidental spaces
    to handle minor formatting inconsistencies from the client side. It strictly
    expects the date string to follow the 'DD.MM.YYYYTHH:MM' format
    (e.g., '29.06.2026T20:00').

    Args:
        date_str (str): The raw date string received from the HTTP request.

    Returns:
        datetime | None: A timezone-aware datetime object ready to be safely
            used with the database and business logic. Returns None if the
            input string is empty, missing, or fails to match the required format.
    """
    if not date_str:
        return None
    clean_str = date_str.replace(' ', "")
    try:
        naive_dt = datetime.strptime(clean_str, '%d.%m.%YT%H:%M')
        return timezone.make_aware(naive_dt)
    except ValueError:
        return None
