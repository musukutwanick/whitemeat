from django.db import migrations


def use_cage3(apps, schema_editor):
    HeroSlide = apps.get_model("frontend", "HeroSlide")
    HeroSlide.objects.filter(
        background_image_filename__in=["equip.jpg", "equip.png"],
    ).update(background_image_filename="cage3.jpg")


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0039_update_country_style_description"),
    ]

    operations = [
        migrations.RunPython(use_cage3, migrations.RunPython.noop),
    ]
