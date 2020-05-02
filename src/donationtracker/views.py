from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from donationtracker.models import BalanceAccount, Donation

# registration: create a User object (for authentication) and corresponding BalanceAccount
class RegisterForm(forms.ModelForm):
    name = forms.CharField(label='Your name', max_length=80, required=True)

    class Meta:
        model = User
        fields = ('email', 'password')
        widgets = {
            'password': forms.PasswordInput,
        }

    def save(self):
        user = User.objects.create_user(self['email'].value(), self['email'].value(), self['password'].value())
        user.first_name = self['name'].value()
        user.save()

        acct = BalanceAccount()
        acct.name = user.first_name
        acct.user = user
        acct.save()
        return user

class RegisterView(CreateView):
    template_name = 'register.html'
    form_class = RegisterForm
    model = User

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Account created successfully')
        return HttpResponseRedurect(reverse('leaderboard'))

def leaderboard(request):
    return render(request, 'leaderboard.html')

class DonateForm(forms.ModelForm):
    # not completed yet
    class Meta:
        model = Donation
        fields = ('acct_to',)
        widgets = {
            'acct_to': forms.ChoiceField(),
        }

    def save(self):
        user = User.objects.create_user(self['email'].value(), self['email'].value(), self['password'].value())
        user.first_name = self['name'].value()
        user.save()

        acct = BalanceAccount()
        acct.name = user.first_name
        acct.user = user
        acct.save()
        return user

class DonateView(LoginRequiredMixin, CreateView):
    template_name = 'makedonation.html'
    form_class = DonateForm
    model = Donation

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Account created successfully')
        return HttpResponseRedurect(reverse('leaderboard'))
