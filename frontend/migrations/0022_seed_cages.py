"""Seed the two cage systems that were previously hard-coded into
templates/cages.html so the page keeps its content after it switches to
being database-driven. All fields are editable in the dashboard under
Cages. Reversible."""
from django.db import migrations

CAGES = [
    dict(
        name="12Sdx Breeders Cage", slug="12sdx-breeders-cage", category="breeders", order=1,
        description="Professional breeding system with 12 compartments designed to house 1 buck "
                    "and 11 does for optimal breeding efficiency.",
        features="12 compartments: 1 buck + 11 does\n"
                 "Galvanised steel construction\n"
                 "Integrated drinkers and feeding troughs\n"
                 "Manure & urine collection system",
        price="455.00", capacity="Houses 1 buck + 11 does",
        image_filename="cage3.jpg", image_alt="12Sdx Breeders Cage",
        is_featured=True,
    ),
    dict(
        name="6Sdx Weaners Cage", slug="6sdx-weaners-cage", category="weaners", order=2,
        description="High-capacity weaning system with 6 compartments designed to house up to "
                    "90 weaners for efficient growth management.",
        features="6 compartments, up to 90 weaners\n"
                 "Galvanised steel construction\n"
                 "Integrated drinkers and feeding troughs\n"
                 "Manure & urine collection system",
        price="455.00", capacity="Up to 90 weaners",
        image_filename="cage4.jpg", image_alt="6Sdx Weaners Cage",
    ),
]


def seed(apps, schema_editor):
    Cage = apps.get_model("frontend", "Cage")
    if not Cage.objects.exists():
        for data in CAGES:
            Cage.objects.create(**data)


def unseed(apps, schema_editor):
    Cage = apps.get_model("frontend", "Cage")
    Cage.objects.filter(slug__in=[c["slug"] for c in CAGES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0021_cage"),
    ]
    operations = [migrations.RunPython(seed, unseed)]
