# filters.py
import django_filters
from .models import Car

class CarPriceFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price_per_day", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price_per_day", lookup_expr='lte')

    class Meta:
        model = Car
        fields = ['car_type', 'is_available', 'min_price', 'max_price']
