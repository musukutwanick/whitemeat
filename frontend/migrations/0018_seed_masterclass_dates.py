"""Seed a handful of upcoming Masterclass dates (2nd Saturday of the next
6 months) so the calendar isn't empty on a fresh install. Purely starter
data - admins add/edit the real yearly calendar in Django admin under
Masterclass dates. Reversible."""
import calendar
from datetime import date

from django.db import migrations
from django.utils import timezone


def _second_saturday(year, month):
    cal = calendar.Calendar()
    saturdays = [
        d for d in cal.itermonthdates(year, month)
        if d.month == month and d.weekday() == calendar.SATURDAY
    ]
    return saturdays[1] if len(saturdays) > 1 else saturdays[0]


def seed(apps, schema_editor):
    MasterclassDate = apps.get_model("frontend", "MasterclassDate")
    MasterclassEvent = apps.get_model("frontend", "MasterclassEvent")
    if MasterclassDate.objects.exists():
        return

    event = MasterclassEvent.objects.order_by("-id").first()

    today = timezone.localdate()
    year, month = today.year, today.month
    for i in range(6):
        m = month + i
        y = year + (m - 1) // 12
        m = ((m - 1) % 12) + 1
        d = _second_saturday(y, m)
        if d <= today:
            continue
        MasterclassDate.objects.get_or_create(
            date=d,
            defaults=dict(event=event, capacity=20, is_active=True, location="Belvedere, Harare"),
        )


def unseed(apps, schema_editor):
    # Starter data only - safe to leave in place on rollback since admins
    # may have already booked against these dates. No-op.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0017_masterclassevent_certification_fee_and_more"),
    ]
    operations = [migrations.RunPython(seed, unseed)]
