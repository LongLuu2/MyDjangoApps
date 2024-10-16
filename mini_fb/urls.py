from django.urls import path
from .views import ShowAllProf, ShowProfilePageView, CreateProfileView, CreateStatusMessageView

urlpatterns = [
    path('', ShowAllProf.as_view(), name="mini_fb"),
    path('/profile/<int:pk>', ShowProfilePageView.as_view(), name='show_profile'),
    path('/create_profile/', CreateProfileView.as_view(), name='create_profile'),
    path('/profile/<int:pk>/create_status/', CreateStatusMessageView.as_view(), name='create_status'),
]