from datetime import datetime

import pytest
from django.utils import timezone

from db.models import Table
from repositories.booking_repo import BookingRepository
from repositories.table_repo import TableRepository


# --- Fixtures ---

@pytest.fixture
def booking_repo():
    return BookingRepository()


@pytest.fixture
def table_repo():
    return TableRepository()


@pytest.fixture
def table_1():
    return Table.objects.create(name='Table 1')


@pytest.fixture
def table_2():
    return Table.objects.create(name='Table 2')


@pytest.fixture
def base_time():
    return timezone.make_aware(datetime(2026, 6, 29, 20, 0))
