from django.urls import path
from .views import *
urlpatterns = [
    path('process-image/', process_image, name='process_image'),
    path('image/<int:pk>/', image_detail, name='image_detail'),
    path('api/images/',ProcessedImageListCreate.as_view(),name='image-list-create'),
    path('api/images/<int:pk>/',ProcessedImageDetailDelete.as_view(),name='image-detail-delete'),



]