from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Voter
from django.db.models import Q
from django import forms
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from django.utils.safestring import mark_safe

class VoterFilterForm(forms.Form):
    party_affiliation = forms.ChoiceField(choices=[('', 'Any')] + [(p, p) for p in Voter.objects.values_list('party_affiliation', flat=True).distinct()], required=False)
    min_dob = forms.ChoiceField(choices=[('', 'Any')] + [(y, y) for y in range(1900, datetime.now().year + 1)], required=False)
    max_dob = forms.ChoiceField(choices=[('', 'Any')] + [(y, y) for y in range(1900, datetime.now().year + 1)], required=False)
    voter_score = forms.ChoiceField(choices=[('', 'Any')] + [(str(s), s) for s in Voter.objects.values_list('voter_score', flat=True).distinct()], required=False)
    v20state = forms.BooleanField(required=False)
    v21town = forms.BooleanField(required=False)
    v21primary = forms.BooleanField(required=False)
    v22general = forms.BooleanField(required=False)
    v23town = forms.BooleanField(required=False)

class VoterListView(ListView):
    model = Voter
    template_name = 'voter_analytics/voter_list.html'
    context_object_name = 'voters'
    paginate_by = 100

    def get_queryset(self):
        queryset = Voter.objects.all()
        form = VoterFilterForm(self.request.GET)

        if form.is_valid():
            if form.cleaned_data['party_affiliation']:
                queryset = queryset.filter(party_affiliation=form.cleaned_data['party_affiliation'])
            if form.cleaned_data['min_dob']:
                queryset = queryset.filter(date_of_birth__year__gte=form.cleaned_data['min_dob'])
            if form.cleaned_data['max_dob']:
                queryset = queryset.filter(date_of_birth__year__lte=form.cleaned_data['max_dob'])
            if form.cleaned_data['voter_score']:
                queryset = queryset.filter(voter_score=form.cleaned_data['voter_score'])
            for election_field in ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']:
                if form.cleaned_data.get(election_field) is True:
                    queryset = queryset.filter(**{election_field: True})

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = VoterFilterForm(self.request.GET)
        return context

class VoterDetailView(DetailView):
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'
    context_object_name = 'voter'

class GraphsView(ListView):
    model = Voter
    template_name = 'voter_analytics/graphs.html'
    context_object_name = 'voters'

    def get_queryset(self):
        queryset = Voter.objects.all()
        form = VoterFilterForm(self.request.GET)

        if form.is_valid():
            if form.cleaned_data['party_affiliation']:
                queryset = queryset.filter(party_affiliation=form.cleaned_data['party_affiliation'])
            if form.cleaned_data['min_dob']:
                queryset = queryset.filter(date_of_birth__year__gte=form.cleaned_data['min_dob'])
            if form.cleaned_data['max_dob']:
                queryset = queryset.filter(date_of_birth__year__lte=form.cleaned_data['max_dob'])
            if form.cleaned_data['voter_score']:
                queryset = queryset.filter(voter_score=form.cleaned_data['voter_score'])
            for election_field in ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']:
                if form.cleaned_data.get(election_field) is True:
                    queryset = queryset.filter(**{election_field: True})

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voters = self.get_queryset()

        birth_year_data = voters.values_list('date_of_birth__year', flat=True)
        birth_year_counts = {}
        for year in birth_year_data:
            if year:
                birth_year_counts[year] = birth_year_counts.get(year, 0) + 1
        birth_year_chart = go.Figure(
            data=[go.Bar(x=list(birth_year_counts.keys()), y=list(birth_year_counts.values()))],
            layout_title_text="Voter Distribution by Year of Birth"
        )
        context['birth_year_chart'] = mark_safe(birth_year_chart.to_html(full_html=False))

        party_data = voters.values_list('party_affiliation', flat=True)
        party_counts = {}
        for party in party_data:
            party_counts[party] = party_counts.get(party, 0) + 1
        party_chart = go.Figure(
            data=[go.Pie(labels=list(party_counts.keys()), values=list(party_counts.values()))],
            layout_title_text="Voter Distribution by Party Affiliation"
        )
        context['party_chart'] = mark_safe(party_chart.to_html(full_html=False))

        participation_counts = {
            "2020 State": voters.filter(v20state=True).count(),
            "2021 Town": voters.filter(v21town=True).count(),
            "2021 Primary": voters.filter(v21primary=True).count(),
            "2022 General": voters.filter(v22general=True).count(),
            "2023 Town": voters.filter(v23town=True).count()
        }
        participation_chart = go.Figure(
            data=[go.Bar(
                x=list(participation_counts.keys()),
                y=list(participation_counts.values())
            )],
            layout_title_text="Voter Participation by Election"
        )
        context['participation_chart'] = mark_safe(participation_chart.to_html(full_html=False))

        context['form'] = VoterFilterForm(self.request.GET)

        return context
