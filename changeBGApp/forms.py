# forms.py

from django import forms
from .models import ProcessedImage

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ProcessedImage
        fields = ['user','original_image','background_img']
from django import forms
from .models import ProcessedImage
import os
from django.conf import settings

class ImageUploadForm(forms.ModelForm):
    # Create a dropdown for predefined background images
    BACKGROUND_CHOICES = [
    (f, f) for f in os.listdir(os.path.join(settings.MEDIA_ROOT, 'background_image'))
]

    
    background_choice = forms.ChoiceField(choices=BACKGROUND_CHOICES, label="Select Background Image", required=False)

    class Meta:
        model = ProcessedImage
        fields = ['user', 'original_image']
        # background_img will be optional, allowing the user to select a predefined background

    def clean(self):
        cleaned_data = super().clean()
        background_img = cleaned_data.get('background_img')
        background_choice = cleaned_data.get('background_choice')

        # Ensure that either a background image is uploaded or a background choice is selected
        if not background_img and not background_choice:
            raise forms.ValidationError("Please either upload a background image or select one from the options.")
        
        return cleaned_data