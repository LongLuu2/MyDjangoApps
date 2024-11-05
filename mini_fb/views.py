from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .models import Profile, StatusMessage, Image
from .forms import CreateProfileForm, CreateStatusMessageForm, UpdateProfileForm, UpdateStatusMessageForm 
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
class ShowAllProf(ListView):
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'

class ShowProfilePageView(DetailView):
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'

    def get_object(self):
        if 'pk' in self.kwargs:
            return get_object_or_404(Profile, pk=self.kwargs['pk'])
        return get_object_or_404(Profile, user=self.request.user)

class CreateProfileView(CreateView):
    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = UserCreationForm()  
        return context

    def form_valid(self, form):
        user_form = UserCreationForm(self.request.POST)
        if user_form.is_valid():
            user = user_form.save()  
            form.instance.user = user  
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('show_profile')

class CreateStatusMessageView(CreateView):
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'

    def form_valid(self, form):
        # Save the status message to the database
        sm = form.save(commit=False)
        sm.profile = get_object_or_404(Profile, user=self.request.user)  
        sm.save()
        # Handle the file uploads
        files = self.request.FILES.getlist('files')  
        for file in files:
            img = Image()
            img.image_file = file
            img.status_message = sm  
            img.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('show_profile') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(Profile, pk=self.kwargs['pk'])
        return context

class UpdateProfileView(UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'
    
    def get_object(self):
        # Return the Profile associated with the logged-in user
        return get_object_or_404(Profile, user=self.request.user)

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})

class DeleteStatusMessageView(DeleteView):
    model = StatusMessage
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status_message'

    def get_success_url(self):
        return reverse('show_profile')

class UpdateStatusMessageView(UpdateView):
    model = StatusMessage
    form_class = UpdateStatusMessageForm
    template_name = 'mini_fb/update_status_form.html'

    def get_success_url(self):
        return reverse('show_profile')
    
class CreateFriendView(View):
    def dispatch(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, user=self.request.user)
        other = get_object_or_404(Profile, pk=self.kwargs['other_pk'])
        profile.add_friend(other)  
        return redirect('show_profile_with_pk', pk=profile.pk)
    
    
    
class ShowFriendSuggestionsView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suggested_friends'] = self.object.get_friend_suggestions()  
        return context
    
    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)
    
class ShowNewsFeedView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_feed'] = self.object.get_news_feed()  
        return context
    
    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)
    
class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)
    
    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})