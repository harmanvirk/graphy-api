from django.db import models

# Create your models here.

class Story(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    user_name = models.CharField(max_length=255, default='Some User')
    name = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField()
    latitude = models.DecimalField(max_digits=9,decimal_places=6)
    longitude = models.DecimalField(max_digits=9,decimal_places=6)

class Media(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    story = models.OneToOneField(Story, on_delete=models.CASCADE)
    media_type = models.CharField(max_length=255)
    duration = models.IntegerField()
    original_file = models.CharField(max_length=255, blank=True, null=True)
    compressed_file = models.CharField(max_length=255, blank=True, null=True)

