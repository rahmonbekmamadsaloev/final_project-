from rest_framework import generics, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, F, ExpressionWrapper, DurationField
from django.utils import timezone

from .models import Booking, Car
from .serilaizer import BookingSerializer, CarSerializer


# =========================================================
# Права: владелец или админ
# =========================================================
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user


# =========================================================
# Обновление статусов (ТОЛЬКО активные брони)
# =========================================================
def update_expired_bookings():
    Booking.objects.filter(
        is_active=True,
        status='active',
        end_time__lt=timezone.now()
    ).update(status='completed')


# =========================================================
# ВСЕ бронирования (list + create)
# =========================================================
class BookingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        update_expired_bookings()
        user = self.request.user

        qs = Booking.objects.filter(is_active=True)

        if not user.is_staff:
            qs = qs.filter(user=user)

        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save()


# =========================================================
# Одно бронирование (retrieve / update / soft delete)
# =========================================================
class BookingRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = Booking.objects.filter(is_active=True)

        if not user.is_staff:
            qs = qs.filter(user=user)

        return qs

    def destroy(self, request, *args, **kwargs):
        booking = self.get_object()
        booking.is_active = False
        booking.status = 'canceled'
        booking.save(update_fields=['is_active', 'status'])

        return Response(
            {'detail': 'Бронирование удалено (soft delete)'},
            status=status.HTTP_204_NO_CONTENT
        )





# =========================================================
# История бронирований
# =========================================================
class BookingHistoryListAPIView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        update_expired_bookings()
        user = self.request.user

        # Игнорируем статус и soft delete
        qs = Booking.objects.all()  # теперь поле is_activ не фильтруем

        if not user.is_staff:
            qs = qs.filter(user=user)

        return qs.order_by('-created_at')


# =========================================================
# Автомобили (list)
# =========================================================
class CarListAPIView(generics.ListAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter
    ]

    filterset_fields = {
        'car_type': ['exact'],
        'is_available': ['exact']
    }

    ordering_fields = ['price_per_day', 'year', 'name']
    ordering = ['name']
    search_fields = ['name']


# =========================================================
# Автомобиль (detail)
# =========================================================
class CarRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# =========================================================
# Статистика бронирований по автомобилям
# =========================================================
class CarBookingStatsAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        rental_duration_expr = ExpressionWrapper(
            F('bookings__end_time') - F('bookings__start_time'),
            output_field=DurationField()
        )

        stats = Car.objects.annotate(
            bookings_count=Count(
                'bookings',
                filter=F('bookings__is_active'),
                distinct=True
            ),
            total_revenue=Sum(
                'bookings__total_price',
                filter=F('bookings__is_active')
            ),
            total_rental_duration=Sum(
                rental_duration_expr,
                filter=F('bookings__is_active')
            )
        ).values(
            'name',
            'bookings_count',
            'total_revenue',
            'total_rental_duration'
        )

        result = []

        for car in stats:
            duration = car['total_rental_duration']
            total_days = duration.total_seconds() / 86400 if duration else 0

            avg_days = (
                total_days / car['bookings_count']
                if car['bookings_count'] else 0
            )

            result.append({
                'name': car['name'],
                'bookings_count': car['bookings_count'],
                'total_revenue': car['total_revenue'] or 0,
                'avg_rental_days': round(avg_days, 2)
            })

        return Response(result)
