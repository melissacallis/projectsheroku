from django import forms
from .models import Listing


class ListingForm(forms.ModelForm):
    CATEGORIES = (
        ('books', 'Books'),
        ('electronics', 'Electronics'),
        ('fashion', 'Fashion'),
        ('home', 'Home'),
        ('sport', 'Sport'),
    )

    #category = forms.ChoiceField(choices=CATEGORIES, widget=forms.Select(attrs={"class": 'form-control'}))

    class Meta:
        model = Listing
        fields = ('title', 'description', 'price', 'image_url', 'category', )

        widgets = {
            'title': forms.TextInput(attrs={"class": 'form-control'}),
            'description': forms.TextInput(attrs={"class": 'form-control'}),
            'price': forms.TextInput(attrs={"class": 'form-control'}),
            'image_url': forms.TextInput(attrs={"class": 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}, choices=Listing.CATEGORIES),
            
        }









