from tests.test_repositories.base import *

from datetime import timedelta

from db.models import Booking
from entities.booking_entity import BookingEntity


@pytest.mark.django_db
def test_get_conflicts(booking_repo, table_1, base_time):
    Booking.objects.create(
        table=table_1,
        date=base_time,
        client_name='Client A',
        client_phone='111'
    )

    # 1. 20:00 -> Conflict
    assert booking_repo.get_conflicts(table_1.id, base_time) is True

    # 2. 21:00-23:00 -> Conflict (20:00-22:00)
    assert booking_repo.get_conflicts(table_1.id, base_time + timedelta(hours=1)) is True

    # 3. 22:00-00:00 -> Success
    assert booking_repo.get_conflicts(table_1.id, base_time + timedelta(hours=2)) is False

    # 4. Other table -> Success
    assert booking_repo.get_conflicts(999, base_time) is False


@pytest.mark.django_db
def test_get_busy_bookings(booking_repo, table_1, table_2, base_time):
    Booking.objects.create(
        table=table_1,
        date=base_time,
        client_name='Client A',
        client_phone='111'
    )

    # 21:00 (20:00-22:00 booked, 1 table busy) -> 1 output
    target_time = base_time + timedelta(hours=1)
    available_tables = booking_repo.get_busy_bookings(target_time)

    assert len(available_tables) == 1
    assert available_tables[0].table_id == table_1.id

    # 22:00 -> 0 output
    target_time = base_time + timedelta(hours=2)
    available_tables = booking_repo.get_busy_bookings(target_time)

    assert len(available_tables) == 0


@pytest.mark.django_db
def test_create_booking(booking_repo, table_1, base_time):
    entity_to_create = BookingEntity(
        table_id=table_1.id,
        date=base_time,
        client_name='Test Client',
        client_phone='1234567890'
    )
    result_entity = booking_repo.create(entity_to_create)

    assert result_entity.id is not None
    assert result_entity.table_id == table_1.id

    assert Booking.objects.count() == 1
    db_booking = Booking.objects.first()
    assert db_booking.client_name == 'Test Client'
