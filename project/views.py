from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, TemplateView, FormView, DetailView, ListView, DeleteView, UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.contrib.auth import login 
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from .forms import CustomListForm
from .models import VocabList, VocabWord, WrongList
# Create your views here.

def home(request):
    return render(request, 'project/base.html', {'name': 'home'})

class RegistrationView(FormView):
    template_name = 'project/register.html'
    form_class = UserCreationForm
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        #creates chapters 1-24 for each user, as their wrong list will be different
        #for these chapters will be different
        for i in range(1, 24):
            vocab_list = VocabList.objects.create(list_name=f"Chapter {i}", user=user)
            
            words = VocabWord.objects.filter(lesson_num=i)
            vocab_list.vocabulary_words.set(words)
        return redirect(reverse('my_study'))
    
class MyStudyView(TemplateView):
    template_name = 'project/my_study.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_name'] = 'SecondList'
        return context
    
    
class ChaptersNavView(TemplateView):
    template_name = "project/nav.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_type"] = "chapters"
        context["chapters"] = VocabList.objects.filter(
            user=self.request.user,
            list_name__startswith="Chapter"
        )
        return context
    
class CustomNavView(TemplateView):
    template_name = "project/nav.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_type"] = "custom"
        context["custom_lists"] = VocabList.objects.filter(
            user=self.request.user
        ).exclude(list_name__startswith="Chapter")
        return context
    
