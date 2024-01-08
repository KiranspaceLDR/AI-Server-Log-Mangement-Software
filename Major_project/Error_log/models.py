# models.py
from django.db import models

class FileUpload(models.Model):
    upload_date = models.DateField(auto_now_add=True)
    error_count = models.IntegerField(default=0)
    threat_level = models.CharField(max_length=20, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
