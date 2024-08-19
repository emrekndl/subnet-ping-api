from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('subnet/<int:pk>', views.subnet, name='subnet'),
    # path('del/<int:pk>/', views.delete_ip, name='delete-ip'),
    path('state/<int:pk>/', views.ip_state_check, name='ip-state'),
]
