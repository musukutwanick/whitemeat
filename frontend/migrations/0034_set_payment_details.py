"""Populate SiteSettings with the real EcoCash / bank / remittance details
so they show up in the checkout payment-info panel (cart checkout modal +
the Pagomo reservation form) wherever a customer is about to pay.
Editable afterwards in Django admin or the staff dashboard - Site
settings -> Payment."""
from django.db import migrations

BANK_DETAILS = """CBZ Nostro (USD)
The White Meat Company
Branch Code: 661
Account Number: 62739740014

CBZ Local (ZWG)
The White Meat Company
Branch Code: 661
Account Number: 62739740024

NBS Nostro (USD)
Account name: The White Meat
Branch code: 3253
Account number: 3253014903451

NBS Local (ZWG)
Account name: The White Meat
Branch code: 3253
Account No.: 014903001

Mukuru / World Remit
Bright Tozivei Makuchete
ID No. 63-832798A07
No. 1793 Tredgold Drive, Belvedere"""


def forwards(apps, schema_editor):
    SiteSettings = apps.get_model("frontend", "SiteSettings")
    s, _ = SiteSettings.objects.get_or_create(pk=1)
    if not s.payment_ecocash_number:
        s.payment_ecocash_number = "263772333369"
    if not s.payment_ecocash_name:
        s.payment_ecocash_name = "Bright Makuchete"
    if not s.payment_bank_details:
        s.payment_bank_details = BANK_DETAILS
    s.save()


def backwards(apps, schema_editor):
    SiteSettings = apps.get_model("frontend", "SiteSettings")
    SiteSettings.objects.filter(pk=1).update(
        payment_ecocash_number="", payment_ecocash_name="", payment_bank_details="",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0033_alter_order_source"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
