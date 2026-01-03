from rest_framework import serializers
from .models import Car
import datetime
from rest_framework.exceptions import ValidationError


class CarSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Car
        fields = '__all__'  # включает amount
        read_only_fields = ['user', 'balance']
        ref_name = "UserCarSerializer"

    def get_balance(self, obj):
        user = getattr(self.context['request'], 'user', None)
        if user is None or user.is_anonymous:
            return None
        balance = getattr(user, 'balance', None)
        return balance.amount if balance else 0

    def validate_year(self, value):
        current_year = datetime.datetime.now().year
        if value < 1886:
            raise serializers.ValidationError("Год выпуска не может быть раньше 1886.")
        if value > current_year:
            raise serializers.ValidationError(f"Год выпуска не может быть больше текущего года ({current_year}).")
        return value

    def validate_price_per_day(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена за день должна быть больше 0.")
        return value

    def validate_car_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Имя автомобиля не может быть пустым.")
        return value

    def validate_car_type(self, value):
        valid_types = [choice[0] for choice in Car._meta.get_field('car_type').choices]
        if value not in valid_types:
            raise serializers.ValidationError(f"Неверный тип автомобиля. Допустимые: {', '.join(valid_types)}")
        return value

    def validate_location(self, value):
        if not value.strip():
            raise serializers.ValidationError("Локация не может быть пустой.")
        return value

    def create(self, validated_data):
        user = getattr(self.context['request'], 'user', None)
        if user is None or user.is_anonymous:
            raise ValidationError("Пользователь должен быть аутентифицирован для создания машины.")
        validated_data['user'] = user
        car = Car.objects.create(**validated_data)
        return car


class CarRentalSerializer(serializers.ModelSerializer):
    owner_balance = serializers.SerializerMethodField(read_only=True)
    amount = serializers.SerializerMethodField(read_only=True)  # если поле есть логически

    class Meta:
        model = Car
        fields = ['id', 'car_name', 'year', 'car_type', 'price_per_day', 'location', 'owner_balance', 'amount']

    def get_owner_balance(self, obj):
        owner = getattr(obj, 'user', None)
        balance = getattr(owner, 'balance', None)
        return balance.amount if balance else 0

    def get_amount(self, obj):
        # возвращаем количество доступных машин
        return getattr(obj, 'amount', 0)
