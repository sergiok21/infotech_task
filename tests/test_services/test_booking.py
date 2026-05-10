import pytest
from datetime import datetime

from entities.booking_entity import BookingEntity
from entities.table_entity import TableEntity
from repositories.booking_repo import BookingRepository
from repositories.table_repo import TableRepository
from services.booking_service import BookingService


# --- Fixtures ---

@pytest.fixture
def mock_booking_repo(mocker):
    return mocker.Mock(spec=BookingRepository)


@pytest.fixture
def mock_table_repo(mocker):
    return mocker.Mock(spec=TableRepository)


@pytest.fixture
def booking_service(mock_booking_repo, mock_table_repo):
    return BookingService(
        repository=mock_booking_repo,
        table_repository=mock_table_repo
    )


@pytest.fixture
def target_date():
    return datetime(2026, 6, 29, 20, 0)


# --- Tests ---

def test_get_available_tables_without_date(booking_service, mock_table_repo):
    expected_tables = [
        TableEntity(id=1, name='Table 1'),
        TableEntity(id=2, name='Table 2')
    ]
    mock_table_repo.get_all.return_value = expected_tables

    result = booking_service.get_available_tables()

    assert result == expected_tables
    mock_table_repo.get_all.assert_called_once()
    booking_service.repository.get_busy_bookings.assert_not_called()


def test_get_available_tables_with_date(booking_service, mock_booking_repo, mock_table_repo, target_date):
    # Table 1 is busy
    mock_booking_repo.get_busy_bookings.return_value = [
        BookingEntity(table_id=1, date=target_date, client_name='A', client_phone='111')
    ]

    expected_tables = [TableEntity(id=2, name='Table 2')]
    mock_table_repo.exclude_by_ids.return_value = expected_tables

    result = booking_service.get_available_tables(target_date)

    assert result == expected_tables
    mock_booking_repo.get_busy_bookings.assert_called_once_with(target_date)
    mock_table_repo.exclude_by_ids.assert_called_once_with([1])


def test_create_booking_table_not_found(booking_service, mock_table_repo, target_date):
    # Table does not exist
    mock_table_repo.exists.return_value = False

    with pytest.raises(ValueError, match='Table does not exist'):
        booking_service.create(
            table_id=999,
            parsed_date=target_date,
            client_name='Test',
            client_phone='123'
        )

    mock_table_repo.exists.assert_called_once_with(999)


def test_create_booking_conflict(booking_service, mock_table_repo, mock_booking_repo, target_date):
    # Table exists, but busies
    mock_table_repo.exists.return_value = True
    mock_booking_repo.get_conflicts.return_value = True

    with pytest.raises(ValueError, match='Table is already booked for this time window'):
        booking_service.create(
            table_id=1,
            parsed_date=target_date,
            client_name='Test',
            client_phone='123'
        )

    mock_booking_repo.get_conflicts.assert_called_once_with(1, target_date)


def test_create_booking_success(booking_service, mock_table_repo, mock_booking_repo, target_date):
    # Table exists and available
    mock_table_repo.exists.return_value = True
    mock_booking_repo.get_conflicts.return_value = False

    expected_created_entity = BookingEntity(
        id=100,
        table_id=1,
        date=target_date,
        client_name='Test',
        client_phone='123'
    )
    mock_booking_repo.create.return_value = expected_created_entity

    result = booking_service.create(
        table_id=1,
        parsed_date=target_date,
        client_name='Test',
        client_phone='123'
    )

    assert result == expected_created_entity

    mock_booking_repo.create.assert_called_once()
    called_args = mock_booking_repo.create.call_args[0]
    passed_entity = called_args[0]

    assert isinstance(passed_entity, BookingEntity)
    assert passed_entity.table_id == 1
    assert passed_entity.client_name == 'Test'
    assert passed_entity.date == target_date
