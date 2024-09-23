
from django.urls import path
from . import views

urlpatterns = [
    path(r"", views.home, name="home"),
    path(r"quote", views.quote, name="quote"),  
    path(r"show_all/", views.show_all, name="show_all"),
    path(r"about/", views.about, name="about"),
]
