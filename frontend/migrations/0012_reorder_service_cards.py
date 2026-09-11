"""Reorder the homepage service strip to the sequence requested by the
client:  Breeding stock, Rabbit Farm Equipment, Masterclass, Outgrower
Initiatives, Rabbit Hole, Whitemeat Butchery.

Matches on the stable `icon` key so it still works if titles were edited
in the admin. Idempotent and reversible.
"""
from django.db import migrations

NEW_ORDER = {
    "breeding": 1,
    "equipment": 2,
    "masterclass": 3,
    "outgrower": 4,
    "restaurant": 5,
    "butchery": 6,
}

OLD_ORDER = {
    "equipment": 1,
    "outgrower": 2,
    "breeding": 3,
    "masterclass": 4,
    "restaurant": 5,
    "butchery": 6,
}


def _apply(model, mapping):
    for icon_key, order in mapping.items():
        model.objects.filter(icon=icon_key).update(order=order)


def forwards(apps, schema_editor):
    _apply(apps.get_model("frontend", "HomeServiceCard"), NEW_ORDER)


def backwards(apps, schema_editor):
    _apply(apps.get_model("frontend", "HomeServiceCard"), OLD_ORDER)


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0011_alter_homeservicecard_icon_alter_homeservicecard_url"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
