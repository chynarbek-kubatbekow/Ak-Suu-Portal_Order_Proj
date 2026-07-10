# Copyright (c) 2026 Ak-Suu Portal Project Team. All rights reserved.
# Proprietary software. See LICENSE for terms.
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
]

for page_slug in views.PAGES:
    urlpatterns.extend(
        [
            path(f"{page_slug}/", views.page, {"slug": page_slug}, name=f"page_{page_slug}"),
            path(f"{page_slug}", views.page, {"slug": page_slug}, name=f"page_{page_slug}_no_slash"),
        ]
    )

urlpatterns.extend(
    [
        path("<slug:slug>/", views.page, name="page"),
        path("<slug:slug>", views.page, name="page_no_slash"),
    ]
)
