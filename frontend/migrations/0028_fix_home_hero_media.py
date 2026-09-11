"""Fix the homepage hero slider:

- The Whitemeat Butchery slide was seeded with pagomo.jpg (a Rabbit Hole
  Pagomo branch photo) - that image belongs on the Rabbit Hole slide, not
  Butchery. Move it there (replacing restraurant.jpg).
- Give the Whitemeat Butchery slide a neutral placeholder image instead,
  and an autoplaying video (but.mp4) in place of a static photo.
- Give the Breeding Stock ("View breeds") slide an autoplaying video
  (breed.mp4) too, keeping new.jpg as the poster/fallback.

Only touches rows that still hold the original seeded values, so it's a
no-op if these slides have since been edited in the dashboard.
"""
from django.db import migrations

CHANGES = [
    # order, only-if-image-still, new_image, new_video
    (5, "restraurant.jpg", "pagomo.jpg", None),
    (6, "pagomo.jpg", "default-menu-item.jpg", "but.mp4"),
    (2, "new.jpg", "new.jpg", "breed.mp4"),
]


def forwards(apps, schema_editor):
    HeroSlide = apps.get_model("frontend", "HeroSlide")
    for order, only_if, new_image, new_video in CHANGES:
        slide = HeroSlide.objects.filter(
            page="home", order=order, background_image_filename=only_if,
        ).first()
        if not slide:
            continue
        slide.background_image_filename = new_image
        if new_video:
            slide.background_video_filename = new_video
        slide.save(update_fields=["background_image_filename", "background_video_filename"])


def backwards(apps, schema_editor):
    HeroSlide = apps.get_model("frontend", "HeroSlide")
    originals = {5: "restraurant.jpg", 6: "pagomo.jpg", 2: "new.jpg"}
    for order, image in originals.items():
        HeroSlide.objects.filter(page="home", order=order).update(
            background_image_filename=image, background_video_filename="",
        )


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0027_heroslide_background_video_and_more"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
