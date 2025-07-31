from django import forms

from .models import HowDidYouHearAboutUs, Accessory

class HowDidYouHearAboutUsForm(forms.ModelForm):
    class Meta:
        model = HowDidYouHearAboutUs
        fields = ['choice', 'other_text']
        widgets = {
            'choice': forms.RadioSelect,
            'other_text': forms.TextInput(attrs={'placeholder': 'If other, please specify'}),
        }


# Form for adding accessories/equipment
class AccessoryForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = ['name', 'description', 'price', 'image', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Accessory Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'is_available': forms.Select(choices=[(True, 'Yes'), (False, 'No')], attrs={'class': 'form-control'}),
        }
