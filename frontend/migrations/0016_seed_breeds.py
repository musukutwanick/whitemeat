"""Seed the two breeds that were previously hardcoded into breeding.html
(New Zealand White, Californian) so the now-dynamic Breeding Stock page
isn't empty. Price is a placeholder - update it in admin. Reversible."""
from django.db import migrations

BREEDS = [
    dict(
        name="New Zealand White",
        slug="new-zealand-white",
        tagline="The gold standard of commercial rabbit farming",
        description=(
            "Known for rapid growth, excellent feed conversion, and superior meat quality "
            "with distinctive white fur and red eyes."
        ),
        characteristics=(
            "Mature weight: 4-5.5 kg\n"
            "Excellent mothering ability\n"
            "Fast growth rate to market weight\n"
            "Superior feed conversion ratio\n"
            "Hardy and disease resistant\n"
            "Large litter sizes (8-12 kits)\n"
            "Premium meat quality"
        ),
        price="25.00",
        image_filename="new.jpg",
        image_alt="New Zealand White rabbit",
        is_featured=True,
        order=1,
    ),
    dict(
        name="Californian",
        slug="californian",
        tagline="Superior meat-to-bone ratio, calm temperament",
        description=(
            "Distinctive white rabbits with black points on ears, nose, feet and tail. "
            "Excellent for meat production with a superior muscle-to-bone ratio."
        ),
        characteristics=(
            "Mature weight: 4-5 kg\n"
            "Excellent meat-to-bone ratio\n"
            "Calm and easy to handle\n"
            "Good feed efficiency\n"
            "Distinctive colour pattern\n"
            "Reliable breeding performance\n"
            "Market-preferred carcass quality"
        ),
        price="25.00",
        image_filename="carli.jpg",
        image_alt="Californian rabbit",
        is_featured=False,
        order=2,
    ),
]


def seed(apps, schema_editor):
    Breed = apps.get_model("frontend", "Breed")
    if not Breed.objects.exists():
        for data in BREEDS:
            Breed.objects.create(**data)


def unseed(apps, schema_editor):
    Breed = apps.get_model("frontend", "Breed")
    Breed.objects.filter(slug__in=["new-zealand-white", "californian"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0015_breed"),
    ]
    operations = [migrations.RunPython(seed, unseed)]
