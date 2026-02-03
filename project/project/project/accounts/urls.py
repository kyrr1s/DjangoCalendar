from django.urls import path

from accounts import views

app_name = "accounts"

# we can register view-class with ".as_view()"

# ideas
# - password change view

urlpatterns = [
    path("register/", views.Register.as_view(), name="register"), 
    path("login/", views.Login.as_view(), name="login"),
    path("exit/", views.Exit, name="exit"), #probably just sign out without any form, so we do not need a view
]