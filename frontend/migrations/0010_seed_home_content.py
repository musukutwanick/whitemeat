"""Seed the singleton SiteSettings row plus starter hero slides and
homepage service cards so the redesigned homepage is never empty on a
fresh database. Fully reversible and idempotent-friendly (only creates
rows that don't exist yet)."""
from django.db import migrations


HERO_SLIDES = [
    dict(
        heading="Pioneering Zimbabwe's white meat revolution",
        subheading=(
            "Premium breeding stock, international-standard equipment, expert training "
            "and a guaranteed market for your rabbit produce - from farm to table."
        ),
        background_image_filename="home.jpeg",
        image_alt="Rabbit farming at The White Meat Company",
        cta_primary_label="Explore what we do", cta_primary_url="#about",
        cta_secondary_label="Book a masterclass", cta_secondary_url="/masterclass/",
        overlay="dark", order=1,
    ),
    dict(
        heading="Pure, health-certified breeding stock",
        subheading="New Zealand White and Californian rabbits from certified bloodlines.",
        background_image_filename="new.jpg",
        image_alt="Breeding stock rabbits",
        cta_primary_label="View breeds", cta_primary_url="/breeding/",
        overlay="dark", order=2,
    ),
    dict(
        heading="International-standard cages & accessories",
        subheading="Galvanised steel systems with feeding and waste management built in.",
        background_image_filename="equip.jpg",
        image_alt="Rabbit farm cages and equipment",
        cta_primary_label="Browse equipment", cta_primary_url="/equipment/",
        overlay="dark", order=3,
    ),
    dict(
        heading="The Rabbitry Masterclass",
        subheading="Two days of setup, nutrition, health, breeding and business planning.",
        background_image_filename="master.jpg",
        image_alt="Rabbitry masterclass training",
        cta_primary_label="See dates & book", cta_primary_url="/masterclass/",
        overlay="dark", order=4,
    ),
    dict(
        heading="The Rabbit Hole Bar & Grill",
        subheading="White-meat cuisine done properly - full rabbit, curries, stews and sides.",
        background_image_filename="restraurant.jpg",
        image_alt="The Rabbit Hole Bar and Grill",
        cta_primary_label="Visit Rabbit Hole", cta_primary_url="/rabbithole/",
        overlay="dark", order=5,
    ),
    dict(
        heading="Whitemeat Butchery",
        subheading="Fresh rabbit cuts and portions, straight from our farms.",
        background_image_filename="pagomo.jpg",
        image_alt="Whitemeat Butchery products",
        cta_primary_label="Shop the butchery", cta_primary_url="/butchery/",
        overlay="dark", order=6,
    ),
]

SERVICE_CARDS = [
    dict(title="Rabbit Farm Equipment", icon="equipment", url="/equipment/", order=1,
         description="Galvanised cages plus drinkers, feeders and nesting boxes."),
    dict(title="Outgrower Initiatives", icon="outgrower", url="/outgrowers/", order=2,
         description="Certified training and a guaranteed buy-back market."),
    dict(title="Breeding Stock", icon="breeding", url="/breeding/", order=3,
         description="Pure New Zealand White and Californian bloodlines."),
    dict(title="Masterclass", icon="masterclass", url="/masterclass/", order=4,
         description="Zimbabwe's most complete rabbitry training."),
    dict(title="Rabbit Hole", icon="restaurant", url="/rabbithole/", order=5,
         description="White-meat cuisine at our Bar & Grill."),
    dict(title="Whitemeat Butchery", icon="butchery", url="/butchery/", order=6,
         description="Fresh rabbit cuts and portions."),
]


def seed(apps, schema_editor):
    SiteSettings = apps.get_model("frontend", "SiteSettings")
    HeroSlide = apps.get_model("frontend", "HeroSlide")
    HomeServiceCard = apps.get_model("frontend", "HomeServiceCard")

    SiteSettings.objects.get_or_create(pk=1)

    if not HeroSlide.objects.exists():
        for data in HERO_SLIDES:
            HeroSlide.objects.create(**data)

    if not HomeServiceCard.objects.exists():
        for data in SERVICE_CARDS:
            HomeServiceCard.objects.create(**data)


def unseed(apps, schema_editor):
    HeroSlide = apps.get_model("frontend", "HeroSlide")
    HomeServiceCard = apps.get_model("frontend", "HomeServiceCard")
    SiteSettings = apps.get_model("frontend", "SiteSettings")
    HeroSlide.objects.all().delete()
    HomeServiceCard.objects.all().delete()
    SiteSettings.objects.filter(pk=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0009_heroslide_homeservicecard_sitesettings"),
    ]
    operations = [
        migrations.RunPython(seed, unseed),
    ]
