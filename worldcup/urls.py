from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('schedule/', views.schedule, name='schedule'),
    path('bracket/', views.bracket, name='bracket'),
    path('teams/<str:team_name>', views.team, name="teams"),
    path('match/<int:match_id>', views.match, name="match"),
    path('live/<int:match_id>', views.live, name="live")
]