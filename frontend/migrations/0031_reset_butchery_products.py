"""The Whitemeat Butchery is repositioning around species categories
(Fish, Chicken, Rabbit Meat) instead of cut-type categories. Clear out the
old whole/portions/value/offal/bulk starter lineup and seed a single
starter product - Rabbit Meat, $8.90/kg - the only one stocked for now.
Fish and Chicken categories exist on the model, ready for products to be
added in the dashboard once they're available. Reversible."""
from django.db import migrations

OLD_SLUGS = [
    "whole-rabbit", "half-rabbit", "rabbit-portions-pack",
    "rabbit-mince", "rabbit-sausages", "bulk-wholesale-order",
]

NEW_PRODUCT = dict(
    name="Rabbit Meat", slug="rabbit-meat", category="rabbit", order=1,
    description="Fresh, dressed rabbit meat - lean, high in protein and low in cholesterol. "
                "Traceable to our own outgrower farms, no hormones or additives.",
    price="8.90", unit="per kg", stock_note="Fresh daily",
    image_filename="rabbi.jpg", image_alt="Fresh rabbit meat portions",
    is_featured=True,
)


def forwards(apps, schema_editor):
    ButcheryProduct = apps.get_model("frontend", "ButcheryProduct")
    ButcheryProduct.objects.filter(slug__in=OLD_SLUGS).delete()
    if not ButcheryProduct.objects.filter(slug=NEW_PRODUCT["slug"]).exists():
        ButcheryProduct.objects.create(**NEW_PRODUCT)


def backwards(apps, schema_editor):
    ButcheryProduct = apps.get_model("frontend", "ButcheryProduct")
    ButcheryProduct.objects.filter(slug=NEW_PRODUCT["slug"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0030_alter_butcheryproduct_category"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
