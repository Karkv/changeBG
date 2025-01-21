from django.urls import path
from .views import *
urlpatterns = [
    path('home', lambda request: render(request, 'landing_page.html'), name='landing_page'),
    path('change-image/', lambda request: render(request, 'change_image.html'), name='change_background_image'),
    path('change-video/', lambda request: render(request, 'change_video.html'), name='change_background_video'),
    path('results/', lambda request: render(request, 'results.html', {'images': ProcessedImage.objects.all()}), name='results'),
    path('process-image/', process_image, name='process_image'),
    path('image/<int:pk>/', image_detail, name='image_detail'),
    path('api/images/', ProcessedImageListCreate.as_view(), name='image-list-create'),
    path('api/images/<int:pk>/', ProcessedImageDetailDelete.as_view(), name='image-detail-delete'),
]