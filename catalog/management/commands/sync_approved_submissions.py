from django.core.management.base import BaseCommand

from catalog.models import ContentSubmission
from catalog.submission_product import try_create_product_for_submission


class Command(BaseCommand):
    help = "Создаёт сервисы в каталоге для уже одобренных заявок без created_product."

    def handle(self, *args, **options):
        qs = ContentSubmission.objects.filter(
            status=ContentSubmission.Status.APPROVED,
            created_product__isnull=True,
        )
        n_ok = 0
        n_skip = 0
        for sub in qs.iterator():
            p = try_create_product_for_submission(sub.pk)
            if p:
                self.stdout.write(self.style.SUCCESS(f"{sub.public_code} → Product pk={p.pk} «{p.name}»"))
                n_ok += 1
            else:
                self.stdout.write(self.style.WARNING(f"{sub.public_code} — пропуск (см. логи / данные заявки)"))
                n_skip += 1
        self.stdout.write(self.style.NOTICE(f"Готово: создано {n_ok}, пропущено {n_skip}."))
