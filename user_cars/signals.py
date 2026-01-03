from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Car, Balance

@receiver(post_save, sender=Car)
def create_balance_for_user(sender, instance, created, **kwargs):
    if created:
        # Проверяем, есть ли уже баланс у пользователя
        if not hasattr(instance.user, 'balance'):
            Balance.objects.create(user=instance.user)
