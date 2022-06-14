from django import forms

class SearchForm(forms.Form):
    city1 = forms.CharField(label='Start From ',max_length=100)
    city2 = forms.CharField(label='Destination ',max_length=100)
