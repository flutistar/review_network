from django import forms 
from .models import *
  
class ImageUploadForm(forms.Form): 
    task = forms.CharField(max_length=10, widget=forms.HiddenInput())
    screenshot = forms.ImageField()