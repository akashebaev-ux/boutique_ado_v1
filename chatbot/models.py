from django.db import models


class KnowledgeEntry(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    keywords = models.CharField(
        max_length=500,
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Knowledge entries"

    def __str__(self):
        return self.title
