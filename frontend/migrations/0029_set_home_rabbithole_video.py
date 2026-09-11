"""Give the homepage's Rabbit Hole slide its autoplaying video (hole.mp4)."""
from django.db import migrations


def forwards(apps, schema_editor):
    HeroSlide = apps.get_model("frontend", "HeroSlide")
    HeroSlide.objects.filter(page="home", order=5).update(background_video_filename="hole.mp4")


def backwards(apps, schema_editor):
    HeroSlide = apps.get_model("frontend", "HeroSlide")
    HeroSlide.objects.filter(page="home", order=5).update(background_video_filename="")


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0028_fix_home_hero_media"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
