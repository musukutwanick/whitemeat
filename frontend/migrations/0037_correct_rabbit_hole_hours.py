from django.db import migrations, models


RABBIT_HOLE_HOURS = "Monday to Thursday: 9:30am to 7:00pm\nFriday to Sunday: 9:30am to 10:00pm"


def correct_hours(apps, schema_editor):
    SiteSettings = apps.get_model("frontend", "SiteSettings")
    SiteSettings.objects.filter(pk=1).update(rabbit_hole_hours=RABBIT_HOLE_HOURS)


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0036_site_settings_hours"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="rabbit_hole_hours",
            field=models.TextField(
                blank=True,
                default=RABBIT_HOLE_HOURS,
                help_text="Rabbit Hole restaurant opening hours",
            ),
        ),
        migrations.RunPython(correct_hours, migrations.RunPython.noop),
    ]
