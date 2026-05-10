from datetime import timedelta, datetime

from django.db.models import Model

from db.models import Booking
from entities.booking_entity import BookingEntity
from repositories.base import BaseRepository


class BookingRepository(BaseRepository[BookingEntity, Booking]):
    """
    Repository for managing Booking data access.

    This class abstracts the Django ORM queries for the Booking model,
    ensuring that the upper layers (Services) only interact with pure
    Python dataclasses (BookingEntity) and remain decoupled from the database.
    """
    def __init__(self, entity: type[BookingEntity] = BookingEntity, model: type[Model] = Booking):
        """
        Initializes the repository with the specific entity and model types.

        Args:
            entity (type[BookingEntity]): The dataclass used for business logic.
            model (type[Model]): The Django ORM model representing the database table.
        """
        super().__init__(entity, model)

    def _to_entity(self, model: Booking) -> BookingEntity:
        """
        Maps a Django ORM Booking model instance to a BookingEntity dataclass.

        Args:
            model (Booking): The database model instance.

        Returns:
            BookingEntity: A pure Python object representing the booking.
        """
        return self.entity(
            id=model.id,
            table_id=model.table_id,
            date=model.date,
            client_name=model.client_name,
            client_phone=model.client_phone
        )

    def get_busy_bookings(self, target_time: datetime) -> list[BookingEntity]:
        """
        Retrieves all bookings that overlap with a specified target time.

        A booking is considered overlapping if it falls within a 4-hour window
        (2 hours before and 2 hours after the target time).

        Args:
            target_time (datetime): The time to check for busy tables.

        Returns:
            list[BookingEntity]: A list of entities representing the bookings
                that occupy tables during the specified time window.
        """
        time_min = target_time - timedelta(hours=2)
        time_max = target_time + timedelta(hours=2)

        bookings = self.model.objects.filter(date__gt=time_min, date__lt=time_max)
        return [self._to_entity(b) for b in bookings]

    def get_conflicts(self, table_id: int, target_time: datetime) -> bool:
        """
        Checks if a specific table is already booked around a given time.

        Applies the same 4-hour window rule (2 hours before and after) to determine
        if the table is unavailable for a new reservation.

        Args:
            table_id (int): The ID of the table to check.
            target_time (datetime): The desired booking time.

        Returns:
            bool: True if there is a scheduling conflict, False if the table is free.
        """
        time_min = target_time - timedelta(hours=2)
        time_max = target_time + timedelta(hours=2)
        return self.model.objects.filter(
            table_id=table_id,
            date__gt=time_min,
            date__lt=time_max
        ).exists()

    def create(self, entity: BookingEntity) -> BookingEntity:
        """
        Persists a new booking to the database.

        Takes a BookingEntity containing the booking details, saves it to the
        database using the Django ORM, and returns the newly created entity
        (which now includes the generated database ID).

        Args:
            entity (BookingEntity): The booking data to be saved.

        Returns:
            BookingEntity: The saved booking entity, complete with its database ID.
        """
        model = self.model.objects.create(
            table_id=entity.table_id,
            date=entity.date,
            client_name=entity.client_name,
            client_phone=entity.client_phone
        )
        return self._to_entity(model=model)
