from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Transfer


@receiver(post_save, sender=Transfer)
def post_save_transfer_created_receiver(
    sender, instance: Transfer, created, **kwargs
) -> None:
    """
    Update Related Accounts
    """
    if created:
        instance.update_accounts()
