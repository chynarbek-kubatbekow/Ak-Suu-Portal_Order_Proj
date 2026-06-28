from django.db import migrations


OLD_TO_NEW = {
    "myapp/images/content/hotel-school-students-opt.webp": "myapp/images/content/ak-suu-lyceum-visit-opt.webp",
    "myapp/images/content/restaurant-kitchen-cooking-opt.webp": "myapp/images/content/hospitality-kitchen-opt.webp",
    "myapp/images/content/future-campus-opt.webp": "myapp/images/content/hotel-lobby-commons-opt.webp",
    "myapp/images/content/future-classroom-opt.webp": "myapp/images/content/culinary-class-commons-opt.webp",
}


def replace_images(apps, schema_editor):
    NewsItem = apps.get_model("myapp", "NewsItem")
    for old, new in OLD_TO_NEW.items():
        NewsItem.objects.filter(image=old).update(image=new)


def restore_images(apps, schema_editor):
    NewsItem = apps.get_model("myapp", "NewsItem")
    for old, new in OLD_TO_NEW.items():
        NewsItem.objects.filter(image=new).update(image=old)


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0002_seed_news"),
    ]

    operations = [
        migrations.RunPython(replace_images, restore_images),
    ]
