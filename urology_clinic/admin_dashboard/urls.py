from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard_home, name='admin_dashboard_home'),  # Dashboard home
]