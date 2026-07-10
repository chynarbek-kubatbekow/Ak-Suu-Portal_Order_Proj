# Copyright (c) 2026 Kubatbek uulu Chynarbek. All rights reserved.
# Proprietary software. See LICENSE for terms.
from django.test import TestCase
from django.urls import reverse

from .models import NewsItem
from .views import PAGES


class PublicPagesTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "новая культура туризма")

    def test_all_content_pages_render(self):
        for slug, page in PAGES.items():
            with self.subTest(slug=slug):
                response = self.client.get(reverse("page", args=[slug]))

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, page["title"])

    def test_all_content_pages_render_without_trailing_slash(self):
        for slug, page in PAGES.items():
            with self.subTest(slug=slug):
                response = self.client.get(f"/{slug}")

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, page["title"])

    def test_unknown_page_returns_404(self):
        response = self.client.get(reverse("page", args=["unknown"]))

        self.assertEqual(response.status_code, 404)

    def test_news_page_uses_published_database_news(self):
        NewsItem.objects.create(
            title="Admin Test News",
            category=NewsItem.CATEGORY_DEVELOPMENT,
            date="2026",
            text="Editable from Django admin.",
            image="myapp/images/content/ak-suu-kutbilim-visit-opt.webp",
            order=1,
        )

        response = self.client.get(reverse("page", args=["news"]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Test News")
