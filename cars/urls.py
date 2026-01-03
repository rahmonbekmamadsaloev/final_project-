from django.urls import path
from .views import (
    BookingListCreateAPIView,
    BookingRetrieveUpdateDestroyAPIView,
    BookingHistoryListAPIView,
    CarListAPIView,
    CarRetrieveAPIView,
    CarBookingStatsAPIView,
)

urlpatterns = [
    # ==============================
    # Бронирования
    # ==============================
    path('bookings/', BookingListCreateAPIView.as_view(), name='booking-list-create'),
    path('bookings/<int:pk>/', BookingRetrieveUpdateDestroyAPIView.as_view(), name='booking-detail'),
    path('bookings/history/', BookingHistoryListAPIView.as_view(), name='booking-history'),

    # ==============================
    # Автомобили
    # ==============================
    path('cars/', CarListAPIView.as_view(), name='car-list'),
    path('cars/<int:pk>/', CarRetrieveAPIView.as_view(), name='car-detail'),

    # ==============================
    # Статистика бронирований (только админ)
    # ==============================
    path('stats/cars/', CarBookingStatsAPIView.as_view(), name='car-booking-stats'),
]
