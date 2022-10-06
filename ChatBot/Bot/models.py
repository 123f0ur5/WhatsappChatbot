from statistics import mode
from unittest.util import _MAX_LENGTH
from django.db import models

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=32)
    phone_number = models.CharField(max_length=16, unique=True)
    first_message = models.BooleanField(default=True)

    def get_absolute_url(self):
        return f"/chat/{self.id}"

class Message(models.Model):
    from_number = models.CharField(max_length=16)
    to_number = models.CharField(max_length=16)
    message_text = models.TextField()
    sent_datetime = models.DateTimeField(auto_now=True)
    contact_id = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE
    )