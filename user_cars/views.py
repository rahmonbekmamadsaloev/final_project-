from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Car, Rental
from .serializer import CarSerializer, CarRentalSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# --- CRUD Машин пользователя ---

class CarListCreateView(ListCreateAPIView):
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Car.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
       
    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        if user is None or user.is_anonymous:
            return Car.objects.none()  # или return Car.objects.all() для публичного отображения
        return Car.objects.filter(user=user)
    

    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        if user is None or user.is_anonymous:
            return Car.objects.none()
        return Car.objects.filter(user=user)



class CarDetailView(RetrieveAPIView):
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Car.objects.filter(user=self.request.user)
    
    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        if user is None or user.is_anonymous:
            return Car.objects.none()  # или return Car.objects.all() для публичного отображения
        return Car.objects.filter(user=user)



class CarUpdateView(UpdateAPIView):
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Car.objects.filter(user=self.request.user)
    
    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        if user is None or user.is_anonymous:
            return Car.objects.none()  # или return Car.objects.all() для публичного отображения
        return Car.objects.filter(user=user)


class CarDeleteView(DestroyAPIView):
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Car.objects.filter(user=self.request.user)
    
    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        if user is None or user.is_anonymous:
            return Car.objects.none()  # или return Car.objects.all() для публичного отображения
        return Car.objects.filter(user=user)


# --- Список доступных машин для аренды ---
class AvailableCarsListView(ListAPIView):
    serializer_class = CarRentalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Car.objects.exclude(user=user)


# --- Аренда машины ---
class RentCarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        try:
            car = Car.objects.get(pk=pk)
        except Car.DoesNotExist:
            return Response({"detail": "Машина не найдена"}, status=status.HTTP_404_NOT_FOUND)

        # Нельзя арендовать свою машину
        if car.user == user:
            return Response({"detail": "Нельзя арендовать свою машину"}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка доступности машины
        if car.amount <= 0:
            return Response({"detail": "Машина недоступна для аренды"}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка баланса арендатора
        renter_balance = getattr(user, 'balance', None)
        if renter_balance is None or renter_balance.amount < car.price_per_day:
            return Response({"detail": "Недостаточно средств"}, status=status.HTTP_400_BAD_REQUEST)

        # Списание денег арендатора
        renter_balance.amount -= car.price_per_day
        renter_balance.save()

        # Начисление денег владельцу
        owner_balance = getattr(car.user, 'balance', None)
        if owner_balance:
            owner_balance.amount += car.price_per_day
            owner_balance.save()

        # Уменьшение количества доступных машин
        car.amount -= 1
        car.save()

        # Создание записи аренды
        Rental.objects.create(car=car, renter=user)

        return Response(
            {"detail": f"Вы успешно арендовали машину {car.car_name}. "
                       f"Списано {car.price_per_day} со счета."},
            status=status.HTTP_200_OK
        )
