# survey/urls.py
from django.urls import path
from . import views

app_name = 'survey'

urlpatterns = [
    path('', views.SurveyListCreateView.as_view(), name='surveys-list'),
    path('<int:pk>/', views.SurveyDetailView.as_view(), name='surveys-detail'),
]
