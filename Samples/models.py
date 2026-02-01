

from django.db import models
from django.contrib.auth.models import User

class RFIDTag(models.Model):
    uid = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.uid


class Sample(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('checked', 'RFID Checked'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    sample_number = models.CharField(max_length=50, unique=True)
    sample_type = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    person_name = models.CharField(max_length=100)
    collected_date = models.DateField()
    location = models.CharField(max_length=100, blank=True)  # Added field for location
    rfid = models.OneToOneField(RFIDTag, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    sample = models.ForeignKey(Sample, on_delete=models.PROTECT, null=True, blank=True)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
