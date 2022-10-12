from unicodedata import category
from .models import Products, Categories
from django import forms

class ProductForm(forms.ModelForm):
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