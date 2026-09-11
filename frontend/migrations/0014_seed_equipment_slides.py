"""Seed starter slides for the Rabbit Farm Equipment page slider so it is
never empty. Uses bundled static images. Reversible."""
from django.db import migrations

EQUIPMENT_SLIDES = [
    dict(
        page="equipment", order=1, overlay="dark",
        heading="International-standard rabbit cages",
        subheading=(
            "Galvanised steel breeder and weaner systems, complete with drinkers, "
            "feed troughs and an advanced manure & urine collection system."
        ),
        background_image_filename="cage3.jpg",
        image_alt="Galvanised steel rabbit breeder cage",
        cta_primary_label="View cages", cta_primary_url="#cages",
    ),
    dict(
        page="equipment", order=2, overlay="dark",
        heading="Accessories for a productive rabbitry",
        subheading="Nesting boxes, water bottles, feeders, collection bottles, hay and pellets.",
        background_image_filename="equip.jpg",
        image_alt="Rabbit farming accessories",
        cta_primary_label="View accessories", cta_primary_url="#accessories",
    ),
    dict(
        page="equipment", order=3, overlay="dark",
        heading="Built for Zimbabwe's commercial farmers",
        subheading="Durable construction, innovative drainage, and full installation on delivery.",
        background_image_filename="cage2.jpg",
        image_alt="Rabbit cage with dimensions",
    ),
]


def seed(apps, schema_editor):
    HeroSlide = apps.get_model("frontend", "HeroSlide")
    if not HeroSlide.objects.filter(page="equipment").exists():
        for data in EQUIPMENT_SLIDES:
            HeroSlide.objects.create(**data)


def unseed(apps, schema_editor):
    HeroSlide = apps.get_model("frontend", "HeroSlide")
    HeroSlide.objects.filter(page="equipment").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0013_alter_heroslide_options_heroslide_page"),
    ]
    operations = [migrations.RunPython(seed, unseed)]
