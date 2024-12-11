from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, TemplateView, FormView, DetailView, ListView, DeleteView, UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.contrib.auth import login 
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from .forms import CustomListForm
from .models import VocabList, VocabWord, WrongList

# base home page
def home(request):
    return render(request, 'project/base.html', {'name': 'home'})

# handles user registration and setup of vocab lists for chapters 1-24
class RegistrationView(FormView):
    template_name = 'project/register.html'
    form_class = UserCreationForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)

        # createt the chapters 1-23 for the new user
        for i in range(1, 24):
            vocab_list = VocabList.objects.create(list_name=f"Chapter {i}", user=user)
            words = VocabWord.objects.filter(lesson_num=i)
            vocab_list.vocabulary_words.set(words)

        return redirect(reverse('my_study'))

# displays page where the use study
class MyStudyView(TemplateView):
    template_name = 'project/my_study.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_name'] = 'SecondList'  # just a placeholder for context data
        return context

# help listing the 23 chapter navigations
class ChaptersNavView(TemplateView):
    template_name = "project/nav.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_type"] = "chapters"
        # get all the chapters to put in context
        context["chapters"] = VocabList.objects.filter(
            user=self.request.user,
            list_name__startswith="Chapter"
        )
        return context

# help listing the custom list navigations
class CustomNavView(TemplateView):
    template_name = "project/nav.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_type"] = "custom"
        # Get all the custom made list the user have
        context["custom_lists"] = VocabList.objects.filter(
            user=self.request.user
        ).exclude(list_name__startswith="Chapter")
        return context

# detailView for studying a specific chapter or custom vocab list
class ChapterStudyView(DetailView):
    model = VocabList
    template_name = "project/chapter_study.html"
    context_object_name = "vocab_list"

    def get_object(self):
        # fetch the vocab list based on the list name
        list_name = self.kwargs.get("list_name")
        return VocabList.objects.get(list_name=list_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["update_url"] = reverse_lazy("custom_list_update", kwargs={"list_name": self.object.list_name})
        list_name = self.object.list_name

        # determine if we are looking at chapters or our own custom list
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

        # get the current word to be studied based on session index
        all_words = self.object.vocabulary_words.all()
        index = self.request.session.get("index", 0)
        if index < len(all_words):
            context["current_word"] = all_words[index]
        else:
            context["current_word"] = None

        # add feedback and display settings to context
        context["feedback"] = self.request.session.pop("feedback", None)
        context["display"] = self.request.session.get("display", "Japanese")

        return context
    # major part of my assignment here, its the form the use to study vocab
    # handle things such as switching from enlgish to japanese and back, case where
    # they put wrong or right answer, adding to wrong list, displaying feedback.
    def post(self, request, *args, **kwargs):
        # toggle between japanese and english, the switch
        if "toggle" in request.POST:
            mode = request.session.get("display", "Japanese")
            request.session["display"] = "English" if mode == "Japanese" else "Japanese"
            return redirect(request.path)

        # process user answers and track progress through the vocab list
        vocab_list = self.get_object()
        all_words = vocab_list.vocabulary_words.all()
        index = request.session.get("index", 0)
        wrong_words = request.session.get("wrong_words", [])

        if index < len(all_words):
            current_word = all_words[index]
            user_answer = request.POST.get("user_answer", "").strip().lower()
            current_display = request.session.get("display", "Japanese")

            # determine if answers based on display mode
            correct_answer = []
            if current_display == "Japanese":
                correct_answer.append(current_word.english_meaning.strip().lower().replace("...", ""))
                prompt = f"{current_word.hiragana} ({current_word.kanji})" if current_word.kanji else current_word.hiragana
            else:
                correct_answer.append(current_word.hiragana.replace("~", ""))
                if current_word.kanji:
                    correct_answer.append(current_word.kanji.replace("~", ""))
                prompt = current_word.english_meaning

            # provide feedback based on user input
            if user_answer in correct_answer:
                request.session["feedback"] = "Correct!"
            else:
                wrong_words.append(current_word.id)
                request.session["feedback"] = f"Incorrect! The answer for {prompt} is: {' or '.join(correct_answer)}"

            request.session["index"] = index + 1
        else:
            # handle completion of the vocab list
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

# CreatVIew used for creating new vocab lists
class ListCreateView(CreateView):
    model = VocabList
    form_class = CustomListForm
    template_name = 'project/create_list.html'

    def form_valid(self, form):
        # link new list with the current user and save it
        form.instance.user = self.request.user
        response = super().form_valid(form)
        form.instance.vocabulary_words.set(form.cleaned_data['vocabulary_words'])
        return response

    def get_success_url(self):
        return reverse_lazy('custom_nav')

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)

        # Filter vocabulary words based on th user input
        query = self.request.GET.get('search', '').strip() 
        chapter_filter = self.request.GET.get('chapter', '').strip() 
        all_words = VocabWord.objects.all()

        if chapter_filter:
            all_words = all_words.filter(lesson_num=chapter_filter)
        if query:
            all_words = all_words.filter(
                Q(hiragana__icontains=query) |
                Q(kanji__icontains=query) |
                Q(english_meaning__icontains=query)
            )

        form.fields['vocabulary_words'].queryset = all_words
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_type"] = "custom"
        # add custom lists to context for navigation
        context["custom_lists"] = VocabList.objects.filter(
            user=self.request.user
        ).exclude(list_name__startswith="Chapter")
        return context

