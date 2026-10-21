from django.db import migrations, models


COMPANY_HOURS = "Monday to Friday: 8:00am to 5:00pm\nSaturday: 8:00am to 3:00pm"
RABBIT_HOLE_HOURS = "Monday to Thursday: 9:30am to 7:00pm\nFriday to Sunday: 12:30pm to 10:00pm"


def set_hours(apps, schema_editor):
    SiteSettings = apps.get_model("frontend", "SiteSettings")
    settings = SiteSettings.objects.filter(pk=1).first()
    if settings:
        settings.business_hours = COMPANY_HOURS
        settings.rabbit_hole_hours = RABBIT_HOLE_HOURS
        settings.save(update_fields=["business_hours", "rabbit_hole_hours"])


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0035_retire_main_branch"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="rabbit_hole_hours",
            field=models.TextField(
                blank=True,
                default=RABBIT_HOLE_HOURS,
                help_text="Rabbit Hole restaurant opening hours",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="business_hours",
            field=models.TextField(
                blank=True,
                default=COMPANY_HOURS,
            ),
        ),
        migrations.RunPython(set_hours, migrations.RunPython.noop),
    ]
