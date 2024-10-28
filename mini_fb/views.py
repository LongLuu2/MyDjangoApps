from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .models import Profile, StatusMessage, Image
from .forms import CreateProfileForm, CreateStatusMessageForm, UpdateProfileForm, UpdateStatusMessageForm
from django.urls import reverse
from django.shortcuts import get_object_or_404
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
    
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.edit import CreateView
from .models import StatusMessage, Image, Profile
from .forms import CreateStatusMessageForm

class CreateStatusMessageView(CreateView):
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'

    def form_valid(self, form):
        # Save the status message to the database
        sm = form.save(commit=False)
        sm.profile = get_object_or_404(Profile, pk=self.kwargs['pk'])  

        # Handle the file uploads
        files = self.request.FILES.getlist('files')  
        for file in files:
            img = Image()
            img.image_file = file
            img.status_message = sm  
            img.save()

        return super().form_valid(form)

    def get_success_url(self):

        return reverse('show_profile', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(Profile, pk=self.kwargs['pk'])
        return context

class UpdateProfileView(UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})

class DeleteStatusMessageView(DeleteView):
    model = StatusMessage
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status_message'

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})

class UpdateStatusMessageView(UpdateView):
    model = StatusMessage
    form_class = UpdateStatusMessageForm
    template_name = 'mini_fb/update_status_form.html'

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})
    
class CreateFriendView(View):
    def dispatch(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
        other = get_object_or_404(Profile, pk=self.kwargs['other_pk'])
        profile.add_friend(other)  
        return redirect('show_profile', pk=profile.pk)
    
class ShowFriendSuggestionsView(DetailView):
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suggested_friends'] = self.object.get_friend_suggestions()  
        return context
    
class ShowNewsFeedView(DetailView):
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_feed'] = self.object.get_news_feed()  
        return context