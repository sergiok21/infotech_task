import pytest
import json
from django.urls import reverse
from db.models import Table, Booking
from django.utils import timezone
from datetime import datetime


@pytest.mark.django_db
class TestBookingView:
    @pytest.fixture
    def setup_data(self):
        self.table = Table.objects.create(name='Public')
        self.url = reverse('booking')

    def test_get_available_tables_success(self, client, setup_data):
        response = client.get(self.url)

        assert response.status_code == 200
        data = response.json()
        assert 'tables' in data
        assert data['tables'][0]['name'] == 'Public'

    def test_get_with_invalid_date(self, client, setup_data):
        response = client.get(self.url, {'date': 'invalid-date'})

        assert response.status_code == 400
        assert response.json()['error'] == 'Invalid date format'

    def test_post_create_booking_success(self, client, setup_data):
        payload = {
            'client_name': 'Serhii',
            'client_phone': '+380931234567',
            'date': '29.06.2026T20:00',
            'table': self.table.id
        }

        response = client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 201
        assert response.json()['message'] == 'Booking created successfully'
        assert Booking.objects.filter(client_name='Serhii').exists()

    def test_post_missing_fields(self, client, setup_data):
        payload = {
            'client_name': 'Serhii',
            'date': '29.06.2026T20:00',
            'table': self.table.id
        }

        response = client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400
        assert 'Missing required fields' in response.json()['error']

    def test_post_booking_conflict(self, client, setup_data):
        booking_date_str = '29.06.2026T20:00'
        parsed_date = timezone.make_aware(datetime(2026, 6, 29, 20, 0))

        Booking.objects.create(
            table=self.table,
            date=parsed_date,
            client_name='Existing Client',
            client_phone='000'
        )

        payload = {
            'client_name': 'New Client',
            'client_phone': '111',
            'date': booking_date_str,
            'table': self.table.id
        }

        response = client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 409
        assert 'already booked' in response.json()['error']
