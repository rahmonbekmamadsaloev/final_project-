from django.urls import path
from .views import (
    CarListCreateView,
    CarDetailView,
    CarUpdateView,
    CarDeleteView,
    AvailableCarsListView,
    RentCarView,
)

urlpatterns = [
    # CRUD машин пользователя
    path('cars/', CarListCreateView.as_view(), name='car-list-create'),       # GET список / POST создать
    path('cars/<int:pk>/', CarDetailView.as_view(), name='car-detail'),       # GET детально
    path('cars/<int:pk>/update/', CarUpdateView.as_view(), name='car-update'),# PUT/PATCH обновление
    path('cars/<int:pk>/delete/', CarDeleteView.as_view(), name='car-delete'),# DELETE

    # Доступные для аренды машины
    path('cars/available/', AvailableCarsListView.as_view(), name='available-cars'),

    # Аренда машины
    path('cars/<int:pk>/rent/', RentCarView.as_view(), name='rent-car'),
]
