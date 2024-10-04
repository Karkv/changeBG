from rest_framework import serializers
from .models import *

class ProcessedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProcessedImage
        fields = ['id', 'user', 'original_image', 'background_img', 'processed_image', 'uploaded_at']
        read_only_fields = ['id', 'user', 'processed_image', 'uploaded_at']
