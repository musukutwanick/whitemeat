"""Rabbit Hole - Main Branch and Rabbit Hole - PaGomo held an identical
24-item menu (same names, prices, categories) - Main Branch's copies just
had no uploaded photos, while Pagomo's did. /rabbithole/ and /pagomo/ have
only ever read from the Pagomo branch, so Main Branch's items were dead,
invisible duplicates.

Deletes Main Branch's 24 menu items (Pagomo's matching, better copies are
untouched) and deactivates the branch so it drops out of the admin's
branch picker (RestaurantBranch.objects.filter(is_active=True)) - without
deleting the branch record itself. Reversible (reactivates the branch;
the deleted menu items are not restored)."""
from django.db import migrations

MAIN_SLUG = "rabbit-hole-main"


def forwards(apps, schema_editor):
    RestaurantBranch = apps.get_model("frontend", "RestaurantBranch")
    MenuItem = apps.get_model("frontend", "MenuItem")
    main = RestaurantBranch.objects.filter(slug=MAIN_SLUG).first()
    if not main:
        return
    MenuItem.objects.filter(branch=main).delete()
    main.is_active = False
    main.save(update_fields=["is_active"])


def backwards(apps, schema_editor):
    RestaurantBranch = apps.get_model("frontend", "RestaurantBranch")
    RestaurantBranch.objects.filter(slug=MAIN_SLUG).update(is_active=True)


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0034_set_payment_details"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
