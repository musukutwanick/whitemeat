from decimal import Decimal

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


def seed_local_menu_images(apps, schema_editor):
    RestaurantBranch = apps.get_model("frontend", "RestaurantBranch")
    MenuCategory = apps.get_model("frontend", "MenuCategory")
    MenuItem = apps.get_model("frontend", "MenuItem")

    branch = RestaurantBranch.objects.filter(
        slug__in=["rabbit-hole-pagomo", "pagomo"],
        is_active=True,
    ).first()
    if not branch:
        return

    for name, image_filename in MENU_IMAGES.items():
        MenuItem.objects.filter(branch=branch, name=name).update(
            image_filename=image_filename,
        )

    category, _ = MenuCategory.objects.get_or_create(
        slug="grills",
        defaults={"name": "Grills", "order": 1},
    )
    country_style = MenuItem.objects.filter(
        branch=branch,
        name__iexact="Country style",
    ).first()
    if not country_style:
        MenuItem.objects.create(
            branch=branch,
            name="Country style",
            description="Borewors sausage grilled with local spices and served hot.",
            price=Decimal("10.00"),
            category=category,
            image_filename="menu/country-style.jpg",
            is_available=True,
        )
    else:
        country_style.image_filename = "menu/country-style.jpg"
        country_style.price = Decimal("10.00")
        country_style.save(update_fields=["image_filename", "price"])


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0037_correct_rabbit_hole_hours"),
    ]

    operations = [
        migrations.RunPython(seed_local_menu_images, migrations.RunPython.noop),
    ]
