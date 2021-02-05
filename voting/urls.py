from django.urls import path
from django.conf.urls import handler404

from . import views

app_name = 'voting'
urlpatterns = [
	#ex : /voting/
	path('', views.Homepage.as_view(), name='homepage'),
	path('login/', views.loginpage, name='login'),
	path('index/', views.IndexView.as_view(), name='index'),
	path('<int:pk>/', views.DetailView.as_view(), name='detail'),
	path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
	path('<int:question_id>/vote/', views.vote, name='vote'),
	#path('register/', views.registerpage, name='register'),
	path('logout/', views.logoutuser, name='logout'),
	path('common_homepage', views.commonhomepage, name='common_homepage'),
	path('common', views.common, name='common'),
	path('<int:question_id>/dekripsivote/', views.dekripsivote, name='dekripsivote'),
]

