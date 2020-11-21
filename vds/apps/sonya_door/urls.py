from django.urls import path

from . import views 

app_name = 'sonya_door'
urlpatterns = [
	path('', views.list, name = 'list'),
	path('<int:userid>/', views.detail, name = 'detail')
]