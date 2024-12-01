from django import forms
from .models import VocabList, VocabWord

class CustomListForm(forms.ModelForm):
    vocabulary_words = forms.ModelMultipleChoiceField(
        queryset=VocabWord.objects.none(),  # Dynamically set in the view
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search...'}),
    )
    chapter = forms.ChoiceField(
        choices=[("", "All Chapters")] + [(i, f"Chapter {i}") for i in range(1, 24)],
        required=False,
    )

    class Meta:
        model = VocabList
        fields = ['list_name', 'vocabulary_words']  # Ensure 'vocabulary_words' is included

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically populate the vocabulary_words field in the view
        self.fields['vocabulary_words'].queryset = VocabWord.objects.all()