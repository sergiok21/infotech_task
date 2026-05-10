from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from app.views import BookingView

urlpatterns = [
    path('', csrf_exempt(BookingView.as_view()), name='booking'),
]
