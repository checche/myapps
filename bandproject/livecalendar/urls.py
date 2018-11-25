from django.urls import path, include
from . import views

app_name = 'livecalendar'

urlpatterns=[
    path('', views.LiveIndexView.as_view(), name='index'),
#    path('add/', views.AddView.as_view(), name='add')
]
