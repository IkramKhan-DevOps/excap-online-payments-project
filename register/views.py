from django.contrib import messages
from django.contrib.auth import login
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from register.forms import SignUpForm


def register_request(request):

    if request.user.is_authenticated:
        return redirect("payapp:dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("payapp:dashboard")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = SignUpForm()
    return render(request=request, template_name="register/signup.html", context={"form": form})


def cross_auth(request):

    if request.user.is_authenticated:
        return redirect("payapp:dashboard")
    else:
        return redirect("register:login")
