from django.test import TestCase
from django.urls import reverse

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

# Create your tests here.
