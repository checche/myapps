from django.urls import path, include
from . import views

app_name = 'livecalendar'

urlpatterns=[
    path('', views.LiveIndexView.as_view(), name='index'),
    path('detail/<int:pk>/', views.LiveDetailView.as_view(), name='detail'),
    path('band/', views.BandListView.as_view(), name='band_list'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('signup/',views.Register.as_view(),name='signup'),
    path('signup/done/',views.RegisterDone.as_view(),name='signup_done'),
    path('signup/complete/<token>',views.RegisterComplete.as_view(),name='signup_complete'),
    path('calendar/<int:year>/<int:month>/', views.MonthCalendar.as_view(), name='calendar'),
    path('edit/<int:pk>/',views.EditUserInfo.as_view(), name='edit'),
    path('follow/<int:pk>/', views.followBand, name='follow'),
    path('band/<int:pk>/',views.BandDetailView.as_view(), name='band_detail'),
    path('mylive/',views.FollowLiveView.as_view(),name='follow_live'),
    path('myband/',views.FollowBandView.as_view(),name='follow_band')
]
