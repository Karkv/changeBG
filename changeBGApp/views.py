import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .forms import ImageUploadForm
from .models import ProcessedImage
from io import BytesIO
from rembg import remove
from PIL import Image
from rest_framework import generics, permissions
from .models import ProcessedImage
from .serializers import ProcessedImageSerializer

import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from PIL import Image
from io import BytesIO
from rembg import remove
from .forms import ImageUploadForm
from .models import ProcessedImage


def process_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                # Save the original image metadata
                uploaded_image = form.save(commit=False)
                uploaded_image.original_image = request.FILES['original_image']

                # Handle the background image selection
                background_choice = form.cleaned_data.get('background_choice')

                # Determine the background image path
                if background_choice:
                    background_img_path = os.path.join(settings.MEDIA_ROOT, 'background_image', background_choice)
                    if not os.path.exists(background_img_path):
                        raise ValidationError(f"Background image '{background_choice}' not found.")
                elif 'background_img' in request.FILES:
                    # Use user-uploaded background image if provided
                    background_img_path = request.FILES['background_img'].temporary_file_path()
                else:
                    raise ValidationError("No valid background image provided.")

                # Save the uploaded image instance
                uploaded_image.save()

                # Process the uploaded image
                img_path = uploaded_image.original_image.path
                img_name = os.path.basename(img_path)

                # Load the original image
                with open(img_path, 'rb') as img_file:
                    input_data = img_file.read()

                # Remove the background using rembg
                subject = remove(input_data, alpha_matting=True, alpha_matting_background_threshold=50)

                # Open the processed foreground image in memory
                foreground_img = Image.open(BytesIO(subject)).convert("RGBA")

                # Load the background image and resize to match the foreground image size
                background_img = Image.open(background_img_path).resize(foreground_img.size).convert("RGBA")

                # Overlay the foreground image onto the background image
                background_img.paste(foreground_img, (0, 0), foreground_img)

                # Save the final image to the 'masked' folder
                masked_dir = os.path.join(settings.MEDIA_ROOT, 'masked')
                os.makedirs(masked_dir, exist_ok=True)
                final_image_path = os.path.join(masked_dir, f"processed_{img_name}")
                background_img.save(final_image_path, format='PNG')

                # Update the processed image path in the database
                uploaded_image.processed_image = f"masked/processed_{img_name}"
                uploaded_image.save()

                # Redirect to display the processed image
                return redirect('image_detail', pk=uploaded_image.pk)
            except Exception as e:
                # Handle errors and show an error message to the user
                form.add_error(None, f"An error occurred during processing: {str(e)}")
        else:
            # If the form is invalid, redisplay it with errors
            form.add_error(None, "Please correct the errors below.")
    else:
        form = ImageUploadForm()

    return render(request, 'process_image.html', {'form': form})


def image_detail(request, pk):
    image = ProcessedImage.objects.get(pk=pk)
    return render(request, 'image_detail.html', {'image': image})

# ???????????????????????????API??????????????????????????????????????

class ProcessedImageListCreate(generics.ListCreateAPIView):
    queryset = ProcessedImage.objects.all()
    serializer_class = ProcessedImageSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        original_image = self.request.FILES['original_image']
        background_img = self.request.FILES.get('background_img')
        user = self.request.user
        
        # Save the original and background images
        instance = serializer.save(user=user, original_image=original_image, background_img=background_img)
        
        # Process the uploaded image
        img_path = instance.original_image.path
        img_name = os.path.basename(img_path)
        
        # Remove the background from the original image
        output_path = os.path.join(settings.MEDIA_ROOT, 'masked', img_name)
        with open(output_path, 'wb') as f:
            input_data = open(img_path, 'rb').read()
            subject = remove(input_data, alpha_matting=True, alpha_matting_background_threshold=50)
            f.write(subject)
        
        # Open the processed image and the user-uploaded background image
        foreground_img = Image.open(output_path)
        if background_img:
            background_img_path = instance.background_img.path
            background_img = Image.open(background_img_path)
            background_img = background_img.resize(foreground_img.size)
            background_img.paste(foreground_img, (0, 0), foreground_img)
        else:
            background_img = foreground_img
        
        # Save the final image
        final_image_path = os.path.join(settings.MEDIA_ROOT, 'masked', f"processed_{img_name}")
        background_img.save(final_image_path, format='JPEG')
        
        # Update the processed image path in the instance
        instance.processed_image = f"masked/processed_{img_name}"
        instance.save()

class ProcessedImageDetailDelete(generics.RetrieveDestroyAPIView):
    queryset = ProcessedImage.objects.all()
    serializer_class = ProcessedImageSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ensure that users can only delete their own images
        return self.queryset.filter(user=self.request.user)