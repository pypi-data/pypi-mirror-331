from django.contrib import admin
from django.urls import path
from states.views import indian_states_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", indian_states_list),
]
