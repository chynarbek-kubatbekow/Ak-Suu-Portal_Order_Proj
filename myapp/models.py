from django.db import models


class NewsItem(models.Model):
    CATEGORY_ADMISSION = "\u041f\u043e\u0441\u0442\u0443\u043f\u043b\u0435\u043d\u0438\u0435"
    CATEGORY_PARTNERSHIP = "\u041f\u0430\u0440\u0442\u043d\u0451\u0440\u0441\u0442\u0432\u0430"
    CATEGORY_DEVELOPMENT = "\u0420\u0430\u0437\u0432\u0438\u0442\u0438\u0435"

    CATEGORY_CHOICES = [
        (CATEGORY_ADMISSION, CATEGORY_ADMISSION),
        (CATEGORY_PARTNERSHIP, CATEGORY_PARTNERSHIP),
        (CATEGORY_DEVELOPMENT, CATEGORY_DEVELOPMENT),
    ]

    title = models.CharField("\u0437\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a", max_length=220)
    category = models.CharField("\u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f", max_length=40, choices=CATEGORY_CHOICES)
    date = models.CharField("\u0434\u0430\u0442\u0430 \u043d\u0430 \u0441\u0430\u0439\u0442\u0435", max_length=80)
    text = models.TextField("\u0442\u0435\u043a\u0441\u0442")
    image = models.CharField(
        "\u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u0438\u0437 static",
        max_length=220,
        blank=True,
        default="myapp/images/content/ak-suu-kutbilim-visit-opt.webp",
        help_text=(
            "\u041d\u0430\u043f\u0440\u0438\u043c\u0435\u0440: myapp/images/content/ak-suu-kutbilim-visit-opt.webp. "
            "\u041c\u043e\u0436\u043d\u043e \u043e\u0441\u0442\u0430\u0432\u0438\u0442\u044c \u043f\u0443\u0441\u0442\u044b\u043c, "
            "\u0435\u0441\u043b\u0438 \u0437\u0430\u0433\u0440\u0443\u0436\u0435\u043d\u043e \u0444\u043e\u0442\u043e \u043d\u0438\u0436\u0435."
        ),
    )
    image_file = models.ImageField(
        "\u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044c \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435",
        upload_to="news/",
        blank=True,
        help_text=(
            "\u0414\u043b\u044f \u043d\u043e\u0432\u044b\u0445 \u043d\u043e\u0432\u043e\u0441\u0442\u0435\u0439 "
            "\u0443\u0434\u043e\u0431\u043d\u0435\u0435 \u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044c "
            "\u0444\u043e\u0442\u043e \u0437\u0434\u0435\u0441\u044c. \u041e\u043d\u043e \u0431\u0443\u0434\u0435\u0442 "
            "\u043f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c\u0441\u044f \u0432\u043c\u0435\u0441\u0442\u043e "
            "static-\u043f\u0443\u0442\u0438 \u0432\u044b\u0448\u0435."
        ),
    )
    order = models.PositiveIntegerField("\u043f\u043e\u0440\u044f\u0434\u043e\u043a", default=100)
    is_published = models.BooleanField("\u043e\u043f\u0443\u0431\u043b\u0438\u043a\u043e\u0432\u0430\u043d\u043e", default=True)
    created_at = models.DateTimeField("\u0441\u043e\u0437\u0434\u0430\u043d\u043e", auto_now_add=True)
    updated_at = models.DateTimeField("\u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u043e", auto_now=True)

    class Meta:
        verbose_name = "\u043d\u043e\u0432\u043e\u0441\u0442\u044c \u043b\u0438\u0446\u0435\u044f"
        verbose_name_plural = "\u043d\u043e\u0432\u043e\u0441\u0442\u0438 \u043b\u0438\u0446\u0435\u044f"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title
