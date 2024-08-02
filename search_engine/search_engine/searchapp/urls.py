from django.urls import path 
from .views import search_result, index

urlpatterns = [
    path('search-result/', search_result, name='search-result'),
    path('',index,name = 'home')
]