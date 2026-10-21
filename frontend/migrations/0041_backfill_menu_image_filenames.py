from django.db import migrations


MENU_IMAGES = {
    "Full Rabbit": "menu/full-rabbit.jpg",
    "Half Rabbit": "menu/half-rabbit.jpg",
    "Bream": "menu/bream.jpg",
    "Full chicken": "menu/full-chicken.jpg",
    "Country style": "menu/country-style.jpg",
    "Pork chop": "menu/pork-chop.jpg",
    "Grilled Lamb": "menu/grilled-lamb.jpg",
    "Rabbit curry": "menu/rabbit-curry.jpg",
    "Knuckle bones": "menu/knucklebones.jpg",
    "Maguru": "menu/maguru.jpg",
    "Oxtail": "menu/oxtail.jpg",
    "Beef stew": "menu/beef-stew.jpg",
    "Roadrunner": "menu/roadrunner-chicken.jpg",
    "Haifiridzi": "menu/haifiridzi.jpg",
    "Stewed Lamb": "menu/stewed-lamb.jpg",
    "Zviyo": "menu/zviyo.jpg",
    "Mhunga": "menu/mhunga.jpg",
    "Mapfunde": "menu/mapfunde.jpg",
    "Rice dovi": "menu/rice-dovi.jpg",
    "Fries / chips": "menu/fries.jpg",
    "Plain rice": "menu/plain-rice.jpg",
    "Braai salad": "menu/braai-salad.jpg",
    "Mugaiwa": "menu/mugaiwa.jpg",
    "Samoosas (rabbit / beef)": "menu/samoosas.jpg",
}


def backfill_menu_images(apps, schema_editor):
    MenuItem = apps.get_model("frontend", "MenuItem")
    for name, filename in MENU_IMAGES.items():
        MenuItem.objects.filter(name__iexact=name).update(image_filename=filename)


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0040_use_cage3_for_equipment_images"),
    ]

    operations = [
        migrations.RunPython(backfill_menu_images, migrations.RunPython.noop),
    ]
