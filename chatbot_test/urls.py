from django.urls import path
from . import views

urlpatterns = [
    # Other URL patterns
    path('chat/', views.chat, name='chat'),
]

