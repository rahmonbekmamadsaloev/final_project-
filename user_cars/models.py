from django.db import models
from users.models import User
import datetime


class Car(models.Model):
    CAR_TYPE = (
        ('electric', 'Электромобиль'),
        ('premium', 'Премиум'),
        ('suv', 'Кроссовер / SUV'),
        ('cargo', 'Грузовой / Минивэн'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cars")
    car_name = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    car_type = models.CharField(max_length=50, choices=CAR_TYPE)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    location  = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.car_name} ({self.year}) - {self.car_type}, ${self.price_per_day}/day"



class Rental(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='rentals')
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rentals')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="balance")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.user.username} - ${self.amount}"
