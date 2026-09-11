"""Seed starter Whitemeat Butchery products so the page isn't empty.
All fields (price, unit, description, availability) are editable in admin
under Butchery products. Prices are indicative - update them. Reversible."""
from django.db import migrations

PRODUCTS = [
    dict(
        name="Whole Rabbit", slug="whole-rabbit", category="whole", order=1,
        description="Whole dressed rabbit, cleaned and ready to cook. Farm-fresh, approx. 1.2-1.5 kg.",
        price="12.00", unit="each", stock_note="Fresh daily",
        image_filename="menu/full-rabbit.jpg", image_alt="Whole dressed rabbit",
        is_featured=True,
    ),
    dict(
        name="Half Rabbit", slug="half-rabbit", category="whole", order=2,
        description="Half a dressed rabbit - ideal for smaller households or a quick braai.",
        price="6.50", unit="each", stock_note="Fresh daily",
        image_filename="menu/half-rabbit.jpg", image_alt="Half rabbit portion",
    ),
    dict(
        name="Rabbit Portions Pack", slug="rabbit-portions-pack", category="portions", order=3,
        description="Mixed bone-in rabbit portions - legs, saddle and ribs - trimmed and vacuum-sealed.",
        price="8.00", unit="500g pack", stock_note="Frozen",
        image_filename="menu/rabbit-curry.jpg", image_alt="Rabbit meat portions",
    ),
    dict(
        name="Rabbit Mince", slug="rabbit-mince", category="value", order=4,
        description="Freshly minced rabbit - lean and versatile for burgers, meatballs and sauces. No additives.",
        price="9.00", unit="per kg", stock_note="Fresh daily",
        image_alt="Fresh rabbit mince",
    ),
    dict(
        name="Rabbit Sausages", slug="rabbit-sausages", category="value", order=5,
        description="Rabbit sausages in natural casing, lightly seasoned with herbs.",
        price="7.50", unit="500g pack", stock_note="Frozen",
        image_alt="Rabbit sausages",
    ),
    dict(
        name="Bulk & Wholesale Order", slug="bulk-wholesale-order", category="bulk", order=6,
        description="Wholesale rabbit meat for restaurants, butcheries and events, straight from our farms. "
                    "Minimum 20 kg - add to cart and we'll send a quote.",
        price="8.50", unit="per kg (min 20 kg)", stock_note="Pre-order",
        image_filename="house.jpg", image_alt="Wholesale rabbit meat",
    ),
]


def seed(apps, schema_editor):
    ButcheryProduct = apps.get_model("frontend", "ButcheryProduct")
    if not ButcheryProduct.objects.exists():
        for data in PRODUCTS:
            ButcheryProduct.objects.create(**data)


def unseed(apps, schema_editor):
    ButcheryProduct = apps.get_model("frontend", "ButcheryProduct")
    ButcheryProduct.objects.filter(slug__in=[p["slug"] for p in PRODUCTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0019_butcheryproduct"),
    ]
    operations = [migrations.RunPython(seed, unseed)]
