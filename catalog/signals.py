from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ContentSubmission
from .submission_product import try_create_product_for_submission


@receiver(post_save, sender=ContentSubmission)
def create_catalog_product_on_submission_approval(sender, instance: ContentSubmission, **kwargs) -> None:
    """При статусе «Одобрено» создаётся карточка сервиса (если ещё не создана)."""
    try_create_product_for_submission(instance.pk)
