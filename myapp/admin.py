# Copyright (c) 2026 Kubatbek uulu Chynarbek. All rights reserved.
# Proprietary software. See LICENSE for terms.
from django.contrib import admin
from django.templatetags.static import static
from django.utils.html import format_html

from .models import NewsItem


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = (
        "preview",
        "title",
        "category",
        "date",
        "order",
        "is_published",
        "updated_at",
    )
    list_display_links = ("preview", "title")
    list_editable = ("order", "is_published")
    list_filter = ("category", "is_published", "updated_at")
    search_fields = ("title", "text", "date")
    ordering = ("order", "-created_at")
    readonly_fields = ("preview", "created_at", "updated_at")
    actions = ("publish_items", "unpublish_items")
    fieldsets = (
        ("\u0421\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435", {"fields": ("title", "category", "date", "text")}),
        ("\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435", {"fields": ("preview", "image_file", "image")}),
        ("\u041f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u044f", {"fields": ("order", "is_published", "created_at", "updated_at")}),
    )

    @admin.display(description="\u0424\u043e\u0442\u043e")
    def preview(self, obj):
        if not obj.pk:
            return "\u041f\u043e\u0441\u043b\u0435 \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u044f \u0437\u0434\u0435\u0441\u044c \u043f\u043e\u044f\u0432\u0438\u0442\u0441\u044f \u043f\u0440\u0435\u0432\u044c\u044e."
        if obj.image_file:
            image_url = obj.image_file.url
        elif obj.image:
            image_url = static(obj.image)
        else:
            return "\u041d\u0435\u0442 \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f"
        return format_html(
            '<img src="{}" alt="" style="width:96px;height:64px;object-fit:cover;border-radius:6px;">',
            image_url,
        )

    @admin.action(description="\u041e\u043f\u0443\u0431\u043b\u0438\u043a\u043e\u0432\u0430\u0442\u044c \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u0435 \u043d\u043e\u0432\u043e\u0441\u0442\u0438")
    def publish_items(self, request, queryset):
        queryset.update(is_published=True)

    @admin.action(description="\u0421\u043d\u044f\u0442\u044c \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u0435 \u043d\u043e\u0432\u043e\u0441\u0442\u0438 \u0441 \u043f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u0438")
    def unpublish_items(self, request, queryset):
        queryset.update(is_published=False)
