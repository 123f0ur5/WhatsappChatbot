from unicodedata import category

from django.forms import Widget
from .models import Products, Categories
from django import forms

class ProductForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs= {
        "cols" : 25,
        "rows" : 6,
    }))
    price = forms.FloatField(widget=forms.NumberInput(attrs={
        'min' : 0.01,
    }))
    class Meta:
        model = Products
        fields = (
            'name',
            'price',
            'category',
            'image',
            'description',  
        )
    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = (
            'name',
        )