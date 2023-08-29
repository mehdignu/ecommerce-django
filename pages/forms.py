from django import forms

class SearchForm(forms.Form):
    
    search_input = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control appended-form-control',
        'placeholder': 'Search for products'
    }), label='')

class MobileSearchForm(forms.Form):
    
    search_input = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control prepended-form-control',
        'placeholder': 'Search for products'
    }), label='')