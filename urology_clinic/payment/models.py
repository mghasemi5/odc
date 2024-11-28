from django.db import models

# Create your models here.
class Payment(models.Model):
    authority = models.CharField(max_length=50, unique=True)
    amount = models.IntegerField()
    status = models.CharField(max_length=20, default='pending')  # pending, success, failed
    ref_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)