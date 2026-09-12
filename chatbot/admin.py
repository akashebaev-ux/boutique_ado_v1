from django.contrib import admin

from .models import KnowledgeEntry


@admin.register(KnowledgeEntry)
class KnowledgeEntryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_active',
        'updated_at',
    )

    search_fields = (
        'title',
        'content',
        'keywords',
    )

    list_filter = ('is_active',)
