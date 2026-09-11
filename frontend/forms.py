from django import forms
from django.core.validators import FileExtensionValidator
from django.utils import timezone

from .models import (
    HowDidYouHearAboutUs, Accessory, MasterclassBooking, MasterclassDate,
    Cage, Shed, Breed, ButcheryProduct, HeroSlide, MenuItem, MasterclassEvent,
    Order,
)

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


# ---------------------------------------------------------------------------
#  Dashboard content forms  (generic CRUD - see frontend/dashboard.py)
# ---------------------------------------------------------------------------
class StyledModelForm(forms.ModelForm):
    """Applies the dashboard's .form-control / .form-check styling to every
    widget so the generic content_form.html template stays dumb."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, (forms.ClearableFileInput, forms.FileInput)):
                widget.attrs.setdefault("class", "form-control-file")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-control")
            else:
                widget.attrs.setdefault("class", "form-control")
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("rows", 4)


class CageForm(StyledModelForm):
    class Meta:
        model = Cage
        fields = [
            "name", "slug", "category", "description", "features", "price",
            "capacity", "image", "image_filename", "image_alt",
            "is_available", "is_featured", "order",
        ]


class ShedForm(StyledModelForm):
    class Meta:
        model = Shed
        fields = [
            "name", "slug", "category", "description", "features", "price",
            "capacity", "image", "image_filename", "image_alt",
            "is_available", "is_featured", "order",
        ]


class BreedForm(StyledModelForm):
    class Meta:
        model = Breed
        fields = [
            "name", "slug", "tagline", "description", "characteristics",
            "price", "stock_quantity", "image", "image_filename", "image_alt",
            "is_available", "is_featured", "order",
        ]


class ButcheryProductForm(StyledModelForm):
    class Meta:
        model = ButcheryProduct
        fields = [
            "name", "slug", "category", "description", "price", "unit",
            "stock_note", "image", "image_filename", "image_alt",
            "is_available", "is_featured", "order",
        ]


class HeroSlideForm(StyledModelForm):
    class Meta:
        model = HeroSlide
        fields = [
            "page", "heading", "subheading", "background_image",
            "background_image_filename", "image_alt",
            "background_video", "background_video_filename", "overlay",
            "cta_primary_label", "cta_primary_url",
            "cta_secondary_label", "cta_secondary_url",
            "order", "is_active",
        ]


class MenuItemForm(StyledModelForm):
    class Meta:
        model = MenuItem
        fields = [
            "name", "category", "description", "price", "image", "image_filename",
            "ingredients", "allergens", "preparation_time", "calories",
            "is_available", "is_featured",
        ]


class MasterclassDateForm(StyledModelForm):
    class Meta:
        model = MasterclassDate
        fields = ["date", "capacity", "location", "notes", "is_active"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}


MAX_PROOF_SIZE = 5 * 1024 * 1024  # 5 MB


class MasterclassBookingForm(forms.ModelForm):
    masterclass_date = forms.ModelChoiceField(
        queryset=MasterclassDate.objects.none(),
        label="Select a date",
        empty_label="Choose an available date...",
    )

    class Meta:
        model = MasterclassBooking
        fields = ['masterclass_date', 'name', 'email', 'phone', 'attendees', 'notes', 'payment_proof']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': "Anything else we should know? (optional)"}),
            'attendees': forms.NumberInput(attrs={'min': 1, 'value': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Backend-authoritative: only ever offer dates that are active,
        # not in the past, and not already full.
        upcoming = MasterclassDate.objects.filter(
            is_active=True, date__gte=timezone.localdate(),
        )
        self.fields['masterclass_date'].queryset = upcoming
        self.fields['masterclass_date'].choices = [
            ('', 'Choose an available date...'),
        ] + [
            (d.pk, f"{d.date:%A, %d %B %Y} — {d.spaces_left} space{'s' if d.spaces_left != 1 else ''} left")
            for d in upcoming if d.is_bookable
        ]
        self.fields['payment_proof'].required = True
        self.fields['payment_proof'].validators.append(
            FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png', 'webp'])
        )
        self.fields['payment_proof'].widget.attrs['accept'] = '.pdf,.jpg,.jpeg,.png,.webp'

    def clean_payment_proof(self):
        f = self.cleaned_data.get('payment_proof')
        if f and f.size > MAX_PROOF_SIZE:
            raise forms.ValidationError("File is too large - please keep it under 5 MB.")
        return f

    def clean(self):
        cleaned = super().clean()
        mdate = cleaned.get('masterclass_date')
        attendees = cleaned.get('attendees') or 1
        if mdate:
            if not mdate.is_bookable:
                raise forms.ValidationError("Sorry, that date is no longer available. Please pick another.")
            if attendees > mdate.spaces_left:
                raise forms.ValidationError(
                    f"Only {mdate.spaces_left} space(s) left on that date - please reduce the number of attendees."
                )
        return cleaned


# ---------------------------------------------------------------------------
#  Unified cart checkout  (cages, sheds, accessories, breeding stock,
#  restaurant orders/reservations - see /api/place-order/ in views.py)
# ---------------------------------------------------------------------------
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'source', 'customer_name', 'customer_phone', 'items_summary',
            'total', 'payment_method', 'proof_of_payment', 'notes',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proof_of_payment'].required = False  # conditionally required in clean()
        self.fields['proof_of_payment'].validators.append(
            FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png', 'webp'])
        )

    def clean_proof_of_payment(self):
        f = self.cleaned_data.get('proof_of_payment')
        if f and f.size > MAX_PROOF_SIZE:
            raise forms.ValidationError("File is too large - please keep it under 5 MB.")
        return f

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('payment_method') == 'proof' and not cleaned.get('proof_of_payment'):
            raise forms.ValidationError(
                "Please attach your proof of payment, or choose to pay in cash instead."
            )
        return cleaned
