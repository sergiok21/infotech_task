import pytest
from django.utils import timezone
from db.models import Table, Booking
from services.booking_service import BookingService
from repositories.booking_repo import BookingRepository
from repositories.table_repo import TableRepository


@pytest.mark.django_db
def test_get_available_tables_query_count(django_assert_num_queries):
    table = Table.objects.create(name='Test Table')
    Booking.objects.bulk_create([
        Booking(
            table=table,
            date=timezone.now(),
            client_name=f'Client {i}',
            client_phone='123'
        ) for i in range(50)
    ])

    service = BookingService(BookingRepository(), TableRepository())

    with django_assert_num_queries(2):
        service.get_available_tables(timezone.now())
