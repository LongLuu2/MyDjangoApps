from django.urls import path
from .views import home, RegistrationView, MyStudyView, ChapterStudyView, ChaptersNavView, CustomNavView, ListCreateView, WrongListStudyView, WrongListListView
from django.contrib.auth import views as auth_views

urlpatterns = [
path('', home, name="project"),
path('register/', RegistrationView.as_view(), name='register'),
path('login/', auth_views.LoginView.as_view(template_name='project/login.html'), name='login'),
path('logout/', auth_views.LogoutView.as_view(template_name ='project/logout.html'), name='logout'),
path('my_study/', MyStudyView.as_view(), name='my_study'),
path('chapter_study/<str:list_name>/', ChapterStudyView.as_view(), name='chapter_study'),
path('chapters/', ChaptersNavView.as_view(), name='chapters_nav'),
path('custom/', CustomNavView.as_view(), name='custom_nav'),
path('create_list/', ListCreateView.as_view(), name='create_list'),
path('wronglist_study/<int:wronglist_id>/', WrongListStudyView.as_view(), name='wronglist_study'),
path('wronglists/<str:list_name>/', WrongListListView.as_view(), name='wronglist_list'),
]

