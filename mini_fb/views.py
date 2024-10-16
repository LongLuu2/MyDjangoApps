from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from .models import Profile, StatusMessage
from .forms import CreateProfileForm, CreateStatusMessageForm
from django.urls import reverse
# Create your views here.
class ShowAllProf(ListView):
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'

class ShowProfilePageView(DetailView):
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'

class CreateProfileView(CreateView):
    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})
    
class CreateStatusMessageView(CreateView):
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'

    # This method provides context for the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(pk=self.kwargs['pk']) 
        context['profile'] = profile  
        return context
    
    def form_valid(self, form):
        profile = Profile.objects.get(pk=self.kwargs['pk'])  
        form.instance.profile = profile  
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.kwargs['pk']})