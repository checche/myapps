from django.urls import path, include
from . import views

app_name = 'livecalendar'

urlpatterns=[
    path('', views.LiveIndexView.as_view(), name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('signup/',views.UserCreate.as_view(),name='signup'),
    path('signup/done/',views.UserCreateDone.as_view(),name='signup_done'),
    path('signup/complete/<token>',views.UserCreateComplete.as_view(),name='signup_complete'),
    path('calendar/<int:year>/<int:month>/', views.MonthCalendar.as_view(), name='calendar'),
]
