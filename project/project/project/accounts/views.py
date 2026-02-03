from django.views.generic import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout

from accounts.forms import LoginForm, RegisterForm

# view-func
#@require_http_methods(['GET', 'POST'])
def Exit(request):
    """ Simple sign out function """
    logout(request)
    return redirect("accounts:login")

class Login(View):
    """ User login view """

    template = "auth/login.html"
    form = LoginForm

    #work as view-funcs
    def get(self, request):
        forms = self.form()
        context = {"form": forms}
        return render(request, self.template, context)

    def post(self, request):
        forms = self.form(request.POST)
        if forms.is_valid(): #check if user typed correct username and password
            username = forms.cleaned_data["username"]
            password = forms.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user: #create session
                login(request, user)
                return redirect("planner:planner")
        context = {"form": forms}
        return render(request, self.template, context)
    
class Register(View):
    """ User registration view """

    template = "auth/register.html"
    form = RegisterForm

    def get(self, request):
        forms = self.form()
        context = {"form": forms}
        return render(request, self.template, context)

    def post(self, request):
        forms = self.form(request.POST)
        if forms.is_valid():
            forms.save()
            return redirect("accounts:login")
        context = {"form": forms}
        return render(request, self.template, context)