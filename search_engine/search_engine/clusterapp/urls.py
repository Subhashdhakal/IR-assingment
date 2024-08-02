from django.urls import path 
from .views import cluster_view, cluster_result

urlpatterns = [
    path('cluster-result/', cluster_result, name='cluster-result'),
    path('cluster',cluster_view,name = 'cluster'),
]