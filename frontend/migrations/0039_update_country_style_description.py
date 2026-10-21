from django.db import migrations


DESCRIPTION = "Borewors sausage grilled with local spices and served hot."


def update_country_style(apps, schema_editor):
    MenuItem = apps.get_model("frontend", "MenuItem")
    MenuItem.objects.filter(
        branch__slug__in=["rabbit-hole-pagomo", "pagomo"],
        name__iexact="Country style",
    ).update(
        description=DESCRIPTION,
        price="10.00",
        image_filename="menu/country-style.jpg",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0038_seed_local_menu_images"),
    ]

    operations = [
        migrations.RunPython(update_country_style, migrations.RunPython.noop),
    ]
