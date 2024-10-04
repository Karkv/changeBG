
from django.db import models

class ProcessedImage(models.Model):
    user= models.CharField(max_length=100)
    background_img=models.ImageField(upload_to='background_image/')
    original_image = models.ImageField(upload_to='original/')
    processed_image = models.ImageField(upload_to='masked/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id}"
