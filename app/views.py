import json
from django.http import JsonResponse
from django.views import View

from repositories.table_repo import TableRepository
from utils.date_processor import parse_booking_date
from repositories.booking_repo import BookingRepository
from services.booking_service import BookingService


class BookingView(View):
    """
    API View for handling table reservations.

    This view acts as the presentation layer, bridging HTTP requests to the
    underlying business logic via `BookingService`. It handles retrieving
    available tables and creating new bookings.
    """
    def setup(self, request, *args, **kwargs):
        """
        Initializes the view and its dependencies.

        Overrides the default Django setup to inject repositories and the booking
        service before any HTTP method is dispatched.

        Args:
            request (HttpRequest): The incoming HTTP request.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().setup(request, *args, **kwargs)
        self.booking_repo = BookingRepository()
        self.table_repo = TableRepository()
        self.service = BookingService(
            repository=self.booking_repo,
            table_repository=self.table_repo
        )

    def get(self, request):
        """
        Retrieves a list of available tables.

        If a 'date' query parameter is provided, it returns tables available at
        that specific time. If no date is provided, it returns all tables.

        Args:
            request (HttpRequest): The HTTP GET request containing an optional
                'date' query parameter (e.g., ?date=29.06.2026T20:00).

        Returns:
            JsonResponse: A JSON response containing a list of available tables
                with their 'id' and 'name' (status 200).
                Returns a 400 status code if the date format is invalid.
        """
        date_param = request.GET.get('date')

        target_time = None
        if date_param:
            target_time = parse_booking_date(date_param)
            if not target_time:
                return JsonResponse({'error': 'Invalid date format'}, status=400)

        table_entities = self.service.get_available_tables(target_time)

        response_data = [
            {'id': table.id, 'name': table.name}
            for table in table_entities
        ]

        return JsonResponse({'tables': response_data})

    def post(self, request):
        """
        Creates a new table booking.

        Parses the JSON payload from the request body, validates required fields
        and date formats, and delegates the creation process to the booking service.

        Args:
            request (HttpRequest): The HTTP POST request containing a JSON body
                with the following keys: 'client_name', 'client_phone', 'date',
                and 'table' (table ID).

        Returns:
            JsonResponse:
                - 201 Created: Booking successful, returns the new 'booking_id'.
                - 400 Bad Request: Invalid JSON, missing fields, or invalid date.
                - 409 Conflict: Business logic error (e.g., table already booked
                  or table does not exist).
        """
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        required_fields = ['client_name', 'client_phone', 'date', 'table']
        if not all(field in data for field in required_fields):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        target_time = parse_booking_date(data['date'])
        if not target_time:
            return JsonResponse({'error': 'Invalid date format'}, status=400)

        try:
            booking = self.service.create(
                table_id=data['table'],
                parsed_date=target_time,
                client_name=data['client_name'],
                client_phone=data['client_phone']
            )
            return JsonResponse({
                'message': 'Booking created successfully',
                'booking_id': booking.id
            }, status=201)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=409)
