from django.contrib import admin
from django.urls import path, include
from expenses import views


urlpatterns = [
    
    path('', views.dashboard, name='home'),
    path('admin/', admin.site.urls),
    path('expenses/', include('expenses.urls')),
]
