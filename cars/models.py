from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import User


class Car(models.Model):
    CAR_TYPE_CHOICES = (
        ('electric', 'Электромобиль'),
        ('premium', 'Премиум'),
        ('suv', 'Кроссовер / SUV'),
        ('cargo', 'Грузовой / Минивэн'),
    )

    name = models.CharField(max_length=250, verbose_name='Модель автомобиля')
    photo = models.ImageField(upload_to='cars/%Y/%m/%d/', verbose_name='Главное фото')
    year = models.PositiveSmallIntegerField(verbose_name='Год выпуска')
    car_type = models.CharField(max_length=20, choices=CAR_TYPE_CHOICES, verbose_name='Класс автомобиля')
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за сутки')
    seats = models.PositiveSmallIntegerField(default=5, verbose_name='Количество мест')
    luggage = models.CharField(max_length=100, blank=True, verbose_name='Объём багажника (примерно)')
    is_available = models.BooleanField(default=True, verbose_name='Доступен для брони')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'

    def __str__(self):
        return f"{self.name} ({self.year}) — {self.get_car_type_display()}"




from django.db import models
from users.models   import User
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    with_driver = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # ----------------------------
    # Расчёт цены
    # ----------------------------
    def calculate_price(self, save=False):
        days = max((self.end_time - self.start_time).days, 1)
        price = self.car.price_per_day * days
        if self.with_driver:
            price *= Decimal('1.2')
        price = price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if save:
            self.total_price = price
            self.save(update_fields=['total_price'])
        return price

    # ----------------------------
    # Обновление статуса
    # ----------------------------
    def update_status(self):
        now = timezone.now()
        if self.status in ['canceled', 'completed']:
            return
        if self.start_time <= now <= self.end_time:
            self.status = 'active'
        elif now > self.end_time:
            self.status = 'completed'
            if not self.car.is_available:
                self.car.is_available = True
                self.car.save(update_fields=['is_available'])
        self.save(update_fields=['status'])
