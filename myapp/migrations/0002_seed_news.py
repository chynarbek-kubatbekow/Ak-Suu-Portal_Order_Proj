# Generated manually for initial editable news.

from django.db import migrations


INITIAL_NEWS = [{'category': 'Поступление',
  'date': '11 июня 2026',
  'title': 'Старт приёмной кампании РИТПЛ «Ак-Суу»',
  'text': 'Лицей объявил набор на бесплатное обучение для выпускников 9 и 11 классов. Документы принимаются до '
          'середины августа, финальное зачисление планируется к 25-27 августа.',
  'image': 'myapp/images/content/ak-suu-lyceum-visit-opt.webp'},
 {'category': 'Развитие',
  'date': '10 июня 2026',
  'title': 'Государственная инспекция кампуса и учебной инфраструктуры',
  'text': 'Рабочая группа проверила готовность SMART-классов, кулинарной студии, IT-полигона и учебного ресторана к '
          'запуску образовательного процесса.',
  'image': 'myapp/images/content/ak-suu-kutbilim-visit-opt.webp'},
 {'category': 'Партнёрства',
  'date': 'июнь 2026',
  'title': 'Соглашение с инвесторами и «Ала-Тоо Резорт»',
  'text': 'Партнёры обсуждают квоты, практику и приоритетное трудоустройство выпускников для туристического кластера '
          'Ак-Суйского района.',
  'image': 'myapp/images/content/issyk-kul-aerial-road-opt.webp'},
 {'category': 'Развитие',
  'date': '27 апреля 2026',
  'title': 'Новый юридический статус лицея',
  'text': 'РИТПЛ «Ак-Суу» прошёл государственную перерегистрацию и начал развитие как инновационный центр подготовки '
          'кадров для туризма и гостеприимства.',
  'image': 'myapp/images/content/issyk-kul-cholpon-ata-opt.webp'},
 {'category': 'Партнёрства',
  'date': '2026',
  'title': 'Региональные инициативы и конкурс «Жаш турист»',
  'text': 'Лицей становится площадкой для событий, которые вовлекают молодёжь в культуру ответственного туризма, '
          'сервиса и бережного отношения к природе Кыргызстана.',
  'image': 'myapp/images/content/issyk-kul-yurt-rinat-opt.webp'}]


def seed_news(apps, schema_editor):
    NewsItem = apps.get_model("myapp", "NewsItem")
    if NewsItem.objects.exists():
        return
    for index, item in enumerate(INITIAL_NEWS, start=1):
        NewsItem.objects.create(
            title=item["title"],
            category=item["category"],
            date=item["date"],
            text=item["text"],
            image=item["image"],
            order=index * 10,
            is_published=True,
        )


def unseed_news(apps, schema_editor):
    NewsItem = apps.get_model("myapp", "NewsItem")
    titles = [item["title"] for item in INITIAL_NEWS]
    NewsItem.objects.filter(title__in=titles).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_news, unseed_news),
    ]
