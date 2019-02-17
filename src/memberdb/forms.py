from django import forms

from .models import Member, Membership

"""
Custom ModelForm class with some extra features
"""
class MyModelForm(forms.ModelForm):
    # this must be passed by kwargs upon instantiating the form
    request = None
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
class MyForm(forms.Form):
    # this must be passed by kwargs upon instantiating the form
    request = None
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

class MemberHomeForm(MyModelForm):
    class Meta:
        model = Member
        fields = [ 'email_address', 'phone_number']
