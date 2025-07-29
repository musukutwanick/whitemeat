from django import forms
from .models import HowDidYouHearAboutUs

class HowDidYouHearAboutUsForm(forms.ModelForm):
    class Meta:
        model = HowDidYouHearAboutUs
        fields = ['choice', 'other_text']
        widgets = {
            'choice': forms.RadioSelect,
            'other_text': forms.TextInput(attrs={'placeholder': 'If other, please specify'}),
        }
