from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

# Restrict access to admin users only
def is_admin_user(user):
    return user.is_superuser
@user_passes_test(is_admin_user, login_url='/admin/')
def dashboard_home(request):
    return render(request, '/admin_dashboard.html')
