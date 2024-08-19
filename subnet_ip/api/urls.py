from django.urls import path
from subnet_ip.api import views as api_views


urlpatterns = [
    path('ip/', api_views.IPPrefixListCreateAPIView.as_view(), name='ip-addr'),
    path('ip/prefix/<int:pk>', api_views.IPPrefixDetailAPIView.as_view(),
         name='ip-detail'),
    path('ip/subnet/<int:pk>', api_views.IPSubnetsDetailAPIView.as_view(),
         name='subnet-detail'),
]
