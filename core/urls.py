from django.urls import path

from . import views

app_name = "core"
urlpatterns = [
    path("", views.home, name="home"),
    path("achievements/", views.achievements, name="achievements"),
    path("trophies/", views.trophies, name="trophies"),
    path("players/<path:nickname>/", views.player_detail, name="player_detail"),
    path("join/", views.join, name="join"),
]
