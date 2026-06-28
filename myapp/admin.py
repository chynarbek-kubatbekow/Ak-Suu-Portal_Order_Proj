from django.contrib import admin

from .models import NewsItem


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "date", "order", "is_published", "updated_at")
    list_editable = ("order", "is_published")
    list_filter = ("category", "is_published")
    search_fields = ("title", "text")
    ordering = ("order", "-created_at")
    fieldsets = (
        (None, {"fields": ("title", "category", "date", "text")}),
        ("Публикация", {"fields": ("image", "order", "is_published")}),
    )
