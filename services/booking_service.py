from datetime import datetime

from entities.booking_entity import BookingEntity
from entities.table_entity import TableEntity
from repositories.booking_repo import BookingRepository
from repositories.table_repo import TableRepository
from services.base import BaseService


class BookingService(BaseService[BookingEntity, BookingRepository]):
    """
    Core business logic service for table bookings.

    This service acts as the central orchestrator for booking operations.
    It enforces business rules (e.g., preventing double bookings, validating
    table existence) and coordinates actions between the BookingRepository
    and TableRepository. It operates purely on domain entities, remaining
    agnostic to HTTP or database specifics.
    """
    def __init__(
            self,
            repository: BookingRepository,
            table_repository: TableRepository,
            entity: type[BookingEntity] = BookingEntity,
    ) -> None:
        """
        Initializes the booking service with required dependencies.

        Args:
            repository (BookingRepository): The repository for booking data access.
            table_repository (TableRepository): The repository for table data access.
            entity (type[BookingEntity], optional): The dataclass used for booking
                entities. Defaults to BookingEntity.
        """
        super().__init__(entity, repository)

        self.table_repository = table_repository

    def get_available_tables(self, parsed_date=None) -> list[TableEntity]:
        """
        Retrieves a list of tables available for a specific time.

        If no date is provided, it assumes a general inquiry and returns all
        existing tables. If a date is provided, it identifies tables that are
        already booked during that time window and filters them out.

        Args:
            parsed_date (datetime, optional): The target date and time to check
                for availability. Defaults to None.

        Returns:
            list[TableEntity]: A list of tables that are free to be booked.
        """
        if not parsed_date:
            return self.table_repository.get_all()

        busy_bookings = self.repository.get_busy_bookings(parsed_date)
        busy_ids = [booking.table_id for booking in busy_bookings]

        return self.table_repository.exclude_by_ids(busy_ids)

    def create(
            self,
            table_id: int,
            parsed_date: datetime,
            client_name: str,
            client_phone: str
    ) -> BookingEntity:
        """
        Validates business rules and creates a new booking.

        This method acts as a gatekeeper. It first checks if the requested table
        exists in the restaurant. Then, it checks for scheduling conflicts to
        prevent double booking. If all validations pass, it constructs a new
        booking entity and delegates persistence to the repository.

        Args:
            table_id (int): The ID of the table the client wants to book.
            parsed_date (datetime): The exact date and time for the reservation.
            client_name (str): The name of the client making the booking.
            client_phone (str): The contact phone number of the client.

        Raises:
            ValueError: If the requested `table_id` does not exist in the database.
            ValueError: If the table is already booked for the requested time window.

        Returns:
            BookingEntity: The newly created booking, including its assigned database ID.
        """
        if not self.table_repository.exists(table_id):
            raise ValueError('Table does not exist')

        if self.repository.get_conflicts(table_id, parsed_date):
            raise ValueError('Table is already booked for this time window')

        booking_entity = self.entity(
            table_id=table_id,
            date=parsed_date,
            client_name=client_name,
            client_phone=client_phone
        )

        return self.repository.create(booking_entity)
