from django import forms
from .models import Sample

class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ['sample_type', 'category', 'collected_date', 'person_name', 'location']
        widgets = {
            'collected_date': forms.DateInput(attrs={'type': 'date'}),
        }
