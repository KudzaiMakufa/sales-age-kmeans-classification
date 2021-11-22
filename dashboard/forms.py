from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from dashboard.models import Library ,CVE_Scan 

# model form 
from django.db import models
# from django.forms import ModelForm , Textarea , ModelChoiceField , Select  


class Library_Form(forms.ModelForm):

    class Meta:
        model = Library
        
        
        fields = ['application_name','library_list' ]

             
        widgets = {
            
            'application_name': forms.TextInput(attrs={
                "type" : "text",
                "class":"form-control"
            }),
            'library_list': forms.ClearableFileInput(attrs={
                "class":"form-control",
                "id":"picture",
                "type" : "file",
            }),
            'data_mode': forms.Select(attrs={
                "type" : "text",
                "class":"form-control custom-select",
               
            }),
           
        }


