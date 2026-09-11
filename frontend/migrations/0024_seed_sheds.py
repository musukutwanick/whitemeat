"""Seed a starter rabbit shed so the /sheds/ page isn't empty on launch.
Editable in the dashboard under Sheds. Reversible."""
from django.db import migrations

SHEDS = [
    dict(
        name="Standard Rabbit Shed", slug="standard-rabbit-shed", category="complete", order=1,
        description="A complete timber-framed rabbit house built for commercial production - "
                    "weatherproof, well ventilated and sized to hold a full run of breeder and "
                    "weaner cages. Supplied and installed on site.",
        features="Treated gum-pole and timber frame\n"
                 "IBR galvanised roof sheeting\n"
                 "Mesh sides for year-round ventilation\n"
                 "Lockable access door\n"
                 "Concrete-ready footprint with drainage fall\n"
                 "Fits multiple 12Sdx / 6Sdx cage units",
        price="2500.00", capacity="Houses a full breeder + weaner cage run",
        image_filename="house.jpg", image_alt="Timber rabbit shed with galvanised roof",
        is_featured=True,
    ),
]


def seed(apps, schema_editor):
    Shed = apps.get_model("frontend", "Shed")
    if not Shed.objects.exists():
        for data in SHEDS:
            Shed.objects.create(**data)


def unseed(apps, schema_editor):
    Shed = apps.get_model("frontend", "Shed")
    Shed.objects.filter(slug__in=[s["slug"] for s in SHEDS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0023_shed"),
    ]
    operations = [migrations.RunPython(seed, unseed)]
