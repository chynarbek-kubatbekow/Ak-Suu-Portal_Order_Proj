from django.db import models


class NewsItem(models.Model):
    CATEGORY_ADMISSION = "Поступление"
    CATEGORY_PARTNERSHIP = "Партнёрства"
    CATEGORY_DEVELOPMENT = "Развитие"

    CATEGORY_CHOICES = [
        (CATEGORY_ADMISSION, CATEGORY_ADMISSION),
        (CATEGORY_PARTNERSHIP, CATEGORY_PARTNERSHIP),
        (CATEGORY_DEVELOPMENT, CATEGORY_DEVELOPMENT),
    ]

    title = models.CharField("заголовок", max_length=220)
    category = models.CharField("категория", max_length=40, choices=CATEGORY_CHOICES)
    date = models.CharField("дата на сайте", max_length=80)
    text = models.TextField("текст")
    image = models.CharField(
        "изображение из static",
        max_length=220,
        default="myapp/images/content/ak-suu-kutbilim-visit-opt.webp",
        help_text="Например: myapp/images/content/ak-suu-kutbilim-visit-opt.webp",
    )
    order = models.PositiveIntegerField("порядок", default=100)
    is_published = models.BooleanField("опубликовано", default=True)
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    class Meta:
        verbose_name = "новость лицея"
        verbose_name_plural = "новости лицея"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title
