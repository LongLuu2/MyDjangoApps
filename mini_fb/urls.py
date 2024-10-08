from django.urls import path
from .views import ShowAllProf

urlpatterns = [
    path('', ShowAllProf.as_view(), name="mini_fb"),
]