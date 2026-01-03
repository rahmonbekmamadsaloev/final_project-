from django.apps import AppConfig


class UserCarsConfig(AppConfig):
    name = 'user_cars'


def ready(self):
        import user_cars.signals