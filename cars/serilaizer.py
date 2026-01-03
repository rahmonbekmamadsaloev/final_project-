import math
from rest_framework import serializers
from django.utils import timezone

from .models import Car, Booking


# =========================================================
# Car Serializer
# =========================================================
class CarSerializer(serializers.ModelSerializer):
    car_type_display = serializers.CharField(
        source='get_car_type_display',
        read_only=True
    )

    class Meta:
        model = Car
        fields = [
            'id', 'name', 'photo', 'year',
            'car_type', 'car_type_display',
            'price_per_day', 'seats',
            'luggage', 'is_available'
        ]


# =========================================================
# Booking Serializer
# =========================================================
class BookingSerializer(serializers.ModelSerializer):
    # пользователь (только для чтения)
    user = serializers.StringRelatedField(read_only=True)

    # машина
    car_id = serializers.PrimaryKeyRelatedField(
        queryset=Car.objects.all(),
        write_only=True
    )
    car = serializers.CharField(
        source='car.name',
        read_only=True
    )

    # вычисляемые поля
    rental_days = serializers.SerializerMethodField()
    price_per_day = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'user',
            'car', 'car_id',
            'start_time', 'end_time',
            'with_driver',
            'rental_days', 'price_per_day',
            'total_price',
            'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'status',
            'created_at',
            'updated_at',
            'car',
            'rental_days',
            'price_per_day',
            'total_price'
        ]

    # =====================================================
    # Calculated fields
    # =====================================================
    def get_rental_days(self, obj):
        if not obj.start_time or not obj.end_time:
            return 0

        delta = obj.end_time - obj.start_time
        return max(math.ceil(delta.total_seconds() / 86400), 1)

    def get_price_per_day(self, obj):
        return obj.car.price_per_day if obj.car else 0

    # =====================================================
    # Validation
    # =====================================================
    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        car = data.get('car_id')

        # проверяем даты только если они переданы
        if start_time and end_time:
            if start_time >= end_time:
                raise serializers.ValidationError(
                    'Дата окончания должна быть позже даты начала'
                )

            # запрещаем бронирование в прошлом ТОЛЬКО при создании
            if not self.instance and start_time < timezone.now():
                raise serializers.ValidationError(
                    'Нельзя создавать бронирование в прошлом'
                )

            # проверка пересечений
            if car:
                overlapping = Booking.objects.filter(
                    car=car,
                    status__in=['pending', 'confirmed', 'active'],
                    end_time__gt=start_time,
                    start_time__lt=end_time
                )

                if self.instance:
                    overlapping = overlapping.exclude(pk=self.instance.pk)

                if overlapping.exists():
                    raise serializers.ValidationError(
                        'Автомобиль уже забронирован на этот период'
                    )

        return data

    # =====================================================
    # Create
    # =====================================================
    def create(self, validated_data):
        car = validated_data.pop('car_id')
        user = self.context['request'].user

        booking = Booking.objects.create(
            user=user,
            car=car,
            **validated_data
        )

    # Вычисляем и сохраняем цену
        booking.calculate_price(save=True)

        return booking


    # =====================================================
    # Update
    # =====================================================
    def update(self, instance, validated_data):
        car = validated_data.pop('car_id', None)

        if car:
            instance.car = car

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.calculate_price()
        instance.save()
        return instance
