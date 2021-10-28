from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from store.models import Customer

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_for_new_user(sender, **kwargs):
# sender=> class who is sending the notification or signal
    if kwargs['created']:
        # check to see if a new model instance is created
        Customer.objects.create(user=kwargs['instance'])

        



