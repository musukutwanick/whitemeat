"""Give the homepage's Equipment/Cages slide and Masterclass slide their
autoplaying videos (cage.mp4 and master.mp4 respectively)."""
from django.db import migrations


def forwards(apps, schema_editor):
    HeroSlide = apps.get_model("frontend", "HeroSlide")
    HeroSlide.objects.filter(page="home", order=3).update(background_video_filename="cage.mp4")
    HeroSlide.objects.filter(page="home", order=4).update(background_video_filename="master.mp4")


def backwards(apps, schema_editor):
    HeroSlide = apps.get_model("frontend", "HeroSlide")
    HeroSlide.objects.filter(page="home", order__in=[3, 4]).update(background_video_filename="")


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0031_reset_butchery_products"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
