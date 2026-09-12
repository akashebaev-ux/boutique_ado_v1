from django.urls import path

from . import views


urlpatterns = [
    path('', views.chatbot, name='chatbot'),

    path(
        'api/message/',
        views.chatbot_message,
        name='chatbot_message'
    ),
]
