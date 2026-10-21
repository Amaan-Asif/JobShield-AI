
from django.conf import settings
from django.db import models


class AnalysisReport(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="analysis_reports",
    )
    job_description = models.TextField()
    score = models.PositiveSmallIntegerField()
    risk_level = models.CharField(max_length=20)
    warnings = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.risk_level} Risk - {self.score}/100"