# Detailview for studying the words users got wrong
class WrongListStudyView(DetailView):
    model = WrongList
    template_name = "project/wronglist_study.html"
    context_object_name = "wrong_list"

    def get_object(self):
        # get the wrong list by id and user
        return get_object_or_404(
            WrongList,
            id=self.kwargs.get("wronglist_id"),
            user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wrong_list = self.object

        # get current word for study session based on session index
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

        #add feedback, display settings, and word existence check to context
        context["feedback"] = self.request.session.pop(f"wrong_feedback_{wrong_list.id}", None)
        context["display"] = self.request.session.get(f"wrong_display_{wrong_list.id}", "Japanese")
        context['has_words'] = wrong_list.vocabulary_words.exists()

        return context
    
    #this is mostly similar to the normal studying forms but you are instead 
    #studying what you got wrong. The difference is that it delete words as you
    #get them right, and when you get to the end of the list it will start over
    #with what left until you get all the wrong words right.
    def post(self, request, *args, **kwargs):
        wrong_list = self.get_object()
        all_words = list(wrong_list.vocabulary_words.all())  
        index = request.session.get(f"wrong_index_{wrong_list.id}", 0)

        if "toggle" in request.POST:
            mode = request.session.get(f"wrong_display_{wrong_list.id}", "Japanese")
            request.session[f"wrong_display_{wrong_list.id}"] = "English" if mode == "Japanese" else "Japanese"
            return redirect(request.path)

        if index < len(all_words):
            current_word = all_words[index]
            user_answer = request.POST.get("user_answer", "").strip().lower()
            current_display = request.session.get(f"wrong_display_{wrong_list.id}", "Japanese")

            correct_answers = []
            if current_display == "Japanese":
                correct_answers.append(current_word.english_meaning.strip().lower().replace("...", ""))
                prompt = f"{current_word.hiragana} ({current_word.kanji})" if current_word.kanji else current_word.hiragana
            else:
                correct_answers.append(current_word.hiragana.replace("~", ""))
                if current_word.kanji:
                    correct_answers.append(current_word.kanji.replace("~", ""))
                prompt = current_word.english_meaning

            if user_answer in correct_answers:
                request.session[f"wrong_feedback_{wrong_list.id}"] = "Correct!"
                wrong_list.vocabulary_words.remove(current_word)  
            else:
                request.session[f"wrong_feedback_{wrong_list.id}"] = f"Incorrect! The answer for {prompt} is: {' or '.join(correct_answers)}"

            request.session[f"wrong_index_{wrong_list.id}"] = index + 1
        else:
            if wrong_list.vocabulary_words.exists(): 
                request.session[f"wrong_index_{wrong_list.id}"] = 0
            else:
                wrong_list.delete()
                return redirect('chapter_study', list_name=wrong_list.vocabulary_list.list_name)

        return redirect(request.path)

# ListView to display the wrong list for that study list as user can have multiple wrong
#list for study list. Example they complete 2 cycles of studies, and in each get something 
#wrong. Then when they go look at the wrong list, they will see 2.
class WrongListListView(ListView):
    model = WrongList
    template_name = "project/wronglist_list.html"
    context_object_name = "wrong_lists"

    def get_queryset(self):
        # getwrong lists for the specified vocab list and user
        vocab_list = get_object_or_404(VocabList, list_name=self.kwargs.get("list_name"), user=self.request.user)
        return WrongList.objects.filter(vocabulary_list=vocab_list, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vocab_list = get_object_or_404(VocabList, list_name=self.kwargs.get("list_name"), user=self.request.user)
        context["vocab_list"] = vocab_list

        # add navigation context 
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

# Delete for deleting a vocab list and make sure they confirm it
class VocabListDeleteView(DeleteView):
    model = VocabList
    template_name = 'project/vocablist_confirm_delete.html'

    def get_object(self):
        # get the vocab list to be deleted 
        return get_object_or_404(VocabList, list_name=self.kwargs.get("list_name"), user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_name"] = self.kwargs.get("list_name")  
        return context

    def get_success_url(self):
        return reverse_lazy('custom_nav')

# UpdateView for updating a vocab list
class VocabListUpdateView(UpdateView):
    model = VocabList
    form_class = CustomListForm  
    template_name = 'project/vocablist_update.html'

    def get_object(self):
        return get_object_or_404(VocabList, list_name=self.kwargs.get("list_name"), user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filter vocab words based on user input
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