class ChapterStudyView(DetailView):
    model = VocabList
    template_name = "project/chapter_study.html"
    context_object_name = "vocab_list"

    def get_object(self):
        list_name = self.kwargs.get("list_name")
        return VocabList.objects.get(list_name=list_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["update_url"] = reverse_lazy("custom_list_update", kwargs={"list_name": self.object.list_name})
        list_name = self.object.list_name

        if list_name.startswith("Chapter"):
            context["nav_type"] = "chapters"
            context["chapters"] = VocabList.objects.filter(
                user=self.request.user, list_name__startswith="Chapter"
            )
        else:
            context["nav_type"] = "custom"
            context["custom_lists"] = VocabList.objects.filter(
                user=self.request.user
            ).exclude(list_name__startswith="Chapter")
        
        all_words = self.object.vocabulary_words.all()
        index = self.request.session.get("index", 0)
        if index < len(all_words):
            context["current_word"] = all_words[index]
        else:
            context["current_word"] = None

        context["feedback"] = self.request.session.pop("feedback", None)
        context["display"] = self.request.session.get("display", "Japanese")
        
        return context

    def post(self, request, *args, **kwargs):
        if "toggle" in request.POST:
            mode = request.session.get("display", "Japanese")
            request.session["display"] = "English" if mode == "Japanese" else "Japanese"
            
            return redirect(request.path)

        vocab_list = self.get_object()
        all_words = vocab_list.vocabulary_words.all()
        index = request.session.get("index", 0)
        wrong_words = request.session.get("wrong_words", [])

        if index < len(all_words):
            current_word = all_words[index]
            user_answer = request.POST.get("user_answer", "").strip().lower()
            current_display = request.session.get("display", "Japanese")

            correct_answer = []
            if current_display == "Japanese":
                correct_answer.append(current_word.english_meaning.strip().lower().replace("...", ""))
                prompt = f"{current_word.hiragana} ({current_word.kanji})" if current_word.kanji else current_word.hiragana
            else:
                correct_answer.append(current_word.hiragana.replace("〜", ""))
                if current_word.kanji:
                    correct_answer.append(current_word.kanji.replace("〜", ""))
                prompt = current_word.english_meaning

            if user_answer in correct_answer:
                request.session["feedback"] = "Correct!"
            else:
                wrong_words.append(current_word.id)
                request.session["feedback"] = f"Incorrect! The answer for {prompt} is: {' or '.join(correct_answer)}"

            request.session["index"] = index + 1
        else:
            if wrong_words:
                wrong_list = WrongList.objects.create(
                    vocabulary_list=vocab_list,
                    user=request.user,
                    list_number=(WrongList.objects.filter(vocabulary_list=vocab_list).count() + 1)
                )
                wrong_list.vocabulary_words.set(VocabWord.objects.filter(id__in=wrong_words))
            request.session["index"] = 0  
            request.session["wrong_words"] = []

        return redirect(request.path)

class ListCreateView(CreateView):
    model = VocabList
    form_class = CustomListForm
    template_name = 'project/create_list.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        form.instance.vocabulary_words.set(form.cleaned_data['vocabulary_words'])
        return response
    
    def get_success_url(self):
        return reverse_lazy('custom_nav')
    
    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        
        query = self.request.GET.get('search', '').strip() 
        chapter_filter = self.request.GET.get('chapter', '').strip() 
        all_words = VocabWord.objects.all()
        
        if chapter_filter:
            all_words = all_words.filter(lesson_num = chapter_filter)
        if query:
            all_words = all_words.filter(
                Q(hiragana__icontains = query) |
                Q(kanji__icontains = query) |
                Q(english_meaning__icontains = query)
            )
            
        form.fields['vocabulary_words'].queryset = all_words
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_type"] = "custom"
        context["custom_lists"] = VocabList.objects.filter(
            user=self.request.user
        ).exclude(list_name__startswith="Chapter")
        return context

    
class WrongListStudyView(DetailView):
    model = WrongList
    template_name = "project/wronglist_study.html"
    context_object_name = "wrong_list"

    def get_object(self):
        return get_object_or_404(
            WrongList,
            id=self.kwargs.get("wronglist_id"),
            user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wrong_list = self.object

        all_words = wrong_list.vocabulary_words.all()
        index = self.request.session.get(f"wrong_index_{wrong_list.id}", 0)
        context["nav_type"] = "custom"
        context["custom_lists"] = VocabList.objects.filter(
            user=self.request.user
        ).exclude(list_name__startswith="Chapter")
        
        if index < len(all_words):
            context["current_word"] = all_words[index]
        else:
            context["current_word"] = None

        context["feedback"] = self.request.session.pop(f"wrong_feedback_{wrong_list.id}", None)
        context["display"] = self.request.session.get(f"wrong_display_{wrong_list.id}", "Japanese")
        context['has_words'] = wrong_list.vocabulary_words.exists()
        
        return context

    def post(self, request, *args, **kwargs):
        wrong_list = self.get_object()
        all_words = list(wrong_list.vocabulary_words.all())  
        index = request.session.get(f"wrong_index_{wrong_list.id}", 0)

        if "toggle" in request.POST:
            # Toggle between Japanese and English display mode
            mode = request.session.get(f"wrong_display_{wrong_list.id}", "Japanese")
            request.session[f"wrong_display_{wrong_list.id}"] = "English" if mode == "Japanese" else "Japanese"
            return redirect(request.path)

        if index < len(all_words):
            current_word = all_words[index]
            user_answer = request.POST.get("user_answer", "").strip().lower()
            current_display = request.session.get(f"wrong_display_{wrong_list.id}", "Japanese")

            # Determine correct answers and the prompt
            correct_answers = []
            if current_display == "Japanese":
                correct_answers.append(current_word.english_meaning.strip().lower().replace("...", ""))
                prompt = f"{current_word.hiragana} ({current_word.kanji})" if current_word.kanji else current_word.hiragana
            else:
                correct_answers.append(current_word.hiragana.replace("〜", ""))
                if current_word.kanji:
                    correct_answers.append(current_word.kanji.replace("〜", ""))
                prompt = current_word.english_meaning

            # Check user answer
            if user_answer in correct_answers:
                request.session[f"wrong_feedback_{wrong_list.id}"] = "Correct!"
                wrong_list.vocabulary_words.remove(current_word)  
            else:
                request.session[f"wrong_feedback_{wrong_list.id}"] = f"Incorrect! The answer for {prompt} is: {' or '.join(correct_answers)}"

            # Move to the next index
            request.session[f"wrong_index_{wrong_list.id}"] = index + 1
        else:
            # Reset index if we've gone through all words
            if wrong_list.vocabulary_words.exists(): 
                request.session[f"wrong_index_{wrong_list.id}"] = 0
            else:
                # Delete the wrong list if it's empty
                wrong_list.delete()
                return redirect('chapter_study', list_name=wrong_list.vocabulary_list.list_name)

        return redirect(request.path)


class WrongListListView(ListView):
    model = WrongList
    template_name = "project/wronglist_list.html"
    context_object_name = "wrong_lists"

    def get_queryset(self):
        vocab_list = get_object_or_404(VocabList, list_name=self.kwargs.get("list_name"), user=self.request.user)
        return WrongList.objects.filter(vocabulary_list=vocab_list, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vocab_list = get_object_or_404(VocabList, list_name=self.kwargs.get("list_name"), user=self.request.user)
        context["vocab_list"] = vocab_list

        if vocab_list.list_name.startswith("Chapter"):
            context["nav_type"] = "chapters"
            context["chapters"] = VocabList.objects.filter(
                user=self.request.user, list_name__startswith="Chapter"
            )
        else:
            context["nav_type"] = "custom"
            context["custom_lists"] = VocabList.objects.filter(
                user=self.request.user
            ).exclude(list_name__startswith="Chapter")
        return context
    
class VocabListDeleteView(DeleteView):
    model = VocabList
    template_name = 'project/vocablist_confirm_delete.html'

    def get_object(self):
        return get_object_or_404(VocabList, list_name=self.kwargs.get("list_name"), user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_name"] = self.kwargs.get("list_name")  
        return context

    def get_success_url(self):
        return reverse_lazy('custom_nav')
    
class VocabListUpdateView(UpdateView):
    model = VocabList
    form_class = CustomListForm  
    template_name = 'project/vocablist_update.html'

    def get_object(self):
        return get_object_or_404(VocabList, list_name=self.kwargs.get("list_name"), user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('search', '').strip()
        chapter_filter = self.request.GET.get('chapter', '').strip()


        allWords = VocabWord.objects.all()
        if chapter_filter:
            allWords = allWords.filter(lesson_num=chapter_filter)
        if query:
            allWords = allWords.filter(
                Q(hiragana__icontains=query) |
                Q(kanji__icontains=query) |
                Q(english_meaning__icontains=query)
            )

        context['vocab_words'] = allWords
        return context

    def get_success_url(self):
        return reverse_lazy('custom_nav')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        form.instance.vocabulary_words.set(form.cleaned_data['vocabulary_words'])
        return response